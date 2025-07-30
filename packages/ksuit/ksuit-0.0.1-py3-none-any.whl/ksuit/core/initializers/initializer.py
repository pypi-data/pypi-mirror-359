from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

from torch import nn

if TYPE_CHECKING:
    from ksuit.core.providers import PathProvider
    from ksuit.core.trainers import TrainingContext


class Initializer(ABC):
    def __init__(self, path_provider: PathProvider | None = None):
        self.logger = logging.getLogger(type(self).__name__)
        self.path_provider = path_provider

    @abstractmethod
    def __call__(self, ctx: TrainingContext) -> None:
        pass

    def get_initializer_context(self) -> dict[str, Any]:
        return {}

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.extra_repr()})"

    def extra_repr(self) -> str:
        return ""

    def __str__(self) -> str:
        return repr(self)
