from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

from choco.client import ChocolateyClient
from choco.config import read_all
from choco.constants import DEFAULT_CONFIG
from choco.utils import append_dir_to_zip_recursive, parse_int_tag

if TYPE_CHECKING:
    from collections.abc import Iterator
    from xml.etree.ElementTree import Element  # noqa: S405

    from pytest_mock.plugin import MockerFixture


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
        self.iterdir_called = False

    def is_dir(self) -> bool:
        return self.path == './a'

    def __truediv__(self, x: Any) -> FakePath:
        return FakePath(f'{self.path}/{x}')

    def iterdir(self) -> Iterator[Path]:
        self.iterdir_called = True
        yield from (Path(x) for x in ('a', 'b', 'c', 'xx.nupkg'))


def test_append_dir_to_zip_recursive(mocker: MockerFixture) -> None:
    fake_zip = mocker.Mock()
    fake_path = FakePath('.')
    append_dir_to_zip_recursive(cast('Path', fake_path), fake_zip)
    assert fake_path.iterdir_called


def test_parse_int_tag_bad_value() -> None:
    class FakeTag:
        text = '0zei3023jf'

    assert parse_int_tag(cast('Element', FakeTag())) == 0
