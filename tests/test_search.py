from __future__ import annotations

from typing import TYPE_CHECKING
from urllib.parse import quote, urlencode

from choco.main import main as choco

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
    requests_mock.get(f'https://somehost/Packages()?{qs}', text=bad_feed)
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
    requests_mock.get(f'https://somehost/Packages()?{qs}', text=bad_feed)
    for run in (runner.invoke(choco, ('search', '--id-only', '-s', 'https://somehost', terms)),
                runner.invoke(choco, ('search', '--idonly', '-s', 'https://somehost', terms))):
        assert not run.stdout
        assert run.exit_code == 0


def test_search_all_versions_exact(runner: CliRunner, requests_mock: req_mock.Mocker,
                                   chrome_all_versions_exact_feed: str) -> None:
    terms = 'chrome'
    qs = urlencode({'id': f"'{terms}'"}, quote_via=quote)
    requests_mock.get(f'https://somehost/FindPackagesById()?{qs}',
                      text=chrome_all_versions_exact_feed)
    for run in (runner.invoke(choco, ('search', '-a', '-e', '-s', 'https://somehost', terms)),
                runner.invoke(choco,
                              ('search', '--all', '--exact', '-s', 'https://somehost', terms)),
                runner.invoke(choco,
                              ('search', '--allversions', '-e', '-s', 'https://somehost', terms)),
                runner.invoke(choco,
                              ('search', '--all-versions', '-e', '-s', 'https://somehost', terms))):
        lines = run.stdout.splitlines()
        assert lines[0].strip() == 'GoogleChrome 111.0.5563.111 [Approved]'
        assert lines[-1].strip() == 'GoogleChrome 10.0.0 [Approved]'
        assert run.exit_code == 0


def test_search_no_duplicates(runner: CliRunner, requests_mock: req_mock.Mocker,
                              dupe_feed: str) -> None:
    terms = 'chrome'
    qs = urlencode({'id': f"'{terms}'"}, quote_via=quote)
    requests_mock.get(f'https://somehost/FindPackagesById()?{qs}', text=dupe_feed)
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
