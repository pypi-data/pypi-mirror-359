from abc import abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

import torch
from torchvision.transforms.functional import to_pil_image


@dataclass
class DataGenerator:
    def sample_one(self, seed: int | None = None) -> Any:
        """Samples a single data point. Optionally uses a `seed` for determinism."""
        return self.sample_many(size=1, seed=seed)[0]

    def sample_many(self, size: int, seed: int | None = None) -> Sequence[Any]:
        """Samples `size` data points (by default 1 data point). Optionally uses a `seed` for determinism."""
        if seed is None:
            generator = None
        else:
            generator = torch.Generator().manual_seed(seed)
        return self._sample(size=size, generator=generator)

    @abstractmethod
    def _sample(self, size: int, generator: torch.Generator | None = None) -> Sequence[Any]:
        """Samples `size` data points (optionally) using a (seeded) `torch.Generator`."""


@dataclass
class GaussianGenerator(DataGenerator):
    """Samples a gaussian-distributed tensor of shape `(size, *shape)` with corresponding `mean` and `std`."""

    shape: tuple[int, ...]
    mean: float = 0.0
    std: float = 1.0

    def _sample(self, size: int, generator: torch.Generator | None = None) -> Sequence[Any]:
        return torch.randn(size=(size, *self.shape), generator=generator) * self.std + self.mean


@dataclass
class UniformGenerator(DataGenerator):
    """Samples a uniform-distributed float tensor of shape `(size, *shape)` within `[lower_bound, upper_bound]`."""
    shape: tuple[int, ...]
    lower_bound: float = 0.0
    upper_bound: float = 1.0

    def __post_init__(self):
        if self.lower_bound > self.upper_bound:
            raise ValueError(f"expected lower_bound <= upper_bound ({self.lower_bound} > {self.upper_bound})")

    def _sample(self, size: int, generator: torch.Generator | None = None) -> Sequence[Any]:
        lb = self.lower_bound
        ub = self.upper_bound
        return torch.rand(size=(size, *self.shape), generator=generator) * (ub - lb) + lb


@dataclass
class UniformCategoricalGenerator(DataGenerator):
    """Samples a uniform-distributed class index tensor of shape `(size,)` with long values that are smaller
    than `num_classes`.
    """
    # TODO rename to something else (e.g., language modeling doesnt have classes)
    num_classes: int
    shape: tuple[int, ...] | None = None

    def __post_init__(self):
        if self.num_classes < 2:
            raise ValueError("num_classes must be >= 2")

    def _sample(self, size: int, generator: torch.Generator | None = None) -> Sequence[Any]:
        return torch.randint(high=self.num_classes, size=(size, *(self.shape or [])), generator=generator)


@dataclass
class ImageGenerator(DataGenerator):
    """Samples list of `PIL.Image` with uniform-distributed pixels with corresponding `height` and `width`."""
    height: int
    width: int
    num_channels: int = 3

    def __post_init__(self):
        if self.num_channels not in [1, 3]:
            raise ValueError("num_channels must be 1 (grayscale) or 3 (RGB)")

    def _sample(self, size: int, generator: torch.Generator | None = None) -> Sequence[Any]:
        imgs = torch.rand(size=(size, self.num_channels, self.height, self.width), generator=generator)
        return [to_pil_image(img) for img in imgs]
