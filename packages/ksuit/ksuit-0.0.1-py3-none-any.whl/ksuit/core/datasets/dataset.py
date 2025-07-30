import logging
from collections.abc import Iterator
from typing import Any, Self

import torch.utils.data


class Dataset(torch.utils.data.Dataset):
    @classmethod
    def get_testrun_dataset(cls, config: dict[str, Any]) -> Self:
        raise NotImplementedError(f"{Dataset.__name__} does not support get_testrun_dataset")

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(type(self).__name__)

    @property
    def items(self) -> set[str]:
        """Returns all items of the dataset."""
        # NOTE: while this is static for datasets and their implementation, it is not  static for
        # wrappers and is therefore implemented as instance attribute instead of a class attribute
        return {
            attr[len("getitem_"):]
            for attr in dir(self)
            if attr.startswith("getitem_") and callable(getattr(self, attr))
        }

    def getitem(self, item: str, idx: int) -> Any:
        assert item in self.items
        return getattr(self, f"getitem_{item}")(idx)

    def __len__(self) -> int:
        raise NotImplementedError

    def __getitem__(self, idx: int) -> dict[str, Any]:
        result = {}
        for item in self.items:
            getitem_fn = getattr(self, f"getitem_{item}")
            result[item] = getitem_fn(idx)
        return result

    def __iter__(self) -> Iterator[Any]:
        # torch.utils.data.Dataset doesn't define __iter__ which makes 'for sample in dataset' run endlessly.
        for i in range(len(self)):
            yield self[i]
