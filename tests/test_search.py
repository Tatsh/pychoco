from __future__ import annotations

from typing import TYPE_CHECKING
from urllib.parse import quote, urlencode

from choco.main import main as choco

if TYPE_CHECKING:
    from click.testing import CliRunner
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
