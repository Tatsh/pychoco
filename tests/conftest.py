"""Configuration for Pytest."""
from os.path import dirname
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


@pytest.fixture()
def conftest_dirname() -> str:
    return dirname(__file__)


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def bad_feed(conftest_dirname: str) -> str:
    with open(f'{conftest_dirname}/feeds/bad.xml') as f:
        return f.read()


@pytest.fixture()
def firefox_feed(conftest_dirname: str) -> str:
    with open(f'{conftest_dirname}/feeds/firefox.xml') as f:
        return f.read()


@pytest.fixture()
def firefox_feed_exact(conftest_dirname: str) -> str:
    with open(f'{conftest_dirname}/feeds/firefox-exact.xml') as f:
        return f.read()


@pytest.fixture()
def chrome_all_versions_feed(conftest_dirname: str) -> str:
    with open(f'{conftest_dirname}/feeds/chrome-all-versions.xml') as f:
        return f.read()


@pytest.fixture()
def chrome_all_versions_exact_feed(conftest_dirname: str) -> str:
    with open(f'{conftest_dirname}/feeds/chrome-all-versions-exact.xml') as f:
        return f.read()


@pytest.fixture()
def dupe_feed(conftest_dirname: str) -> str:
    with open(f'{conftest_dirname}/feeds/dupe.xml') as f:
        return f.read()
