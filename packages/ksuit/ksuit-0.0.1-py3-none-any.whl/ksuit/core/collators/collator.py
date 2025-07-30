from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable

from torch.utils.data import default_collate

from ksuit.core.factories import Factory
from .batch_processor import BatchProcessor
from .sample_processor import SampleProcessor
from .samples_to_batch_processor import SamplesToBatchProcessor

if TYPE_CHECKING:
    from ksuit.core.datasets import Dataset


class Collator:
    def __init__(
        self,
        sample_processors: list[SampleProcessor] | None = None,
        sample_to_batch_processors: list[SamplesToBatchProcessor] | None = None,
        batch_processors: list[BatchProcessor] | None = None,
    ):
        self.sample_processors = Factory.create_list(
            sample_processors,
            expected_base_type=SampleProcessor,
        )
        self.sample_to_batch_processors = Factory.create_list(
            sample_to_batch_processors,
            expected_base_type=SamplesToBatchProcessor,
        )
        self.batch_processors = Factory.create_list(
            batch_processors,
            expected_base_type=BatchProcessor,
        )

    def get_processor(self, predicate: Callable[[Any], bool]) -> Any:
        processors = self.sample_processors + self.sample_to_batch_processors + self.batch_processors
        result = None
        for processor in processors:
            if predicate(processor):
                if result is None:
                    result = processor
                else:
                    raise RuntimeError(
                        f"get_processor found at least two valid processors "
                        f"(their types are {type(result).__name__} and {type(processor).__name__})"
                    )
        if result is None:
            raise RuntimeError("no valid processor found")
        return result

    def __call__(self, samples: list[dict[str, Any]], dataset: Dataset | None = None) -> dict[str, Any]:
        # process samples (e.g., image augmentations)
        for sample_processor in self.sample_processors:
            samples = sample_processor(samples, dataset=dataset)

        # create a batch out of individual samples
        if len(self.sample_to_batch_processors) > 0:
            batch = {}
            for sample_to_batch_processor in self.sample_to_batch_processors:
                # sample_to_batch_processors return a dict of batched items -> check overlap
                items = sample_to_batch_processor(samples, dataset=dataset)
                for key, value in items.items():
                    assert key not in batch
                    batch[key] = value
        else:
            batch = default_collate(samples)

        # process the batch (e.g., normalization, mixup/cutmix, ...)
        for batch_processor in self.batch_processors:
            batch = batch_processor(batch, dataset=dataset)
        return batch
