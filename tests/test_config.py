from __future__ import annotations

from typing import TYPE_CHECKING, Any
from unittest.mock import AsyncMock

from choco.config import write_api_keys
from choco.main import main as choco
import pytest

if TYPE_CHECKING:
    from click.testing import CliRunner
    from pytest_mock.plugin import MockerFixture


def test_config_no_file(runner: CliRunner, mocker: MockerFixture) -> None:
    saved = None

    async def read_error(*_args: Any, **_kwargs: Any) -> None:  # noqa: RUF029
        raise FileNotFoundError

    async def save_config(res: Any, *_args: Any, **_kwargs: Any) -> None:  # noqa: RUF029
        nonlocal saved
        saved = res

    path_mock = mocker.patch('choco.config.AsyncPath')
    path_mock.return_value.read_text = AsyncMock(side_effect=read_error)
    path_mock.return_value.write_text = AsyncMock(side_effect=save_config)
    run = runner.invoke(choco, ('config', 'set', '-n', 'defaultPushSource', '-v', 'http://new'))
    assert run.exit_code == 0
    assert saved is not None
    assert saved == '[pychoco]\ndefaultPushSource = "http://new"\n'


def test_config_existing_file(runner: CliRunner, mocker: MockerFixture) -> None:
    saved = '[pychoco]\ndefaultPushSource = "http://old-value"\notherValue = "something"\n'

    async def read_config(*_args: Any, **_kwargs: Any) -> str:  # noqa: RUF029
        nonlocal saved
        return saved

    async def save_config(res: Any, *_args: Any, **_kwargs: Any) -> None:  # noqa: RUF029
        nonlocal saved
        saved = res

    path_mock = mocker.patch('choco.config.AsyncPath')
    path_mock.return_value.read_text = AsyncMock(side_effect=read_config)
    path_mock.return_value.write_text = AsyncMock(side_effect=save_config)
    run = runner.invoke(choco, ('config', 'set', '-n', 'defaultPushSource', '-v', 'http://new'))
    assert run.exit_code == 0
    assert saved is not None
    assert saved == '[pychoco]\ndefaultPushSource = "http://new"\notherValue = "something"\n'


@pytest.mark.asyncio
async def test_write_api_keys(mocker: MockerFixture) -> None:
    written = None

    async def fake_write(content: str, **_kwargs: Any) -> None:  # noqa: RUF029
        nonlocal written
        written = content

    path_mock = mocker.patch('choco.config.AsyncPath')
    path_mock.return_value.write_text = AsyncMock(side_effect=fake_write)
    await write_api_keys({'https://source': 'my-key'})
    assert written is not None
    assert 'my-key' in written
