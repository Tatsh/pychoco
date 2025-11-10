from __future__ import annotations

from typing import TYPE_CHECKING, cast

from choco.client import ChocolateyClient

if TYPE_CHECKING:
    from choco.typing import SearchResult
    from pytest_mock import MockerFixture


def test_client_exact(mocker: MockerFixture) -> None:
    """Test the id_only option."""
    config = mocker.MagicMock()
    response = mocker.MagicMock()
    request = mocker.patch('choco.client.requests.Request')
    session = mocker.patch('choco.client.requests.Session')
    session.send.return_value = response
    entry = mocker.MagicMock()
    tag = mocker.MagicMock()
    tag.text = 'chrome'
    entry.find.return_value = tag
    mocker.patch('choco.client.parse_xml').return_value.findall.return_value = [entry]
    mocker.patch('choco.client.entry_to_search_result').return_value = {'id': 'chrome'}

    client = ChocolateyClient(config)
    assert list(client.search('test', exact=True)) == cast('list[SearchResult]', [{'id': 'chrome'}])
    request.assert_called_once_with('GET',
                                    mocker.ANY,
                                    params={
                                        '$filter': "(tolower(Id) eq 'test') and IsLatestVersion",
                                    })


def test_client_by_id_only(mocker: MockerFixture) -> None:
    """Test the id_only option."""
    config = mocker.MagicMock()
    response = mocker.MagicMock()
    request = mocker.patch('choco.client.requests.Request')
    session = mocker.patch('choco.client.requests.Session')
    session.send.return_value = response
    entry = mocker.MagicMock()
    tag = mocker.MagicMock()
    tag.text = 'chrome'
    entry.find.return_value = tag
    mocker.patch('choco.client.parse_xml').return_value.findall.return_value = [entry]
    mocker.patch('choco.client.entry_to_search_result').return_value = {'id': 'chrome'}

    client = ChocolateyClient(config)
    assert list(client.search('test', by_id_only=True)) == cast('list[SearchResult]', [{
        'id': 'chrome'
    }])
    request.assert_called_once_with(
        'GET',
        mocker.ANY,
        params={
            '$filter': "(substringof('test',tolower(Id))) and IsLatestVersion",
            '$orderby': 'Id',
            '$skip': '0',
            '$top': '30',
            'includePrerelease': 'false',
            'searchTerm': "'test'",
            'targetFramework': "''",
        })


def test_client_by_id_starts_with(mocker: MockerFixture) -> None:
    """Test the id_only option."""
    config = mocker.MagicMock()
    response = mocker.MagicMock()
    request = mocker.patch('choco.client.requests.Request')
    session = mocker.patch('choco.client.requests.Session')
    session.send.return_value = response
    entry = mocker.MagicMock()
    tag = mocker.MagicMock()
    tag.text = 'chrome'
    entry.find.return_value = tag
    mocker.patch('choco.client.parse_xml').return_value.findall.return_value = [entry]
    mocker.patch('choco.client.entry_to_search_result').return_value = {'id': 'chrome'}

    client = ChocolateyClient(config)
    assert list(client.search('test', id_starts_with=True)) == cast('list[SearchResult]', [{
        'id': 'chrome'
    }])
    request.assert_called_once_with(
        'GET',
        mocker.ANY,
        params={
            '$filter': "(startswith(tolower(Id),'test')) and IsLatestVersion",
            '$orderby': 'Id',
            '$skip': '0',
            '$top': '30',
            'includePrerelease': 'false',
            'searchTerm': "'test'",
        })


def test_client_by_tag_only(mocker: MockerFixture) -> None:
    """Test the id_only option."""
    config = mocker.MagicMock()
    response = mocker.MagicMock()
    request = mocker.patch('choco.client.requests.Request')
    session = mocker.patch('choco.client.requests.Session')
    session.send.return_value = response
    entry = mocker.MagicMock()
    tag = mocker.MagicMock()
    tag.text = 'chrome'
    entry.find.return_value = tag
    mocker.patch('choco.client.parse_xml').return_value.findall.return_value = [entry]
    mocker.patch('choco.client.entry_to_search_result').return_value = {'id': 'chrome'}

    client = ChocolateyClient(config)
    assert list(client.search('test', by_tag_only=True)) == cast('list[SearchResult]', [{
        'id': 'chrome'
    }])
    request.assert_called_once_with('GET',
                                    mocker.ANY,
                                    params={
                                        '$filter': "(substringof('test',Tags)) and IsLatestVersion",
                                        '$orderby': 'Id',
                                        '$skip': '0',
                                        '$top': '30',
                                        'includePrerelease': 'false',
                                        'searchTerm': "'test'",
                                        'targetFramework': "''",
                                    })
