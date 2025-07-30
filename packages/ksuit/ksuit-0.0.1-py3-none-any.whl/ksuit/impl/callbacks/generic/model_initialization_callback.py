from __future__ import annotations

from typing import TYPE_CHECKING

from ksuit.core.callbacks import Callback
from ksuit.utils import module_utils

if TYPE_CHECKING:
    from ksuit.core.trainers import TrainingContext


class ModelInitializationCallback(Callback):
    def __init__(self, *args, merge_depth: int = 2, **kwargs):
        super().__init__(*args, **kwargs)
        self.merge_depth = merge_depth

    def _on_fit_start(self, ctx: TrainingContext) -> None:
        if self.distributed_provider.has_tensor_parallel:
            return

        groups = module_utils.get_grouped_model_initialization_groups(ctx.model, merge_depth=self.merge_depth)
        self.logger.info("--------------------")
        self.logger.info("model initialization")
        self.logger.info("--------------------")
        self.logger.info("weights (init_std != 0.02)")
        for group in groups.weight_groups:
            if group.initialization == "std=2e-2":
                continue
            if len(group) > 0:
                len_str = f" ({len(group)} params)"
            else:
                len_str = ""
            self.logger.info(f"- {group.group_name}{len_str}: {group.initialization}")
        self.logger.info("biases (initialization != zeros)")
        for group in groups.bias_groups:
            if group.initialization == "zeros":
                continue
            if len(group) > 0:
                len_str = f" ({len(group)} params)"
            else:
                len_str = ""
            self.logger.info(f"- {group.group_name}{len_str}: {group.initialization}")
        self.logger.info("nn.Parameters")
        for group in groups.parameter_groups:
            self.logger.info(f"- {group.group_name} ({len(group)} params): {group.initialization}")
