import importlib
import inspect
from typing import Any, TypeVar

T = TypeVar("T")


def cls_to_ctor_arg_and_kwarg_names(cls: type) -> set[str]:
    own_names = set(inspect.signature(cls).parameters.keys())
    if cls.__base__ is not None:
        return own_names | cls_to_ctor_arg_and_kwarg_names(cls.__base__)
    return own_names


def obj_to_ctor_attr_names(obj: Any) -> set[str]:
    """Returns all attrs that are also an argument in the constructor."""
    # get all names of arguments
    names = cls_to_ctor_arg_and_kwarg_names(type(obj))
    # remove names that are not stored as attrs
    for name in list(names):
        if not hasattr(obj, name):
            names.remove(name)
    return names


# TODO can be solved via overload
def type_from_fully_qualified_name_typed(fqn: str, expected_base_type: type[T]) -> type[T]:
    result = type_from_fully_qualified_name(fqn=fqn)
    if not issubclass(result, expected_base_type):
        raise TypeError(f"expecting type inherited from '{expected_base_type.__name__}', not '{result.__name__}'")
    return result


def type_from_fully_qualified_name(fqn: str) -> type:
    if "." not in fqn == 1:
        raise NotImplementedError(f"fully qualified name '{fqn}' has no no module path")
    split = fqn.split(".")
    module_path = ".".join(split[:-1])
    class_name = split[-1]
    module = importlib.import_module(module_path)
    if not hasattr(module, class_name):
        raise ModuleNotFoundError(f"{module_path=} has no {class_name=}")
    return getattr(module, class_name)
