from __future__ import annotations

from typing import TYPE_CHECKING

from choco.client import ChocolateyClient
from choco.constants import OBJECT_REF_NOT_SET_ERROR_MESSAGE
import pytest

if TYPE_CHECKING:
    from niquests_mock import MockRouter

FEED_TEMPLATE = """<?xml version="1.0" encoding="utf-8" standalone="yes" ?>
<feed xmlns="http://www.w3.org/2005/Atom"
      xmlns:d="http://schemas.microsoft.com/ado/2007/08/dataservices"
      xmlns:m="http://schemas.microsoft.com/ado/2007/08/dataservices/metadata">
  <title type="text">Packages</title>
  <id>https://push.chocolatey.org/Packages</id>
  <updated>2023-09-21T18:48:55Z</updated>
  <entry>
    <id>https://push.chocolatey.org/Packages(Id='{id}',Version='{version}')</id>
    <title type="text">{title}</title>
    <summary type="text">{summary}</summary>
    <content type="application/zip"
             src="https://push.chocolatey.org/package/{id}/{version}" />
    <m:properties>
      <d:Version>{version}</d:Version>
      <d:IsApproved m:type="Edm.Boolean">true</d:IsApproved>
      <d:DownloadCount m:type="Edm.Int32">100</d:DownloadCount>
      <d:VersionDownloadCount m:type="Edm.Int32">50</d:VersionDownloadCount>
      <d:Tags> {tags} </d:Tags>
      <d:PackageTestResultStatus>Passing</d:PackageTestResultStatus>
    </m:properties>
  </entry>
</feed>"""


@pytest.mark.asyncio
async def test_client_exact(niquests_mock: MockRouter) -> None:
    feed = FEED_TEMPLATE.format(id='test',
                                version='1.0.0',
                                title='test',
                                summary='A test package.',
                                tags='test')
    niquests_mock.get('https://push.chocolatey.org/api/v2/Packages',
                      params={
                          '$filter': "(tolower(Id) eq 'test') and IsLatestVersion"
                      }).respond(text=feed)
    client = ChocolateyClient()
    results = [r async for r in client.search('test', exact=True)]
    assert len(results) == 1
    assert results[0]['title'] == 'test'
    assert results[0]['version'] == '1.0.0'


@pytest.mark.asyncio
async def test_client_by_id_only(niquests_mock: MockRouter) -> None:
    feed = FEED_TEMPLATE.format(id='test',
                                version='1.0.0',
                                title='test',
                                summary='A test package.',
                                tags='test')
    niquests_mock.get('https://push.chocolatey.org/api/v2/Packages',
                      params={
                          '$filter': "(substringof('test',tolower(Id))) and IsLatestVersion"
                      }).respond(text=feed)
    client = ChocolateyClient()
    results = [r async for r in client.search('test', by_id_only=True)]
    assert len(results) == 1
    assert results[0]['title'] == 'test'


@pytest.mark.asyncio
async def test_client_by_id_starts_with(niquests_mock: MockRouter) -> None:
    feed = FEED_TEMPLATE.format(id='test-pkg',
                                version='2.0.0',
                                title='test-pkg',
                                summary='A test package.',
                                tags='test')
    niquests_mock.get('https://push.chocolatey.org/api/v2/Search()',
                      params={
                          '$filter': "(startswith(tolower(Id),'test')) and IsLatestVersion"
                      }).respond(text=feed)
    client = ChocolateyClient()
    results = [r async for r in client.search('test', id_starts_with=True)]
    assert len(results) == 1
    assert results[0]['title'] == 'test-pkg'


@pytest.mark.asyncio
async def test_client_by_tag_only(niquests_mock: MockRouter) -> None:
    feed = FEED_TEMPLATE.format(id='tagged',
                                version='1.0.0',
                                title='tagged',
                                summary='A tagged package.',
                                tags='test browser')
    niquests_mock.get('https://push.chocolatey.org/api/v2/Packages',
                      params={
                          '$filter': "(substringof('test',Tags)) and IsLatestVersion"
                      }).respond(text=feed)
    client = ChocolateyClient()
    results = [r async for r in client.search('test', by_tag_only=True)]
    assert len(results) == 1
    assert results[0]['title'] == 'tagged'


