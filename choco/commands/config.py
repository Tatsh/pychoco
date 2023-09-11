from typing import cast

from tomlkit.items import Table
import click
import tomlkit

from ..constants import PYCHOCO_TOML_PATH

__all__ = ('config',)


@click.command()
@click.option('-n', '--name', required=True, type=click.Choice(['defaultPushSource']))
@click.option('-v', '--value', required=True)
def config_set(name: str, value: str) -> None:
    PYCHOCO_TOML_PATH.parent.mkdir(parents=True, exist_ok=True)
    if PYCHOCO_TOML_PATH.exists():
        with PYCHOCO_TOML_PATH.open() as f:
            config_ = tomlkit.load(f)
    else:
        config_ = tomlkit.document()
    if 'pychoco' not in config_:
        config_['pychoco'] = tomlkit.table()
    if name == 'defaultPushSource':
        value = value.rstrip('/')
    cast(Table, config_['pychoco']).add(name, value)  # pylint: disable=no-member
    with PYCHOCO_TOML_PATH.open('w') as f:
        tomlkit.dump(config_, f)


@click.group()
def config() -> None:
    """Manage configuration."""


config.add_command(config_set, 'set')
