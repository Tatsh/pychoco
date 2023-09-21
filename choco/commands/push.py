from requests import HTTPError
import click

from ..client import ChocolateyClient


@click.command()
@click.option('-s', '--source', help='Source to upload to.', metavar='URL')
@click.argument('package', type=click.Path(dir_okay=False, readable=True))
def push(package: str, source: str | None = None) -> None:
    """Push a package to a source."""
    try:
        ChocolateyClient().push(package, source)
    except HTTPError as e:
        click.echo(e.response)
        raise click.Abort()
