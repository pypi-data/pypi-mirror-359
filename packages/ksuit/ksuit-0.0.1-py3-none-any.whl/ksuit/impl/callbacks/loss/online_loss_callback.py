from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING

import torch

from ksuit.core.callbacks import PeriodicCallback

if TYPE_CHECKING:
    from ksuit.core.trainers import TrainingContext


class OnlineLossCallback(PeriodicCallback):
    def __init__(self, verbose: bool, **kwargs):
        super().__init__(**kwargs)
        self.verbose = verbose
        self.tracked_losses = defaultdict(list)

    def _on_after_backward(self, ctx: TrainingContext) -> None:
        self.tracked_losses["total"].append(ctx.state["loss"].detach())

    def _invoke(self, ctx: TrainingContext) -> None:
        for name, tracked_loss in self.tracked_losses.items():
            mean_loss = self.distributed_provider.all_reduce_mean_nograd(
                torch.stack(tracked_loss).mean(),
                mesh_dim_name="data",
            )
            # TODO: not trainer.skip_nan_loss and
            # if torch.isnan(mean_loss):
            #     losses = all_gather_nograd(torch.stack(tracked_loss))
            #     num_nans = torch.isnan(losses).sum()
            #     msg = f"encountered nan loss ({num_nans.item()} nans): {losses}"
            #     self.logger.error(msg)
            #     raise RuntimeError(msg)
            self.tracker.add_scalar(
                key=f"loss/online/{name}/{self.short_interval_string}",
                value=mean_loss,
                logger=self.logger if self.verbose else None,
                summary="min",
            )
        self.tracked_losses.clear()
