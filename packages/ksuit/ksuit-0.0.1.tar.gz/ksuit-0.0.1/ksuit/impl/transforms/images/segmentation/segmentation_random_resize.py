from typing import Any

import numpy as np
import torch
from torch import nn
from torchvision.transforms import InterpolationMode
from torchvision.transforms.functional import resize

from ksuit.utils.param_checking import to_2tuple


class SegmentationRandomResize(nn.Module):
    """ resize image and mask to base_size * ratio where ratio is randomly sampled """

    def __init__(self, ratio_resolution, ratio_range, interpolation="bilinear", **kwargs):
        super().__init__(**kwargs)
        self.ratio_resolution = to_2tuple(ratio_resolution)
        self.ratio_range = to_2tuple(ratio_range)
        self.interpolation = InterpolationMode(interpolation)

    def __call__(self, sample: dict[str, Any]) -> dict[str, Any]:
        # copy
        sample = dict(sample)
        x = sample["x"]
        seg = sample["y"]

        # get params
        if torch.is_tensor(x):
            _, h, w = x.shape
        else:
            h = x.height
            w = x.width
        suggested_height, suggested_width = self._get_params()
        # scale by smallest scaleing while keeping aspect ratio
        max_long_edge = max(suggested_height, suggested_width)
        max_short_edge = min(suggested_height, suggested_width)
        smallest_scale = min(max_long_edge / max(h, w), max_short_edge / min(h, w))

        new_height = round(h * smallest_scale)
        new_width = round(w * smallest_scale)
        new_size = new_height, new_width

        # resize
        x = resize(x, size=new_size, interpolation=self.interpolation)
        squeeze = False
        if torch.is_tensor(seg):
            seg = seg.unsqueeze(0)
            squeeze = True
        seg = resize(seg, size=new_size, interpolation=InterpolationMode.NEAREST)
        if squeeze:
            seg = seg.squeeze(0)

        # update
        sample["x"] = x
        sample["y"] = seg
        return sample

    def _get_params(self) -> tuple[int, int]:
        ratio_min, ratio_max = self.ratio_range
        rng = np.random.default_rng()
        ratio = rng.uniform(ratio_min, ratio_max)
        height, width = self.ratio_resolution
        suggested_height = height * ratio
        suggested_width = width * ratio
        return suggested_height, suggested_width
