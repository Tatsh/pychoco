from typing import cast

from defusedxml.ElementTree import fromstring as parse_xml
import click
import requests
import tomlkit

# isort: off
from ..constants import (
    FEED_ENTRY_TAG, FEED_ID_TAG, FEED_PROPERTIES_TAG, FEED_SUMMARY_TAG, FEED_TITLE_TAG,
    METADATA_DESCRIPTION_TAG, METADATA_DOCS_URL_TAG, METADATA_DOWNLOAD_CACHE_STATUS_TAG,
    METADATA_DOWNLOAD_COUNT_TAG, METADATA_GALLERY_DETAILS_URL_TAG, METADATA_IS_APPROVED_TAG,
    METADATA_LICENSE_URL_TAG, METADATA_PACKAGE_APPROVED_DATE_TAG, METADATA_PACKAGE_SOURCE_URL_TAG,
    METADATA_PACKAGE_TEST_RESULT_STATUS_DATE_TAG, METADATA_PACKAGE_TEST_RESULT_STATUS_TAG,
    METADATA_PROJECT_URL_TAG, METADATA_PUBLISHED_TAG, METADATA_RELEASE_NOTES_TAG, METADATA_TAGS_TAG,
    METADATA_VERSION_DOWNLOAD_COUNT_TAG, METADATA_VERSION_TAG, PYCHOCO_API_KEYS_TOML_PATH)
