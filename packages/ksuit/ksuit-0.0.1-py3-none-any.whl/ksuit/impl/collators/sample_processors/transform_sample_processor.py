from typing import Any, Callable

from ksuit.core.collators import SampleProcessor
from ksuit.core.datasets import Dataset
from ksuit.core.factories import Factory


class TransformSampleProcessor(SampleProcessor):
    def __init__(self, transform: Callable[[Any], Any], item: str | None = None, _recursive_: bool = True):
        super().__init__()
        self.item = item
        self.transform = Factory.create_object(transform, _recursive_=_recursive_)

    def _process(self, samples: list[dict[str, Any]], dataset: Dataset | None = None) -> list[dict[str, Any]]:
        for i in range(len(samples)):
            samples[i] = dict(samples[i])
            if self.item is not None:
                if self.item not in samples[i]:
                    raise RuntimeError(f"item '{self.item}' not in sample (keys={set(samples[i].keys())}")
                samples[i][self.item] = self.transform(samples[i][self.item])
            else:
                samples[i] = self.transform(samples[i])
        return samples
