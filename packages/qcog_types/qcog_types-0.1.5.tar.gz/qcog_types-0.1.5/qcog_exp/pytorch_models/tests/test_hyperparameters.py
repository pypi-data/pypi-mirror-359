# type: ignore

import pytest
import logging
import pandas as pd
import torch

from ..hyperparameters import (
    ModelHyperparameters,
    OptimizerConfig,
    LossFunctionConfig,
    SchedulerConfig,
    EarlyStoppingConfig,
    PerGroupOptimizerParams,
    GeneralHSModelHyperparameters,
    PauliHSModelHyperparameters,
    GradientClippingConfig,
)


# Define the logger name consistently
HYPERPARAMS_LOGGER_NAME = "qcog_exp.pytorch_models.hyperparameters"


class TestOptimizerConfig:
    def test_optimizer_config_minimal(self):
        config = OptimizerConfig(type="Adam")
        assert config.type == "Adam"
        assert config.default_params == {}
        assert config.group_params is None

    def test_optimizer_config_with_defaults(self):
        config = OptimizerConfig(
            type="SGD", default_params={"lr": 0.01, "momentum": 0.9}
        )
        assert config.type == "SGD"
        assert config.default_params == {"lr": 0.01, "momentum": 0.9}

    def test_optimizer_config_with_groups(self):
        group_params = [
            PerGroupOptimizerParams(param_name_contains=["bias"], params={"lr": 0.001}),
            PerGroupOptimizerParams(
                param_name_contains=["weight"],
                params={"lr": 0.002, "weight_decay": 0.01},
            ),
        ]
        config = OptimizerConfig(
            type="AdamW", default_params={"lr": 0.0005}, group_params=group_params
        )
        assert config.type == "AdamW"
        assert config.default_params == {"lr": 0.0005}
        assert len(config.group_params) == 2
        assert config.group_params[0].param_name_contains == ["bias"]
        assert config.group_params[1].params == {"lr": 0.002, "weight_decay": 0.01}


class TestLossFunctionConfig:
    def test_loss_function_config_string_type(self):
        config = LossFunctionConfig(type="MSELoss", params={"reduction": "sum"})
        assert config.type == "MSELoss"
        assert config.params == {"reduction": "sum"}

    def test_loss_function_config_minimal_string(self):
        config = LossFunctionConfig(type="CrossEntropyLoss")
        assert config.type == "CrossEntropyLoss"
        assert config.params == {}


class TestSchedulerConfig:
    def test_scheduler_config_minimal(self):
        config = SchedulerConfig(type="StepLR", params={"step_size": 30})
        assert config.type == "StepLR"
        assert config.params == {"step_size": 30}
        assert config.interval == "epoch"

    def test_scheduler_config_with_interval(self):
        config = SchedulerConfig(
            type="CosineAnnealingLR", params={"T_max": 100}, interval="step"
        )
        assert config.type == "CosineAnnealingLR"
        assert config.params == {"T_max": 100}
        assert config.interval == "step"


