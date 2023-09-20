from urllib.parse import quote, urlencode

from click.testing import CliRunner
import requests_mock as req_mock

from choco.main import main as choco

FEED_HEADER = '''<?xml version="1.0" encoding="utf-8" standalone="yes"?>
<feed xml:base="http://community.chocolatey.org/api/v2/"
    xmlns:d="http://schemas.microsoft.com/ado/2007/08/dataservices"
    xmlns:m="http://schemas.microsoft.com/ado/2007/08/dataservices/metadata"
    xmlns="http://www.w3.org/2005/Atom">
  <title type="text">Packages</title>
  <id>http://community.chocolatey.org/api/v2/Packages</id>
  <updated>2023-09-20T15:12:14Z</updated>
  <link rel="self" title="Packages" href="Packages" />'''
FEED_FOOTER = '</feed>'
BAD_ENTRY_OUTPUT = '''no title? no version?
 Title: no title? | Published: n/a
 Package approved as a trusted package on n/a.
 Package testing status: n/a on n/a.
 Number of Downloads: n/a | Downloads for this version: n/a
 Package url n/a
 Chocolatey Package Source: n/a
 Tags: n/a
 Software Site: n/a
 Software License: n/a
 Documentation: n/a
 Summary: n/a
 Description: n/a
 Release Notes: n/a'''


def test_search_no_options_bad_entry(runner: CliRunner, requests_mock: req_mock.Mocker) -> None:
    id_field = "<id>http://somehost/Packages(Id='somename',Version='2.0.0')</id>"
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
    requests_mock.get(f'https://somehost/Packages()?{qs}',
                      text=f'''{FEED_HEADER}<entry>
    {id_field}
</entry>{FEED_FOOTER}''')
    run = runner.invoke(choco, ('search', '-s', 'https://somehost', '-d', terms))
    for line in BAD_ENTRY_OUTPUT.splitlines():
        assert line in run.stdout
    assert FEED_HEADER in run.stdout
    assert id_field in run.stdout
    assert run.exit_code == 0
