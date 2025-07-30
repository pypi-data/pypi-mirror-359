import logging
from abc import ABC, abstractmethod

from ksuit.core.trackers import Tracker


class Runner(ABC):
    def __init__(self):
        self.logger = logging.getLogger(type(self).__name__)

    @abstractmethod
    def run(self) -> Tracker:
        pass
