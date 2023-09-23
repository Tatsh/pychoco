import click

from ..config import read_config, write_config
from ..constants import DEFAULT_CONFIG, PYCHOCO_TOML_PATH
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
@click.option('-p',
              '--path',
              default=PYCHOCO_TOML_PATH,
              help='Storage file.',
              metavar='PATH',
              type=click.Path(dir_okay=False, resolve_path=True))
def set_(name: ConfigKey, value: str, path: str | None) -> None:
    """Set a configuration value."""
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