class TestModelHyperparametersBase:
    @pytest.fixture
    def minimal_optimizer_config(self):
        return OptimizerConfig(type="Adam", default_params={"lr": 0.001})

    @pytest.fixture
    def minimal_loss_config(self):
        return LossFunctionConfig(type="MSELoss")

    def test_model_hyperparameters_minimal(
        self, minimal_optimizer_config, minimal_loss_config
    ):
        config = ModelHyperparameters(
            hsm_model="general",
            epochs=10,
            batch_size=32,
            optimizer_config=minimal_optimizer_config,
            loss_fn_config=minimal_loss_config,
            targets="output_value",
        )
        assert config.hsm_model == "general"
        assert config.epochs == 10
        assert config.batch_size == 32
        assert config.targets == "output_value"
        assert config.seed == 42
        assert config.num_workers == 0
        assert config.pin_memory is False
        assert config.device in ["cpu", "cuda", "mps"]

    def test_model_hyperparameters_device_cpu(
        self, minimal_optimizer_config, minimal_loss_config
    ):
        config = ModelHyperparameters(
            hsm_model="general",
            epochs=10,
            batch_size=32,
            optimizer_config=minimal_optimizer_config,
            loss_fn_config=minimal_loss_config,
            targets="output_value",
            device="cpu",
        )
        assert config.device == "cpu"

    def test_model_hyperparameters_invalid_device(
        self, minimal_optimizer_config, minimal_loss_config
    ):
        with pytest.raises(ValueError, match="Unsupported device: my_gpu"):
            ModelHyperparameters(
                hsm_model="general",
                epochs=10,
                batch_size=32,
                optimizer_config=minimal_optimizer_config,
                loss_fn_config=minimal_loss_config,
                targets="output_value",
                device="my_gpu",
            )

    def test_model_hyperparameters_full(
        self, minimal_optimizer_config, minimal_loss_config
    ):
        scheduler_conf = SchedulerConfig(type="StepLR", params={"step_size": 10})
        early_stop_conf = EarlyStoppingConfig(monitor="val_loss", patience=5)
        grad_clip_conf = GradientClippingConfig(max_norm=1.0)

        config = ModelHyperparameters(
            hsm_model="pauli",
            epochs=100,
            batch_size=64,
            seed=123,
            optimizer_config=minimal_optimizer_config,
            loss_fn_config=minimal_loss_config,
            scheduler_config=scheduler_conf,
            early_stopping_config=early_stop_conf,
            gradient_clipping_config=grad_clip_conf,
            num_workers=4,
            pin_memory=True,
            targets="target_col",
            device="cuda",
        )
        assert config.hsm_model == "pauli"
        assert config.epochs == 100
        assert config.batch_size == 64
        assert config.seed == 123
        assert config.num_workers == 4
        assert config.pin_memory is True
        assert config.targets == "target_col"
        assert config.device == "cuda"
        assert config.scheduler_config.type == "StepLR"
        assert config.early_stopping_config.monitor == "val_loss"
        assert config.gradient_clipping_config.max_norm == 1.0

    def test_scheduler_early_stopping_monitor_mismatch_warning(
        self, minimal_optimizer_config, minimal_loss_config, caplog
    ):
        scheduler_conf = SchedulerConfig(
            type="ReduceLROnPlateau", params={"monitor": "val_accuracy"}
        )
        early_stop_conf = EarlyStoppingConfig(monitor="val_loss", patience=5)

        caplog.clear()
        with caplog.at_level(logging.WARNING):
            ModelHyperparameters(
                hsm_model="general",
                epochs=10,
                batch_size=32,
                optimizer_config=minimal_optimizer_config,
                loss_fn_config=minimal_loss_config,
                scheduler_config=scheduler_conf,
                early_stopping_config=early_stop_conf,
                targets="output",
            )
        assert any(
            "Scheduler 'ReduceLROnPlateau' monitors 'val_accuracy' while EarlyStopping monitors 'val_loss'"
            in record.message
            for record in caplog.records
        )

    def test_scheduler_non_standard_monitor_warning(
        self, minimal_optimizer_config, minimal_loss_config, caplog
    ):
        scheduler_conf = SchedulerConfig(
            type="ReduceLROnPlateau", params={"monitor": "custom_metric"}
        )
        caplog.clear()
        with caplog.at_level(logging.WARNING):
            ModelHyperparameters(
                hsm_model="general",
                epochs=10,
                batch_size=32,
                optimizer_config=minimal_optimizer_config,
                loss_fn_config=minimal_loss_config,
                scheduler_config=scheduler_conf,
                targets="output",
            )
        assert any(
            "Scheduler 'ReduceLROnPlateau' monitor 'custom_metric' might not be standard"
            in record.message
            for record in caplog.records
        )

    def test_early_stopping_non_standard_monitor_warning(
        self, minimal_optimizer_config, minimal_loss_config, caplog
    ):
        early_stop_conf = EarlyStoppingConfig(monitor="my_custom_metric", patience=5)
        caplog.clear()
        with caplog.at_level(logging.WARNING):
            ModelHyperparameters(
                hsm_model="general",
                epochs=10,
                batch_size=32,
                optimizer_config=minimal_optimizer_config,
                loss_fn_config=minimal_loss_config,
                early_stopping_config=early_stop_conf,
                targets="output",
            )
        assert any(
            "EarlyStopping monitor 'my_custom_metric' might not be standard"
            in record.message
            for record in caplog.records
        )

    def test_optimizer_lr_warning(self, minimal_loss_config, caplog):
        opt_conf = OptimizerConfig(type="Adam")  # No lr
        caplog.clear()
        with caplog.at_level(logging.WARNING):
            ModelHyperparameters(
                hsm_model="general",
                epochs=10,
                batch_size=32,
                optimizer_config=opt_conf,
                loss_fn_config=minimal_loss_config,
                targets="output",
            )
        assert any(
            (
                "Learning rate ('lr' or 'learning_rate') not found" in record.message
                and "The optimizer's default LR will be used if available."
                in record.message
            )
            for record in caplog.records
        )

    def test_optimizer_lr_in_group_no_warning(self, minimal_loss_config, caplog):
        group_params = [
            PerGroupOptimizerParams(param_name_contains=["layer1"], params={"lr": 0.01})
        ]
        opt_conf = OptimizerConfig(type="Adam", group_params=group_params)
        caplog.clear()
        with caplog.at_level(logging.WARNING):
            ModelHyperparameters(
                hsm_model="general",
                epochs=10,
                batch_size=32,
                optimizer_config=opt_conf,
                loss_fn_config=minimal_loss_config,
                targets="output",
            )
        assert not any(
            "Learning rate ('lr' or 'learning_rate') not found" in record.message
            for record in caplog.records
        )


