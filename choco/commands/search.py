"""Search command."""
from __future__ import annotations

from typing import TYPE_CHECKING, cast

from bascom import setup_logging
from choco.client import ChocolateyClient
from choco.config import read_all
from choco.templates import ALL_VERSIONS_SEARCH_RESULT_TEMPLATE, SEARCH_RESULT_TEMPLATE
import click

if TYPE_CHECKING:
    from datetime import datetime

__all__ = ('search',)


@click.command(context_settings={'help_option_names': ('-h', '--help')})
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
def search(page: int | None, password: str, source: str, terms: str, user: str, *,
           all_versions: bool, by_id_only: bool, by_tag_only: bool, debug: bool, exact: bool,
           id_only: bool, id_starts_with: bool, include_prerelease: bool, order_by_popularity: bool,
           page_size: bool) -> None:
    """Search a source."""
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
    config, api_keys = read_all()
    for result in ChocolateyClient(config, api_keys).search(
            terms,
            auth=(user, password) if user and password else None,
            all_versions=all_versions,
            by_id_only=by_id_only,
            by_tag_only=by_tag_only,
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
            substitutes = cast('dict[str, str | bool | datetime | None]', result)
            substitutes.update(
                cached_state='Downloads cached for licensed users' if result['is_cached'] else '',
                state='[Approved]' if result['is_approved'] else '')
            click.echo(ALL_VERSIONS_SEARCH_RESULT_TEMPLATE.safe_substitute(**substitutes))
        else:
            substitutes = cast('dict[str, str | bool | datetime | None]', result)
            substitutes.update(
                cached_state='Downloads cached for licensed users' if result['is_cached'] else '',
                state='[Approved]' if result['is_approved'] else '',
                tags=' '.join(result['tags']))
            substitutes['testing_status'] = f"{result['testing_status']}"
            if result['testing_date'] and substitutes['testing_status']:
                substitutes[
                    'testing_status'] += f" on {result['testing_date']}"  # type: ignore[assignment,operator]
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
