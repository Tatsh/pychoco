from __future__ import annotations

import logging

import click

from choco.packaging import pack as do_pack

__all__ = ('pack',)


@click.command()
@click.option('-d', '--debug', is_flag=True, help='Enable debug logging.')
@click.argument('work_dir', type=click.Path(file_okay=False, resolve_path=True), default='.')
def pack(work_dir: str = '.', *, debug: bool = False) -> None:
    """Create a package file for distribution."""
    logging.basicConfig(level=logging.DEBUG if debug else logging.ERROR)
    try:
        do_pack(work_dir)
    except (FileNotFoundError, ValueError) as e:
        click.secho(str(e), err=True)
        raise click.Abort from e
