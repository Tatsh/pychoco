from __future__ import annotations

from typing import TYPE_CHECKING
from urllib.parse import quote, urlencode

from choco.main import main as choco
import pytest

if TYPE_CHECKING:
    from click.testing import CliRunner
    from pytest_mock import MockerFixture
    import requests_mock as req_mock


def test_search_no_options_bad_entry(runner: CliRunner, requests_mock: req_mock.Mocker,
                                     bad_feed: str) -> None:
    terms = 'rt-hd-dump'
    qs = urlencode(
        {
            '$filter': f"((((Id ne null) and substringof('{terms}',tolower(Id))) or "
                       f"((Description ne null) and substringof('{terms}',tolower(Description))))"
                       f" or ((Tags ne null) and substringof(' {terms} ',tolower(Tags)))) "
                       "and IsLatestVersion",
            '$orderby': 'Id',
            '$skip': '0',
            '$top': '30'
        },
        quote_via=quote)
    requests_mock.get(f'https://somehost/api/v2/Packages?{qs}', text=bad_feed)
    run = runner.invoke(choco, ('search', '-s', 'https://somehost', terms))
    assert not run.stdout
    assert run.exit_code == 0


def test_search_no_options_bad_entry_id_only(runner: CliRunner, requests_mock: req_mock.Mocker,
                                             bad_feed: str) -> None:
    terms = 'rt-hd-dump'
    qs = urlencode(
        {
            '$filter': f"((((Id ne null) and substringof('{terms}',tolower(Id))) or "
                       f"((Description ne null) and substringof('{terms}',tolower(Description))))"
                       f" or ((Tags ne null) and substringof(' {terms} ',tolower(Tags)))) "
                       "and IsLatestVersion",
            '$orderby': 'Id',
            '$skip': '0',
            '$top': '30'
        },
        quote_via=quote)
    requests_mock.get(f'https://somehost/api/v2/Packages?{qs}', text=bad_feed)
    for run in (runner.invoke(choco, ('search', '--id-only', '-s', 'https://somehost', terms)),
                runner.invoke(choco, ('search', '--idonly', '-s', 'https://somehost', terms))):
        assert not run.stdout
        assert run.exit_code == 0


@pytest.mark.parametrize('args',
                         [('search', '-a', '-e', '-s', 'https://somehost', 'chrome'),
                          ('search', '--all', '--exact', '-s', 'https://somehost', 'chrome'),
                          ('search', '--allversions', '-e', '-s', 'https://somehost', 'chrome'),
                          ('search', '--all-versions', '-e', '-s', 'https://somehost', 'chrome')])
def test_search_all_versions_exact(runner: CliRunner, requests_mock: req_mock.Mocker,
                                   chrome_all_versions_exact_feed: str, args: tuple[str,
                                                                                    ...]) -> None:
    terms = 'chrome'
    qs = urlencode({'id': f"'{terms}'"})
    requests_mock.get(f'https://somehost/api/v2/FindPackagesById()?{qs}',
                      text=chrome_all_versions_exact_feed)
    requests_mock.get(
        ("http://community.chocolatey.org/api/v2/FindPackagesById()?id='googlechrome'&"
         "$skiptoken='GoogleChrome','111.0.5563.111'"),
        text="""<?xml version="1.0" encoding="utf-8" standalone="yes" ?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title type="text">FindPackagesById</title>
  <id>http://somehost/api/v2/FindPackagesById</id>
  <updated>2023-09-21T18:48:55Z</updated>
</feed>""")
    run = runner.invoke(choco, args)
    assert run.exit_code == 0
    lines = run.stdout.splitlines()
    assert lines[0].strip() == 'GoogleChrome 111.0.5563.111 [Approved]'
    assert lines[-1].strip() == 'GoogleChrome 10.0.0 [Approved]'


def test_search_no_duplicates(runner: CliRunner, requests_mock: req_mock.Mocker,
                              dupe_feed: str) -> None:
    terms = 'chrome'
    qs = urlencode({'id': f"'{terms}'"}, quote_via=quote)
    requests_mock.get(f'https://somehost/api/v2/FindPackagesById()?{qs}', text=dupe_feed)
    run = runner.invoke(choco, ('search', '-a', '-e', '-s', 'https://somehost', terms))
    lines = run.stdout.splitlines()
    assert len(lines) == 1


def test_search_id_only(runner: CliRunner, mocker: MockerFixture) -> None:
    mocker.patch('choco.commands.search.ChocolateyClient.search',
                 return_value=[{
                     'title': 'chrome1'
                 }])
    run = runner.invoke(choco, ('search', '--idonly', "'chrome'"))
    assert run.exit_code == 0
    assert run.output.strip() == 'chrome1'


