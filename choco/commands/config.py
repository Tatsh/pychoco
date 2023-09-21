import click

from ..client import ChocolateyClient
from ..typing import ConfigKey

__all__ = ('config',)


@click.command('set')
@click.option('-n',
              '--name',
              required=True,
              type=click.Choice(['defaultPushSource']),
              help='Key to set.',
              metavar='KEY')
@click.option('-v', '--value', required=True, help='Value to set.', metavar='VALUE')
def set_(name: ConfigKey, value: str) -> None:
    """Set a configuration value."""
    ChocolateyClient().config_set(name, value)


@click.group()
def config() -> None:
    """Manage configuration."""


config.add_command(set_, 'set')
