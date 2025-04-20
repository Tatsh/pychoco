from __future__ import annotations

from typing import TYPE_CHECKING, Any

from choco.main import main as choco

if TYPE_CHECKING:
    from click.testing import CliRunner
    from pytest_mock.plugin import MockerFixture


def test_apikey_list(runner: CliRunner, mocker: MockerFixture) -> None:
    mocker.patch('choco.commands.apikey.read_api_keys', return_value=['key1', 'key2'])
    run = runner.invoke(choco, ('apikey', 'list'))
    assert run.exit_code == 0
    assert 'key1' in run.output
    assert 'key2' in run.output


def test_apikey_add_and_list_new_file(runner: CliRunner, mocker: MockerFixture) -> None:
    path_mock = mocker.patch('choco.config.Path')
    saved = None

    def save_key(res: Any, encoding: str | None = None) -> None:
        nonlocal saved
        saved = res

    def load_key_error(encoding: str | None = None) -> None:
        raise FileNotFoundError

    def load_key() -> Any:
        return saved

    path_mock.return_value.write_text.side_effect = save_key
    path_mock.return_value.read_text.side_effect = load_key_error
    run = runner.invoke(choco, ('apikey', 'add', '-k', 'key1', '-s', 'https://push-source'))
    assert run.exit_code == 0
    assert saved is not None
    path_mock.return_value.read_text.side_effect = load_key
    run = runner.invoke(choco, ('apikey', 'list'))
    assert 'key1' not in run.stdout


def test_apikey_list_no_file(runner: CliRunner, mocker: MockerFixture) -> None:
    path_mock = mocker.patch('choco.config.Path')

    def load_key_error(encoding: str | None = None) -> None:
        raise FileNotFoundError

    path_mock.return_value.read_text.side_effect = load_key_error
    run = runner.invoke(choco, ('apikey', 'list'))
    assert isinstance(run.exception, SystemExit)
    assert run.exit_code != 0
