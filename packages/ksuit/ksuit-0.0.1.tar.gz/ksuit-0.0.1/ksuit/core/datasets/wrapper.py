from typing import Any

from ksuit.core.factories import Factory

from .dataset import Dataset


class Wrapper(Dataset):
    def __init__(self, dataset: Dataset):
        super().__init__()
        self.dataset = Factory.create_object(dataset, expected_base_type=Dataset)

    @property
    def items(self) -> set[str]:
        """Returns all items of the wrapped dataset and the (optional) items of the wrapper."""
        return self.dataset.items | super().items

    def __len__(self) -> int:
        return len(self.dataset)

    def __getattr__(self, item: str) -> Any:
        """Forwards calls to methods starting with getitem_ to the underlying dataset."""
        if item.startswith("getitem_"):
            return getattr(self.dataset, item)
        return getattr(self.dataset, item)
