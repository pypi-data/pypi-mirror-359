import torch
from torch import nn


class Sequential(nn.Sequential):
    def __init__(self, *args, residual: bool = False, **kwargs):
        super().__init__(*args, **kwargs)
        self.residual = residual

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        y = super().forward(x)
        if self.residual:
            return x + y
        return y
