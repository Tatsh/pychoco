from __future__ import annotations

from typing import TYPE_CHECKING, Any
from unittest.mock import AsyncMock

from choco.main import main as choco

if TYPE_CHECKING:
    from click.testing import CliRunner
    from pytest_mock.plugin import MockerFixture


def test_apikey_list(runner: CliRunner, mocker: MockerFixture) -> None:
    mocker.patch('choco.commands.apikey.read_api_keys',
                 new_callable=AsyncMock,
                 return_value=['key1', 'key2'])
    run = runner.invoke(choco, ('apikey', 'list'))
    assert run.exit_code == 0
    assert 'key1' in run.output
    assert 'key2' in run.output


def test_apikey_add_and_list_new_file(runner: CliRunner, mocker: MockerFixture) -> None:
    saved = None

    async def save_key(keys: Any, *_args: Any, **_kwargs: Any) -> None:  # noqa: RUF029
        nonlocal saved
        saved = keys

    read_mock = mocker.patch('choco.commands.apikey.read_api_keys', new_callable=AsyncMock)
    read_mock.side_effect = FileNotFoundError
    mocker.patch('choco.commands.apikey.write_api_keys',
                 new_callable=AsyncMock,
                 side_effect=save_key)
    run = runner.invoke(choco, ('apikey', 'add', '-k', 'key1', '-s', 'https://push-source'))
    assert run.exit_code == 0
    assert saved is not None
    read_mock.side_effect = None
    read_mock.return_value = saved
    run = runner.invoke(choco, ('apikey', 'list'))
    assert 'key1' not in run.stdout


def test_apikey_list_no_file(runner: CliRunner, mocker: MockerFixture) -> None:
    mocker.patch('choco.commands.apikey.read_api_keys',
                 new_callable=AsyncMock,
                 side_effect=FileNotFoundError)
    run = runner.invoke(choco, ('apikey', 'list'))
    assert isinstance(run.exception, SystemExit)
    assert run.exit_code != 0
