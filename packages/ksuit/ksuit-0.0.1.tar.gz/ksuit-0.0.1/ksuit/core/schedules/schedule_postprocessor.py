import logging
from abc import ABC, abstractmethod

class SchedulePostprocessor(ABC):
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(type(self).__name__)

    @abstractmethod
    def __call__(self, value: float) -> float:
        pass