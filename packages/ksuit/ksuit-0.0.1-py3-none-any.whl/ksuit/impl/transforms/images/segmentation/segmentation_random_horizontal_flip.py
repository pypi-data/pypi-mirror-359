from typing import Any

import numpy as np
from torch import nn
from torchvision.transforms.functional import hflip


class SegmentationRandomHorizontalFlip(nn.Module):
    def __init__(self, p=0.5, **kwargs):
        super().__init__(**kwargs)
        self.p = p

    def __call__(self, sample: dict[str, Any]) -> dict[str, Any]:
        # copy
        sample = dict(sample)
        x = sample["x"]
        seg = sample["y"]

        # flip
        rng = np.random.default_rng()
        apply = rng.random() < self.p
        if apply:
            x = hflip(x)
            seg = hflip(seg)

        # update
        sample["x"] = x
        sample["y"] = seg
        return sample
