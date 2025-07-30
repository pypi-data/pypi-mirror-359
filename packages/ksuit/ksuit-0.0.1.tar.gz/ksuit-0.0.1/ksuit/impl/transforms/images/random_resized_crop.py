from torchvision.transforms import RandomResizedCrop as TVRandomResizedCrop
from torchvision.transforms.functional import InterpolationMode


class RandomResizedCrop(TVRandomResizedCrop):
    def __init__(self, *args, interpolation: str = "bicubic", **kwargs):
        super().__init__(*args, interpolation=InterpolationMode(interpolation), **kwargs)
