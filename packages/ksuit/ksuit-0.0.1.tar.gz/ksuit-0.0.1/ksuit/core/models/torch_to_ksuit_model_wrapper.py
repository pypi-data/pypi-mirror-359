from torch import nn

from ksuit.core.factories import Factory
from ksuit.core.models import Model


class TorchToKsuitModelWrapper(Model):
    """Wraps a `torch.nn.Module` into `ksuit.Module`."""
    def __init__(self, model: nn.Module, **kwargs):
        super().__init__()
        self.module = Factory.create_object(model, expected_base_type=nn.Module, **kwargs)

    def forward(self, *args, **kwargs):
        return self.module(*args, **kwargs)
