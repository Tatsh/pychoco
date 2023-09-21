"""Client."""
from os.path import basename
from pathlib import Path
from typing import Iterator, cast

from defusedxml.ElementTree import fromstring as parse_xml
from loguru import logger
from requests.auth import HTTPBasicAuth
from tomlkit.container import Container
from tomlkit.items import Item, Table
import requests
import tomlkit

from .constants import (FEED_ENTRY_TAG, FEED_ID_TAG, FEED_NAMESPACES, NUGET_API_KEY_HTTP_HEADER,
                        PYCHOCO_API_KEYS_TOML_PATH, PYCHOCO_TOML_PATH)
from .typing import ConfigKey, SearchResult
from .utils import InvalidEntryError, entry_to_search_result, tag_text_or

Auth = tuple[str, str] | HTTPBasicAuth


class ChocolateyClient:
    """
    Chocolatey client. Anything that involves interactions with the server will be in this class.
    """
    def __init__(self,
                 api_keys_path: Path | str | None = None,
                 config_path: Path | str | None = None) -> None:
        self.api_keys_path = Path(api_keys_path or PYCHOCO_API_KEYS_TOML_PATH)
        self.api_keys = (cast(dict[str, str], tomlkit.loads(self.api_keys_path.read_text()))
                         if self.api_keys_path.exists() else {})
        self.config_path = Path(config_path or PYCHOCO_TOML_PATH)
        self.config = (tomlkit.loads(self.config_path.read_text())
                       if self.config_path.exists() else {})
        self.session = requests.Session()

    def get_keys_available(self) -> Iterator[str]:
        """Return an iterator of the sources that have keys."""
        if self.api_keys_path.exists():
            with self.api_keys_path.open() as f:
                yield from sorted(tomlkit.load(f))

    def add_key(self, key: str, source: str) -> None:
        """Add an API key for a source."""
        self.api_keys_path.parent.mkdir(parents=True, exist_ok=True)
        if self.api_keys_path.exists():
            with self.api_keys_path.open() as f:
                keys = tomlkit.load(f)
        else:
            keys = tomlkit.document()
        keys.add(source, cast(Item, key))
        with self.api_keys_path.open('w') as f:
            tomlkit.dump(keys, f)

    def config_set(self, name: ConfigKey, value: str) -> None:
        """Set a configuration value."""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        if self.config_path.exists():
            with self.config_path.open() as f:
                config_ = tomlkit.load(f)
        else:
            config_ = tomlkit.document()
        if 'pychoco' not in config_:
            config_['pychoco'] = tomlkit.table()
        if name == 'defaultPushSource':
            value = value.rstrip('/')
        cast(Table, config_['pychoco']).add(name, value)
        with self.config_path.open('w') as f:
            tomlkit.dump(config_, f)

    def get_default_push_source(self) -> str:
        """Gets the default push source URL."""
        try:
            return cast(str, cast(Container, self.config['pychoco'])['defaultPushSource'])
        except (KeyError, FileNotFoundError):
            return 'https://push.chocolatey.org'

    def update_api_key_header(self, source: str | None = None) -> None:
        """
        Updates the shared session API key header. If one does not exist, the existing header is
        removed if it is present.
        """
        source = source or self.get_default_push_source()
        try:
            self.session.headers.update({NUGET_API_KEY_HTTP_HEADER: self.api_keys[source]})
        except KeyError:
            try:
                del self.session.headers[NUGET_API_KEY_HTTP_HEADER]
            except KeyError:
                pass

    def push(self, package: str, source: str | None = None, auth: Auth | None = None) -> None:
        """Push a package to a source."""
        self.update_api_key_header(source)
        api_v2 = self._get_api_v2(source)
        with open(package, 'rb') as f:
            r = self.session.put(f'{source}{api_v2}/package/',
                                 auth=auth,
                                 files={basename(package): f})
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
                # FIXME In both cases, pagination is not implemented. For non-exact, multiple
                # requests to FindPackagesById() are necessary with every package found. For exact,
                # $skiptoken must be used to paginate.
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
                logger.debug(r.text)
                try:
                    with open(f'result-{i:03}.xml', 'w') as f:
                        f.write(r.text)
                except IOError:
                    pass
            root = parse_xml(r.text)
            for entry in root.findall(FEED_ENTRY_TAG, ns):
                id_url = tag_text_or(entry.find(FEED_ID_TAG, ns))
                if not id_url or id_url in results:
                    continue
                try:
                    results[id_url] = entry_to_search_result(entry, ns)
                except InvalidEntryError:
                    pass
        for result in reversed(results.values()):
            yield result
