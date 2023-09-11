from typing import cast

from tomlkit.items import Item
import click
import tomlkit

from ..constants import PYCHOCO_API_KEYS_TOML_PATH

__all__ = ('apikey',)


@click.command('list')
def list_() -> None:
    """Lists sources associated with API keys. Does not display the API key values."""
    if PYCHOCO_API_KEYS_TOML_PATH.exists():
        with open(PYCHOCO_API_KEYS_TOML_PATH) as f:
            for key in sorted(tomlkit.load(f)):
                click.echo(key)


@click.command()
@click.option('-k', '--key', required=True, help='API key.', metavar='API_KEY')
@click.option('-s', '--source', required=True, help='Source URI.', metavar='SOURCE_URL')
def add(key: str, source: str) -> None:
    """Add an API key for a source."""
    PYCHOCO_API_KEYS_TOML_PATH.parent.mkdir(parents=True, exist_ok=True)
    if PYCHOCO_API_KEYS_TOML_PATH.exists():
        with open(PYCHOCO_API_KEYS_TOML_PATH) as f:
            keys = tomlkit.load(f)
    else:
        keys = tomlkit.document()
    keys.add(source, cast(Item, key))
    with open(PYCHOCO_API_KEYS_TOML_PATH, 'w') as f:
        tomlkit.dump(keys, f)


@click.group()
def apikey() -> None:
    """Manage API keys."""


apikey.add_command(add, 'add')
apikey.add_command(list_, 'list')
