"""Client."""
from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING
import contextlib
import logging

from defusedxml.ElementTree import fromstring as parse_xml
from requests.auth import HTTPBasicAuth
import requests

from .constants import (
    DEFAULT_CONFIG,
    DEFAULT_PUSH_SOURCE,
    FEED_ENTRY_TAG,
    FEED_ID_TAG,
    FEED_NAMESPACES,
    NUGET_API_KEY_HTTP_HEADER,
)
from .utils import InvalidEntryError, entry_to_search_result, tag_text_or

if TYPE_CHECKING:
    from collections.abc import Iterator

    from .typing import Config, ConfigKey, SearchResult

Auth = tuple[str, str] | HTTPBasicAuth
"""Authentication details."""
log = logging.getLogger(__name__)


class ChocolateyClient:
    """
    Chocolatey client.

    Anything that involves interactions with the server will be in this class.
    """
    def __init__(self,
                 config: Config = DEFAULT_CONFIG,
                 api_keys: dict[str, str] | None = None) -> None:
        self.config = config
        self.api_keys = api_keys or {}
        self.session = requests.Session()

    def get_keys_available(self) -> Iterator[str]:
        """Return an iterator of the sources that have keys."""
        yield from self.api_keys.keys()

    def add_key(self, key: str, source: str) -> None:
        """Add an API key for a source."""
        self.api_keys[source] = key

    def config_set(self, name: ConfigKey, value: str) -> None:
        """Set a configuration value."""
        self.config['pychoco'][name] = value

    def get_default_push_source(self) -> str:
        """Get the default push source URL."""
        return (self.config['pychoco'].get('defaultPushSource', DEFAULT_PUSH_SOURCE)
                or DEFAULT_PUSH_SOURCE)

    def update_api_key_header(self, source: str | None = None) -> None:
        """
        Update the shared session API key header.

        If one does not exist, the existing header is removed if it is present.
        """
        source = source or self.get_default_push_source()
        try:
            self.session.headers.update({NUGET_API_KEY_HTTP_HEADER: self.api_keys[source]})
        except KeyError:
            with contextlib.suppress(KeyError):
                del self.session.headers[NUGET_API_KEY_HTTP_HEADER]

    def push(self, package: Path, source: str | None = None, auth: Auth | None = None) -> None:
        """Push a package to a source."""
        source = source or self.get_default_push_source()
        self.update_api_key_header(source)
        api_v2 = self._get_api_v2(source)
        with package.open('rb') as f:
            r = self.session.put(f'{source}{api_v2}/package/', auth=auth, files={package.name: f})
            r.raise_for_status()

    def _get_api_v2(self, source: str | None = None) -> str:
        source = source or self.get_default_push_source()
        return '/api/v2' if '/api/v2' not in source else ''

    def search(self,
               terms: str,
               *,
               auth: Auth | None = None,
               all_versions: bool = False,
               by_id_only: bool = False,
               by_tag_only: bool = False,
               debug: bool = False,
               exact: bool = False,
               id_starts_with: bool = False,
               include_prerelease: bool = False,
               order_by_popularity: bool = False,
               page: int | None = None,
               page_size: bool = False,
               source: str | None = None) -> Iterator[SearchResult]:
        """Search packages. Returns a deduplicated iterator of results."""
        self.update_api_key_header(source)
        ns = FEED_NAMESPACES
        api_v2 = self._get_api_v2(source)
        source = source or self.get_default_push_source()
        searches: list[requests.Request] = []
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
                            f"((Description ne null) and substringof('{terms}',"
                            'tolower(Description))))'
                            f" or ((Tags ne null) and substringof(' {terms} ',tolower(Tags)))) "
                            "and IsLatestVersion",
                        '$orderby': order_by,
                        '$skip': str(0 if page is None else page * page_size),
                        '$top': str(page_size)
                    }))
        else:
            if all_versions:
                searches.append(
                    requests.
                    Request('GET',
                            f'{source}{api_v2}/Search()',
                            params={
                                '$filter': 'IsLatestVersion',
                                '$orderby': order_by,
                                'includePrerelease': 'true' if include_prerelease else 'false',
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
                        f'{source}{api_v2}/Search()',
                        params={
                            '$filter': f"(startswith(tolower(Id),'{terms}')) and IsLatestVersion",
                            '$orderby': 'Id',
                            '$skip': str(0 if page is None else page * page_size),
                            '$top': str(page_size),
                            'includePrerelease': 'true' if include_prerelease else 'false',
                            'searchTerm': f"'{terms}'"
                        }))
        results: dict[str, SearchResult] = {}
        for i, req in enumerate(searches):
            req.auth = auth
            req.params['semVerLevel'] = '2.0.0'
            r = self.session.send(req.prepare())
            r.raise_for_status()
            if debug:  # pragma no cover
                log.debug(r.text)
                try:
                    with Path(f'result-{i:03}.xml').open('w', encoding='utf-8') as f:
                        f.write(r.text)
                except OSError:
                    pass
            root = parse_xml(r.text)
            for entry in root.findall(FEED_ENTRY_TAG, ns):
                id_url = tag_text_or(entry.find(FEED_ID_TAG, ns))
                if not id_url or id_url in results:
                    continue
                with contextlib.suppress(InvalidEntryError):
                    results[id_url] = entry_to_search_result(entry, ns)
        yield from reversed(results.values())
