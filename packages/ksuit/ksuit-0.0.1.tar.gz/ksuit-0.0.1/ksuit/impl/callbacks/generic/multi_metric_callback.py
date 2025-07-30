from __future__ import annotations

from typing import TYPE_CHECKING, Any, Sequence

from ksuit.core.callbacks import ForwardFnResult, IterateOverDatasetResult, MetricCallback, PeriodicCallback
from ksuit.core.factories import Factory

if TYPE_CHECKING:
    from ksuit.core.trainers import TrainingContext


class MultiMetricCallback(PeriodicCallback):
    def __init__(
        self,
        metric_callbacks: Sequence[MetricCallback],
        dataset_key: str,
        collator_key: str | None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.metric_callbacks = Factory.create_list(
            metric_callbacks,
            dataset_key=dataset_key,
            collator_key=collator_key,
            every_n_epochs=self.every_n_epochs,
            every_n_updates=self.every_n_updates,
            every_n_samples=self.every_n_samples,
            tracker=self.tracker,
            data_provider=self.data_provider,
            distributed_provider=self.distributed_provider,
            expected_base_type=MetricCallback,
        )
        self.dataset_key = dataset_key
        self.collator_key = collator_key

    def _register_interleaved_sampler_configs(self, ctx: TrainingContext) -> None:
        items = ctx.trainer.get_dataset_items() or set()
        for metric_callback in self.metric_callbacks:
            items = items | metric_callback.input_items | metric_callback.target_items
        self._register_interleaved_sampler_config_with_key(
            dataset_key=self.dataset_key,
            items=items,
            collator_key=self.collator_key,
        )

    def _forward(self, batch: dict[str, Any], ctx: TrainingContext) -> list[ForwardFnResult]:
        batch = ctx.trainer.move_batch_to_device(batch=batch, ctx=ctx)
        # select target variables and exclude them from forward pass
        targets = []
        for metric_callback in self.metric_callbacks:
            targets.append({target_item: batch[target_item] for target_item in metric_callback.target_items})
        for metric_callback in self.metric_callbacks:
            for target_item in metric_callback.target_items:
                batch.pop(target_item, None)
        # forward pass
        with ctx.trainer.autocast_context:
            model_outputs = ctx.model(**batch)
        # calculate metrics
        metrics = []
        for i, metric_callback in enumerate(self.metric_callbacks):
            metrics.append(metric_callback.model_output_to_metric(model_outputs=model_outputs, targets=targets[i]))
        return metrics

    def _invoke(self, ctx: TrainingContext) -> None:
        metrics = self._iterate_over_dataset(forward_fn=self._forward, ctx=ctx)
        for i, metric_callback in enumerate(self.metric_callbacks):
            metric_callback.track_metric(iterate_over_dataset_result=metrics[i])

    def _concat_iterate_over_dataset_results(
        self,
        results: list[list[ForwardFnResult]],
        max_length: int,
    ) -> list[IterateOverDatasetResult]:
        if any(len(results[i]) != len(self.metric_callbacks) for i in range(len(results))):
            raise RuntimeError

        # concat results of different metric_callbacks independently
        all_results = []
        for i in range(len(self.metric_callbacks)):
            metric_callback_results = [results[j][i] for j in range(len(results))]
            all_results.append(
                self._concat_iterate_over_dataset_results_impl(
                    results=metric_callback_results,
                    max_length=max_length,
                    allow_collection_type=True,
                ),
            )

        return all_results
