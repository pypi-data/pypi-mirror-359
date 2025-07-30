"""Useful protocols for structural subtyping."""

from typing import (
    Any,
    Protocol,
    TypeVar,
    runtime_checkable,
)

_T_contra = TypeVar("_T_contra", contravariant=True)

# Comparison protocols


@runtime_checkable
class SupportsDunderLT(Protocol[_T_contra]):  # noqa: D101
    def __lt__(self, other: _T_contra, /) -> bool: ...


@runtime_checkable
class SupportsDunderGT(Protocol[_T_contra]):  # noqa: D101
    def __gt__(self, other: _T_contra, /) -> bool: ...


@runtime_checkable
class SupportsDunderLE(Protocol[_T_contra]):  # noqa: D101
    def __le__(self, other: _T_contra, /) -> bool: ...


@runtime_checkable
class SupportsDunderGE(Protocol[_T_contra]):  # noqa: D101
    def __ge__(self, other: _T_contra, /) -> bool: ...


@runtime_checkable
class SupportsAllComparisons[T](  # noqa: D101
    SupportsDunderLT[T],
    SupportsDunderGT[T],
    SupportsDunderLE[T],
    SupportsDunderGE[T],
    Protocol,
): ...


type SupportsRichComparison = SupportsDunderLT[Any] | SupportsDunderGT[Any]
SupportsRichComparisonT = TypeVar("SupportsRichComparisonT", bound=SupportsRichComparison)
