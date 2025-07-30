import hashlib
from functools import partial
from typing import Any

from ksuit.core.factories import Factory
from ksuit.utils.data_generation_utils import DataGenerator

from .dataset import Dataset


class DummyDataset(Dataset):
    def __init__(
        self,
        data_generators: dict[str, DataGenerator | dict[str, Any]],
        size: int,
        attributes: dict[str, Any] | None = None,
        seed: int | None = 0,
    ):
        super().__init__()
        self.data_generators = Factory.create_dict(data_generators, expected_base_type=DataGenerator)
        self.seed = seed
        self.size = size
        # patch getitems
        for key in data_generators.keys():
            assert not hasattr(self, f"getitem_{key}")
            setattr(self, f"getitem_{key}", partial(self._getitem, item=key))
        # patch attributes
        if attributes is not None:
            for key, value in attributes.items():
                assert not hasattr(self, key)
                setattr(self, key, value)

    def _getitem(self, idx: int, item: str) -> Any:
        data_generator = self.data_generators[item]
        if self.seed is None:
            seed = None
        else:
            # hash item and idx to avoid potential patterns/redundancies
            item_hash_bytes = hashlib.sha256(f"{item}-{idx}".encode()).digest()
            item_hash = int.from_bytes(item_hash_bytes[:4], byteorder="big") % (2**32 - 1)
            seed = item_hash + self.seed
        sample = data_generator.sample_one(seed=seed)
        return sample

    def __len__(self) -> int:
        return self.size
