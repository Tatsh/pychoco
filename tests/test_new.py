from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import AsyncMock

from choco.main import main as choco

if TYPE_CHECKING:
    from click.testing import CliRunner
    from pytest_mock.plugin import MockerFixture


def test_new(runner: CliRunner, mocker: MockerFixture) -> None:
    path_mock = mocker.patch('choco.packaging.AsyncPath')
    path_mock.return_value.exists = AsyncMock(return_value=False)
    path_mock.return_value.mkdir = AsyncMock()
    path_mock.return_value.__truediv__ = lambda _self, _x: path_mock.return_value
    path_mock.return_value.write_text = AsyncMock()
    run = runner.invoke(choco, ('new', 'okay-name'))
    assert run.exit_code == 0
    assert path_mock.return_value.write_text.call_count == 3


def test_new_file_exists(runner: CliRunner, mocker: MockerFixture) -> None:
    path_mock = mocker.patch('choco.packaging.AsyncPath')
    path_mock.return_value.exists = AsyncMock(return_value=True)
    run = runner.invoke(choco, ('new', 'okay-name.install'))
    assert isinstance(run.exception, SystemExit)
    assert run.exit_code != 0


def test_new_bad_name(runner: CliRunner) -> None:
    run = runner.invoke(choco, ('new', 'bad_name'))
    assert isinstance(run.exception, SystemExit)
    assert run.exit_code != 0
