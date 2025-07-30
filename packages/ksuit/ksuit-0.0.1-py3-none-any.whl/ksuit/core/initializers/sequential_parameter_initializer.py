from __future__ import annotations
from abc import ABC
from typing import Sequence, TYPE_CHECKING

from torch import nn
from ksuit.core.factories import Factory
from .initializer import Initializer
from .single_parameter_initializer import SingleParameterInitializer

if TYPE_CHECKING:
    from ksuit.core.trainers import TrainingContext

class SequentialParameterInitializer(Initializer):
    def __init__(
        self,
        parameter_initializers: Sequence[SingleParameterInitializer],
        allow_uninitialized_parameters: bool = False,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.parameter_initializers = Factory.create_list(
            parameter_initializers,
            expected_base_type=SingleParameterInitializer,
        )
        self.allow_uninitialized_parameters = allow_uninitialized_parameters

    def __call__(self, ctx: TrainingContext) -> None:
        initialized_param_names = set()
        for initializer in self.parameter_initializers:
            initializer(ctx=ctx, initialized_param_names=initialized_param_names)

        # Check for uninitialized parameters
        all_param_names = {name for name, _ in ctx.model.named_parameters()}
        uninitialized = all_param_names - initialized_param_names
        if not self.allow_uninitialized_parameters and uninitialized:
            raise RuntimeError(f"uninitialized parameters: {sorted(uninitialized)}")
