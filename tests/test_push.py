from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING
from unittest.mock import AsyncMock

from choco.main import main as choco

if TYPE_CHECKING:
    from click.testing import CliRunner
    from niquests_mock import MockRouter
    from pytest_mock.plugin import MockerFixture


def test_push_error(runner: CliRunner, mocker: MockerFixture, niquests_mock: MockRouter) -> None:
    saved = '[pychoco]\ndefaultPushSource = "http://old-value"\n'
    path_mock = mocker.patch('choco.config.AsyncPath')
    path_mock.return_value.read_text = AsyncMock(return_value=saved)
    niquests_mock.put('http://old-value/api/v2/package/').respond(status_code=400)
    with runner.isolated_filesystem():
        Path('okay-name-1.0.0.nuget').write_text('', encoding='utf-8')
        run = runner.invoke(choco, ('push', 'okay-name-1.0.0.nuget'))
    assert isinstance(run.exception, SystemExit)
    assert run.exit_code != 0


def test_push_normal(runner: CliRunner, mocker: MockerFixture, niquests_mock: MockRouter) -> None:
    saved = '[pychoco]\ndefaultPushSource = "http://old-value"\n'
    path_mock = mocker.patch('choco.config.AsyncPath')
    path_mock.return_value.read_text = AsyncMock(return_value=saved)
    niquests_mock.put('http://old-value/api/v2/package/').respond(status_code=201)
    with runner.isolated_filesystem():
        Path('okay-name-1.0.0.nuget').write_text('', encoding='utf-8')
        run = runner.invoke(choco, ('push', 'okay-name-1.0.0.nuget'))
    assert run.exit_code == 0
