"""Client."""
from __future__ import annotations

from typing import TYPE_CHECKING
import asyncio
import contextlib
import logging

from defusedxml.ElementTree import fromstring as parse_xml
from niquests import AsyncSession, Request
from niquests.auth import HTTPBasicAuth
from niquests_cache import AsyncCachedSession

from .constants import (
    DEFAULT_CONFIG,
    DEFAULT_PUSH_SOURCE,
    FEED_ENTRY_TAG,
    FEED_ID_TAG,
    FEED_NAMESPACES,
    NUGET_API_KEY_HTTP_HEADER,
    OBJECT_REF_NOT_SET_ERROR_MESSAGE,
)
from .utils import InvalidEntryError, entry_to_search_result, tag_text_or

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Mapping, MutableMapping
    from pathlib import Path

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
                 api_keys: Mapping[str, str] | None = None) -> None:
        self.config = config
        self.api_keys: dict[str, str] = dict(api_keys) if api_keys else {}
        self.session: AsyncSession = AsyncCachedSession(allowable_codes=(200, 201),
                                                        always_revalidate=True,
                                                        cache_control=True)

    def get_keys_available(self) -> list[str]:
        """
        Return a list of the sources that have keys.

        Returns
        -------
        list[str]
        """
        return list(self.api_keys.keys())

    def add_key(self, key: str, source: str) -> None:
        """Add an API key for a source."""
        self.api_keys[source] = key

    def config_set(self, name: ConfigKey, value: str) -> None:
        """Set a configuration value."""
        self.config['pychoco'][name] = value

    def get_default_push_source(self) -> str:
        """
        Get the default push source URL.

        Returns
        -------
        str
        """
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

    async def push(self,
                   package: Path,
                   source: str | None = None,
                   auth: Auth | None = None) -> None:
        """Push a package to a source."""
        source = source or self.get_default_push_source()
        self.update_api_key_header(source)
        api_v2 = self._get_api_v2(source)
        with package.open('rb') as f:
            r = await self.session.put(f'{source}{api_v2}/package/',
                                       auth=auth,
                                       files={package.name: f})
            r.raise_for_status()

    def _get_api_v2(self, source: str | None = None) -> str:
        source = source or self.get_default_push_source()
        return '/api/v2' if '/api/v2' not in source else ''

    async def search(self,
                     terms: str,
                     *,
                     auth: Auth | None = None,
                     all_versions: bool = False,
                     by_id_only: bool = False,
                     by_tag_only: bool = False,
                     exact: bool = False,
                     id_starts_with: bool = False,
                     include_prerelease: bool = False,
                     order_by_popularity: bool = False,
                     page: int | None = None,
                     page_size: int = 30,
                     source: str | None = None) -> AsyncIterator[SearchResult]:
        """
        Search packages. Returns a deduplicated async iterator of results.

        Yields
        ------
        SearchResult
        """
        self.update_api_key_header(source)
        terms = terms.lower()
        ns = FEED_NAMESPACES
        api_v2 = self._get_api_v2(source)
        source = source or self.get_default_push_source()
        searches: list[Request] = []
        order_by = 'Id' if not order_by_popularity else 'DownloadCount desc,Id'
        if (not all_versions and not by_id_only and not by_tag_only and not exact
                and not id_starts_with):
            searches.append(
                Request('GET',
                        f'{source}{api_v2}/Packages',
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
                    Request('GET',
                            f'{source}{api_v2}/Search()',
                            params={
                                '$filter': 'IsLatestVersion',
                                '$orderby': order_by,
                                'includePrerelease': 'true' if include_prerelease else 'false',
                                'searchTerm': f"'{terms}'",
                                'targetFramework': "''"
                            }) if not exact else Request('GET',
                                                         f'{source}{api_v2}/FindPackagesById()',
                                                         params={'id': f"'{terms}'"}))
            elif exact:
                searches.append(
                    Request('GET',
                            f'{source}{api_v2}/Packages',
                            params={'$filter': f"(tolower(Id) eq '{terms}') and IsLatestVersion"}))
            if by_id_only:
                searches.append(
                    Request(
                        'GET',
                        f'{source}{api_v2}/Packages',
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
                    Request('GET',
                            f'{source}{api_v2}/Packages',
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
                    Request(
                        'GET',
                        f'{source}{api_v2}/Search()',
                        params={
                            '$filter': f"(startswith(tolower(Id),'{terms}')) and IsLatestVersion",
                            '$orderby': order_by,
                            '$skip': str(0 if page is None else page * page_size),
                            '$top': str(page_size),
                            'includePrerelease': 'true' if include_prerelease else 'false',
                            'searchTerm': f"'{terms}'"
                        }))
        results: dict[str, SearchResult] = {}
        for req in searches:
            req.auth = auth
            params = dict(req.params) if isinstance(req.params, dict) else {}
            params['semVerLevel'] = '2.0.0'
            req.params = params
        initial_responses = await asyncio.gather(*(self._send_prepared(req) for req in searches))
        for content in initial_responses:
            await self._process_pages(content, auth, ns, results)
        for result in reversed(results.values()):
            yield result

    async def _send_prepared(self, req: Request) -> str:
        prepared_req = req.prepare()
        if prepared_req.url is None:  # pragma: no cover
            return ''
        prepared_req.url = prepared_req.url.replace('%28', '(').replace('%29', ')').replace(
            "'", '%27').replace('+', '%20')
        r = await self.session.send(prepared_req)
        r.raise_for_status()
        return r.text or ''

    async def _process_pages(self, content: str, auth: Auth | None, ns: Mapping[str, str],
                             results: MutableMapping[str, SearchResult]) -> None:
        ns_dict = dict(ns)
        if OBJECT_REF_NOT_SET_ERROR_MESSAGE in content:
            content += '\n  </link>\n</feed>'
        root = parse_xml(content)
        for entry in root.findall(FEED_ENTRY_TAG, ns_dict):
            id_url = tag_text_or(entry.find(FEED_ID_TAG, ns_dict))
            if not id_url or id_url in results:
                continue
            with contextlib.suppress(InvalidEntryError):
                results[id_url] = entry_to_search_result(entry, ns_dict)
        next_link = root.find("link[@rel='next']", ns_dict)
        if results and next_link is not None:
            href = next_link.get('href')
            next_url = href if isinstance(href, str) and href else None
        else:
            next_url = None
        while next_url:
            log.debug('Using next_url: %s', next_url)
            prepared_req = Request('GET', next_url, auth=auth).prepare()
            if prepared_req.url is None:  # pragma: no cover
                break
            r = await self.session.send(prepared_req)
            r.raise_for_status()
            content = r.text or ''
            if OBJECT_REF_NOT_SET_ERROR_MESSAGE in content:
                content += '\n  </link>\n</feed>'
            root = parse_xml(content)
            for entry in root.findall(FEED_ENTRY_TAG, ns_dict):
                id_url = tag_text_or(entry.find(FEED_ID_TAG, ns_dict))
                if not id_url or id_url in results:
                    continue
                with contextlib.suppress(InvalidEntryError):
                    results[id_url] = entry_to_search_result(entry, ns_dict)
            next_link = root.find("link[@rel='next']", ns_dict)
            if results and next_link is not None:
                href = next_link.get('href')
                next_url = href if isinstance(href, str) and href else None
            else:
                next_url = None
