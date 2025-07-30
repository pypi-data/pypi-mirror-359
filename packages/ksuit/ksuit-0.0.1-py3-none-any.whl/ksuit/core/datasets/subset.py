from collections.abc import Callable, Iterator, Sequence
from functools import partial
from typing import Any, Self

from ksuit.utils import reflection_utils

from .dataset import Dataset
from .wrapper import Wrapper


class Subset(Wrapper):
    @classmethod
    def get_testrun_dataset(cls, config: dict[str, Any]) -> Self:
        config = dict(config)
        _ = config.pop("_target_", None)
        dataset_config = config.pop("dataset")
        dataset_config = dict(dataset_config)
        dataset = reflection_utils.type_from_fully_qualified_name_typed(
            dataset_config.pop("_target_"),
            expected_base_type=Dataset,
        )
        return Subset(dataset=dataset.get_testrun_dataset(dataset_config), **config)

    def __init__(self, dataset: Dataset, indices: Sequence[int]):
        super().__init__(dataset=dataset)
        self.indices = indices

    def __len__(self) -> int:
        return len(self.indices)

    def __getattr__(self, item: str) -> Any:
        if item.startswith("getitem_"):
            # all methods starting with getitem_ are called with self.indices[idx]
            getitem_fn = getattr(self.dataset, item)
            return partial(self._call_getitem, getitem_fn)
        return super().__getattr__(item)

    def _call_getitem(self, func: Callable[[int], Any], idx: int) -> Any:
        return func(int(self.indices[idx]))

    def __getitem__(self, idx: int) -> Any:
        return self.dataset[self.indices[idx]]

    def __iter__(self) -> Iterator[Any]:
        # torch.utils.data.Dataset doesn't define __iter__ which makes 'for sample in dataset' run endlessly.
        for i in range(len(self.indices)):
            yield self[self.indices[int(i)]]