@pytest.mark.asyncio
async def test_client_pagination_three_pages(niquests_mock: MockRouter) -> None:
    page1 = """<?xml version="1.0" encoding="utf-8" standalone="yes" ?>
<feed xmlns="http://www.w3.org/2005/Atom"
      xmlns:d="http://schemas.microsoft.com/ado/2007/08/dataservices"
      xmlns:m="http://schemas.microsoft.com/ado/2007/08/dataservices/metadata">
  <title type="text">Packages</title>
  <id>https://push.chocolatey.org/Packages</id>
  <updated>2023-09-21T18:48:55Z</updated>
  <entry>
    <id>https://push.chocolatey.org/Packages(Id='PkgA',Version='1.0.0')</id>
    <title type="text">PkgA</title>
    <content type="application/zip"
             src="https://push.chocolatey.org/package/PkgA/1.0.0" />
    <m:properties>
      <d:Version>1.0.0</d:Version>
      <d:IsApproved m:type="Edm.Boolean">true</d:IsApproved>
    </m:properties>
  </entry>
  <link rel="next" href="https://push.chocolatey.org/P?skip=1" />
</feed>"""
    page2 = """<?xml version="1.0" encoding="utf-8" standalone="yes" ?>
<feed xmlns="http://www.w3.org/2005/Atom"
      xmlns:d="http://schemas.microsoft.com/ado/2007/08/dataservices"
      xmlns:m="http://schemas.microsoft.com/ado/2007/08/dataservices/metadata">
  <title type="text">Packages</title>
  <id>https://push.chocolatey.org/Packages</id>
  <updated>2023-09-21T18:48:55Z</updated>
  <entry>
    <id>https://push.chocolatey.org/Packages(Id='PkgB',Version='2.0.0')</id>
    <title type="text">PkgB</title>
    <content type="application/zip"
             src="https://push.chocolatey.org/package/PkgB/2.0.0" />
    <m:properties>
      <d:Version>2.0.0</d:Version>
      <d:IsApproved m:type="Edm.Boolean">true</d:IsApproved>
    </m:properties>
  </entry>
  <link rel="next" href="https://push.chocolatey.org/P?skip=2" />
</feed>"""
    page3 = """<?xml version="1.0" encoding="utf-8" standalone="yes" ?>
<feed xmlns="http://www.w3.org/2005/Atom"
      xmlns:d="http://schemas.microsoft.com/ado/2007/08/dataservices"
      xmlns:m="http://schemas.microsoft.com/ado/2007/08/dataservices/metadata">
  <title type="text">Packages</title>
  <id>https://push.chocolatey.org/Packages</id>
  <updated>2023-09-21T18:48:55Z</updated>
  <entry>
    <id>https://push.chocolatey.org/Packages(Id='PkgC',Version='3.0.0')</id>
    <title type="text">PkgC</title>
    <content type="application/zip"
             src="https://push.chocolatey.org/package/PkgC/3.0.0" />
    <m:properties>
      <d:Version>3.0.0</d:Version>
      <d:IsApproved m:type="Edm.Boolean">true</d:IsApproved>
    </m:properties>
  </entry>
</feed>"""
    niquests_mock.get('https://push.chocolatey.org/api/v2/Packages',
                      params={
                          '$filter': "(tolower(Id) eq 'pkga') and IsLatestVersion"
                      }).respond(text=page1)
    niquests_mock.get('https://push.chocolatey.org/P', params={'skip': '1'}).respond(text=page2)
    niquests_mock.get('https://push.chocolatey.org/P', params={'skip': '2'}).respond(text=page3)
    client = ChocolateyClient()
    results = [r async for r in client.search('pkga', exact=True)]
    assert len(results) == 3
    titles = {r['title'] for r in results}
    assert titles == {'PkgA', 'PkgB', 'PkgC'}


