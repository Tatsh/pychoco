from __future__ import annotations

from typing import TYPE_CHECKING
import logging

import click

from choco.config import read_config, write_config
from choco.constants import DEFAULT_CONFIG, PYCHOCO_TOML_PATH

if TYPE_CHECKING:
    from choco.typing import ConfigKey

__all__ = ('config',)


@click.command('set')
@click.option('-d', '--debug', is_flag=True, help='Enable debug logging.')
@click.option('-n',
              '--name',
              required=True,
              type=click.Choice(['defaultPushSource']),
              help='Key to set.',
              metavar='KEY')
@click.option('-v', '--value', required=True, help='Value to set.', metavar='VALUE')
@click.option('-p',
              '--path',
              default=PYCHOCO_TOML_PATH,
              help='Storage file.',
              metavar='PATH',
              type=click.Path(dir_okay=False, resolve_path=True))
def set_(name: ConfigKey, value: str, path: str | None, *, debug: bool = False) -> None:
    """Set a configuration value."""
    logging.basicConfig(level=logging.DEBUG if debug else logging.ERROR)
    try:
        config = read_config(path)
    except FileNotFoundError:
        config = DEFAULT_CONFIG
    config['pychoco'][name] = value
    write_config(config, path)


@click.group()
def config() -> None:
    """Manage configuration."""


config.add_command(set_, 'set')
