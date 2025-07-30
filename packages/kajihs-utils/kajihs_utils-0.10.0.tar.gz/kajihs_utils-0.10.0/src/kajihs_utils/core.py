"""General utils without dependencies."""

import operator
from collections.abc import Callable, Iterable, Mapping, Sequence
from itertools import pairwise, starmap
from typing import Any, Literal, overload

from kajihs_utils.protocols import (
    SupportsDunderLT,
)


@overload
def get_first[K, V, D](d: Mapping[K, V], /, keys: Iterable[K], default: D = None) -> V | D: ...


@overload
def get_first[K, V, D](
    d: Mapping[K, V],
    /,
    keys: Iterable[K],
    default: Any = None,  # noqa: ANN401 # TODO: Check if it's possible to annotate default with D instead
    *,
    no_default: Literal[True] = True,
) -> V: ...


@overload
def get_first[K, V, D](
    d: Mapping[K, V], /, keys: Iterable[K], default: D = None, *, no_default: bool = True
) -> V | D: ...


def get_first[K, V, D](
    d: Mapping[K, V], /, keys: Iterable[K], default: D = None, *, no_default: bool = False
) -> V | D:
    """
    Return the value of the first key that exists in the mapping.

    Args:
        d: The dictionary to search in.
        keys: The sequence of keys to look for.
        default: The value to return if no key is found.
        no_default: If `True`, raises a `KeyError` if no key is found.

    Returns:
        The value associated with the first found key, or the default value if not found.

    Raises:
        KeyError: If `no_default` is `True` and none of the keys are found.

    Examples:
        >>> d = {"a": 1, "b": 2, "c": 3}
        >>> get_first(d, ["x", "a", "b"])
        1
        >>> get_first(d, ["x", "y"], default=0)
        0
        >>> get_first(d, ["x", "y"], no_default=True)  # Raises: KeyError
        Traceback (most recent call last):
        ...
        KeyError: "None of the keys ['x', 'y'] were found in the mapping."
    """
    for key in keys:
        if key in d:
            return d[key]

    if no_default:
        msg = f"None of the keys {list(keys)} were found in the mapping."
        raise KeyError(msg)

    return default


def is_sorted(values: Iterable[SupportsDunderLT[Any]], /, *, reverse: bool = False) -> bool:
    """
    Determine if the given iterable is sorted in ascending or descending order.

    Args:
        values: An iterable of comparable items supporting the < operator.
        reverse: If False (default), checks for non-decreasing order; if True,
            checks for non-increasing order.

    Returns:
        True if the sequence is sorted according to the given order, False otherwise.

    Examples:
        >>> is_sorted([1, 2, 2, 3])
        True
        >>> is_sorted([3, 2, 1], reverse=True)
        True
        >>> is_sorted([2, 1, 3])
        False
        >>> is_sorted([])
        True
        >>> is_sorted([42])
        True
        >>> # Works with generators as well
        >>> is_sorted(x * x for x in [1, 2, 3, 4])
        True
        >>> # Equal elements are considered sorted
        >>> is_sorted([1, 1, 1])
        True
    """
    op = operator.le if not reverse else operator.ge
    return all(starmap(op, pairwise(values)))


def bisect_predicate[T](
    seq: Sequence[T],
    predicate: Callable[[T], bool],
    lo: int = 0,
    hi: int | None = None,
) -> int:
    """
    Find the first index where predicate flips from True to False using binary search.

    In other words: Find first index where predicate(seq[i]) becomes False.

    The sequence must be partitioned such that all elements where predicate(item) is True
    appear before elements where predicate(item) is False. This is a generalized version
    of bisect_right that works with arbitrary predicates rather than comparison operators.

    Args:
        seq: Partitioned sequence to search. Must have all True-predicate elements
            before any False-predicate elements.
        predicate: Function that returns True for elements that should be considered
            "left" of the insertion point. Typically a condition like lambda x: x < target.
        lo: Lower bound index to start search (inclusive).
        hi: Upper bound index to end search (exclusive). Defaults to len(seq).

    Returns:
        Insertion point index where predicate first fails. This will be:
        - 0 if predicate fails for all elements
        - len(seq) if predicate holds for all elements
        - First index where predicate(seq[i]) == False otherwise

    Examples:
        Find first non-positive number (predicate=lambda x: x <= 0):
        >>> bisect_predicate([-5, -3, 0, 2, 5], lambda x: x <= 0)
        3

        All elements satisfy predicate:
        >>> bisect_predicate([True, True, True], lambda b: b)
        3

        Edge case - empty sequence:
        >>> bisect_predicate([], lambda x: True)
        0

        Custom search range:
        >>> bisect_predicate([1, 3, 5, 7, 9], lambda x: x < 6, lo=1, hi=4)
        3

    Note:
        Similar to bisect.bisect_right but works with arbitrary predicates.
        Requires the array to be properly partitioned - undefined behavior otherwise.
    """
    hi = hi or len(seq)

    while lo < hi:
        mid = (lo + hi) // 2
        if predicate(seq[mid]):
            # print(f"Can complete {mid}")
            lo = mid + 1
        else:
            # print(f"Can't complete {mid}")
            hi = mid
    return lo
