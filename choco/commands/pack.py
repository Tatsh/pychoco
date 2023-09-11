from datetime import datetime
from os import chdir
from pathlib import Path
import glob
import hashlib
import zipfile

from defusedxml.ElementTree import parse as parse_xml
from loguru import logger
import click

from ..constants import (CONTENT_TYPES_XML, NUSPEC_FIELD_AUTHORS, NUSPEC_FIELD_DESCRIPTION,
                         NUSPEC_FIELD_ID, NUSPEC_FIELD_TAGS, NUSPEC_FIELD_VERSION)
from ..templates import PSMDCP_XML_TEMPLATE, RELS_XML_TEMPLATE
from ..utils import (append_dir_to_zip_recursive, generate_unique_id, get_unique_tag_text,
                     setup_logging)

__all__ = ('pack',)


@click.command()
@click.option('-d', '--debug', is_flag=True, help='Enable debug logging.')
@click.argument('work_dir', type=click.Path(file_okay=False, resolve_path=True), default='.')
def pack(work_dir: str = '.', debug: bool = False) -> None:
    """Create a package file for distribution."""
    setup_logging(debug)
    if not (nuspecs := glob.glob('*.nuspec', root_dir=work_dir)):
        logger.error('No nuspec files found.')
        raise click.Abort()
    if len(nuspecs) > 1:
        logger.error(f'Only one nuspec file should be present in {work_dir}.')
    with (Path(work_dir) / nuspecs[0]).open() as spec:
        root = parse_xml(spec).getroot()
    package_id = get_unique_tag_text(root, NUSPEC_FIELD_ID)
    version = get_unique_tag_text(root, NUSPEC_FIELD_VERSION)
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
                creator=get_unique_tag_text(root, NUSPEC_FIELD_AUTHORS),
                description=get_unique_tag_text(root, NUSPEC_FIELD_DESCRIPTION),
                keywords=get_unique_tag_text(root, NUSPEC_FIELD_TAGS),
                package_id=package_id,
                version=version))
