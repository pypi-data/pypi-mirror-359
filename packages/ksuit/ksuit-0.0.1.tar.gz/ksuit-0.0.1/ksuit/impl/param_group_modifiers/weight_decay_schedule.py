from typing import Any

from torch import nn

from ksuit.core.factories import ScheduleFactory
from ksuit.core.optim import ParamGroupModifier
from ksuit.core.schedules import Schedule


class WeightDecaySchedule(ParamGroupModifier):
    def __init__(self, schedule: Schedule, **kwargs):
        super().__init__(**kwargs)
        self.schedule = ScheduleFactory.create_object(
            schedule,
            max_value=self.param_group_defaults["weight_decay"],
            training_progress_provider=self.training_progress_provider,
        )

    def populate_parameter_properties(
        self,
        parameter_properties: list[dict[str, Any]],
        model: nn.Module | None = None,
    ) -> list[dict[str, Any]]:
        for parameter_properties_item in parameter_properties:
            if "weight_decay" in parameter_properties_item:
                if parameter_properties_item["weight_decay"] == 0.0:
                    assert "exclude_from_weight_decay_schedule" not in parameter_properties_item
                    parameter_properties_item["exclude_from_weight_decay_schedule"] = True
                else:
                    raise RuntimeError(
                        f"{type(WeightDecaySchedule).__name__} "
                        f"assumes the same weight_decay for all param_groups"
                    )

    def on_before_optimizer_step(
        self,
        param_groups: list[dict[str, Any]],
        step: int | None = None,
        total_steps: int | None = None
    ) -> None:
        weight_decay = self.schedule.evaluate(step=step, total_steps=total_steps)
        for param_group in param_groups:
            if param_group.get("exclude_from_weight_decay_schedule", False):
                continue
            param_group["weight_decay"] = weight_decay
