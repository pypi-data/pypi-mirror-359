from __future__ import annotations

from typing import TYPE_CHECKING, Any

import torch

from ksuit.core.callbacks import PeriodicCallback

if TYPE_CHECKING:
    from ksuit.core.trainers import TrainingContext


class OfflineLossCallback(PeriodicCallback):
    def __init__(self, dataset_key: str, collator_key: str | None = None, **kwargs):
        super().__init__(**kwargs)
        self.dataset_key = dataset_key
        self.collator_key = collator_key

    @staticmethod
    def _forward(batch: dict[str, Any], ctx: TrainingContext) -> torch.Tensor:
        batch = ctx.trainer.move_batch_to_device(batch=batch, ctx=ctx)
        loss = ctx.trainer.batch_to_loss(batch=batch, ctx=ctx)
        return loss

    def _register_interleaved_sampler_configs(self, ctx: TrainingContext) -> None:
        self._register_interleaved_sampler_config_with_key(
            dataset_key=self.dataset_key,
            items=ctx.trainer.get_dataset_items(),
            collator_key=self.collator_key,
        )

    def _invoke(self, ctx: TrainingContext):
        loss = self._iterate_over_dataset(forward_fn=self._forward, ctx=ctx)

        # log loss
        mean_loss = loss.mean()
        self.logger.info(f"loss/{self.dataset_key}/total: {mean_loss.item():.6f}")
        self.tracker.add_scalar(
            key=f"loss/{self.dataset_key}/total",
            value=mean_loss,
            logger=self.logger,
            summary="min",
        )
