from pathlib import Path
from typing import Any, cast
from xml.etree.ElementTree import Element

from pytest_mock.plugin import MockerFixture

from choco.client import ChocolateyClient
from choco.config import read_all
from choco.constants import DEFAULT_CONFIG
from choco.utils import append_dir_to_zip_recursive, parse_int_tag


def test_client_keys_available() -> None:
    client = ChocolateyClient()
    keys = list(client.get_keys_available())
    assert len(keys) == 0
    client.add_key('key1', 'https://new-source')
    keys = list(client.get_keys_available())
    assert len(keys) == 1
    assert keys[0] == 'https://new-source'


def test_client_config_set() -> None:
    client = ChocolateyClient()
    client.config_set('defaultPushSource', 'https://new-source')
    assert client.config['pychoco'].get('defaultPushSource') == 'https://new-source'


def test_config_read_all_defaults(mocker: MockerFixture) -> None:
    read_config_mock = mocker.patch('choco.config.read_config')
    read_config_mock.side_effect = FileNotFoundError()
    read_api_keys_mock = mocker.patch('choco.config.read_api_keys')
    read_api_keys_mock.side_effect = FileNotFoundError()
    config, api_keys = read_all()
    assert config == DEFAULT_CONFIG
    assert api_keys is None


class FakePath:
    def __init__(self, path: str | None = None) -> None:
        self.path = path

    def is_dir(self) -> bool:
        return True if self.path == './a' else False

    def __truediv__(self, x: Any) -> 'FakePath':
        return FakePath(f'{self.path}/{x}')


def test_append_dir_to_zip_recursive(mocker: MockerFixture) -> None:
    listdir_mock = mocker.patch('choco.utils.listdir')
    listdir_mock.return_value = ['a', 'b', 'c', 'xx.nupkg']
    fake_zip = mocker.Mock()
    append_dir_to_zip_recursive(cast(Path, FakePath('.')), fake_zip)
    assert listdir_mock.called


def test_parse_int_tag_bad_value() -> None:
    class FakeTag:
        text = '0zei3023jf'

    assert parse_int_tag(cast(Element, FakeTag())) == 0