class TestMultiTargetFunctionality:
    """Test the new multi-target and input_features functionality."""
    
    @pytest.fixture
    def minimal_optimizer_config(self):
        return OptimizerConfig(type="Adam", default_params={"lr": 0.001})

    @pytest.fixture
    def minimal_loss_config(self):
        return LossFunctionConfig(type="MSELoss")

    def test_targets_string_format(self, minimal_optimizer_config, minimal_loss_config):
        """Test that targets accepts a string."""
        config = ModelHyperparameters(
            hsm_model="general",
            epochs=10,
            batch_size=32,
            optimizer_config=minimal_optimizer_config,
            loss_fn_config=minimal_loss_config,
            targets="target1",
        )
        assert config.targets == "target1"
        assert config.targets_list == ["target1"]

    def test_targets_list_format(self, minimal_optimizer_config, minimal_loss_config):
        """Test that targets accepts a list of strings."""
        config = ModelHyperparameters(
            hsm_model="general",
            epochs=10,
            batch_size=32,
            optimizer_config=minimal_optimizer_config,
            loss_fn_config=minimal_loss_config,
            targets=["target1"],
        )
        assert config.targets == ["target1"]
        assert config.targets_list == ["target1"]

    def test_multiple_targets(self, minimal_optimizer_config, minimal_loss_config):
        """Test multiple targets functionality."""
        config = ModelHyperparameters(
            hsm_model="general",
            epochs=10,
            batch_size=32,
            optimizer_config=minimal_optimizer_config,
            loss_fn_config=minimal_loss_config,
            targets=["target1", "target2", "target3"],
        )
        assert config.targets == ["target1", "target2", "target3"]
        assert config.targets_list == ["target1", "target2", "target3"]

    def test_input_features_specified(self, minimal_optimizer_config, minimal_loss_config):
        """Test input_features specification."""
        config = ModelHyperparameters(
            hsm_model="general",
            epochs=10,
            batch_size=32,
            optimizer_config=minimal_optimizer_config,
            loss_fn_config=minimal_loss_config,
            targets="target1",
            input_features=["feature1", "feature2", "feature3"],
        )
        assert config.targets == "target1"
        assert config.input_features == ["feature1", "feature2", "feature3"]

    def test_empty_targets_validation(self, minimal_optimizer_config, minimal_loss_config):
        """Test that empty targets list raises validation error."""
        with pytest.raises(ValueError, match="At least one target must be specified"):
            ModelHyperparameters(
                hsm_model="general",
                epochs=10,
                batch_size=32,
                optimizer_config=minimal_optimizer_config,
                loss_fn_config=minimal_loss_config,
                targets=[],
            )

    def test_duplicate_targets_validation(self, minimal_optimizer_config, minimal_loss_config):
        """Test that duplicate targets raise validation error."""
        with pytest.raises(ValueError, match="Target columns must be unique"):
            ModelHyperparameters(
                hsm_model="general",
                epochs=10,
                batch_size=32,
                optimizer_config=minimal_optimizer_config,
                loss_fn_config=minimal_loss_config,
                targets=["target1", "target1"],
            )

    def test_empty_input_features_validation(self, minimal_optimizer_config, minimal_loss_config):
        """Test that empty input_features list raises validation error."""
        with pytest.raises(ValueError, match="If input_features is specified, it cannot be empty"):
            ModelHyperparameters(
                hsm_model="general",
                epochs=10,
                batch_size=32,
                optimizer_config=minimal_optimizer_config,
                loss_fn_config=minimal_loss_config,
                targets="target1",
                input_features=[],
            )

    def test_duplicate_input_features_validation(self, minimal_optimizer_config, minimal_loss_config):
        """Test that duplicate input features raise validation error."""
        with pytest.raises(ValueError, match="Input feature columns must be unique"):
            ModelHyperparameters(
                hsm_model="general",
                epochs=10,
                batch_size=32,
                optimizer_config=minimal_optimizer_config,
                loss_fn_config=minimal_loss_config,
                targets="target1",
                input_features=["feature1", "feature1"],
            )

    def test_targets_input_features_overlap_validation(self, minimal_optimizer_config, minimal_loss_config):
        """Test that overlap between targets and input_features raises validation error."""
        with pytest.raises(ValueError, match="Target columns and input feature columns cannot overlap"):
            ModelHyperparameters(
                hsm_model="general",
                epochs=10,
                batch_size=32,
                optimizer_config=minimal_optimizer_config,
                loss_fn_config=minimal_loss_config,
                targets=["target1", "target2"],
                input_features=["feature1", "target1", "feature2"],
            )

    def test_targets_list_property_with_string(self, minimal_optimizer_config, minimal_loss_config):
        """Test targets_list property returns list for string input."""
        config = ModelHyperparameters(
            hsm_model="general",
            epochs=10,
            batch_size=32,
            optimizer_config=minimal_optimizer_config,
            loss_fn_config=minimal_loss_config,
            targets="single_target",
        )
        assert isinstance(config.targets_list, list)
        assert config.targets_list == ["single_target"]

    def test_targets_list_property_with_list(self, minimal_optimizer_config, minimal_loss_config):
        """Test targets_list property returns same list for list input."""
        targets = ["target1", "target2"]
        config = ModelHyperparameters(
            hsm_model="general",
            epochs=10,
            batch_size=32,
            optimizer_config=minimal_optimizer_config,
            loss_fn_config=minimal_loss_config,
            targets=targets,
        )
        assert isinstance(config.targets_list, list)
        assert config.targets_list == targets


