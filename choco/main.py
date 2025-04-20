"""Root command."""
from __future__ import annotations

import click

from choco.commands.apikey import apikey
from choco.commands.config import config
from choco.commands.new import new
from choco.commands.pack import pack
from choco.commands.push import push
from choco.commands.search import search


@click.group()
def main() -> None:
    """Minimal choco command."""


main.add_command(apikey, 'apikey')
main.add_command(config, 'config')
main.add_command(new, 'new')
main.add_command(pack, 'pack')
main.add_command(push, 'push')
main.add_command(search, 'search')
