from requests import HTTPError
import click

from ..client import ChocolateyClient
from ..config import read_all
from ..constants import PYCHOCO_API_KEYS_TOML_PATH, PYCHOCO_TOML_PATH


@click.command()
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
              type=click.Path(dir_okay=False, resolve_path=True, readable=True))
@click.argument('package', type=click.Path(dir_okay=False, readable=True))
def push(package: str,
         source: str | None = None,
         config_path: str | None = None,
         api_keys_path: str | None = None) -> None:
    """Push a package to a source."""
    config, api_keys = read_all(config_path, api_keys_path)
    try:
        ChocolateyClient(config, api_keys).push(package, source)
    except HTTPError as e:
        click.echo(e.response)
        raise click.Abort() from e
