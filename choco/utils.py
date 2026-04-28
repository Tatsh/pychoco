"""Utility functions."""
from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar, cast
import logging
import re
import uuid

from dateutil.parser import isoparse

from .constants import (
    FEED_NAMESPACES,
    FEED_PROPERTIES_TAG,
    FEED_SUMMARY_TAG,
    FEED_TITLE_TAG,
    METADATA_DESCRIPTION_TAG,
    METADATA_DOCS_URL_TAG,
    METADATA_DOWNLOAD_COUNT_TAG,
    METADATA_GALLERY_DETAILS_URL_TAG,
    METADATA_IS_APPROVED_TAG,
    METADATA_IS_DOWNLOAD_CACHE_AVAILABLE_TAG,
    METADATA_LICENSE_URL_TAG,
    METADATA_PACKAGE_APPROVED_DATE_TAG,
    METADATA_PACKAGE_SOURCE_URL_TAG,
    METADATA_PACKAGE_TEST_RESULT_STATUS_DATE_TAG,
    METADATA_PACKAGE_TEST_RESULT_STATUS_TAG,
    METADATA_PROJECT_URL_TAG,
    METADATA_PUBLISHED_TAG,
    METADATA_RELEASE_NOTES_TAG,
    METADATA_TAGS_TAG,
    METADATA_VERSION_DOWNLOAD_COUNT_TAG,
    METADATA_VERSION_TAG,
)
from .typing import SearchResult, TestingStatus

if TYPE_CHECKING:
    from collections.abc import Mapping
    from datetime import datetime
    from pathlib import Path
    from xml.etree.ElementTree import Element
    import zipfile

__all__ = ('append_dir_to_zip_recursive', 'entry_to_search_result', 'generate_unique_id',
           'tag_text_or')

T = TypeVar('T')
utils_logger = logging.getLogger(__name__)


def generate_unique_id() -> str:
    """
    Generate a unique ID for elements in ``_rels/.rels``.

    Returns
    -------
    str
    """
    return f'R{str(uuid.uuid4()).replace("-", "")}'.upper()


def append_dir_to_zip_recursive(root: Path, z: zipfile.ZipFile) -> None:
    """
    Append a directory recursively to a zip file.

    Parameters
    ----------
    root : Path
        The root directory to append.
    z : zipfile.ZipFile
        The zip file to append to.
    """
    for item in root.iterdir():
        if item.name.endswith('.nupkg'):
            continue
        abs_item = root / item
        if abs_item.is_dir():
            utils_logger.debug('Recursing into %s', abs_item)
            append_dir_to_zip_recursive(abs_item, z)
        else:
            utils_logger.debug('Adding %s', abs_item)
            z.write(abs_item)


class InvalidEntryError(ValueError):
    """Raised when an ``<entry>`` is invalid."""


def parse_boolean_tag(tag: Element | None) -> bool:
    return ((tag.text or 'false') if tag is not None else 'false') == 'true'


def parse_iso_date_tag(tag: Element | None) -> datetime | None:
    return isoparse(tag.text) if tag is not None and tag.text else None


def parse_int_tag(tag: Element | None, default: int = 0) -> int:
    try:
        return int(tag.text) if tag is not None and tag.text else default
    except ValueError:
        return default


def tag_text_or(tag: Element | None, default: str | None = None) -> str | None:
    """
    Return text from a tag or the default value specified.

    Parameters
    ----------
    tag : Element | None
        The XML element to extract text from.
    default : str | None
        The default value to return if the tag has no text.

    Returns
    -------
    str | None
    """
    return tag.text if tag is not None and tag.text else default


def entry_to_search_result(entry: Element, ns: Mapping[str, str] = FEED_NAMESPACES) -> SearchResult:
    """
    Convert an ``<entry>`` to a :py:class:`~choco.typing.SearchResult` dict.

    Parameters
    ----------
    entry : Element
        The XML entry element to convert.
    ns : Mapping[str, str]
        XML namespace mapping.

    Returns
    -------
    SearchResult

    Raises
    ------
    InvalidEntryError
        If the entry is invalid or does not contain the required metadata.
    """
    ns_dict = dict(ns)
    metadata = entry.find(FEED_PROPERTIES_TAG, ns_dict)
    if metadata is None:
        raise InvalidEntryError
    return SearchResult(
        approval_date=parse_iso_date_tag(metadata.find(METADATA_PACKAGE_APPROVED_DATE_TAG,
                                                       ns_dict)),
        description=tag_text_or(metadata.find(METADATA_DESCRIPTION_TAG, ns_dict)),
        documentation_uri=tag_text_or(metadata.find(METADATA_DOCS_URL_TAG, ns_dict)),
        is_approved=parse_boolean_tag(metadata.find(METADATA_IS_APPROVED_TAG, ns_dict)),
        is_cached=parse_boolean_tag(metadata.find(METADATA_IS_DOWNLOAD_CACHE_AVAILABLE_TAG)),
        license=tag_text_or(metadata.find(METADATA_LICENSE_URL_TAG, ns_dict)),
        num_downloads=parse_int_tag(metadata.find(METADATA_DOWNLOAD_COUNT_TAG, ns_dict)),
        num_version_downloads=parse_int_tag(
            metadata.find(METADATA_VERSION_DOWNLOAD_COUNT_TAG, ns_dict)),
        package_src_uri=tag_text_or(metadata.find(METADATA_PACKAGE_SOURCE_URL_TAG, ns_dict)),
        package_url=tag_text_or(metadata.find(METADATA_GALLERY_DETAILS_URL_TAG, ns_dict)),
        publish_date=parse_iso_date_tag(metadata.find(METADATA_PUBLISHED_TAG, ns_dict)),
        release_notes_uri=tag_text_or(metadata.find(METADATA_RELEASE_NOTES_TAG, ns_dict)),
        site=tag_text_or(metadata.find(METADATA_PROJECT_URL_TAG, ns_dict)),
        summary=tag_text_or(entry.find(FEED_SUMMARY_TAG, ns_dict)),
        tags=re.split(r'\s+', cast('str', tag_text_or(metadata.find(METADATA_TAGS_TAG, ns_dict),
                                                      ''))),
        testing_status=cast(
            'TestingStatus',
            tag_text_or(metadata.find(METADATA_PACKAGE_TEST_RESULT_STATUS_TAG, ns_dict),
                        'Failing')),
        testing_date=parse_iso_date_tag(
            metadata.find(METADATA_PACKAGE_TEST_RESULT_STATUS_DATE_TAG, ns_dict)),
        title=tag_text_or(entry.find(FEED_TITLE_TAG, ns_dict)),
        version=tag_text_or(metadata.find(METADATA_VERSION_TAG, ns_dict)))
