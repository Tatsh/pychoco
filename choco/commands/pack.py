import click

from ..packaging import pack as do_pack
from ..utils import setup_logging

__all__ = ('pack',)


@click.command()
@click.option('-d', '--debug', is_flag=True, help='Enable debug logging.')
@click.argument('work_dir', type=click.Path(file_okay=False, resolve_path=True), default='.')
def pack(work_dir: str = '.', debug: bool = False) -> None:
    """Create a package file for distribution."""
    setup_logging(debug)
    try:
        do_pack(work_dir)
    except (FileNotFoundError, ValueError) as e:
        click.secho(str(e), err=True)
        raise click.Abort() from e
