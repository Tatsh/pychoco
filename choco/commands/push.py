"""Push command."""
from __future__ import annotations

from pathlib import Path
import asyncio

from bascom import setup_logging
from choco.client import ChocolateyClient
from choco.config import read_all
from choco.constants import PYCHOCO_API_KEYS_TOML_PATH, PYCHOCO_TOML_PATH
from niquests import HTTPError
import click

__all__ = ('push',)


@click.command(context_settings={'help_option_names': ('-h', '--help')})
@click.option('-d', '--debug', is_flag=True, help='Enable debug logging.')
@click.option('-s', '--source', help='Source to upload to.', metavar='URL')
@click.option('--config-path',
              default=PYCHOCO_TOML_PATH,
              help='Configuration storage file.',
              metavar='PATH',
              type=click.Path(dir_okay=False, path_type=Path, resolve_path=True, readable=True))
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
    """Push a package to a source."""
    setup_logging(debug=debug, loggers={'choco': {}, 'urllib3': {}})
    asyncio.run(
        _push_async(api_keys_path=api_keys_path,
                    config_path=config_path,
                    package=package,
                    source=source))


async def _push_async(package: Path, source: str | None, config_path: Path | None,
                      api_keys_path: Path | None) -> None:
    config, api_keys = await read_all(config_path, api_keys_path)
    try:
        await ChocolateyClient(config, api_keys).push(package, source)
    except HTTPError as e:
        click.echo(e.response)
        raise click.Abort from e
