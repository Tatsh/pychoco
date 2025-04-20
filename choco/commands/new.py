from __future__ import annotations

import logging

import click

from choco.packaging import new_package


@click.command()
@click.argument('name')
@click.option('-d', '--debug', is_flag=True, help='Enable debug logging.')
def new(name: str, *, debug: bool = False) -> None:
    """Create a new package."""
    logging.basicConfig(level=logging.DEBUG if debug else logging.ERROR)
    try:
        new_package(name)
    except (FileExistsError, ValueError) as e:
        click.secho(str(e), err=True)
        raise click.Abort from e
