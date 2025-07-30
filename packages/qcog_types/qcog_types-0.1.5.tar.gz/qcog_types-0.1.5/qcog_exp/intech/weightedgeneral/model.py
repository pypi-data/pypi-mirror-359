import numpy as np  # type: ignore
from typing import Any, Callable, Literal, NotRequired, TypedDict, Unpack
import torch  # type: ignore
from qcog_torch.layers.general import PytorchGeneralHSM  # type: ignore
from qcog_torch.layers.weighted import WeightedLayer  # type: ignore
import pandas as pd  # type: ignore
from torch.utils.data import Dataset, DataLoader  # type: ignore
from qcog_torch import nptype  # type: ignore
from resolve_dataset import resolve_dataset  # type: ignore
from split_dataset import split_dataset  # type: ignore
from hyperparameters import Hyperparameters  # type: ignore

# HELLO
# Required exports --------------------------------------------------------+
# The following exports are used by the API to determine the version       |
# of the train and predict functions.                                      |
#                                                                          |
# Hyperparameters will eventually be used to generate a package for        |
# the client that will be used to validate and type hint the parameters    |
# -------------------------------------------------------------------------+

TRAIN_VERSION = "v0.0.1"
PREDICT_VERSION = "v0.0.1"

# -------------------------------------------------------------------------+


ColumnName = str
Function = Literal["to_datetime"]
ApplyTransform = dict[ColumnName, Function]


class DataFrameDataset(Dataset):
    """DataFrame Dataset."""

    def __init__(self, df: pd.DataFrame, target: str, device: str):
        """
        Initialize a dataset from a dataframe

        Parameters
        ----------
        df: pd.DataFrame
            Dataframe with data to use
        target: str
            Target variable name which must be a column in df
        device: str
            Device for torch
        """
        target_data = df[[target]].values.astype(nptype(), copy=True)
        inputs_data = df.drop([target], axis=1).values.astype(nptype(), copy=True)
        self.target = torch.tensor(target_data).to(device=device)
        self.inputs = torch.tensor(inputs_data).to(device=device)

    def __len__(self) -> int:
        """Get the length of the dataset."""
        return len(self.target)

    def __getitem__(self, idx: int) -> tuple[np.ndarray, np.ndarray]:
        """Get an item from the dataset."""
        return self.inputs[idx, :], self.target[idx, :]


StateDict = dict[str, Any]


class Checkpoint(TypedDict):
    model_state_dict: StateDict
    timestamp: str
    current_epoch: int
    other_states: dict[str, Any] | None
    optimizer_state_dict: dict[str, Any] | None
    hyperparameters: dict[str, Any] | None
    metrics: dict[str, Any] | None


class SaveCheckpointKwargs(TypedDict):
    """
    Kwargs for the save_checkpoint method.

    model_state_dict: The model state dictionary when the checkpoint was saved.
    current_epoch: The current epoch when the checkpoint was saved.
    other_states: Other states to save (e.g, loss, optimizers, etc.)
    optimizer_state_dict: The optimizer state dictionary when the checkpoint was saved.
    hyperparameters: The hyperparameters of the experiment.
    metrics: The metrics of the experiment at the time the checkpoint was saved.
    """

    model_state_dict: dict[str, Any]
    current_epoch: int
    other_states: dict[str, Any] | None
    hyperparameters: dict[str, Any] | None
    metrics: dict[str, Any] | None


class TrainContext(TypedDict):
    status_id: str  # The train identifier
    save_checkpoint: NotRequired[Callable[[Unpack[SaveCheckpointKwargs]], None]]
    load_last_checkpoint: NotRequired[Callable[[], Checkpoint | None]]
    dataset_bucket: str
    dataset_format: str


