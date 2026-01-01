"""Configuration for Pytest."""
from __future__ import annotations

from pathlib import Path
from typing import NoReturn
import os

from click.testing import CliRunner
import pytest

if os.getenv('_PYTEST_RAISE', '0') != '0':  # pragma no cover

    @pytest.hookimpl(tryfirst=True)
    def pytest_exception_interact(call: pytest.CallInfo[None]) -> NoReturn:
        assert call.excinfo is not None
        raise call.excinfo.value

    @pytest.hookimpl(tryfirst=True)
    def pytest_internalerror(excinfo: pytest.ExceptionInfo[BaseException]) -> NoReturn:
        raise excinfo.value


@pytest.fixture
def conftest_dirname() -> str:
    return str(Path(__file__).parent)


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture
def bad_feed(conftest_dirname: str) -> str:
    return Path(f'{conftest_dirname}/feeds/bad.xml').read_text(encoding='utf-8')


@pytest.fixture
def firefox_feed(conftest_dirname: str) -> str:
    return Path(f'{conftest_dirname}/feeds/firefox.xml').read_text(encoding='utf-8')


@pytest.fixture
def firefox_feed_exact(conftest_dirname: str) -> str:
    return Path(f'{conftest_dirname}/feeds/firefox-exact.xml').read_text(encoding='utf-8')


@pytest.fixture
def chrome_all_versions_feed(conftest_dirname: str) -> str:
    return Path(f'{conftest_dirname}/feeds/chrome-all-versions.xml').read_text(encoding='utf-8')


@pytest.fixture
def chrome_all_versions_exact_feed(conftest_dirname: str) -> str:
    return Path(f'{conftest_dirname}/feeds/chrome-all-versions-exact.xml').read_text(
        encoding='utf-8')


@pytest.fixture
def dupe_feed(conftest_dirname: str) -> str:
    return Path(f'{conftest_dirname}/feeds/dupe.xml').read_text(encoding='utf-8')


@pytest.fixture
def logparser_search_error_feed(conftest_dirname: str) -> str:
    return Path(f'{conftest_dirname}/feeds/logparser-search-error.xml').read_text(encoding='utf-8')
