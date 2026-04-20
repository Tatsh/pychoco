"""Packaging-related functions."""
from __future__ import annotations

from datetime import datetime, timezone
from os import chdir
from pathlib import Path
import asyncio
import hashlib
import re
import zipfile

from anyio import Path as AsyncPath
from defusedxml.ElementTree import parse as parse_xml

from .constants import (
    CHOCOLATEY_UNINSTALL_PS1,
    CONTENT_TYPES_XML,
    NUSPEC_FIELD_AUTHORS,
    NUSPEC_FIELD_DESCRIPTION,
    NUSPEC_FIELD_ID,
    NUSPEC_FIELD_TAGS,
    NUSPEC_FIELD_VERSION,
    VALID_NAME_RE,
)
from .templates import (
    CHOCOLATEY_INSTALL_PS1_TEMPLATE,
    NUSPEC_TEMPLATE,
    PSMDCP_XML_TEMPLATE,
    RELS_XML_TEMPLATE,
)
from .utils import append_dir_to_zip_recursive, generate_unique_id, tag_text_or

__all__ = ('is_valid_package_name', 'new_package')


def is_valid_package_name(value: str) -> bool:
    """
    Check if a package name is valid.

    Parameters
    ----------
    value : str
        The package name to validate.

    Returns
    -------
    bool
    """
    return bool(re.match(VALID_NAME_RE, value))


class DirectoryExistsError(FileExistsError):
    def __init__(self) -> None:
        super().__init__('Directory already exists.')


class InvalidPackageName(ValueError):
    def __init__(self) -> None:
        super().__init__(f'Invalid package name. Name must match "{VALID_NAME_RE}".')


async def new_package(name: str) -> Path:
    """
    Scaffolding to create a new package.

    Parameters
    ----------
    name : str
        The name of the package to create.

    Returns
    -------
    Path

    Raises
    ------
    InvalidPackageName
        If the package name is invalid.
    DirectoryExistsError
        If a directory with the specified name already exists.
    """
    if not is_valid_package_name(name):
        raise InvalidPackageName
    p_name = AsyncPath(name)
    if await p_name.exists():
        raise DirectoryExistsError
    await p_name.mkdir()
    tools = p_name / 'tools'
    await tools.mkdir()
    await asyncio.gather((p_name / f'{name}.nuspec').write_text(
        NUSPEC_TEMPLATE.safe_substitute(package_id=name), encoding='utf-8'),
                         (tools / 'chocolateyInstall.ps1').write_text(
                             CHOCOLATEY_INSTALL_PS1_TEMPLATE.safe_substitute(package_id=name),
                             encoding='utf-8'), (tools / 'chocolateyUninstall.ps1').write_text(
                                 CHOCOLATEY_UNINSTALL_PS1, encoding='utf-8'))
    return Path(name)


class NoNuspecFilesFound(FileNotFoundError):
    def __init__(self) -> None:
        super().__init__('No nuspec files found.')


class TooManyNuspecFiles(RuntimeError):
    def __init__(self, work_dir: str) -> None:
        super().__init__(f'Only one nuspec file should be present in {work_dir}.')


async def pack(work_dir: str = '.') -> zipfile.ZipFile:
    """
    Pack a package directory for distribution (create a nupkg).

    Returns
    -------
    zipfile.ZipFile

    Raises
    ------
    NoNuspecFilesFound
        If nuspec files are not found in the specified directory.
    TooManyNuspecFiles
        If more than one nuspec file is found in the specified directory.
    RuntimeError
        If the nuspec file cannot be parsed.
    """
    nuspecs = [p async for p in AsyncPath(work_dir).glob('*.nuspec')]
    if not nuspecs:
        raise NoNuspecFilesFound
    if len(nuspecs) > 1:
        raise TooManyNuspecFiles(work_dir)
    root = parse_xml(Path(work_dir) / str(nuspecs[0])).getroot()
    if root is None:  # pragma: no cover
        msg = 'Failed to parse nuspec file.'
        raise RuntimeError(msg)
    package_id = tag_text_or(root.find(NUSPEC_FIELD_ID))
    version = tag_text_or(root.find(NUSPEC_FIELD_VERSION))
    sha = hashlib.sha1()  # noqa: S324
    sha.update(f'{package_id}{version}{datetime.now(tz=timezone.utc)}'.encode())
    psmdcp_filename = f'{sha.hexdigest()}.psmdcp'
    with zipfile.ZipFile(f'test-{package_id}.{version}.nupkg', 'w') as z:
        chdir(work_dir)
        append_dir_to_zip_recursive(Path(), z)
        z.writestr('[Content_Types].xml', CONTENT_TYPES_XML)
        z.writestr(
            '_rels/.rels',
            RELS_XML_TEMPLATE.safe_substitute(nuspec_id=generate_unique_id(),
                                              package_id=package_id,
                                              psmdcp_filename=psmdcp_filename,
                                              psmdcp_id=generate_unique_id()))
        z.writestr(
            f'package/services/metadata/core-properties/{psmdcp_filename}',
            PSMDCP_XML_TEMPLATE.safe_substitute(
                creator=tag_text_or(root.find(NUSPEC_FIELD_AUTHORS)),
                description=tag_text_or(root.find(NUSPEC_FIELD_DESCRIPTION)),
                keywords=tag_text_or(root.find(NUSPEC_FIELD_TAGS)),
                package_id=package_id,
                version=version))
        return z
