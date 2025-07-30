from typing import Any

from .dataset import Dataset
from .wrapper import Wrapper


class SelectItemsWrapper(Wrapper):
    """Selects a (sub)set of items from the underlying dataset."""

    def __init__(self, dataset: Dataset, items: set[str]):
        super().__init__(dataset=dataset)
        assert isinstance(items, set)
        self._items = items

        # select the getitem functions based on the passed items
        self._getitem_fns = {}
        for item in items:
            if item == "index":
                # getitem_index can be implemented directly, the index of the outer-most dataset will be used
                # (i.e., Subset will not remap the indices)
                self._getitem_fns[item] = self._getitem_index
            else:
                getitem_fn_name = f"getitem_{item}"
                if not hasattr(self.dataset, getitem_fn_name):
                    raise RuntimeError(f"{type(self.dataset)} has no method getitem_{item}")
                self._getitem_fns[item] = getattr(self.dataset, getitem_fn_name)

    @property
    def items(self) -> set[str]:
        return self._items

    @staticmethod
    def _getitem_index(idx: int) -> int:
        return idx

    def __getitem__(self, idx: int) -> dict[str, Any]:
        # check + preprocess idx
        assert isinstance(idx, int), "__getitem__ only supports int indices"
        if idx < 0:
            idx = len(self) + idx

        # load items
        items = {}
        for key, getitem_fn in self._getitem_fns.items():
            items[key] = getitem_fn(idx)
        return items

    def __getattr__(self, item: str) -> Any:
        """Disables __getitems__ support as this is not implemented yet."""
        if item == "__getitems__":
            # new torch versions (>=2.1) implements this which leads to wrappers being circumvented
            # -> disable batched getitems and call getitem instead
            # this occoured when doing DataLoader(dataset) where dataset is SelectItemsWrapper(Subset(...))
            # Subset implements __getitems__ which leads to the fetcher from the DataLoader believing that the
            # SelectItemsWrapper has a __getitems__ and therefore calls it instead of the __getitem__ function
            # returning None makes the DataLoader believe that __getitems__ is not supported
            return None
        return super().__getattr__(item)
