from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from choco.main import main as choco

if TYPE_CHECKING:
    from click.testing import CliRunner
    from pytest_mock.plugin import MockerFixture
    import requests_mock as req_mock


def test_push_error(
    runner: CliRunner,
    mocker: MockerFixture,
    requests_mock: req_mock.Mocker,
) -> None:
    saved = '[pychoco]\ndefaultPushSource = "http://old-value"\n'

    def read_config(encoding: str | None = None) -> str:
        nonlocal saved
        return saved

    path_mock = mocker.patch('choco.config.Path')
    path_mock.return_value.read_text.side_effect = read_config
    requests_mock.put('http://old-value/api/v2/package/', status_code=400)
    with runner.isolated_filesystem():
        with Path('okay-name-1.0.0.nuget').open('w', encoding='utf-8') as f:
            f.write('')
        run = runner.invoke(choco, ('push', 'okay-name-1.0.0.nuget'))
    assert isinstance(run.exception, SystemExit)
    assert run.exit_code != 0


def test_push_normal(
    runner: CliRunner,
    mocker: MockerFixture,
    requests_mock: req_mock.Mocker,
) -> None:
    saved = '[pychoco]\ndefaultPushSource = "http://old-value"\n'

    def read_config(encoding: str | None = None) -> str:
        nonlocal saved
        return saved

    path_mock = mocker.patch('choco.config.Path')
    path_mock.return_value.read_text.side_effect = read_config
    requests_mock.put('http://old-value/api/v2/package/', status_code=201)
    with runner.isolated_filesystem():
        with Path('okay-name-1.0.0.nuget').open('w', encoding='utf-8') as f:
            f.write('')
        run = runner.invoke(choco, ('push', 'okay-name-1.0.0.nuget'))
    assert run.exit_code == 0
