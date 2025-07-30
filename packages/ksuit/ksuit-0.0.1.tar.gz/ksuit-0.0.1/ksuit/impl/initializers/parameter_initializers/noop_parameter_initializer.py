import fnmatch
from abc import ABC, abstractmethod

from torch import nn

from ksuit.core.initializers import SingleParameterInitializer


class NoopParameterInitializer(SingleParameterInitializer):
    def initialize_parameter(self, parameter: nn.Parameter) -> None:
        pass
