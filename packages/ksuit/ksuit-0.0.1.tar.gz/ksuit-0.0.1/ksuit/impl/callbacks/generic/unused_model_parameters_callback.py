from __future__ import annotations

from typing import TYPE_CHECKING

from ksuit.core.callbacks import Callback

if TYPE_CHECKING:
    from ksuit.core.trainers import TrainingContext


class UnusedModelParametersCallback(Callback):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.was_called = False

    def _on_after_backward(self, ctx: TrainingContext) -> None:
        if self.was_called:
            return
        self.was_called = True
        unused_params = [
            (name, param)
            for name, param in ctx.model.named_parameters()
            if param.grad is None and param.requires_grad
        ]
        unused_param_names = [name for name, _ in unused_params]
        self.logger.info(f"{len(unused_param_names)} unused parameters")
        for unused_param_name in unused_param_names:
            self.logger.info(f"- {unused_param_name}")
        if len(unused_params) > 0:
            unused_param_count = sum(param.numel() for name, param in unused_params)
            self.tracker.set_summary(key="param_count/unused", value=unused_param_count)
