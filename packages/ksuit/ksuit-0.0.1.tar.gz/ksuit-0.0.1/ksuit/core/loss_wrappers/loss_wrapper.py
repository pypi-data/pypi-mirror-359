from __future__ import annotations

from typing import TYPE_CHECKING, Any

import torch
from torch import nn

if TYPE_CHECKING:
    from ksuit.core.trainers import TrainingContext


class LossWrapper(nn.Module):
    def __init__(self, model: nn.Module):
        super().__init__()
        self.model = model

    def forward(self, batch: dict[str, Any], ctx: TrainingContext | None = None) -> torch.Tensor:
        return ctx.model(batch=batch, ctx=ctx)
