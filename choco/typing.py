"""Typing helpers."""
from typing import TypeVar

__all__ = ('assert_not_none',)

T = TypeVar('T')


def assert_not_none(x: T | None) -> T:
    """Helper to change ``T | None`` to ``T``."""
    assert x is not None
    return x
