"""Packaging-related functions."""
from datetime import datetime
from os import chdir
from pathlib import Path
import glob
import hashlib
import re
import zipfile

from defusedxml.ElementTree import parse as parse_xml

from .constants import (CHOCOLATEY_UNINSTALL_PS1, CONTENT_TYPES_XML, NUSPEC_FIELD_AUTHORS,
                        NUSPEC_FIELD_DESCRIPTION, NUSPEC_FIELD_ID, NUSPEC_FIELD_TAGS,
                        NUSPEC_FIELD_VERSION, VALID_NAME_RE)
from .templates import (CHOCOLATEY_INSTALL_PS1_TEMPLATE, NUSPEC_TEMPLATE, PSMDCP_XML_TEMPLATE,
                        RELS_XML_TEMPLATE)
from .utils import append_dir_to_zip_recursive, generate_unique_id, tag_text_or

__all__ = ('is_valid_package_name', 'new_package')


def is_valid_package_name(value: str) -> bool:
    """Check if a package name is valid."""
    return bool(re.match(VALID_NAME_RE, value))


def new_package(name: str) -> Path:
    """Scaffolding to create a new package."""
    if not is_valid_package_name(name):
        raise ValueError(f'Invalid package name. Name must match "{VALID_NAME_RE}".')
    if Path(name).exists():
        raise FileExistsError('Directory already exists.')
    p_name = Path(name)
    p_name.mkdir()
    with Path(p_name / f'{name}.nuspec').open('w') as f:
        f.write(NUSPEC_TEMPLATE.safe_substitute(package_id=name))
    tools = p_name / 'tools'
    tools.mkdir()
    with Path(tools / 'chocolateyInstall.ps1').open('w') as f:
        f.write(CHOCOLATEY_INSTALL_PS1_TEMPLATE.safe_substitute(package_id=name))
    with Path(tools / 'chocolateyUninstall.ps1').open('w') as f:
        f.write(CHOCOLATEY_UNINSTALL_PS1)
    return p_name


def pack(work_dir: str = '.') -> zipfile.ZipFile:
    """Pack a package directory for distribution (create a nupkg)."""
    if not (nuspecs := glob.glob('*.nuspec', root_dir=work_dir)):
        raise FileNotFoundError('No nuspec files found.')
    if len(nuspecs) > 1:
        raise ValueError(f'Only one nuspec file should be present in {work_dir}.')
    root = parse_xml(Path(work_dir) / nuspecs[0]).getroot()
    package_id = tag_text_or(root.find(NUSPEC_FIELD_ID))
    version = tag_text_or(root.find(NUSPEC_FIELD_VERSION))
    sha = hashlib.sha1()
    sha.update(f'{package_id}{version}{datetime.now()}'.encode())
    psmdcp_filename = f'{sha.hexdigest()}.psmdcp'
    with zipfile.ZipFile(f'test-{package_id}.{version}.nupkg', 'w') as z:
        chdir(work_dir)
        append_dir_to_zip_recursive(Path('.'), z)
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
