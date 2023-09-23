import click

from ..config import read_api_keys, write_api_keys
from ..constants import PYCHOCO_API_KEYS_TOML_PATH

__all__ = ('apikey',)


@click.command('list')
@click.option('-p',
              '--path',
              default=PYCHOCO_API_KEYS_TOML_PATH,
              help='Storage file.',
              metavar='PATH',
              type=click.Path(dir_okay=False, resolve_path=True))
def list_(path: str | None) -> None:
    """Lists sources associated with API keys. Does not display the API key values."""
    for key in read_api_keys(path).keys():
        click.echo(key)


@click.command()
@click.option('-k', '--key', required=True, help='API key.', metavar='API_KEY')
@click.option('-s', '--source', required=True, help='Source URI.', metavar='SOURCE_URL')
@click.option('-p',
              '--path',
              default=PYCHOCO_API_KEYS_TOML_PATH,
              help='Storage file.',
              metavar='PATH',
              type=click.Path(dir_okay=False, resolve_path=True))
def add(key: str, source: str, path: str | None) -> None:
    """Add an API key for a source."""
    keys = read_api_keys(path)
    keys[source] = key
    write_api_keys(keys)


@click.group()
def apikey() -> None:
    """Manage API keys."""


apikey.add_command(add, 'add')
apikey.add_command(list_, 'list')
