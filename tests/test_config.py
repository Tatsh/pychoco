from __future__ import annotations

from typing import TYPE_CHECKING, Any

from choco.main import main as choco

if TYPE_CHECKING:
    from click.testing import CliRunner
    from pytest_mock.plugin import MockerFixture


def test_config_no_file(runner: CliRunner, mocker: MockerFixture) -> None:
    saved = None

    def read_error(encoding: str | None = None) -> None:
        raise FileNotFoundError

    def save_config(res: Any, encoding: str | None = None) -> None:
        nonlocal saved
        saved = res

    path_mock = mocker.patch('choco.config.Path')
    path_mock.return_value.read_text.side_effect = read_error
    path_mock.return_value.write_text.side_effect = save_config
    run = runner.invoke(choco, ('config', 'set', '-n', 'defaultPushSource', '-v', 'http://new'))
    assert run.exit_code == 0
    assert saved is not None
    assert saved == '[pychoco]\ndefaultPushSource = "http://new"\n'


def test_config_existing_file(runner: CliRunner, mocker: MockerFixture) -> None:
    saved = '[pychoco]\ndefaultPushSource = "http://old-value"\notherValue = "something"\n'

    def read_config(encoding: str | None = None) -> str:
        nonlocal saved
        return saved

    def save_config(res: Any, encoding: str | None = None) -> None:
        nonlocal saved
        saved = res

    path_mock = mocker.patch('choco.config.Path')
    path_mock.return_value.read_text.side_effect = read_config
    path_mock.return_value.write_text.side_effect = save_config
    run = runner.invoke(choco, ('config', 'set', '-n', 'defaultPushSource', '-v', 'http://new'))
    assert run.exit_code == 0
    assert saved is not None
    assert saved == '[pychoco]\ndefaultPushSource = "http://new"\notherValue = "something"\n'
