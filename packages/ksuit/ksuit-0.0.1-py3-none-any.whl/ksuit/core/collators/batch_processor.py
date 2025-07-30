from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, final

if TYPE_CHECKING:
    from ksuit.core.datasets import Dataset


class BatchProcessor(ABC):
    def __init_subclass__(cls):
        if cls.__call__ != BatchProcessor.__call__:
            raise TypeError(f"{cls.__name__} must not override __call__, override _process instead.")

    @final
    def __call__(self, batch: dict[str, Any], dataset: Dataset | None = None) -> dict[str, Any]:
        """Creates a shallow-copy of the batch before passing it on to _process. This is done to avoid in-place
        modifications. Ideally, one would deep-copy the batch, but this would incur a runtime overhead.
        """
        batch = dict(batch)
        return self._process(batch, dataset=dataset)

    @abstractmethod
    def _process(self, batch: dict[str, Any], dataset: Dataset | None = None) -> dict[str, Any]:
        pass
