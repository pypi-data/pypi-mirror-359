from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING, Any

import torch

from .periodic_callback import PeriodicCallback

if TYPE_CHECKING:
    from ksuit.core.callbacks import ForwardFnResult, IterateOverDatasetResult
    from ksuit.core.trainers import TrainingContext


class MetricCallback(PeriodicCallback):
    def __init__(self, dataset_key: str, collator_key: str | None, **kwargs):
        super().__init__(**kwargs)
        self.dataset_key = dataset_key
        self.collator_key = collator_key

    @property
    @abstractmethod
    def input_items(self) -> set[str]:
        pass

    @property
    @abstractmethod
    def target_items(self) -> set[str]:
        pass

    def _register_interleaved_sampler_configs(self, ctx: TrainingContext) -> None:
        self._register_interleaved_sampler_config_with_key(
            dataset_key=self.dataset_key,
            items=(ctx.trainer.get_dataset_items() or set()) | self.input_items | self.target_items,
            collator_key=self.collator_key,
        )

    @abstractmethod
    def model_output_to_metric(self, model_outputs: Any, targets: dict[str, Any]) -> ForwardFnResult:
        pass

    @abstractmethod
    def track_metric(self, iterate_over_dataset_result: IterateOverDatasetResult) -> None:
        pass

    def _forward(self, batch: dict[str, Any], ctx: TrainingContext) -> torch.Tensor:
        batch = ctx.trainer.move_batch_to_device(batch=batch, ctx=ctx)
        targets = {target_item: batch[target_item] for target_item in self.target_items}
        for target_item in self.target_items:
            batch.pop(target_item)
        with ctx.trainer.autocast_context:
            model_outputs = ctx.model(**batch)
        is_correct = self.model_output_to_metric(model_outputs=model_outputs, targets=targets)
        return is_correct

    def _invoke(self, ctx: TrainingContext) -> None:
        is_correct = self._iterate_over_dataset(forward_fn=self._forward, ctx=ctx)
        self.track_metric(iterate_over_dataset_result=is_correct)
