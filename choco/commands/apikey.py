"""Manage API keys for sources."""
from __future__ import annotations

from bascom import setup_logging
from choco.config import read_api_keys, write_api_keys
from choco.constants import PYCHOCO_API_KEYS_TOML_PATH
import click

__all__ = ('apikey',)


@click.command('list', context_settings={'help_option_names': ('-h', '--help')})
@click.option('-d', '--debug', is_flag=True, help='Enable debug logging.')
@click.option('-p',
              '--path',
              default=PYCHOCO_API_KEYS_TOML_PATH,
              help='Storage file.',
              metavar='PATH',
              type=click.Path(dir_okay=False, resolve_path=True))
def list_(path: str | None, *, debug: bool = False) -> None:
    """List sources associated with API keys. Does not display the API key values."""  # noqa: DOC501
    setup_logging(debug=debug, loggers={'choco': {'handlers': ('console',), 'propagate': False}})
    try:
        keys = read_api_keys(path)
    except FileNotFoundError as e:
        raise click.Abort from e
    for key in keys:
        click.echo(key)


@click.command()
@click.option('-d', '--debug', is_flag=True, help='Enable debug logging.')
@click.option('-k', '--key', required=True, help='API key.', metavar='API_KEY')
@click.option('-s', '--source', required=True, help='Source URI.', metavar='SOURCE_URL')
@click.option('-p',
              '--path',
              default=PYCHOCO_API_KEYS_TOML_PATH,
              help='Storage file.',
              metavar='PATH',
              type=click.Path(dir_okay=False, resolve_path=True))
def add(key: str, source: str, path: str | None, *, debug: bool = False) -> None:
    """Add an API key for a source."""
    setup_logging(debug=debug, loggers={'choco': {'handlers': ('console',), 'propagate': False}})
    try:
        keys = read_api_keys(path)
    except FileNotFoundError:
        keys = {}
    keys[source] = key
    write_api_keys(keys)


@click.group()
def apikey() -> None:
    """Manage API keys."""


apikey.add_command(add, 'add')
apikey.add_command(list_, 'list')
