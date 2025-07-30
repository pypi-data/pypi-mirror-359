from pathlib import Path
from typing import Any, Literal, Self

from PIL import Image
from torchvision.datasets import CIFAR10

from ksuit.core.datasets import Dataset, DummyDataset
from ksuit.utils import data_generation_utils


class Cifar10Dataset(Dataset):
    @classmethod
    def get_testrun_dataset(cls, config: dict[str, Any]) -> Self:
        return DummyDataset(
            data_generators=dict(
                x=data_generation_utils.ImageGenerator(height=32, width=32, num_channels=3),
                y=data_generation_utils.UniformCategoricalGenerator(num_classes=10),
            ),
            attributes=dict(num_classes=10),
            size=11,
        )

    def __init__(self, split: Literal["train", "test"]):
        super().__init__()
        if split not in ["train", "test"]:
            raise ValueError(f"invalid split '{split}', expected 'train' or 'test'")
        # TODO global path
        root = Path("./data/cifar10")
        root.mkdir(exist_ok=True, parents=True)

        self.split = split
        self.dataset = CIFAR10(root=root, train=split == "train", download=True)

    @property
    def num_classes(self) -> int:
        return 10

    def getitem_x(self, idx: int) -> Image:
        return self.dataset[idx][0]

    def getitem_y(self, idx: int) -> int:
        return self.dataset.targets[idx]

    def __len__(self) -> int:
        return len(self.dataset)
