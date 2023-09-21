import click

from ..client import ChocolateyClient

__all__ = ('apikey',)


@click.command('list')
def list_() -> None:
    """Lists sources associated with API keys. Does not display the API key values."""
    for key in ChocolateyClient().get_keys_available():
        click.echo(key)


@click.command()
@click.option('-k', '--key', required=True, help='API key.', metavar='API_KEY')
@click.option('-s', '--source', required=True, help='Source URI.', metavar='SOURCE_URL')
def add(key: str, source: str) -> None:
    """Add an API key for a source."""
    ChocolateyClient().add_key(key, source)


@click.group()
def apikey() -> None:
    """Manage API keys."""


apikey.add_command(add, 'add')
apikey.add_command(list_, 'list')
