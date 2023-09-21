import click

from ..packaging import new_package


@click.command()
@click.argument('name')
def new(name: str) -> None:
    """Create a new package."""
    try:
        new_package(name)
    except (FileExistsError, ValueError) as e:
        click.secho(str(e), err=True)
        raise click.Abort() from e
