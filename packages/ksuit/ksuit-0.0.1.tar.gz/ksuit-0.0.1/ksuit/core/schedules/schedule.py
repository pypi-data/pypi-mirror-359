import logging
from abc import ABC, abstractmethod
from typing import final
from .schedule_postprocessor import SchedulePostprocessor
from ksuit.core.factories import Factory

class Schedule(ABC):
    def __init_subclass__(cls):
        if cls.__call__ != Schedule.__call__:
            raise TypeError(f"{cls.__name__} must not override '__call__'. Override '_evaluate' instead.")

    def __init__(self, postprocessor: SchedulePostprocessor | None = None):
        super().__init__()
        self.logger = logging.getLogger(type(self).__name__)
        self.postprocessor = Factory.create_object(
            postprocessor,
            expected_base_type=SchedulePostprocessor,
        )


    @final
    def __call__(self, step: int, total_steps: int | None = None) -> float:
        return self.evaluate(step=step, total_steps=total_steps)

    def evaluate(self, step: int, total_steps: int | None) -> float:
        # checks
        if step < 0:
            raise ValueError(f"{step=} should be >= 0")
        if step >= total_steps:
            raise ValueError(f"{step=} should be smaller than {total_steps=}")
        # calculate value
        value = self._evaluate(step=step, total_steps=total_steps)
        # postprocess (e.g., round to int or round to multiple of two for batchsize warmup)
        if self.postprocessor is not None:
            value = self.postprocessor(value)
        return value

    @abstractmethod
    def _evaluate(self, step: int, total_steps: int | None) -> float:
        pass
