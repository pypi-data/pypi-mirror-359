from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, final

if TYPE_CHECKING:
    from ksuit.core.datasets import Dataset


class SamplesToBatchProcessor(ABC):
    def __init_subclass__(cls):
        if cls.__call__ != SamplesToBatchProcessor.__call__:
            raise TypeError(f"{cls.__name__} must not override __call__, override _process instead.")

    @final
    def __call__(self, samples: list[dict[str, Any]], dataset: Dataset | None = None) -> dict[str, Any]:
        """Simply passes samples to _process. This method is used to remain consistent with other processors."""
        return self._process(samples, dataset=dataset)

    @abstractmethod
    def _process(self, samples: list[dict[str, Any]], dataset: Dataset | None = None) -> dict[str, Any]:
        pass
