"""Typing helpers."""
from datetime import datetime
from typing import Literal, TypeVar, TypedDict

__all__ = ('ConfigKey', 'SearchResult', 'TestingStatus', 'assert_not_none')

ConfigKey = Literal['defaultPushSource']
T = TypeVar('T')
TestingStatus = Literal['Passing', 'Failing']


def assert_not_none(x: T | None) -> T:
    """Helper to change ``T | None`` to ``T``."""
    assert x is not None
    return x


class SearchResult(TypedDict):
    approval_date: datetime | None
    description: str | None
    documentation_uri: str | None
    is_approved: bool
    is_cached: bool
    license: str | None
    num_downloads: int
    num_version_downloads: int
    package_src_uri: str | None
    package_url: str | None
    publish_date: datetime | None
    release_notes_uri: str | None
    site: str | None
    summary: str | None
    tags: list[str]
    testing_status: TestingStatus
    testing_date: datetime | None
    title: str | None
    version: str | None
