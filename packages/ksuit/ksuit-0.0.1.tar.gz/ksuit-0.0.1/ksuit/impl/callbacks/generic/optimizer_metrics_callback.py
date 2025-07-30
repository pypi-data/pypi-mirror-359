from __future__ import annotations

from typing import TYPE_CHECKING

import torch

from ksuit.core.callbacks import PeriodicCallback

if TYPE_CHECKING:
    from ksuit.core.trainers import TrainingContext


class OptimizerMetricsCallback(PeriodicCallback):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.metrics = {}

    def _on_before_optimizer_step(self, ctx: TrainingContext) -> None:
        if self.every_n_updates is None:
            raise RuntimeError(f"{type(self).__name__} should be update-based (set every_n_updates)")
        if not self._should_invoke_after_update(ctx.trainer.training_progress_provider.cur_eus.update + 1):
            return
        # calculate total norm of all paramters (also used in torch.nn.utils.clip_grad_norm_)
        names, grads = zip(*[(name, p.grad) for name, p in ctx.model.named_parameters() if p.grad is not None])
        # noinspection PyProtectedMember
        norms = torch._foreach_norm(grads)
        # some devices might not support _foreach_norm, it is equivalen to
        # norms = [grad.norm() for grad in grads]
        total_norm = torch.stack(norms).norm()
        # logging needs to happen in _invoke as update has not increased yet
        self.metrics["total_norm"] = total_norm

    def _invoke(self, ctx: TrainingContext) -> None:
        for name, value in self.metrics.items():
            self.tracker.add_scalar(f"optim/{name}", value)
        self.metrics.clear()