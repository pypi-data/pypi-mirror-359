import torch
from PIL.Image import Image
from torchvision.transforms import ColorJitter


class RandomColorJitter(ColorJitter):
    def __init__(self, p: float = 0.5, **kwargs):
        super().__init__(**kwargs)
        self.p = p

    def forward(self, x: Image | torch.Tensor) -> Image | torch.Tensor:
        if self.p < torch.rand(1):
            return x
        x = super().forward(x)
        return x
