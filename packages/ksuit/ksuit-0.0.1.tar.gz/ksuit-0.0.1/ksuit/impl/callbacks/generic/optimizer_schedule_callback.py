from __future__ import annotations

from typing import TYPE_CHECKING

from ksuit.core.callbacks import PeriodicCallback
from ksuit.core.optim import LrSchedule

if TYPE_CHECKING:
    from ksuit.core.trainers import TrainingContext


class OptimizerScheduleCallback(PeriodicCallback):
    def _should_invoke_after_update(self, update: int) -> bool:
        if update == 1:
            return True
        return super()._should_invoke_after_update(update)

    def _invoke(self, ctx: TrainingContext) -> None:
        for param_group in ctx.optimizer.torch_optim.param_groups:
            group_name = f"/{param_group['name']}" if "name" in param_group else ""
            if len(ctx.optimizer.param_group_modifiers) == 0:
                continue
            # lr schedule is first param_group_modifier if it is passed via lr_schedule
            if isinstance(ctx.optimizer.param_group_modifiers[0], LrSchedule):
                lr = param_group["lr"]
                self.tracker.add_scalar(f"optim/lr{group_name}", lr)
