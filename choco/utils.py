"""Utility functions."""
from os import listdir
from pathlib import Path
from types import FrameType
from typing import Any, cast
from xml.etree.ElementTree import Element
import logging
import sys
import uuid
import zipfile

from loguru import logger
from tomlkit.container import Container
import tomlkit

from .constants import PYCHOCO_TOML_PATH
from .typing import assert_not_none

__all__ = ('append_dir_to_zip_recursive', 'generate_unique_id', 'get_default_push_source',
           'get_unique_tag_text', 'setup_logging')


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
    return f'R{str(uuid.uuid4()).replace("-", "")}'.upper()


def get_unique_tag_text(root: Element | Any, tag_name: str) -> str:
    text = assert_not_none(assert_not_none(root[0].find(tag_name)).text).strip()
    assert len(text) > 0, f'No value in {tag_name}'
    return text


def append_dir_to_zip_recursive(root: Path, z: zipfile.ZipFile) -> None:
    for item in listdir(root):
        if item.endswith('.nupkg'):
            continue
        abs_item = root / item
        if abs_item.is_dir():
            logger.debug(f'Recursing into {abs_item}')
            append_dir_to_zip_recursive(abs_item, z)
        else:
            logger.debug(f'Adding {abs_item}')
            z.write(abs_item)


def get_default_push_source() -> str:
    try:
        with PYCHOCO_TOML_PATH.open() as f:
            return cast(str, cast(Container, tomlkit.load(f)['pychoco'])['defaultPushSource'])
    except (KeyError, FileNotFoundError):
        return 'https://push.chocolatey.org'
