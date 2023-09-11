import click

from choco.commands import apikey, config, new, pack, push


@click.group()
def main() -> None:
    """Minimal choco command."""


main.add_command(apikey, 'apikey')
main.add_command(config, 'config')
main.add_command(new, 'new')
main.add_command(pack, 'pack')
main.add_command(push, 'push')
