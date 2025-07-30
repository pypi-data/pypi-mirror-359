from torchvision.transforms import Resize as TVResize
from torchvision.transforms.functional import InterpolationMode


class Resize(TVResize):
    def __init__(self, *args, interpolation: str = "bicubic", **kwargs):
        super().__init__(*args, interpolation=InterpolationMode(interpolation), **kwargs)
