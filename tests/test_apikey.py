from typing import Any

from click.testing import CliRunner
from pytest_mock.plugin import MockerFixture

from choco.main import main as choco


def test_apikey_add_and_list_new_file(runner: CliRunner, mocker: MockerFixture) -> None:
    path_mock = mocker.patch('choco.config.Path')
    saved = None

    def save_key(res: Any) -> None:
        nonlocal saved
        saved = res

    def load_key_error() -> None:
        raise FileNotFoundError()

    def load_key() -> Any:
        return saved

    path_mock.return_value.write_text.side_effect = save_key
    path_mock.return_value.read_text.side_effect = load_key_error
    run = runner.invoke(choco, ('apikey', 'add', '-k', 'key1', '-s', 'https://push-source'))
    assert run.exit_code == 0
    assert saved is not None
    path_mock.return_value.read_text.side_effect = load_key
    run = runner.invoke(choco, ('apikey', 'list'))
    assert run.stdout.splitlines()[0] == 'https://push-source'
    assert 'key1' not in run.stdout


def test_apikey_list_no_file(runner: CliRunner, mocker: MockerFixture) -> None:
    path_mock = mocker.patch('choco.config.Path')

    def load_key_error() -> None:
        raise FileNotFoundError()

    path_mock.return_value.read_text.side_effect = load_key_error
    run = runner.invoke(choco, ('apikey', 'list'))
    assert isinstance(run.exception, SystemExit)
    assert run.exit_code != 0
