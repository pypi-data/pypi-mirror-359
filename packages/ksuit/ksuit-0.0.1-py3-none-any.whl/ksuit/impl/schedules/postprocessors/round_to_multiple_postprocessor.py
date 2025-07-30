from ksuit.core.schedules import SchedulePostprocessor


class RoundToMultiplePostprocessor(SchedulePostprocessor):
    def __init__(self, multiple: int):
        super().__init__()
        self.multiple = multiple

    def __call__(self, value: float) -> float:
        lower_multiple = value // self.multiple * self.multiple
        if value - lower_multiple < self.multiple / 2:
            return lower_multiple
        return lower_multiple + self.multiple
