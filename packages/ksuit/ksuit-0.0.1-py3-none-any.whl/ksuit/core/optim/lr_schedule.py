from typing import Any

from torch import nn

from ksuit.core.factories import ScheduleFactory
from ksuit.core.schedules import Schedule

from .param_group_modifier import ParamGroupModifier


class LrSchedule(ParamGroupModifier):
    def __init__(self, schedule: Schedule, **kwargs):
        super().__init__(**kwargs)
        self.schedule = ScheduleFactory.create_object(
            schedule,
            max_value=self.param_group_defaults["lr"],
            training_progress_provider=self.training_progress_provider,
        )

    def populate_parameter_properties(
        self,
        parameter_properties: list[dict[str, Any]],
        model: nn.Module | None = None,
    ) -> list[dict[str, Any]]:
        for parameter_properties_item in parameter_properties:
            if "lr" in parameter_properties_item:
                raise RuntimeError(
                    f"{type(LrSchedule).__name__} assumes the same lr for all param_groups",
                )

    def on_before_optimizer_step(
        self,
        param_groups: list[dict[str, Any]],
        step: int | None = None,
        total_steps: int | None = None
    ) -> None:
        lr = self.schedule.evaluate(step=step, total_steps=total_steps)
        for param_group in param_groups:
            param_group["lr"] = lr
