from os.path import basename
from typing import cast

from requests import HTTPError
import click
import requests
import tomlkit

from ..constants import PYCHOCO_API_KEYS_TOML_PATH
from ..utils import get_default_push_source


@click.command()
@click.option('-s',
              '--source',
              default=get_default_push_source,
              help='Source to upload to.',
              metavar='URL')
@click.argument('package', type=click.Path(dir_okay=False, readable=True))
def push(package: str, source: str) -> None:
    """Push a package to a source."""
    session = requests.Session()
    if PYCHOCO_API_KEYS_TOML_PATH.exists():
        with open(PYCHOCO_API_KEYS_TOML_PATH) as f:
            keys = tomlkit.load(f)
            if source in keys.keys():
                session.headers.update({'X-NuGet-ApiKey': cast(str, keys[source])})
    with open(package, 'rb') as f:
        r = session.put(f'{source}/api/v2/package/', files={basename(package): f})
        try:
            r.raise_for_status()
        except HTTPError as e:
            click.echo(e.response)
