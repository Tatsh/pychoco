"""Push command."""
from __future__ import annotations

from pathlib import Path

from bascom import setup_logging
from choco.client import ChocolateyClient
from choco.config import read_all
from choco.constants import PYCHOCO_API_KEYS_TOML_PATH, PYCHOCO_TOML_PATH
from requests import HTTPError
import click


@click.command(context_settings={'help_option_names': ('-h', '--help')})
@click.option('-d', '--debug', is_flag=True, help='Enable debug logging.')
@click.option('-s', '--source', help='Source to upload to.', metavar='URL')
@click.option('--config-path',
              default=PYCHOCO_TOML_PATH,
              help='Configuration storage file.',
              metavar='PATH',
              type=click.Path(dir_okay=False, resolve_path=True, readable=True))
@click.option('--api-keys-path',
              default=PYCHOCO_API_KEYS_TOML_PATH,
              help='API keys storage file.',
              metavar='PATH',
              type=click.Path(dir_okay=False, resolve_path=True, readable=True, path_type=Path))
@click.argument('package', type=click.Path(dir_okay=False, readable=True, path_type=Path))
def push(package: Path,
         source: str | None = None,
         config_path: Path | None = None,
         api_keys_path: Path | None = None,
         *,
         debug: bool = False) -> None:
    """Push a package to a source."""  # noqa: DOC501
    setup_logging(debug=debug,
                  loggers={
                      'choco': {
                          'handlers': ('console',),
                          'propagate': False
                      },
                      'urllib3': {
                          'handlers': ('console',),
                          'propagate': False
                      }
                  })
    config, api_keys = read_all(config_path, api_keys_path)
    try:
        ChocolateyClient(config, api_keys).push(package, source)
    except HTTPError as e:
        click.echo(e.response)
        raise click.Abort from e
