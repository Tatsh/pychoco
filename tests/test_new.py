from __future__ import annotations

from typing import TYPE_CHECKING

from choco.constants import CHOCOLATEY_UNINSTALL_PS1
from choco.main import main as choco

if TYPE_CHECKING:
    from click.testing import CliRunner
    from pytest_mock.plugin import MockerFixture


def test_new(runner: CliRunner, mocker: MockerFixture) -> None:
    path_mock = mocker.patch('choco.packaging.Path')
    path_mock.return_value.exists.return_value = False
    run = runner.invoke(choco, ('new', 'okay-name'))
    assert run.exit_code == 0
    assert path_mock.call_count == 5
    path_mock.assert_any_call('okay-name')
    path_mock.return_value.open.return_value.__enter__.return_value.write.assert_called_with(
        CHOCOLATEY_UNINSTALL_PS1)


def test_new_file_exists(runner: CliRunner, mocker: MockerFixture) -> None:
    path_mock = mocker.patch('choco.packaging.Path')
    path_mock.return_value.exists.return_value = True
    run = runner.invoke(choco, ('new', 'okay-name.install'))
    assert isinstance(run.exception, SystemExit)
    assert run.exit_code != 0


def test_new_bad_name(runner: CliRunner, mocker: MockerFixture) -> None:
    run = runner.invoke(choco, ('new', 'bad_name'))
    assert isinstance(run.exception, SystemExit)
    assert run.exit_code != 0