class TestGeneralHSModelMultiTarget:
    """Test multi-target functionality for GeneralHSModelHyperparameters."""
    
    @pytest.fixture
    def base_hyperparameters(self):
        return {
            "hsm_model": "general",
            "epochs": 1,
            "batch_size": 1,
            "optimizer_config": OptimizerConfig(
                type="Adam", default_params={"lr": 0.001}
            ),
            "loss_fn_config": LossFunctionConfig(type="MSELoss"),
            "device": "cpu",
        }

    def test_single_target_string_matching_output_count(self, base_hyperparameters):
        """Test single target as string with matching output_operator_count."""
        config = GeneralHSModelHyperparameters(
            **base_hyperparameters,
            targets="target1",
            input_operator_count=5,
            output_operator_count=1,
            hilbert_space_dims=4,
        )
        assert config.targets == "target1"
        assert config.targets_list == ["target1"]
        assert config.output_operator_count == 1

    def test_single_target_list_matching_output_count(self, base_hyperparameters):
        """Test single target as list with matching output_operator_count."""
        config = GeneralHSModelHyperparameters(
            **base_hyperparameters,
            targets=["target1"],
            input_operator_count=5,
            output_operator_count=1,
            hilbert_space_dims=4,
        )
        assert config.targets == ["target1"]
        assert config.targets_list == ["target1"]
        assert config.output_operator_count == 1

    def test_multiple_targets_matching_output_count(self, base_hyperparameters):
        """Test multiple targets with matching output_operator_count."""
        config = GeneralHSModelHyperparameters(
            **base_hyperparameters,
            targets=["target1", "target2"],
            input_operator_count=5,
            output_operator_count=2,
            hilbert_space_dims=4,
        )
        assert config.targets == ["target1", "target2"]
        assert config.targets_list == ["target1", "target2"]
        assert config.output_operator_count == 2

    def test_output_count_mismatch_string_target(self, base_hyperparameters):
        """Test validation error when output_operator_count doesn't match single string target."""
        with pytest.raises(ValueError, match="Output operator count .* must match the number of targets"):
            GeneralHSModelHyperparameters(
                **base_hyperparameters,
                targets="target1",  # 1 target
                input_operator_count=5,
                output_operator_count=2,  # Should be 1
                hilbert_space_dims=4,
            )

    def test_output_count_mismatch_multiple_targets(self, base_hyperparameters):
        """Test validation error when output_operator_count doesn't match multiple targets."""
        with pytest.raises(ValueError, match="Output operator count .* must match the number of targets"):
            GeneralHSModelHyperparameters(
                **base_hyperparameters,
                targets=["target1", "target2"],  # 2 targets
                input_operator_count=5,
                output_operator_count=1,  # Should be 2
                hilbert_space_dims=4,
            )


