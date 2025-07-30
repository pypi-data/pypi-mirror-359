from typing import Any

import einops
import torch
import torch.nn.functional as F

from ksuit.core.loss_wrappers import LossWrapper
from ksuit.core.trainers import TrainingContext


class LanguageModelingLossWrapper(LossWrapper):
    def forward(self, batch: dict[str, Any], ctx: TrainingContext | None = None) -> torch.Tensor:
        x = batch.pop("x")
        target = x[:, 1:]
        x = x[:, :-1]
        pred = self.model(x=x, **batch)

        if not torch.is_tensor(pred):
            raise NotImplementedError
        assert pred.shape[:-1] == target.shape

        # cross_entropy expects logits at dim=1
        pred = einops.rearrange(pred, "batch_size seqlen vocabulary_size -> batch_size vocabulary_size seqlen")
        loss = F.cross_entropy(pred, target)
        return loss