def train(
    context: TrainContext,
    dataset_path: str,
    *,
    params: dict[str, Any],
):
    hyperparameters_dict: dict = params.get("hyperparameters", None)
    hyperparameters = Hyperparameters.model_validate(hyperparameters_dict).model_dump()

    if hyperparameters is None:
        raise ValueError("Hyperparameters must be provided")

    # Extract hooks to save and extract checkpoints
    save_checkpoint_hook = context.get("save_checkpoint", None)
    load_last_checkpoint_hook = context.get("load_last_checkpoint", None)

    # Extract dataset information from the context
    dataset_bucket = context.get("dataset_bucket", "s3")
    dataset_format = context.get("dataset_format", "csv")

    # Check if there is a checkpoint
    checkpoint: Checkpoint | None = None

    if load_last_checkpoint_hook:
        checkpoint = load_last_checkpoint_hook()

    seed = hyperparameters.get("seed", 42)
    batch_size = hyperparameters.get("batch_size", 100)
    learning_rate = hyperparameters.get("learning_rate", 1e-2)
    weighted_learning_rate = hyperparameters.get("weighted_learning_rate", 1e-2)
    target = hyperparameters.get("target", None)
    epochs = hyperparameters.get("epochs", 100)
    hilbert_space_dims = hyperparameters.get("hilbert_space_dims", 10)
    split = hyperparameters.get("split", 0.8)

    ###############################################################
    # Referencing checkpoint parameters
    ###############################################################

    epochs_completed: int = 0
    optimizer_state_dict: dict[str, Any] | None = None
    model_state_dict: dict[str, Any] | None = None
    loss: float | None = None

    if checkpoint:
        epochs_completed = checkpoint.get("current_epoch", 0)
        model_state_dict = checkpoint.get("model_state_dict", None)

        if not model_state_dict:
            raise ValueError(
                "Model state dictionary must be provided when saving a checkpoint"
            )

        other_states = checkpoint.get("other_states", None)

        if other_states:
            optimizer_state_dict = other_states.get("optimizer_state_dict", None)
            loss = other_states.get("loss", None)

        if not optimizer_state_dict:
            raise ValueError(
                "Optimizer state dictionary must be provided when saving a checkpoint"
            )

    epochs -= epochs_completed

    # ---------------------------------------------------------------
    if target is None:
        raise ValueError("Target must be provided")

    torch.manual_seed(seed)

    device = (
        "cuda"
        if torch.cuda.is_available()
        else "mps"
        if torch.backends.mps.is_available()
        else "cpu"
    )

    print(f"Using device: {device}")
    print(f"Dataset path: {dataset_path}")

    dataset = resolve_dataset(dataset_path, dataset_bucket, dataset_format)
    train_df, test_df = split_dataset(dataset, test_size=split)

    train_dataset = DataFrameDataset(df=train_df, target=target, device=device)
    test_dataset = DataFrameDataset(df=test_df, target=target, device=device)
    train_dataloader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    test_dataloader = DataLoader(
        test_dataset, batch_size=test_df.shape[0], shuffle=True
    )

    input_operator_count = train_df.shape[1] - 1
    output_operator_count = 1

    hsm_layer = PytorchGeneralHSM(
        input_operator_count=input_operator_count,
        output_operator_count=output_operator_count,
        hilbert_space_dims=hilbert_space_dims,
        device=device,
    )

    model = WeightedLayer(hsm_layer=hsm_layer, device=device)

    # Load the checkpoint if it exists
    if model_state_dict:
        model.load_state_dict(model_state_dict)

    opt_params: list[dict[str, Any]] = [
        {
            "params": [
                p for n, p in model.named_parameters() if "input_weights" not in n
            ]
        },
        {
            "params": [p for n, p in model.named_parameters() if "input_weights" in n],
            "lr": weighted_learning_rate,
        },
    ]

    optimizer = torch.optim.Adam(params=opt_params, lr=learning_rate, amsgrad=True)

    if optimizer_state_dict:
        optimizer.load_state_dict(optimizer_state_dict)

    loss_fn = torch.nn.MSELoss()

    for epoch in range(epochs):
        # Ensure that our model has gradient tracking on
        model.train(True)
        for batch, (X, y) in enumerate(train_dataloader):
            pred = model(X)
            loss = loss_fn(pred, y)
            print(f"Epoch {epoch}[{batch}]: Loss {loss:.4f}")

            if loss is not None:
                # Backpropagation
                loss.backward()  # type: ignore
                optimizer.step()
                optimizer.zero_grad()

        # Save the checkpoint
        if save_checkpoint_hook:
            save_checkpoint_hook(
                model_state_dict=model.state_dict(),
                current_epoch=epoch + 1,
                other_states={
                    "optimizer_state_dict": optimizer.state_dict(),
                    "loss": loss.item() if loss is not None else None,  # type: ignore
                },
                hyperparameters=hyperparameters,
                metrics={
                    "loss": loss.item() if loss is not None else None,  # type: ignore
                },
            )

    # Test
    model.eval()
    num_batches = len(test_dataloader)
    test_loss = 0.0
    with torch.no_grad():
        for X, y in test_dataloader:
            pred = model(X)
            test_loss += loss_fn(pred, y).item()

    test_loss /= num_batches

    return {
        "metrics": {
            "test_loss": test_loss,
        }
    }


class PredictContext(TypedDict):
    pass


def predict(
    context: PredictContext,
    checkpoint: Checkpoint,
    *,
    params: dict[str, Any],
) -> pd.DataFrame:
    hyperparameters = checkpoint.get("hyperparameters", None)

    # Probably we should have some default values here
    if not hyperparameters:
        raise ValueError("Hyperparameters must be provided")

    dataset_bucket = context.get("dataset_bucket", "s3")
    dataset_format = context.get("dataset_format", "csv")

    device = (
        "cuda"
        if torch.cuda.is_available()
        else "mps"
        if torch.backends.mps.is_available()
        else "cpu"
    )

    print(hyperparameters)
    # Rehydrate the model
    model = WeightedLayer(
        hsm_layer=PytorchGeneralHSM(
            input_operator_count=hyperparameters[
                "hilbert_space_dims"
            ],  # Wrong but we are gonna live with it
            output_operator_count=1,
            hilbert_space_dims=hyperparameters["hilbert_space_dims"],
            device=device,
        ),
        device=device,
    )

    model.load_state_dict(checkpoint.get("model_state_dict"))  # type: ignore

    dataset_path = params.get("dataset_path", None)
    dataset_buffer = params.get("dataset_buffer", None)

    if dataset_path is None and dataset_buffer is None:
        raise ValueError("Either dataset path or dataset buffer must be provided")

    dataset = resolve_dataset(dataset_path, dataset_bucket, dataset_format)
    X = dataset.df_ref()

    model.eval()

    with torch.no_grad():
        pred = model(X)

    return {"predictions": pred}


if __name__ == "__main__":
    import dotenv  # type: ignore

    dotenv.load_dotenv()

    train(
        context={
            "status_id": "test",
            "dataset_bucket": "s3",
            "dataset_format": "csv",
        },
        dataset_path="s3://dataset-repository-dev-us-east-2/intech-sample/dataset.csv",
        params={
            "hyperparameters": {
                "epochs": 100,
                "learning_rate": 1e-2,
                "weighted_learning_rate": 1e-2,
                "target": "scaled_demedian_forward_return_22d",
                "batch_size": 100,
                "seed": 42,
                "hilbert_space_dims": 10,
            },
        },
    )
