from pathlib import Path
import re

import click

from ..constants import CHOCOLATEY_UNINSTALL_PS1, VALID_NAME_RE
from ..templates import CHOCOLATEY_INSTALL_PS1_TEMPLATE, NUSPEC_TEMPLATE


def validate_name(_ctx: click.Context, _param: click.Parameter, value: str) -> str:
    if not re.match(VALID_NAME_RE, value):
        raise click.BadParameter(f'format must be "{VALID_NAME_RE}"')
    if Path(value).exists():
        raise click.BadParameter('Directory already exists.')
    return value


@click.command()
@click.argument('name', type=click.UNPROCESSED, callback=validate_name)
def new(name: str) -> None:
    """Create a new package."""
    p_name = Path(name)
    p_name.mkdir()
    with open(p_name / f'{name}.nuspec', 'w') as f:
        f.write(NUSPEC_TEMPLATE.safe_substitute(package_id=name))
    tools = p_name / 'tools'
    tools.mkdir()
    with open(tools / 'chocolateyInstall.ps1', 'w') as f:
        f.write(CHOCOLATEY_INSTALL_PS1_TEMPLATE.safe_substitute(package_id=name))
    with open(tools / 'chocolateyUninstall.ps1', 'w') as f:
        f.write(CHOCOLATEY_UNINSTALL_PS1)
