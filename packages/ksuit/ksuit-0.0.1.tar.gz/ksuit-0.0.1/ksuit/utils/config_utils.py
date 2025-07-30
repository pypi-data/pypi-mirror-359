from copy import deepcopy
from typing import Any, Mapping, Sequence

from .reflection_utils import obj_to_ctor_attr_names


def get_by_path(config: Any, path: str) -> Any:
    for p in path.split("."):
        if isinstance(config, dict):
            if p not in config:
                raise KeyError(f"key '{p}' not found (possible keys: {sorted(config.keys())})")
            config = config[p]
        elif isinstance(config, list):
            if not p.isnumeric():
                raise ValueError(f"key '{p}' should be numeric as it is the index of a list")
            p = int(p)
            if p >= len(config):
                raise IndexError(f"list only has {len(config)} items (index {p} is too big)")
            config = config[p]
        else:
            if not hasattr(config, p):
                raise KeyError(f"key '{p}' is invalid (valid keys: {sorted(config.keys())})")
            config = getattr(config, p)
    return config


def set_by_path(config: Any, path: str, value: Any) -> None:
    split = path.split(".")
    if len(split) > 1:
        config = get_by_path(config, ".".join(split[:-1]))
    p = split[-1]
    if isinstance(config, dict):
        config[p] = value
    elif isinstance(config, list):
        if not p.isnumeric():
            raise ValueError(f"key '{p}' should be numeric as it is the index of a list")
        p = int(p)
        config[p] = value
    else:
        return setattr(config, p, value)


def delete_by_path(config: Any, path: str) -> None:
    split = path.split(".")
    if len(split) > 1:
        config = get_by_path(config, ".".join(split[:-1]))
    p = split[-1]
    if isinstance(config, dict):
        if p not in config:
            raise KeyError(f"key '{p}' not found (possible keys: {sorted(config.keys())})")
        config.pop(p)
    elif isinstance(config, list):
        if not p.isnumeric():
            raise ValueError(f"key '{p}' should be numeric as it is the index of a list")
        p = int(p)
        config.pop(p)
    else:
        raise ValueError(f"{path=} needs to be a dict or list to delete it")


def has_path(config: Any, path: str) -> bool:
    split = path.split(".")
    if len(split) > 1:
        config = get_by_path(config, ".".join(split[:-1]))
    p = split[-1]
    if isinstance(config, dict):
        return p in config
    if isinstance(config, list):
        if not p.isnumeric():
            raise ValueError(f"key '{p}' should be numeric as it is the index of a list")
        p = int(p)
        return p < len(config)
    return hasattr(config, p)


def replace_lists_with_dicts(root: dict[Any, Any]) -> dict[Any, Any]:
    """wandb cant handle lists in configs -> transform lists into dicts with str(i) as key"""
    root = deepcopy(root)
    return _replace_lists_with_dicts_impl(dict(root=root))["root"]


def _replace_lists_with_dicts_impl(root: Any) -> dict[Any, Any]:
    if not isinstance(root, dict):
        return
    for k, v in root.items():
        if isinstance(v, list):
            root[k] = {str(i): vitem for i, vitem in enumerate(v)}
        elif isinstance(v, dict):
            root[k] = _replace_lists_with_dicts_impl(root[k])
    return root


def object_to_config(obj: Any) -> dict[str, Any]:
    if isinstance(obj, int | float | str | bool | type(None)):
        raise RuntimeError(f"serialization of standalone primitive types not supported {type(obj)}")
    return _object_to_config(obj)


def _object_to_config(obj: Any) -> dict[str, Any]:
    if isinstance(obj, int | float | str | bool | type(None)):
        return obj
    if isinstance(obj, Mapping):
        return {key: _object_to_config(value) for key, value in obj.items()}
    if isinstance(obj, Sequence):
        # equality checks between list and tuple with same content fail -> preserve type
        if isinstance(obj, tuple):
            return tuple(_object_to_config(item) for item in obj)
        return [_object_to_config(item) for item in obj]
    # nested objects -> add _target_ and all objects of its constructor
    obj_as_dict = dict(_target_=f"{type(obj).__module__}.{type(obj).__qualname__}")
    ctor_attr_names = obj_to_ctor_attr_names(obj)
    for name in ctor_attr_names:
        obj_as_dict[name] = _object_to_config(getattr(obj, name))
    return obj_as_dict


def populate_from_initializer_contexts(
    config: dict[str, Any],
    initializer_contexts: list[dict[str, Any]],
) -> dict[str, Any]:
    config = deepcopy(config)
    _populate_from_initializer_contexts(config=config, initializer_contexts=initializer_contexts)
    return config


def _populate_from_initializer_contexts(
    config: dict[str, Any],
    initializer_contexts: list[dict[str, Any]],
    parent_key: str | None = None,
    parent_value: Any | None = None,
):
    if isinstance(config, list):
        for item in config:
            _populate_from_initializer_contexts(
                config=item,
                initializer_contexts=initializer_contexts
            )
    elif isinstance(config, dict):
        if "_from_initializer_" in config:
            # select from initializer_contexts
            from_initializer_path = config.pop("_from_initializer_")
            from_initializer_config = get_by_path(config=initializer_contexts, path=from_initializer_path)
            # integrate into config based on retrieved type
            if isinstance(from_initializer_config, dict):
                # merge with specified config (explicitly specified properties preceed initializer_context properties)
                from_initializer_config = deepcopy(from_initializer_config)
                for key, value in from_initializer_config.items():
                    if key not in config:
                        config[key] = value
            elif isinstance(from_initializer_config, list):
                raise NotImplementedError("retrieving list in _from_initializer_ not supported")
            else:
                # scalar assignment
                if len(config) > 0:
                    raise ValueError(
                        f"expecting dict with _from_initializer_ that selects a scalar to be empty (got {config})",
                    )
                if parent_key is None or parent_value is None:
                    raise RuntimeError
                parent_value[parent_key] = from_initializer_config
        else:
            for key, value in config.items():
                _populate_from_initializer_contexts(
                    config=value,
                    initializer_contexts=initializer_contexts,
                    parent_key=key,
                    parent_value=config,
                )
