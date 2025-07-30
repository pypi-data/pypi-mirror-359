import math

from ksuit.core.schedules import Schedule
from ksuit.utils import param_checking


class LinearWarmup(Schedule):
    """Schedule with linear warmup for `warmup_steps` steps or `warmup_ratio * 100`% of the `total_steps`. If
    instantiated via `ScheduleFactory`, `warmup_steps` can also be specified via `warmup_epochs`, `warmup_updates` or
    `warmup_samples`.
    """

    def __init__(
        self,
        warmup_steps: int | None = None,
        warmup_ratio: float | None = None,
        start_value: float = 0.0,
        max_value: float = 1.0,
        **kwargs,
    ):
        super().__init__(**kwargs)
        if not param_checking.exactly_one_non_none(warmup_steps, warmup_ratio):
            raise ValueError(f"define either {warmup_steps=} or {warmup_ratio=}")
        if start_value > max_value:
            raise ValueError
        self.warmup_steps = warmup_steps
        self.warmup_ratio = warmup_ratio
        self.start_value = start_value
        self.max_value = max_value

    def _evaluate(self, step: int, total_steps: int | None) -> float:
        if total_steps is None:
            raise ValueError(f"{type(self).__name__} requires total_steps")

        # convert progress to step
        if self.warmup_ratio is None:
            warmup_steps = self.warmup_steps - 1
            if warmup_steps >= total_steps:
                raise ValueError(f"{warmup_steps=} should be smaller than {total_steps=}")
        else:
            warmup_steps = math.floor(total_steps * self.warmup_ratio)

        # warmup
        if step < warmup_steps:
            warmup_progress = step / warmup_steps
            warmup_delta = self.max_value - self.start_value
            return self.start_value + warmup_progress * warmup_delta
        # constant
        return self.max_value
