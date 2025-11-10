"""Create a new package."""
from __future__ import annotations

from bascom import setup_logging
from choco.packaging import new_package
import click


@click.command(context_settings={'help_option_names': ('-h', '--help')})
@click.argument('name')
@click.option('-d', '--debug', is_flag=True, help='Enable debug logging.')
def new(name: str, *, debug: bool = False) -> None:
    """Create a new package."""  # noqa: DOC501
    setup_logging(debug=debug, loggers={'choco': {'handlers': ('console',), 'propagate': False}})
    try:
        new_package(name)
    except (FileExistsError, ValueError) as e:
        click.secho(str(e), err=True)
        raise click.Abort from e
