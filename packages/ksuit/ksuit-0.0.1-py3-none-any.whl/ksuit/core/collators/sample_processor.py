from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, final

if TYPE_CHECKING:
    from ksuit.core.datasets import Dataset


class SampleProcessor(ABC):
    def __init_subclass__(cls):
        if cls.__call__ != SampleProcessor.__call__:
            raise TypeError(f"{cls.__name__} must not override __call__, override _process instead.")

    @final
    def __call__(self, samples: list[dict[str, Any]], dataset: Dataset | None = None) -> list[dict[str, Any]]:
        """Creates a shallow-copy of the samples list before passing it on to _process. This is done to avoid in-place
        modifications. Ideally, one would deep-copy the samples list, but this would incur a runtime overhead.
        """
        samples = list(samples)
        return self._process(samples, dataset=dataset)

    @abstractmethod
    def _process(self, samples: list[dict[str, Any]], dataset: Dataset | None = None) -> list[dict[str, Any]]:
        pass
