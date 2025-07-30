from typing import Any

import torch

from ksuit.core.callbacks import ForwardFnResult, IterateOverDatasetResult, MetricCallback


class OfflineAccuracyCallback(MetricCallback):
    @property
    def input_items(self) -> set[str]:
        return {"x"}

    @property
    def target_items(self) -> set[str]:
        return {"y"}

    def model_output_to_metric(self, model_outputs: Any, targets: dict[str, Any]) -> ForwardFnResult:
        if not torch.is_tensor(model_outputs):
            raise RuntimeError(f"{type(self).__name__} expects a tensor as model output")
        if model_outputs.ndim != 2:
            raise RuntimeError(f"{type(self).__name__} expects logits as model output")
        logits = model_outputs
        is_correct = logits.argmax(dim=1) == targets["y"]
        return is_correct

    def track_metric(self, iterate_over_dataset_result: IterateOverDatasetResult) -> None:
        is_correct = iterate_over_dataset_result
        accuracy = is_correct.float().mean()
        self.tracker.add_scalar(
            key=f"accuracy/{self.dataset_key}",
            value=accuracy,
            logger=self.logger,
            summary="max",
            format_str=".4f",
        )
