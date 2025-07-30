from __future__ import annotations

from typing import TYPE_CHECKING

from ksuit.core.datasets import SelectItemsWrapper

if TYPE_CHECKING:
    from ksuit.core.collators import Collator
    from ksuit.core.datasets import Dataset


class DataProvider:
    def __init__(self, datasets: dict[str, Dataset], collators: dict[str, Collator] | None = None):
        self.datasets = datasets
        self.collators = collators

    def get_dataset(self, key: str, items: set[str] | None = None):
        dataset = self.datasets[key]
        if items is not None:
            dataset = SelectItemsWrapper(dataset=dataset, items=items)
        return dataset

    def get_collator(self, key: str | None) -> Collator | None:
        if key is None:
            return None
        if self.collators is None:
            raise KeyError(f"no collators defined (could not retrieve {key=})")
        return self.collators[key]
