from functools import partial
from typing import Any, Sequence, TypeVar, overload

from ksuit.utils import reflection_utils

T = TypeVar("T")


class Factory:
    @classmethod
    @overload
    def create_object(
        cls,
        config: Any | dict[str, Any] | None,
        *args,
        expected_base_type: None = ...,
        **kwargs,
    ) -> Any:
        ...

    @classmethod
    @overload
    def create_object(
        cls,
        config: Any | dict[str, Any] | None,
        *args,
        expected_base_type: type[T] = ...,
        **kwargs,
    ) -> T:
        ...

    @classmethod
    def create_object(
        cls,
        config: Any | dict[str, Any] | None,
        *args,
        expected_base_type: type[T] | None = None,
        **kwargs,
    ) -> T | Any:
        """Instantiates a single object via `Factory.instantiate`. By default `hydra.utils.instantiate` is used as
        implementation of `Factory.instantiate`.
        """
        if config is None:
            return None
        obj = cls.instantiate(config, *args, **kwargs)
        if expected_base_type is not None and not isinstance(obj, expected_base_type):
            raise TypeError(f"Created object is type={type(obj).__name__} not {expected_base_type.__name__}")
        return obj

    @classmethod
    @overload
    def create_list(
        cls,
        collection: list[Any] | list[dict[str, Any]] | None,
        *args,
        expected_base_type: None = ...,
        **kwargs,
    ) -> list[Any]:
        ...

    @classmethod
    @overload
    def create_list(
        cls,
        collection: list[Any] | list[dict[str, Any]] | None,
        *args,
        expected_base_type: type[T] = ...,
        **kwargs,
    ) -> list[T]:
        ...

    @classmethod
    def create_list(
        cls,
        collection: list[Any] | list[dict[str, Any]] | None,
        *args,
        expected_base_type: type[T] | None = None,
        **kwargs,
    ) -> list[T | Any]:
        """Instantiates a list of objects. `args` and `kwargs` will be passed to each list entry."""
        if collection is None:
            return []
        if not isinstance(collection, list):
            raise TypeError(f"invalid collection type '{type(collection).__name__}' (expected list)")
        objs = [cls.instantiate(config, *args, **kwargs) for config in collection]
        if objs is not None and len(objs) > 0 and expected_base_type is not None:
            for i, obj in enumerate(objs):
                if not isinstance(obj, expected_base_type):
                    raise TypeError(
                        f"Object[{i}] of created list is type={type(obj).__name__} not {expected_base_type.__name__}"
                    )
        return objs

    @classmethod
    @overload
    def create_dict(
        cls,
        collection: dict[Any, Any] | dict[Any, dict[str, Any]] | None,
        *args,
        expected_base_type: None = ...,
        **kwargs,
    ) -> dict[Any, Any]:
        ...

    @classmethod
    @overload
    def create_dict(
        cls,
        collection: dict[Any, Any] | dict[Any, dict[str, Any]] | None,
        *args,
        expected_base_type: type[T] = ...,
        **kwargs,
    ) -> dict[Any, T]:
        ...

    @classmethod
    def create_dict(
        cls,
        collection: dict[Any, Any] | dict[Any, dict[str, Any]] | None,
        *args,
        expected_base_type: type[T] | None = None,
        **kwargs,
    ) -> dict[Any, Any]:
        """Instantiates a dict of objects. `args` and `kwargs` will be passed to each dictionary item."""
        if collection is None:
            return {}
        if not isinstance(collection, dict):
            raise TypeError(f"invalid collection type '{type(collection).__name__}' (expected dict)")
        objs = {key: cls.instantiate(config, *args, **kwargs) for key, config in collection.items()}
        if objs is not None and len(objs) > 0 and expected_base_type is not None:
            for key, obj in objs.items():
                if not isinstance(obj, expected_base_type):
                    raise TypeError(
                        f"Object[{key}] of created dict is type={type(obj).__name__} not {expected_base_type.__name__}"
                    )
        return objs

    @staticmethod
    def instantiate(
        config: Any | dict[str, Any] | None,
        *args,
        _recursive_: bool = False,
        **kwargs,
    ) -> Any:
        """`hydra.utils.instantiate` has weird behaviors:
        - tuples are converted to lists (tuples should be preserved because equality checks between tuple and lists
          fail even if they contain the same content in the same order)
        - dataclasses can already be objects and can simply be returned (hydra converts them to a dictionary)

        This method aims to mimic `hydra.utils.instantiate` without these edge cases that are not needed for ksuit.
        """
        if isinstance(config, partial | type):
            return config(*args, **kwargs)
        if not isinstance(config, dict):
            return config
        if "_target_" not in config:
            raise KeyError(f"no _target_ key in config (got {list(config.keys())})")
        config = dict(config)

        # _target_
        _target_ = config.pop("_target_")
        if isinstance(_target_, partial | type):
            # passing type as _target_
            # cfg = dict(_target_=SomeClass)
            ctor = _target_
        else:
            ctor = reflection_utils.type_from_fully_qualified_name(_target_)

        # _recursive_
        if _recursive_:
            for key in list(config.keys()):
                if isinstance(config[key], dict) and "_target_" in config[key]:
                    config[key] = Factory.instantiate(config[key], _recursive_=True)
                if isinstance(config[key], list):
                    for i in range(len(config[key])):
                        if isinstance(config[key][i], dict) and "_target_" in config[key][i]:
                            config[key][i] = Factory.instantiate(config[key][i], _recursive_=True)

        # check overlapping keys -> kwargs dominate
        # - e.g., cifar10 classifier -> transfer to cifar100 -> num_classes=10 is in config and needs to be overwritten
        overlapping_keys = config.keys() & kwargs.keys()
        if len(overlapping_keys) > 0:
            for key in overlapping_keys:
                config.pop(key)

        # _partial_
        _partial_ = config.pop("_partial_", False)
        if _partial_:
            return partial(ctor, *args, **config, **kwargs)
        _partial_ = kwargs.pop("_partial_", False)
        if _partial_:
            return partial(ctor, *args, **config, **kwargs)

        # instantiate
        _args_ = config.pop("_args_", [])
        if not isinstance(_args_, Sequence):
            raise TypeError(f"_args_ should be a sequence (e.g., list), got {type(_args_).__name__}")
        if len(_args_) > 0 and len(args) > 0:
            raise RuntimeError(f"got _args_ ({_args_}) and *args {args}")
        return ctor(*args, *_args_, **config, **kwargs)
