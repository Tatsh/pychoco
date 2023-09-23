"""Utility functions."""
from datetime import datetime
from os import listdir
from pathlib import Path
from types import FrameType
from typing import TypeVar, cast
from xml.etree.ElementTree import Element
import logging
import re
import sys
import uuid
import zipfile

from dateutil.parser import isoparse
from loguru import logger

# isort: off
from .constants import (
    FEED_NAMESPACES, FEED_PROPERTIES_TAG, FEED_SUMMARY_TAG, FEED_TITLE_TAG,
    METADATA_DESCRIPTION_TAG, METADATA_DOCS_URL_TAG, METADATA_DOWNLOAD_COUNT_TAG,
    METADATA_GALLERY_DETAILS_URL_TAG, METADATA_IS_APPROVED_TAG,
    METADATA_IS_DOWNLOAD_CACHE_AVAILABLE_TAG, METADATA_LICENSE_URL_TAG,
    METADATA_PACKAGE_APPROVED_DATE_TAG, METADATA_PACKAGE_SOURCE_URL_TAG,
    METADATA_PACKAGE_TEST_RESULT_STATUS_DATE_TAG, METADATA_PACKAGE_TEST_RESULT_STATUS_TAG,
    METADATA_PROJECT_URL_TAG, METADATA_PUBLISHED_TAG, METADATA_RELEASE_NOTES_TAG, METADATA_TAGS_TAG,
    METADATA_VERSION_DOWNLOAD_COUNT_TAG, METADATA_VERSION_TAG)
# isort: on
from .typing import SearchResult, TestingStatus

__all__ = ('append_dir_to_zip_recursive', 'entry_to_search_result', 'generate_unique_id',
           'setup_logging', 'tag_text_or')

T = TypeVar('T')
utils_logger = logging.getLogger(__name__)


class InterceptHandler(logging.Handler):  # pragma: no cover
    """Intercept handler taken from Loguru's documentation."""
    def emit(self, record: logging.LogRecord) -> None:
        level: str | int
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno
        # Find caller from where originated the logged message
        frame: FrameType | None = logging.currentframe()
        depth = 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1
        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def setup_log_intercept_handler() -> None:  # pragma: no cover
    """Sets up Loguru to intercept records from the logging module."""
    logging.basicConfig(handlers=(InterceptHandler(),), level=0)


def setup_logging(debug: bool | None = False) -> None:
    """Shared function to enable logging."""
    if debug:  # pragma: no cover
        setup_log_intercept_handler()
        logger.enable('')
    else:
        logger.configure(handlers=(dict(
            format='<level>{message}</level>',
            level='INFO',
            sink=sys.stderr,
        ),))


def generate_unique_id() -> str:
    """Generates a unique ID for elements in ``_rels/.rels``."""
    return f'R{str(uuid.uuid4()).replace("-", "")}'.upper()


def append_dir_to_zip_recursive(root: Path, z: zipfile.ZipFile) -> None:
    """Appends a directory recursively to a zip file."""
    for item in listdir(root):
        if item.endswith('.nupkg'):
            continue
        abs_item = root / item
        if abs_item.is_dir():
            utils_logger.debug(f'Recursing into {abs_item}')
            append_dir_to_zip_recursive(abs_item, z)
        else:
            utils_logger.debug(f'Adding {abs_item}')
            z.write(abs_item)


class InvalidEntryError(ValueError):
    """Thrown when an ``<entry>`` is invalid."""


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
    """Return text from a tag or the default value specified."""
    return tag.text if tag is not None and tag.text else default


def entry_to_search_result(entry: Element, ns: dict[str, str] = FEED_NAMESPACES) -> SearchResult:
    """Convert an ``<entry>`` to a ``SearchResult`` dict."""
    metadata = entry.find(FEED_PROPERTIES_TAG, ns)
    if not metadata:
        raise InvalidEntryError()
    return SearchResult(
        approval_date=parse_iso_date_tag(metadata.find(METADATA_PACKAGE_APPROVED_DATE_TAG, ns)),
        description=tag_text_or(metadata.find(METADATA_DESCRIPTION_TAG, ns)),
        documentation_uri=tag_text_or(metadata.find(METADATA_DOCS_URL_TAG, ns)),
        is_approved=parse_boolean_tag(metadata.find(METADATA_IS_APPROVED_TAG, ns)),
        is_cached=parse_boolean_tag(metadata.find(METADATA_IS_DOWNLOAD_CACHE_AVAILABLE_TAG)),
        license=tag_text_or(metadata.find(METADATA_LICENSE_URL_TAG, ns)),
        num_downloads=parse_int_tag(metadata.find(METADATA_DOWNLOAD_COUNT_TAG, ns)),
        num_version_downloads=parse_int_tag(metadata.find(METADATA_VERSION_DOWNLOAD_COUNT_TAG, ns)),
        package_src_uri=tag_text_or(metadata.find(METADATA_PACKAGE_SOURCE_URL_TAG, ns)),
        package_url=tag_text_or(metadata.find(METADATA_GALLERY_DETAILS_URL_TAG, ns)),
        publish_date=parse_iso_date_tag(metadata.find(METADATA_PUBLISHED_TAG, ns)),
        release_notes_uri=tag_text_or(metadata.find(METADATA_RELEASE_NOTES_TAG, ns)),
        site=tag_text_or(metadata.find(METADATA_PROJECT_URL_TAG, ns)),
        summary=tag_text_or(entry.find(FEED_SUMMARY_TAG, ns)),
        tags=re.split(r'\s+', cast(str, tag_text_or(metadata.find(METADATA_TAGS_TAG, ns), ''))),
        testing_status=cast(
            TestingStatus,
            tag_text_or(metadata.find(METADATA_PACKAGE_TEST_RESULT_STATUS_TAG, ns), 'Failing')),
        testing_date=parse_iso_date_tag(
            metadata.find(METADATA_PACKAGE_TEST_RESULT_STATUS_DATE_TAG, ns)),
        title=tag_text_or(entry.find(FEED_TITLE_TAG, ns)),
        version=tag_text_or(metadata.find(METADATA_VERSION_TAG, ns)))
