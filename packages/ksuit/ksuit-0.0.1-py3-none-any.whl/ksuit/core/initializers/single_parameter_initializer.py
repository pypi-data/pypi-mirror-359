from __future__ import annotations
import fnmatch
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from torch import nn

from .initializer import Initializer
from ksuit.utils import reflection_utils

if TYPE_CHECKING:
    from ksuit.core.trainers import TrainingContext


class SingleParameterInitializer(Initializer, ABC):
    def __init__(
        self,
        pattern: str,
        module_type: str | type[nn.Module] | None = None,
        allow_duplicate_initialization: bool = False,
    ):
        super().__init__()
        self.pattern = pattern
        if isinstance(module_type, str):
            module_type = reflection_utils.type_from_fully_qualified_name(module_type)
        self.module_type = module_type
        self.allow_duplicate_initialization = allow_duplicate_initialization

    def _apply(
        self,
        model: nn.Module,
        initialized_param_names: set[str] | None = None,
        prefix: str | None = None,
    ) -> None:
        for name, param in model.named_parameters():
            if fnmatch.fnmatch(name, pat=self.pattern):
                if prefix is None:
                    full_name = name
                else:
                    full_name = f"{prefix}.{name}"
                if not self.allow_duplicate_initialization and full_name in initialized_param_names:
                    raise RuntimeError(f"duplicate initialization of {full_name}")
                self.initialize_parameter(param)
                initialized_param_names.add(full_name)

    def __call__(self, ctx: TrainingContext, initialized_param_names: set[str] | None = None) -> None:
        model = ctx.model
        if not self.allow_duplicate_initialization and initialized_param_names is None:
            raise ValueError("allow_duplicate_initialization=False requires passing initialized_param_names")
        if self.module_type is None:
            # matching based on parameter name w.r.t. model
            self._apply(model=model, initialized_param_names=initialized_param_names)
        else:
            # matching based on parameter name w.r.t. submodel where submodel has module_type
            for module_name, module in model.named_modules():
                if isinstance(module, self.module_type):
                    self._apply(model=module, initialized_param_names=initialized_param_names, prefix=module_name)

    @abstractmethod
    def initialize_parameter(self, parameter: nn.Parameter) -> None:
        pass

    def extra_repr(self) -> str:
        result = super().extra_repr() + f"pattern={self.pattern}"
        if self.module_type is not None:
            result += f",module_type={self.module_type.__name__}"
        return result
