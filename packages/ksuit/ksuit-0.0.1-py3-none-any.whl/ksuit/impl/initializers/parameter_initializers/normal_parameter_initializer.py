from torch import nn

from ksuit.core.initializers import SingleParameterInitializer


class NormalParameterInitializer(SingleParameterInitializer):
    def __init__(self, *args, std: float = 0.02, **kwargs):
        super().__init__(*args, **kwargs)
        self.std = std

    def initialize_parameter(self, parameter: nn.Parameter) -> None:
        nn.init.normal_(parameter, mean=0, std=self.std)