def test_search_else_case(runner: CliRunner, mocker: MockerFixture) -> None:
    mocker.patch('choco.commands.search.ChocolateyClient.search',
                 return_value=[{
                     'title': 'chrome1',
                     'testing_status': 'testing',
                     'version': '1.0.0',
                     'is_cached': True,
                     'is_approved': True,
                     'testing_date': '2023-10-01T00:00:00Z',
                     'tags': ['tag1', 'tag2']
                 }])
    run = runner.invoke(choco, ('search', "'chrome'"))
    assert run.exit_code == 0
    assert run.output.strip() == """chrome1 1.0.0 [Approved] Downloads cached for licensed users
 Title: chrome1 | Published: ${publish_date}
 Package approved as a trusted package on ${approval_date}.
 Package testing status: testing on 2023-10-01T00:00:00Z.
 Number of Downloads: ${num_downloads} | Downloads for this version: ${num_version_downloads}
 Package url ${package_url}
 Chocolatey Package Source: ${package_src_uri}
 Tags:tag1 tag2
 Software Site: ${site}
 Software License: ${license}
 Documentation: ${documentation_uri}
 Summary: ${summary}
 Description: ${description}
 Release Notes: ${release_notes_uri}"""


def test_search_else_case_no_title(runner: CliRunner, mocker: MockerFixture) -> None:
    mocker.patch('choco.commands.search.ChocolateyClient.search',
                 return_value=[{
                     'title': None,
                     'testing_status': 'testing',
                     'version': '1.0.0',
                     'is_cached': True,
                     'is_approved': True,
                     'testing_date': '2023-10-01T00:00:00Z',
                     'tags': ['tag1', 'tag2']
                 }])
    run = runner.invoke(choco, ('search', "'chrome'"))
    assert run.exit_code == 0
    assert run.output.strip() == """no title? 1.0.0 [Approved] Downloads cached for licensed users
 Title: no title? | Published: ${publish_date}
 Package approved as a trusted package on ${approval_date}.
 Package testing status: testing on 2023-10-01T00:00:00Z.
 Number of Downloads: ${num_downloads} | Downloads for this version: ${num_version_downloads}
 Package url ${package_url}
 Chocolatey Package Source: ${package_src_uri}
 Tags:tag1 tag2
 Software Site: ${site}
 Software License: ${license}
 Documentation: ${documentation_uri}
 Summary: ${summary}
 Description: ${description}
 Release Notes: ${release_notes_uri}"""


def test_search_else_case_no_version(runner: CliRunner, mocker: MockerFixture) -> None:
    mocker.patch('choco.commands.search.ChocolateyClient.search',
                 return_value=[{
                     'title': 'chrome1',
                     'version': None,
                     'testing_status': 'testing',
                     'is_cached': True,
                     'is_approved': True,
                     'testing_date': '2023-10-01T00:00:00Z',
                     'tags': ['tag1', 'tag2']
                 }])
    run = runner.invoke(choco, ('search', "'chrome'"))
    assert run.exit_code == 0
    assert run.output.strip(
    ) == """chrome1 no version? [Approved] Downloads cached for licensed users
 Title: chrome1 | Published: ${publish_date}
 Package approved as a trusted package on ${approval_date}.
 Package testing status: testing on 2023-10-01T00:00:00Z.
 Number of Downloads: ${num_downloads} | Downloads for this version: ${num_version_downloads}
 Package url ${package_url}
 Chocolatey Package Source: ${package_src_uri}
 Tags:tag1 tag2
 Software Site: ${site}
 Software License: ${license}
 Documentation: ${documentation_uri}
 Summary: ${summary}
 Description: ${description}
 Release Notes: ${release_notes_uri}"""


def test_search_else_case_no_testing_date(runner: CliRunner, mocker: MockerFixture) -> None:
    mocker.patch('choco.commands.search.ChocolateyClient.search',
                 return_value=[{
                     'title': 'chrome1',
                     'version': '1.0.0',
                     'testing_status': 'testing',
                     'is_cached': True,
                     'is_approved': True,
                     'testing_date': None,
                     'tags': ['tag1', 'tag2']
                 }])
    run = runner.invoke(choco, ('search', "'chrome'"))
    assert run.exit_code == 0
    assert run.output.strip() == """chrome1 1.0.0 [Approved] Downloads cached for licensed users
 Title: chrome1 | Published: ${publish_date}
 Package approved as a trusted package on ${approval_date}.
 Package testing status: testing.
 Number of Downloads: ${num_downloads} | Downloads for this version: ${num_version_downloads}
 Package url ${package_url}
 Chocolatey Package Source: ${package_src_uri}
 Tags:tag1 tag2
 Software Site: ${site}
 Software License: ${license}
 Documentation: ${documentation_uri}
 Summary: ${summary}
 Description: ${description}
 Release Notes: ${release_notes_uri}"""


