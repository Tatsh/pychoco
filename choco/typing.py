"""Typing helpers."""
from datetime import datetime
from typing import Literal, TypeVar, TypedDict

__all__ = ('ConfigKey', 'SearchResult', 'TestingStatus', 'assert_not_none')

#: Available keys for ``ChocolateyClient.config_set``.
ConfigKey = Literal['defaultPushSource']
T = TypeVar('T')
#: Testing state of a package.
TestingStatus = Literal['Passing', 'Failing']


def assert_not_none(x: T | None) -> T:
    """Helper to change ``T | None`` to ``T``."""
    assert x is not None
    return x


class SearchResult(TypedDict):
    """Represents a package search result."""
    approval_date: datetime | None
    """Approval date."""
    description: str | None
    """Description."""
    documentation_uri: str | None
    """Documentation URL."""
    is_approved: bool
    """If the package is approved."""
    is_cached: bool
    """If the package has been cached."""
    license: str | None
    """License URL."""
    num_downloads: int
    """Total number of downloads."""
    num_version_downloads: int
    """Number of downloads for this version of the package."""
    package_src_uri: str | None
    """Nuspec source."""
    package_url: str | None
    """Package download URL."""
    publish_date: datetime | None
    """Publication date."""
    release_notes_uri: str | None
    """Release notes URL."""
    site: str | None
    """Package website."""
    summary: str | None
    """Summary."""
    tags: list[str]
    """Associated tags."""
    testing_status: TestingStatus
    """Testing status."""
    testing_date: datetime | None
    """Last testing date."""
    title: str | None
    """Unique title of the package."""
    version: str | None
    """Version."""
