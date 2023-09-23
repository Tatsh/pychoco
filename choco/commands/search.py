from datetime import datetime
from typing import cast

import click

from ..client import ChocolateyClient
from ..config import read_all
from ..templates import ALL_VERSIONS_SEARCH_RESULT_TEMPLATE, SEARCH_RESULT_TEMPLATE
from ..utils import setup_logging

__all__ = ('search',)


@click.command()
@click.option('--by-id-only',
              is_flag=True,
              help='Only return packages where the id contains the search filter.')
@click.option('--by-tag-only',
              '--by-tags-only',
              is_flag=True,
              help='Only return packages where the search filter matches on the tags.')
@click.option('--id-starts-with',
              is_flag=True,
              help='Only return packages where the id starts with the search filter.')
@click.option('--idonly',
              '--id-only',
              'id_only',
              help='Only return Package IDs in the list results.',
              is_flag=True)
@click.option('--order-by-popularity', is_flag=True, help='Sort by package results by popularity.')
@click.option('--page', type=int, help='The "page" of results to return.', default=None)
@click.option('--page-size',
              type=int,
              help='Amount of packages to return in each page of results.',
              default=30)
@click.option('--pre',
              '--prerelease',
              'include_prerelease',
              help='Include prereleases.',
              is_flag=True)
@click.option('-a',
              '--all',
              '--allversions',
              '--all-versions',
              'all_versions',
              is_flag=True,
              help='Include results from all versions.')
@click.option('-d', '--debug', is_flag=True, help='Enable debug logging.')
@click.option('-e', '--exact', is_flag=True, help='Only return packages with this exact name.')
@click.option('-p', '--password', help='Password.')
@click.option('-s', '--source', help='Source to search.', metavar='URL')
@click.option('-u', '--user', help='User name.')
@click.argument('terms')
def search(
    all_versions: bool,
    by_id_only: bool,
    by_tag_only: bool,
    debug: bool,
    exact: bool,
    id_only: bool,
    id_starts_with: bool,
    include_prerelease: bool,
    order_by_popularity: bool,
    page: int | None,
    page_size: bool,
    password: str,
    source: str,
    terms: str,
    user: str,
) -> None:
    """Search a source."""
    setup_logging(debug)
    config, api_keys = read_all()
    for result in ChocolateyClient(config, api_keys).search(
            terms,
            auth=(user, password) if user and password else None,
            all_versions=all_versions,
            by_id_only=by_id_only,
            by_tag_only=by_tag_only,
            debug=debug,
            exact=exact,
            id_starts_with=id_starts_with,
            include_prerelease=include_prerelease,
            order_by_popularity=order_by_popularity,
            page=page,
            page_size=page_size,
            source=source):
        if id_only:
            click.echo(result['title'])
        elif all_versions:
            substitutes = cast(dict[str, str | bool | None | datetime], result)
            substitutes.update(
                cached_state='Downloads cached for licensed users' if result['is_cached'] else '',
                state='[Approved]' if result['is_approved'] else '')
            click.echo(ALL_VERSIONS_SEARCH_RESULT_TEMPLATE.safe_substitute(**substitutes))
        else:
            substitutes = cast(dict[str, str | bool | None | datetime], result)
            substitutes.update(
                cached_state='Downloads cached for licensed users' if result['is_cached'] else '',
                state='[Approved]' if result['is_approved'] else '',
                tags=' '.join(result['tags']))
            substitutes['testing_status'] = f"{result['testing_status']}"
            if result['testing_date']:
                substitutes[
                    'testing_status'] += f" on {result['testing_date']}"  # type: ignore[assignment,operator]  # noqa: E501
            for key, val in substitutes.items():
                if val is None:
                    match key:
                        case 'title':
                            substitutes[key] = 'no title?'
                        case 'version':
                            substitutes[key] = 'no version?'
                        case _:
                            substitutes[key] = ''
            click.echo(SEARCH_RESULT_TEMPLATE.safe_substitute(**substitutes))