def test_search_pagination_exact(runner: CliRunner, requests_mock: req_mock.Mocker) -> None:
    """Test that pagination works correctly for exact searches."""
    terms = 'testpkg'
    # First page with 2 entries and a next link
    page1_feed = """<?xml version="1.0" encoding="utf-8" standalone="yes" ?>
<feed xmlns="http://www.w3.org/2005/Atom"
      xmlns:d="http://schemas.microsoft.com/ado/2007/08/dataservices"
      xmlns:m="http://schemas.microsoft.com/ado/2007/08/dataservices/metadata">
  <title type="text">Packages</title>
  <id>https://somehost/Packages</id>
  <updated>2023-09-21T18:48:55Z</updated>
  <entry>
    <id>https://somehost/Packages(Id='TestPkg',Version='1.0.0')</id>
    <title type="text">TestPkg</title>
    <content type="application/zip" src="https://somehost/package/TestPkg/1.0.0" />
    <m:properties>
      <d:Version>1.0.0</d:Version>
      <d:IsApproved m:type="Edm.Boolean">true</d:IsApproved>
    </m:properties>
  </entry>
  <entry>
    <id>https://somehost/Packages(Id='TestPkg',Version='2.0.0')</id>
    <title type="text">TestPkg</title>
    <content type="application/zip" src="https://somehost/package/TestPkg/2.0.0" />
    <m:properties>
      <d:Version>2.0.0</d:Version>
      <d:IsApproved m:type="Edm.Boolean">true</d:IsApproved>
    </m:properties>
  </entry>
  <link rel="next"
        href="https://somehost/P?f=test&amp;skip=2" />
</feed>"""
    # Second page with 1 entry and no next link
    page2_feed = """<?xml version="1.0" encoding="utf-8" standalone="yes" ?>
<feed xmlns="http://www.w3.org/2005/Atom"
      xmlns:d="http://schemas.microsoft.com/ado/2007/08/dataservices"
      xmlns:m="http://schemas.microsoft.com/ado/2007/08/dataservices/metadata">
  <title type="text">Packages</title>
  <id>https://somehost/Packages</id>
  <updated>2023-09-21T18:48:55Z</updated>
  <entry>
    <id>https://somehost/Packages(Id='TestPkg',Version='3.0.0')</id>
    <title type="text">TestPkg</title>
    <content type="application/zip" src="https://somehost/package/TestPkg/3.0.0" />
    <m:properties>
      <d:Version>3.0.0</d:Version>
      <d:IsApproved m:type="Edm.Boolean">true</d:IsApproved>
    </m:properties>
  </entry>
</feed>"""
    qs = urlencode({'$filter': f"(tolower(Id) eq '{terms}') and IsLatestVersion"}, quote_via=quote)
    requests_mock.get(f'https://somehost/api/v2/Packages?{qs}', text=page1_feed)
    requests_mock.get('https://somehost/P?f=test&skip=2', text=page2_feed)

    run = runner.invoke(choco, ('search', '-e', '-s', 'https://somehost', terms))
    assert run.exit_code == 0
    output = run.stdout
    # Should have all 3 entries from both pages
    assert 'TestPkg 3.0.0' in output
    assert 'TestPkg 2.0.0' in output
    assert 'TestPkg 1.0.0' in output


def test_search_handles_error_at_end_of_xml(logparser_search_error_feed: str, runner: CliRunner,
                                            requests_mock: req_mock.Mocker) -> None:
    params = urlencode({
        '$filter': "(startswith(tolower(Id),'logparser')) and IsLatestVersion",
        '$orderby': 'Id',
        '$skip': '0',
        '$top': '30',
        'includePrerelease': 'false',
        'searchTerm': "'logparser'"
    })
    requests_mock.get(f'https://somehost/api/v2/Search()?{params}',
                      text=logparser_search_error_feed)
    run = runner.invoke(choco,
                        ('search', '-s', 'https://somehost', '--id-starts-with', 'logparser'))
    assert run.exit_code == 0
    output = run.stdout
    assert 'logparser.lizardgui' in output
