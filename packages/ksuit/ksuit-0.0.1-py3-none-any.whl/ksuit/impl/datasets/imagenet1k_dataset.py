from ksuit.core.datasets import Dataset, DummyDataset
from ksuit.utils import data_generation_utils
from typing import Any, Literal, Self
from pathlib import Path
from PIL import Image
from torchvision.datasets import ImageFolder

class ImageNet1kDataset(Dataset):
    @classmethod
    def get_testrun_dataset(cls, config: dict[str, Any]) -> Self:
        return DummyDataset(
            data_generators=dict(
                x=data_generation_utils.ImageGenerator(height=224, width=224, num_channels=3),
                y=data_generation_utils.UniformCategoricalGenerator(num_classes=1000),
            ),
            attributes=dict(num_classes=1000),
            size=11,
        )

    def __init__(self, root: str, split: Literal["train", "val"]):
        super().__init__()
        assert split in ["train", "val"]
        self.root = Path(root) / split
        self.dataset = ImageFolder(root=self.root)

    @property
    def num_classes(self) -> int:
        return 1000

    def getitem_x(self, idx: int) -> Image:
        return self.dataset[idx][0]

    def getitem_y(self, idx: int) -> int:
        return self.dataset.targets[idx]

    def __len__(self):
        return len(self.dataset)
