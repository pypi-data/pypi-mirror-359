from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Sequence

import torch
from torch import nn

if TYPE_CHECKING:
    from ksuit.core.callbacks import Callback
    from ksuit.core.models import Model
    from ksuit.core.optim import Optimizer

    from .trainer import Trainer


@dataclass
class TrainingContext:
    trainer: Trainer
    model: Model
    loss_wrapped_model: nn.Module
    dp_wrapped_model: nn.Module
    callbacks: Sequence[Callback]
    state: dict[str, Any]
    local_batch_size: int | None = None
    global_batch_size: int | None = None
    optimizer: Optimizer | torch.optim.Optimizer | None = None
    interleaved_dataloader_iter: Iterator[dict[str, Any]] | None = None
