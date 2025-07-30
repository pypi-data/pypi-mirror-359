from collections.abc import Callable, Iterable
from itertools import repeat
from typing import Any, TypeVar

T = TypeVar("T")


def _ntuple(n: int) -> Callable[[T | Iterable[T]], tuple[T, ...]]:
    def parse(x: T | Iterable[T]) -> tuple[T, ...]:
        if isinstance(x, Iterable) and not isinstance(x, (str | bytes)):
            x = tuple(x)
            assert len(x) == n
            return x
        return tuple(repeat(x, n))

    return parse


def _is_ntuple(n: int) -> Callable[[Any], bool]:
    def check(x: Any) -> bool:
        return isinstance(x, tuple) and len(x) == n

    return check


def to_ntuple(x: T, n: int) -> tuple[T, ...]:
    return _ntuple(n=n)(x)


def is_ntuple(x: T, n: int) -> bool:
    return _is_ntuple(n=n)(x)


to_2tuple = _ntuple(2)
is_2tuple = _is_ntuple(2)
to_3tuple = _ntuple(3)
is_3tuple = _is_ntuple(3)
to_4tuple = _ntuple(4)
is_4tuple = _is_ntuple(4)
to_5tuple = _ntuple(5)
is_5tuple = _is_ntuple(5)
to_6tuple = _ntuple(6)
is_6tuple = _is_ntuple(6)
to_7tuple = _ntuple(7)
is_7tuple = _is_ntuple(7)
to_8tuple = _ntuple(8)
is_8tuple = _is_ntuple(8)
to_9tuple = _ntuple(9)
is_9tuple = _is_ntuple(9)


def exactly_one_non_none(*args) -> bool:
    """True if exactly one argument is not None."""
    return sum(arg is not None for arg in args) == 1


def all_or_none(*args) -> bool:
    """True if all arguments are None or all are not None."""
    return sum(arg is not None for arg in args) in [0, len(args)]


def at_least_one_non_none(*args) -> bool:
    """True if at least one argument is not None."""
    return sum(arg is not None for arg in args) > 0


def at_least_one_true(*args) -> bool:
    """True if at least one argument is True."""
    assert all(isinstance(arg, bool) for arg in args)
    return sum(arg is True for arg in args) > 0


def at_most_one_non_none(*args) -> bool:
    """True if zero or one arguments are not None."""
    return sum(arg is not None for arg in args) <= 1


def all_none(*args) -> bool:
    """True if all arguments are None."""
    return sum(arg is not None for arg in args) == 0

def string_is_int(value: str) -> bool:
    try:
        _ = int(value)
        return True
    except ValueError:
        return False