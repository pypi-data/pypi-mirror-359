from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Self

import torch.optim
from torch import nn

from ksuit.utils import config_utils, module_utils
from ksuit.utils.epoch_update_sample import EpochUpdateSample

if TYPE_CHECKING:
    from torch.distributed.tensor.parallel import ParallelStyle

    from ksuit.core.checkpoint_converters import CheckpointConverter
    from ksuit.core.initializers import Initializer
    from ksuit.core.providers import DistributedProvider
    from ksuit.core.trainers import TrainingContext


class Model(nn.Module):
    @classmethod
    def get_testrun_model(cls, config: dict[str, Any], **kwargs) -> Self:
        raise NotImplementedError(f"{type(cls).__name__} does not support testrun")

    def __init_subclass__(cls):
        if cls.get_tensor_parallel_plan != Model.get_tensor_parallel_plan:
            raise TypeError(
                f"{cls.__name__} must not override get_tensor_parallel_plan, "
                f"override _get_tensor_parallel_plan instead."
            )
    def __init__(
        self,
        use_model_parameter_initializer: bool = True,
        run_config: dict[str, Any] = None,
        ctor_kwargs_from_trainer: dict[str, Any] | None = None,
        distributed_provider: DistributedProvider | None = None,
    ):
        super().__init__()
        self.logger = logging.getLogger(type(self).__name__)
        self.use_model_parameter_initializer = use_model_parameter_initializer
        self.distributed_provider = distributed_provider
        # store trainer-specific kwargs that were passed to the model constructor
        self.ctor_kwargs_from_trainer = ctor_kwargs_from_trainer
        # store run_config for easy resuming/evaluation
        self.run_config = run_config

    def to_checkpoint(
        self,
        checkpoint: EpochUpdateSample | str,
        eus: EpochUpdateSample,
        run_id: str,
        interval_type: str,
    ) -> dict[str, Any]:
        data = dict(
            state_dict=self.state_dict(),
            eus=dict(eus),
            eus_minspec={interval_type: dict(eus)[interval_type]},
            run_id=run_id,
        )
        ctor_kwargs_from_run_config = (self.run_config or {}).get("model", {})
        data["model_ctor_kwargs"] = dict(
            **ctor_kwargs_from_run_config,
            **(self.ctor_kwargs_from_trainer or {}),
        )
        data["run_config"] = self.run_config
        checkpoint_converters = self.get_checkpoint_converters()
        data["checkpoint_converters"] = {
            key: config_utils.object_to_config(checkpoint_converter)
            for key, checkpoint_converter in checkpoint_converters.items()
        }
        # checkpoint can be, e.g., E1_U2_S8 or "latest"
        if isinstance(checkpoint, EpochUpdateSample):
            data["checkpoint"] = dict(checkpoint)
        elif isinstance(checkpoint, str):
            data["checkpoint"] = checkpoint
        else:
            raise TypeError(f"invalid checkpoint type {type(checkpoint).__name__}")
        return data

    def get_checkpoint_converters(self) -> dict[str, CheckpointConverter]:
        return {}

    def get_tensor_parallel_plan(self) -> dict[str, ParallelStyle]:
        plan = self._get_tensor_parallel_plan()
        name_to_module = {name: module for name, module in self.named_modules()}
        for plan_name in plan.keys():
            if plan_name not in name_to_module:
                raise RuntimeError(f"{plan_name} is not a named module (valid names: {list(name_to_module.keys())})")
            if type(name_to_module[plan_name]) is not nn.Linear:
                raise TypeError(f"{plan_name} is not a nn.Linear but a {type(name_to_module[plan_name]).__name__}")
        return plan

    def _get_tensor_parallel_plan(self) -> dict[str, ParallelStyle]:
        raise RuntimeError("tensor parallel not supported")

    @property
    def device(self) -> torch.device | None:
        return module_utils.get_device(self)

    @property
    def num_parameters(self) -> int:
        return module_utils.get_num_parameters(self)

    @property
    def num_trainable_parameters(self) -> int:
        return module_utils.get_num_trainable_parameters(self)

    @property
    def num_frozen_parameters(self) -> int:
        return module_utils.get_num_frozen_parameters(self)

    def on_fit_start(self, ctx: TrainingContext) -> None:
        pass

    def on_epoch_start(self, ctx: TrainingContext) -> None:
        pass

    def on_update_start(self, ctx: TrainingContext) -> None:
        pass

    def on_after_backward(self, ctx: TrainingContext) -> None:
        pass

    def on_before_optimizer_step(self, ctx: TrainingContext) -> None:
        pass

    def on_before_zero_grad(self, ctx: TrainingContext) -> None:
        pass

    def on_update_end(self, ctx: TrainingContext) -> None:
        pass

    def on_epoch_end(self, ctx: TrainingContext) -> None:
        pass

    def on_fit_end(self, ctx: TrainingContext) -> None:
        pass
