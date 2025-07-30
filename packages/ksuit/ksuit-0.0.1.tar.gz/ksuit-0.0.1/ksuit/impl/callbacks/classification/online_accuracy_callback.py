from __future__ import annotations

from typing import TYPE_CHECKING

import torch

from ksuit.core.callbacks import PeriodicCallback

if TYPE_CHECKING:
    from ksuit.core.trainers import TrainingContext


class OnlineAccuracyCallback(PeriodicCallback):
    def __init__(self, verbose=True, **kwargs):
        super().__init__(**kwargs)
        self.verbose = verbose
        self.tracked_accs = []

    def _on_after_backward(self, ctx: TrainingContext) -> None:
        target = ctx.state["target"]
        # convert back to long (e.g. when label smoothing is used)
        if target.dtype != torch.long:
            target = target.argmax(dim=1)

        acc = (ctx.state["logits"].detach().argmax(dim=1) == target).float().mean()
        self.tracked_accs.append(acc)

    def _invoke(self, ctx: TrainingContext) -> None:
        if self.verbose:
            kwargs = dict(
                logger=self.logger,
                summary="max",
                format_str=".4f",
            )
        else:
            kwargs = {}
        mean_acc = self.distributed_provider.all_reduce_mean_nograd(torch.stack(self.tracked_accs).mean())
        self.tracker.add_scalar(
            key=f"accuracy/online/{self.short_interval_string}",
            value=mean_acc,
            **kwargs,
        )
        self.tracked_accs.clear()