# isort: on
from ..templates import SEARCH_RESULT_TEMPLATE
from ..utils import get_default_push_source, get_unique_tag_text, setup_logging, try_get

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
@click.option('-s',
              '--source',
              default=get_default_push_source,
              help='Source to search.',
              metavar='URL')
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
    searches: list[requests.Request] = []
    session = requests.Session()
    if PYCHOCO_API_KEYS_TOML_PATH.exists():
        with open(PYCHOCO_API_KEYS_TOML_PATH) as f:
            keys = tomlkit.load(f)
            if source in keys.keys():
                session.headers.update({'X-NuGet-ApiKey': cast(str, keys[source])})
    auth = (user, password) if user and password else None
    order_by = 'Id' if not order_by_popularity else 'DownloadCount desc,Id'
    if (not all_versions and not by_id_only and not by_tag_only and not exact
            and not id_starts_with):  # Default case
        searches.append(
            requests.Request(
                'GET',
                f'{source}/Packages()',
                params={
                    '$filter':
                        f"((((Id ne null) and substringof('{terms}',tolower(Id))) or "
                        f"((Description ne null) and substringof('{terms}',tolower(Description))))"
                        f" or ((Tags ne null) and substringof(' {terms} ',tolower(Tags)))) "
                        "and IsLatestVersion",
                    '$orderby': order_by,
                    '$skip': str(0 if page is None else page * page_size),
                    '$top': str(page_size)
                }))
    else:
        if all_versions:
            searches.append(
                requests.Request('GET',
                                 f'{source}/api/v2/Search()',
                                 auth=auth,
                                 params={
                                     '$filter': 'IsLatestVersion',
                                     'includePrerelease': 'true' if include_prerelease else 'false',
                                     'orderby': order_by,
                                     'searchTerm': f"'{terms}'",
                                     'targetFramework': "''"
                                 }) if not exact else requests.
                Request('GET', f'{source}/FindPackagesById()', params={'id': f"'{terms}'"}))
        elif exact:
            searches.append(
                requests.Request(
                    'GET',
                    f'{source}/Packages()',
                    params={'$filter': f"(tolower(Id) eq '{terms}') and IsLatestVersion"}))
        if by_id_only:
            searches.append(
                requests.Request(
                    'GET',
                    f'{source}/Packages()',
                    params={
                        '$filter': f"(substringof('{terms}',tolower(Id))) and IsLatestVersion",
                        '$orderby': order_by,
                        '$skip': str(0 if page is None else page * page_size),
                        '$top': str(page_size),
                        'includePrerelease': 'true' if include_prerelease else 'false',
                        'searchTerm': f"'{terms}'",
                        'targetFramework': "''"
                    }))
        if by_tag_only:
            searches.append(
                requests.Request(
                    'GET',
                    f'{source}/Packages()',
                    params={
                        '$filter': f"(substringof('{terms}',Tags)) and IsLatestVersion",
                        '$orderby': order_by,
                        '$skip': str(0 if page is None else page * page_size),
                        '$top': str(page_size),
                        'includePrerelease': 'true' if include_prerelease else 'false',
                        'searchTerm': f"'{terms}'",
                        'targetFramework': "''"
                    }))
        if id_starts_with:
            searches.append(
                requests.Request(
                    'GET',
                    f'{source}/api/v2/Search()',
                    params={
                        '$filter': f"(startswith(tolower(Id),'{terms}')) and IsLatestVersion",
                        '$orderby': 'Id',
                        '$skip': str(0 if page is None else page * page_size),
                        '$top': str(page_size),
                        'includePrerelease': 'true' if include_prerelease else 'false',
                        'searchTerm': f"'{terms}'"
                    }))
    results: dict[str, str] = {}
    for req in searches:
        req.auth = auth
        req.params['semVerLevel'] = '2.0.0'
        r = session.send(req.prepare())
        try:
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            click.secho(f'Error occurred: {e}', err=True)
            click.Abort()
        root = parse_xml(r.text)
        for entry in ([e] for e in root.findall(FEED_ENTRY_TAG)):
            id_url = get_unique_tag_text(entry, FEED_ID_TAG)
            if id_only:
                results[id_url] = try_get(lambda: get_unique_tag_text(entry, FEED_TITLE_TAG),
                                          'no title?')
            else:
                metadata = entry[0].findall(FEED_PROPERTIES_TAG)
                cache_status_text = try_get(
                    lambda: get_unique_tag_text(metadata, METADATA_DOWNLOAD_CACHE_STATUS_TAG),
                    'Not Available')
                is_approved_text = try_get(
                    lambda: get_unique_tag_text(metadata, METADATA_IS_APPROVED_TAG), 'false')
                testing_pass_fail = try_get(
                    lambda: get_unique_tag_text(metadata, METADATA_PACKAGE_TEST_RESULT_STATUS_TAG),
                    'n/a')
                testing_date = try_get(
                    lambda: get_unique_tag_text(
                        metadata, METADATA_PACKAGE_TEST_RESULT_STATUS_DATE_TAG), 'n/a')
                results[id_url] = SEARCH_RESULT_TEMPLATE.safe_substitute({
                    'approval_date':
                        try_get(
                            lambda: get_unique_tag_text(metadata, METADATA_PACKAGE_APPROVED_DATE_TAG
                                                        ), 'n/a'),
                    'cached_state':
                        'Downloads cached for licensed users'
                        if cache_status_text == 'Available' else '',
                    'description':
                        try_get(lambda: get_unique_tag_text(metadata, METADATA_DESCRIPTION_TAG),
                                'n/a'),
                    'documentation_uri':
                        try_get(lambda: get_unique_tag_text(metadata, METADATA_DOCS_URL_TAG),
                                'n/a'),
                    'license':
                        try_get(lambda: get_unique_tag_text(metadata, METADATA_LICENSE_URL_TAG),
                                'n/a'),
                    'num_downloads':
                        try_get(lambda: get_unique_tag_text(metadata, METADATA_DOWNLOAD_COUNT_TAG),
                                'n/a'),
                    'num_version_downloads':
                        try_get(
                            lambda: get_unique_tag_text(
                                metadata, METADATA_VERSION_DOWNLOAD_COUNT_TAG), 'n/a'),
                    'package_src_uri':
                        try_get(
                            lambda: get_unique_tag_text(metadata, METADATA_PACKAGE_SOURCE_URL_TAG),
                            'n/a'),
                    'package_url':
                        try_get(
                            lambda: get_unique_tag_text(metadata, METADATA_GALLERY_DETAILS_URL_TAG),
                            'n/a'),
                    'publish_date':
                        try_get(lambda: get_unique_tag_text(metadata, METADATA_PUBLISHED_TAG),
                                'n/a'),
                    'release_notes_uri':
                        try_get(lambda: get_unique_tag_text(metadata, METADATA_RELEASE_NOTES_TAG),
                                'n/a'),
                    'site':
                        try_get(lambda: get_unique_tag_text(metadata, METADATA_PROJECT_URL_TAG),
                                'n/a'),
                    'state':
                        '[Approved]' if is_approved_text == 'true' else '',
                    'summary':
                        try_get(lambda: get_unique_tag_text(entry, FEED_SUMMARY_TAG), 'n/a'),
                    'tags':
                        try_get(lambda: get_unique_tag_text(metadata, METADATA_TAGS_TAG), 'n/a'),
                    'testing_status':
                        f'{testing_pass_fail} on {testing_date}',
                    'title':
                        try_get(lambda: get_unique_tag_text(entry, FEED_TITLE_TAG), 'no title?'),
                    'version':
                        try_get(lambda: get_unique_tag_text(metadata, METADATA_VERSION_TAG),
                                'no version?')
                })
    for result in results.values():
        click.echo(f'{result}')