class TestPauliHSModelMultiTarget:
    """Test multi-target functionality for PauliHSModelHyperparameters."""
    
    @pytest.fixture
    def base_hyperparameters_pauli(self):
        return {
            "hsm_model": "pauli",
            "epochs": 1,
            "batch_size": 1,
            "optimizer_config": OptimizerConfig(
                type="Adam", default_params={"lr": 0.001}
            ),
            "loss_fn_config": LossFunctionConfig(type="MSELoss"),
            "device": "cpu",
        }

    def test_single_target_string_matching_output_count(self, base_hyperparameters_pauli):
        """Test single target as string with matching output_operator_count."""
        config = PauliHSModelHyperparameters(
            **base_hyperparameters_pauli,
            targets="target1",
            input_operator_count=3,
            output_operator_count=1,
            qubits_count=2,
        )
        assert config.targets == "target1"
        assert config.targets_list == ["target1"]
        assert config.output_operator_count == 1

    def test_multiple_targets_matching_output_count(self, base_hyperparameters_pauli):
        """Test multiple targets with matching output_operator_count."""
        config = PauliHSModelHyperparameters(
            **base_hyperparameters_pauli,
            targets=["target1", "target2", "target3"],
            input_operator_count=3,
            output_operator_count=3,
            qubits_count=2,
        )
        assert config.targets == ["target1", "target2", "target3"]
        assert config.targets_list == ["target1", "target2", "target3"]
        assert config.output_operator_count == 3

    def test_output_count_mismatch_pauli(self, base_hyperparameters_pauli):
        """Test validation error when output_operator_count doesn't match targets for Pauli model."""
        with pytest.raises(ValueError, match="Output operator count .* must match the number of targets"):
            PauliHSModelHyperparameters(
                **base_hyperparameters_pauli,
                targets=["target1", "target2"],  # 2 targets
                input_operator_count=3,
                output_operator_count=1,  # Should be 2
                qubits_count=2,
            )


