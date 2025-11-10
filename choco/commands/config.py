"""Manage configuration."""
from __future__ import annotations

from typing import TYPE_CHECKING

from bascom import setup_logging
from choco.config import read_config, write_config
from choco.constants import DEFAULT_CONFIG, PYCHOCO_TOML_PATH
import click

if TYPE_CHECKING:
    from choco.typing import ConfigKey

__all__ = ('config',)


@click.command('set', context_settings={'help_option_names': ('-h', '--help')})
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
    setup_logging(debug=debug, loggers={'choco': {'handlers': ('console',), 'propagate': False}})
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
