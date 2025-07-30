import fnmatch
from abc import ABC, abstractmethod

from torch import nn

from ksuit.core.initializers import SingleParameterInitializer


class ZerosParameterInitializer(SingleParameterInitializer):
    def initialize_parameter(self, parameter: nn.Parameter) -> None:
        nn.init.zeros_(parameter)