@pytest.mark.asyncio
async def test_client_pagination_with_duplicate_entry(niquests_mock: MockRouter) -> None:
    page1 = """<?xml version="1.0" encoding="utf-8" standalone="yes" ?>
<feed xmlns="http://www.w3.org/2005/Atom"
      xmlns:d="http://schemas.microsoft.com/ado/2007/08/dataservices"
      xmlns:m="http://schemas.microsoft.com/ado/2007/08/dataservices/metadata">
  <title type="text">Packages</title>
  <id>https://push.chocolatey.org/Packages</id>
  <updated>2023-09-21T18:48:55Z</updated>
  <entry>
    <id>https://push.chocolatey.org/Packages(Id='Dupe',Version='1.0.0')</id>
    <title type="text">Dupe</title>
    <content type="application/zip"
             src="https://push.chocolatey.org/package/Dupe/1.0.0" />
    <m:properties>
      <d:Version>1.0.0</d:Version>
      <d:IsApproved m:type="Edm.Boolean">true</d:IsApproved>
    </m:properties>
  </entry>
  <link rel="next" href="https://push.chocolatey.org/P?skip=1" />
</feed>"""
    page2 = """<?xml version="1.0" encoding="utf-8" standalone="yes" ?>
<feed xmlns="http://www.w3.org/2005/Atom"
      xmlns:d="http://schemas.microsoft.com/ado/2007/08/dataservices"
      xmlns:m="http://schemas.microsoft.com/ado/2007/08/dataservices/metadata">
  <title type="text">Packages</title>
  <id>https://push.chocolatey.org/Packages</id>
  <updated>2023-09-21T18:48:55Z</updated>
  <entry>
    <id>https://push.chocolatey.org/Packages(Id='Dupe',Version='1.0.0')</id>
    <title type="text">Dupe</title>
    <content type="application/zip"
             src="https://push.chocolatey.org/package/Dupe/1.0.0" />
    <m:properties>
      <d:Version>1.0.0</d:Version>
      <d:IsApproved m:type="Edm.Boolean">true</d:IsApproved>
    </m:properties>
  </entry>
</feed>"""
    niquests_mock.get('https://push.chocolatey.org/api/v2/Packages',
                      params={
                          '$filter': "(tolower(Id) eq 'dupe') and IsLatestVersion"
                      }).respond(text=page1)
    niquests_mock.get('https://push.chocolatey.org/P', params={'skip': '1'}).respond(text=page2)
    client = ChocolateyClient()
    results = [r async for r in client.search('dupe', exact=True)]
    assert len(results) == 1


@pytest.mark.asyncio
async def test_client_pagination_with_error_message(niquests_mock: MockRouter) -> None:
    page1 = """<?xml version="1.0" encoding="utf-8" standalone="yes" ?>
<feed xmlns="http://www.w3.org/2005/Atom"
      xmlns:d="http://schemas.microsoft.com/ado/2007/08/dataservices"
      xmlns:m="http://schemas.microsoft.com/ado/2007/08/dataservices/metadata">
  <title type="text">Packages</title>
  <id>https://push.chocolatey.org/Packages</id>
  <updated>2023-09-21T18:48:55Z</updated>
  <entry>
    <id>https://push.chocolatey.org/Packages(Id='ErrPkg',Version='1.0.0')</id>
    <title type="text">ErrPkg</title>
    <content type="application/zip"
             src="https://push.chocolatey.org/package/ErrPkg/1.0.0" />
    <m:properties>
      <d:Version>1.0.0</d:Version>
      <d:IsApproved m:type="Edm.Boolean">true</d:IsApproved>
    </m:properties>
  </entry>
  <link rel="next" href="https://push.chocolatey.org/P?skip=1" />
</feed>"""
    page2_prefix = """<?xml version="1.0" encoding="utf-8" standalone="yes" ?>
<feed xmlns="http://www.w3.org/2005/Atom"
      xmlns:d="http://schemas.microsoft.com/ado/2007/08/dataservices"
      xmlns:m="http://schemas.microsoft.com/ado/2007/08/dataservices/metadata">
  <title type="text">Packages</title>
  <id>https://push.chocolatey.org/Packages</id>
  <updated>2023-09-21T18:48:55Z</updated>
  <entry>
    <id>https://push.chocolatey.org/Packages(Id='ErrPkg2',Version='2.0.0')</id>
    <title type="text">ErrPkg2</title>
    <content type="application/zip"
             src="https://push.chocolatey.org/package/ErrPkg2/2.0.0" />
    <m:properties>
      <d:Version>2.0.0</d:Version>
      <d:IsApproved m:type="Edm.Boolean">true</d:IsApproved>
    </m:properties>
  </entry>
  <link """
    page2 = page2_prefix + OBJECT_REF_NOT_SET_ERROR_MESSAGE
    niquests_mock.get('https://push.chocolatey.org/api/v2/Packages',
                      params={
                          '$filter': "(tolower(Id) eq 'errpkg') and IsLatestVersion"
                      }).respond(text=page1)
    niquests_mock.get('https://push.chocolatey.org/P', params={'skip': '1'}).respond(text=page2)
    client = ChocolateyClient()
    results = [r async for r in client.search('errpkg', exact=True)]
    assert len(results) == 2
    titles = {r['title'] for r in results}
    assert titles == {'ErrPkg', 'ErrPkg2'}
