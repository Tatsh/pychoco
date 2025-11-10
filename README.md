# chocolatey-choco

[![Python versions](https://img.shields.io/pypi/pyversions/chocolatey-choco.svg?color=blue&logo=python&logoColor=white)](https://www.python.org/)
[![PyPI - Version](https://img.shields.io/pypi/v/chocolatey-choco)](https://pypi.org/project/chocolatey-choco/)
[![GitHub tag (with filter)](https://img.shields.io/github/v/tag/Tatsh/pychoco)](https://github.com/Tatsh/pychoco/tags)
[![License](https://img.shields.io/github/license/Tatsh/pychoco)](https://github.com/Tatsh/pychoco/blob/master/LICENSE.txt)
[![GitHub commits since latest release (by SemVer including pre-releases)](https://img.shields.io/github/commits-since/Tatsh/pychoco/v0.1.4/master)](https://github.com/Tatsh/pychoco/compare/v0.1.4...master)
[![CodeQL](https://github.com/Tatsh/pychoco/actions/workflows/codeql.yml/badge.svg)](https://github.com/Tatsh/pychoco/actions/workflows/codeql.yml)
[![QA](https://github.com/Tatsh/pychoco/actions/workflows/qa.yml/badge.svg)](https://github.com/Tatsh/pychoco/actions/workflows/qa.yml)
[![Tests](https://github.com/Tatsh/pychoco/actions/workflows/tests.yml/badge.svg)](https://github.com/Tatsh/pychoco/actions/workflows/tests.yml)
[![Coverage Status](https://coveralls.io/repos/github/Tatsh/pychoco/badge.svg?branch=master)](https://coveralls.io/github/Tatsh/pychoco?branch=master)
[![Documentation Status](https://readthedocs.org/projects/chocolatey-choco/badge/?version=latest)](https://chocolatey-choco.readthedocs.org/?badge=latest)
[![mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![pydocstyle](https://img.shields.io/badge/pydocstyle-enabled-AD4CD3)](http://www.pydocstyle.org/en/stable/)
[![pytest](https://img.shields.io/badge/pytest-zz?logo=Pytest&labelColor=black&color=black)](https://docs.pytest.org/en/stable/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Downloads](https://static.pepy.tech/badge/pychoco/month)](https://pepy.tech/project/pychoco)
[![Stargazers](https://img.shields.io/github/stars/Tatsh/pychoco?logo=github&style=flat)](https://github.com/Tatsh/pychoco/stargazers)

[![@Tatsh](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fpublic.api.bsky.app%2Fxrpc%2Fapp.bsky.actor.getProfile%2F%3Factor%3Ddid%3Aplc%3Auq42idtvuccnmtl57nsucz72%26query%3D%24.followersCount%26style%3Dsocial%26logo%3Dbluesky%26label%3DFollow%2520%40Tatsh&query=%24.followersCount&style=social&logo=bluesky&label=Follow%20%40Tatsh)](https://bsky.app/profile/Tatsh.bsky.social)
[![Mastodon Follow](https://img.shields.io/mastodon/follow/109370961877277568?domain=hostux.social&style=social)](https://hostux.social/@Tatsh)

Minimal `choco` command for use on non-Windows platforms.

## Installation

### Poetry

```shell
poetry add chocolatey-choco
```

### Pip

```shell
pip install chocolatey-choco
```

## Usage

```plain
Usage: choco [OPTIONS] COMMAND [ARGS]...

  Minimal choco command.

Options:
  --help  Show this message and exit.

Commands:
  apikey  Manage API keys.
  config  Manage configuration.
  new     Create a new package.
  pack    Create a package file for distribution.
  push    Push a package to a source.
  search  Search a source.
```
