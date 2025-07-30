import torch
from PIL import ImageFilter
from PIL.Image import Image
from torchvision.transforms import GaussianBlur
from torchvision.transforms.functional import to_pil_image


class GaussianBlurPIL(GaussianBlur):
    def __init__(self, **kwargs):
        # kernel size is not used here as PIL doesn't use a kernel_size
        super().__init__(kernel_size=1, **kwargs)

    def __call__(self, x: Image | torch.Tensor) -> Image:
        if torch.is_tensor(x):
            x = to_pil_image(x)
        sigma_lb, sigma_ub = self.sigma
        sigma = torch.rand(1) * (sigma_ub - sigma_lb) + sigma_lb
        return x.filter(ImageFilter.GaussianBlur(radius=sigma.item()))
