import logging
from abc import ABC, abstractmethod
from typing import Any

import torch


class ParameterRenamer(ABC):
    def __init__(self):
        self.logger = logging.getLogger(type(self).__name__)

    @abstractmethod
    def __call__(self, state_dict: dict[str, torch.Tensor]) -> dict[str, torch.Tensor]:
        pass