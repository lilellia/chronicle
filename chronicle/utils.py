from pathlib import Path
from typing import Callable, TypeVar


T = TypeVar("T")


def datafile_exists(id: str, root: Path) -> bool:
    """
    Determine whether the datafile already exists in the tree.
    """
    g = root.glob(f"**/data_{id}.json")
    return next(g, None) is not None


def function_compose(func: Callable[[T], T], arg: T, n: int) -> T:
    """
    Repeatedly apply the given function the given number of times.
    """
    for _ in range(n):
        arg = func(arg)

    return arg
