from typing import cast

from tomlkit.items import Item
import click
import tomlkit

from ..constants import PYCHOCO_API_KEYS_TOML_PATH

__all__ = ('apikey',)


@click.command()
def apikey_list() -> None:
    if PYCHOCO_API_KEYS_TOML_PATH.exists():
        with open(PYCHOCO_API_KEYS_TOML_PATH) as f:
            for key in sorted(tomlkit.load(f)):
                click.echo(key)


@click.command()
@click.option('-k', '--key', required=True)
@click.option('-s', '--source', required=True)
def apikey_add(key: str, source: str) -> None:
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


apikey.add_command(apikey_add, 'add')
apikey.add_command(apikey_list, 'list')
