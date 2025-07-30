from typing import Any, Literal

from ksuit.utils import reflection_utils

from .factory import Factory


class OptimizerFactory(Factory):
    @staticmethod
    def instantiate(
        config: Any | dict[str, Any] | None,
        *args,
        _recursive_: bool = False,
        **kwargs,
    ) -> Any:
        if not isinstance(config, dict):
            raise NotImplementedError
        # import here to avoid circular imports
        from ksuit.core.optim import Optimizer
        config = dict(config)

        # extract Optimizer kwargs (e.g. clip_grad_value or exclude_bias_from_wd)
        # these should not be passed to the torch optimizer but to the Optimizer afterwards
        wrapped_optim_kwargs = {}
        ctor_arg_and_kwarg_names = reflection_utils.cls_to_ctor_arg_and_kwarg_names(Optimizer)
        for key in ctor_arg_and_kwarg_names:
            if key in config:
                wrapped_optim_kwargs[key] = config.pop(key)

        # fused needs to be set to false for tensor parallel
        if "fused" in kwargs:
            config["fused"] = kwargs.pop("fused")

        torch_optim_ctor = Factory.create_object(
            config,
            _partial_=True,
            _recursive_=_recursive_,
        )
        return Optimizer(
            *args,
            **kwargs,
            **wrapped_optim_kwargs,
            torch_optim_ctor=torch_optim_ctor,
        )
