from typing import Any

import numpy as np
import torch
import torch.nn.functional as F

from ksuit.core.collators import BatchProcessor
from ksuit.core.datasets import Dataset


class Cutmixup(BatchProcessor):
    def __init__(
        self,
        mixup_alpha: float = 0.8,
        cutmix_alpha: float = 1.0,
        x_item: str = "x",
        y_item: str = "y",
        **kwargs,
    ):
        super().__init__(**kwargs)
        # check alphas
        assert isinstance(mixup_alpha, (int, float)) and 0. < mixup_alpha
        assert isinstance(cutmix_alpha, (int, float)) and 0. < cutmix_alpha

        # initialize
        self.mixup_alpha = mixup_alpha
        self.cutmix_alpha = cutmix_alpha
        self.x_item = x_item
        self.y_item = y_item

    def _process(self, batch: dict[str, Any], dataset: Dataset | None = None) -> dict[str, Any]:
        if dataset is None:
            raise RuntimeError(f"{type(self).__name__} requires dataset to be passed to __call__")
        if not hasattr(dataset, "num_classes"):
            raise RuntimeError(f"{type(self).__name__} requires dataset with num_classes attribute in __call__")
        # extract properties from batch
        x = batch.pop(self.x_item).clone()
        y = batch.pop(self.y_item).clone()
        is_binary_classification = False
        # y has to be 2d tensor of in one-hot format (multi-class) or 1d tensor (binary-classification)
        if y.ndim != 2:
            assert y.ndim == 1
            if dataset.num_classes == 2:
                # binary classification
                y = y.unsqueeze(1)
                is_binary_classification = True
            else:
                # to one-hot
                y = F.one_hot(y.long(), num_classes=dataset.num_classes)
        y = y.float()

        # sample parameters (use_cutmix, lamb, bbox)
        rng = np.random.default_rng()
        use_cutmix = rng.random() < 0.5
        alpha = self.cutmix_alpha if use_cutmix else self.mixup_alpha
        lamb = torch.tensor([rng.beta(alpha, alpha)])
        # apply mixup/cutmix to x
        x2 = self._shuffle(item=x)
        if use_cutmix:
            h, w = x.shape[2:]
            bbox, lamb = self._get_random_bbox(h=h, w=w, lamb=lamb, rng=rng)
            top, left, bot, right = bbox[0]
            x[..., top:bot, left:right] = x2[..., top:bot, left:right]
        else:
            x_lamb = lamb.view(-1, *[1] * (x.ndim - 1))
            x.mul_(x_lamb).add_(x2.mul_(1. - x_lamb))
        # apply mixup to y
        y2 = self._shuffle(item=y)
        y_lamb = lamb.view(-1, 1)
        y.mul_(y_lamb).add_(y2.mul_(1. - y_lamb))

        # update properties in batch
        batch[self.x_item] = x
        if is_binary_classification:
            y = y.squeeze(1)
        batch[self.y_item] = y
        return batch

    @staticmethod
    def _get_random_bbox(h: int, w: int, lamb: torch.Tensor, rng: np.random.Generator) -> tuple[torch.tensor, float]:
        n_bboxes = len(lamb)
        bbox_hcenter = torch.from_numpy(rng.integers(h, size=(n_bboxes,)))
        bbox_wcenter = torch.from_numpy(rng.integers(w, size=(n_bboxes,)))

        area_half = 0.5 * (1.0 - lamb).sqrt()
        bbox_h_half = (area_half * h).floor()
        bbox_w_half = (area_half * w).floor()

        top = torch.clamp(bbox_hcenter - bbox_h_half, min=0).type(torch.long)
        bot = torch.clamp(bbox_hcenter + bbox_h_half, max=h).type(torch.long)
        left = torch.clamp(bbox_wcenter - bbox_w_half, min=0).type(torch.long)
        right = torch.clamp(bbox_wcenter + bbox_w_half, max=w).type(torch.long)
        bbox = torch.stack([top, left, bot, right], dim=1)

        lamb_adjusted = 1.0 - (bot - top) * (right - left) / (h * w)

        return bbox, lamb_adjusted

    @staticmethod
    def _shuffle(item: torch.Tensor) -> torch.Tensor:
        if len(item) == 1:
            return item.clone()
        assert len(item) % 2 == 0
        return item.flip(0)
