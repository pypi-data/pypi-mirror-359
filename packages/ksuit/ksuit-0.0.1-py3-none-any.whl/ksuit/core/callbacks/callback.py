from __future__ import annotations

import logging
from abc import ABC
from collections.abc import Sequence
from typing import TYPE_CHECKING, Any

import torch

from ksuit.utils import param_checking

if TYPE_CHECKING:
    from ksuit.core.initializers import ResumeInitializer
    from ksuit.core.providers import DataProvider, DistributedProvider, PathProvider
    from ksuit.core.trackers import Tracker
    from ksuit.core.trainers import TrainingContext


class Callback(ABC):
    @staticmethod
    def at_least_one_override_for_hook(callbacks: Sequence[Callback], hook_name: str) -> bool:
        assert hasattr(Callback, hook_name), f"invalid hook_name: '{hook_name}'"
        hook_impl_name = f"_{hook_name}"
        has_override_for_hook = [
            getattr(type(c), hook_impl_name) != getattr(Callback, hook_impl_name)
            for c in callbacks
        ]
        return param_checking.at_least_one_true(*has_override_for_hook)

    def __init_subclass__(cls):
        for name in dir(Callback):
            if name.startswith("on_") and not name.startswith("_"):
                base_method = getattr(Callback, name)
                child_method = getattr(cls, name, None)
                if child_method is not None and child_method != base_method:
                    raise TypeError(
                        f"{cls.__name__} should not override '{name}'. "
                        f"Override '_{name}' instead to ensure @torch.no_grad() is preserved."
                    )

    def __init__(
        self,
        tracker: Tracker | None = None,
        data_provider: DataProvider | None = None,
        distributed_provider: DistributedProvider | None = None,
        path_provider: PathProvider | None = None,
    ):
        super().__init__()
        self.logger = logging.getLogger(type(self).__name__)
        self.tracker = tracker
        self.data_provider = data_provider
        self.distributed_provider = distributed_provider
        self.path_provider = path_provider

    @torch.no_grad()
    def on_fit_start(self, ctx: TrainingContext) -> None:
        self._on_fit_start(ctx=ctx)

    def _on_fit_start(self, ctx: TrainingContext) -> None:
        pass

    @torch.no_grad()
    def on_epoch_start(self, ctx: TrainingContext) -> None:
        self._on_epoch_start(ctx=ctx)

    def _on_epoch_start(self, ctx: TrainingContext) -> None:
        pass

    @torch.no_grad()
    def on_update_start(self, ctx: TrainingContext) -> None:
        self._on_update_start(ctx=ctx)

    def _on_update_start(self, ctx: TrainingContext) -> None:
        pass

    @torch.no_grad()
    def on_after_backward(self, ctx: TrainingContext) -> None:
        self._on_after_backward(ctx=ctx)

    def _on_after_backward(self, ctx: TrainingContext) -> None:
        pass

    @torch.no_grad()
    def on_before_optimizer_step(self, ctx: TrainingContext) -> None:
        self._on_before_optimizer_step(ctx=ctx)

    def _on_before_optimizer_step(self, ctx: TrainingContext) -> None:
        pass



    @torch.no_grad()
    def on_before_zero_grad(self, ctx: TrainingContext) -> None:
        self._on_before_zero_grad(ctx=ctx)

    def _on_before_zero_grad(self, ctx: TrainingContext) -> None:
        pass

    @torch.no_grad()
    def on_update_end(self, ctx: TrainingContext) -> None:
        self._on_update_end(ctx=ctx)

    def _on_update_end(self, ctx: TrainingContext) -> None:
        pass

    @torch.no_grad()
    def on_epoch_end(self, ctx: TrainingContext) -> None:
        self._on_epoch_end(ctx=ctx)

    def _on_epoch_end(self, ctx: TrainingContext) -> None:
        pass

    @torch.no_grad()
    def on_fit_end(self, ctx: TrainingContext) -> None:
        self._on_fit_end(ctx=ctx)

    def _on_fit_end(self, ctx: TrainingContext) -> None:
        pass

    def __str__(self) -> str:
        return type(self).__name__

    def on_resume(self, ctx: TrainingContext, resume_initializer: ResumeInitializer) -> None:
        pass