class TestGeneralHSModelHyperparameters:
    @pytest.fixture
    def base_hyperparameters(self):
        return {
            "hsm_model": "general",
            "epochs": 1,
            "batch_size": 1,
            "optimizer_config": OptimizerConfig(
                type="Adam", default_params={"lr": 0.001}
            ),
            "loss_fn_config": LossFunctionConfig(type="MSELoss"),
            "targets": "target",
            "device": "cpu",  # Force CPU for tensor comparisons
        }

    def test_general_hsm_minimal(self, base_hyperparameters):
        config = GeneralHSModelHyperparameters(
            **base_hyperparameters,
            input_operator_count=2,
            output_operator_count=1,
            hilbert_space_dims=3,
        )
        assert config.input_operator_count == 2
        assert config.output_operator_count == 1
        assert config.hilbert_space_dims == 3
        assert config.complex is True

    def test_general_hsm_with_optional_params(self, base_hyperparameters):
        config = GeneralHSModelHyperparameters(
            **base_hyperparameters,
            input_operator_count=2,
            output_operator_count=1,
            hilbert_space_dims=3,
            beta=0.5,
            complex=True,
            eigh_eps=1e-7,
        )
        assert config.beta == 0.5
        assert config.complex is True
        assert config.eigh_eps == 1e-7

    # Note: Device validation is covered by ModelHyperparameters tests.


class TestPauliHSModelHyperparameters:
    @pytest.fixture
    def base_hyperparameters_pauli(self):
        return {
            "hsm_model": "pauli",
            "epochs": 1,
            "batch_size": 1,
            "optimizer_config": OptimizerConfig(
                type="Adam", default_params={"lr": 0.001}
            ),
            "loss_fn_config": LossFunctionConfig(type="MSELoss"),
            "targets": "target",
            "device": "cpu",
        }

    def test_pauli_hsm_minimal(self, base_hyperparameters_pauli):
        config = PauliHSModelHyperparameters(
            **base_hyperparameters_pauli,
            input_operator_count=3,
            output_operator_count=1,
            qubits_count=2,
        )
        assert config.input_operator_count == 3
        assert config.output_operator_count == 1
        assert config.qubits_count == 2
        # No assertion for hilbert_space_dims

    def test_pauli_hsm_full(self, base_hyperparameters_pauli):
        config = PauliHSModelHyperparameters(
            **base_hyperparameters_pauli,
            input_operator_count=3,
            output_operator_count=1,
            qubits_count=3,
            input_operator_pauli_weight=1,
            output_operator_pauli_weight=2,
            eigh_eps=1e-9,
        )
        assert config.input_operator_pauli_weight == 1
        assert config.output_operator_pauli_weight == 2
        assert config.eigh_eps == 1e-9


class TestEarlyStoppingConfig:
    def test_early_stopping_minimal(self):
        config = EarlyStoppingConfig(monitor="val_loss")
        assert config.monitor == "val_loss"
        assert config.min_delta == 0.0001
        assert config.patience == 10
        assert config.mode == "min"
        assert config.verbose is False
        assert config.restore_best_weights is True

    def test_early_stopping_full(self):
        config = EarlyStoppingConfig(
            monitor="train_acc",
            min_delta=0.01,
            patience=20,
            mode="max",
            verbose=True,
            restore_best_weights=False,
        )
        assert config.monitor == "train_acc"
        assert config.min_delta == 0.01
        assert config.patience == 20
        assert config.mode == "max"
        assert config.verbose is True
        assert config.restore_best_weights is False


class TestGradientClippingConfig:
    def test_gradient_clipping_minimal(self):
        config = GradientClippingConfig(max_norm=1.0)
        assert config.max_norm == 1.0
        assert config.norm_type == 2.0

    def test_gradient_clipping_full(self):
        config = GradientClippingConfig(max_norm=0.5, norm_type=1.0)
        assert config.max_norm == 0.5
        assert config.norm_type == 1.0



