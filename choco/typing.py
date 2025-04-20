"""Typing helpers."""
from __future__ import annotations

from typing import TYPE_CHECKING, Literal, TypeVar, TypedDict

from typing_extensions import NotRequired

if TYPE_CHECKING:
    from datetime import datetime

__all__ = ('Config', 'ConfigKey', 'SearchResult', 'TestingStatus')

ConfigKey = Literal['defaultPushSource']
"""Available keys for ``ChocolateyClient.config_set``."""
T = TypeVar('T')
TestingStatus = Literal['Passing', 'Failing']
"""Testing state of a package."""


class ConfigPyChocoDict(TypedDict):
    """Inner part of the configuration."""
    defaultPushSource: NotRequired[str | None]


class Config(TypedDict):
    """Configuration dictionary after de-serialisation."""
    pychoco: ConfigPyChocoDict


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
