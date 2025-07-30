import torch
import torchvision.transforms.functional as F
from PIL import ImageOps
from PIL.Image import Image

from .gaussian_blur_pil import GaussianBlurPIL


class ThreeAugment:
    def __init__(self, blur_sigma: tuple[float, float] = (0.1, 2.0), **kwargs):
        super().__init__(**kwargs)
        self.gaussian_blur = GaussianBlurPIL(sigma=blur_sigma)

    def __call__(self, x: Image | torch.Tensor) -> Image:
        # convert to PIL because GaussianBlur/solarize only works on PIL
        if torch.is_tensor(x):
            x = F.to_pil_image(x)
        choice = torch.randint(3, size=(1,)).item()
        if choice == 0:
            return F.rgb_to_grayscale(x, num_output_channels=F.get_image_num_channels(x))
        if choice == 1:
            return ImageOps.solarize(x)
        if choice == 2:
            return self.gaussian_blur(x)
        raise NotImplementedError
