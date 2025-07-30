from typing import Any

import torch
import torch.nn.functional as F
from torch import nn

from ksuit.core.loss_wrappers import LossWrapper
from ksuit.core.trainers import TrainingContext


class ClassificationLossWrapper(LossWrapper):
    def __init__(self, model: nn.Module, num_classes: int):
        super().__init__(model=model)
        self.num_classes = num_classes

    def forward(self, batch: dict[str, Any], ctx: TrainingContext | None = None) -> torch.Tensor:
        target = batch.pop("y")
        pred = self.model(**batch)

        if not torch.is_tensor(pred):
            raise NotImplementedError
        if pred.ndim < 2:
            raise NotImplementedError("prediction of classifier should have shape (batch_size num_classes ...)")
        if pred.size(1) != self.num_classes:
            raise NotImplementedError(f"logits.size(1) ({pred.size(1)} does not match num_classes={self.num_classes}")

        loss = F.cross_entropy(pred, target)
        ctx.state["target"] = target
        ctx.state["logits"] = pred.detach()
        return loss
