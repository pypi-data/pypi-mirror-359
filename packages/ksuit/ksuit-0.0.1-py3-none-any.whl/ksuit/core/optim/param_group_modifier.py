from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, final

from torch import nn

if TYPE_CHECKING:
    from ksuit.core.providers import TrainingProgressProvider

class ParamGroupModifier(ABC):
    def __init__(
        self,
        param_group_defaults: dict[str, Any] | None = None,
        training_progress_provider: TrainingProgressProvider | None = None,
    ):
        super().__init__()
        self.logger = logging.getLogger(type(self).__name__)
        self.param_group_defaults = param_group_defaults
        self.training_progress_provider = training_progress_provider

    @abstractmethod
    def populate_parameter_properties(
        self,
        parameter_properties: list[dict[str, Any]],
        model: nn.Module | None = None,
    ) -> list[dict[str, Any]]:
        pass

    @abstractmethod
    def on_before_optimizer_step(
        self,
        param_groups: list[dict[str, Any]], 
        step: int | None = None,
        total_steps: int | None = None,
    ) -> None:
        pass