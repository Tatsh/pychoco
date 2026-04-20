"""Create a package file for distribution."""
from __future__ import annotations

from pathlib import Path
import asyncio

from bascom import setup_logging
from choco.packaging import pack as do_pack
import click

__all__ = ('pack',)


@click.command(context_settings={'help_option_names': ('-h', '--help')})
@click.option('-d', '--debug', is_flag=True, help='Enable debug logging.')
@click.argument('work_dir',
                type=click.Path(file_okay=False, path_type=Path, resolve_path=True),
                default='.')
def pack(work_dir: Path, *, debug: bool = False) -> None:
    """Create a package file for distribution."""  # noqa: DOC501
    setup_logging(debug=debug, loggers={'choco': {}})
    try:
        asyncio.run(do_pack(str(work_dir)))
    except (FileNotFoundError, ValueError) as e:
        click.secho(str(e), err=True)
        raise click.Abort from e
