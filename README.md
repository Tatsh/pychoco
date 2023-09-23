# pychoco

[![QA](https://github.com/Tatsh/pychoco/actions/workflows/qa.yml/badge.svg)](https://github.com/Tatsh/pychoco/actions/workflows/qa.yml)
[![Tests](https://github.com/Tatsh/pychoco/actions/workflows/tests.yml/badge.svg)](https://github.com/Tatsh/pychoco/actions/workflows/tests.yml)
[![Coverage Status](https://coveralls.io/repos/github/Tatsh/pychoco/badge.svg?branch=master)](https://coveralls.io/github/Tatsh/pychoco?branch=master)
[![Documentation Status](https://readthedocs.org/projects/chocolatey-choco/badge/?version=latest)](https://chocolatey-choco.readthedocs.io/en/latest/?badge=latest)
![PyPI - Version](https://img.shields.io/pypi/v/chocolatey-choco)
![GitHub tag (with filter)](https://img.shields.io/github/v/tag/Tatsh/pychoco)
![GitHub](https://img.shields.io/github/license/Tatsh/pychoco)
![GitHub commits since latest release (by SemVer including pre-releases)](https://img.shields.io/github/commits-since/Tatsh/pychoco/v0.1.1/master)

Minimal choco command for use on non-Windows platforms.

## Installation

```shell
pip install chocolatey-choco
```

## Command line usage

```plain
Usage: choco [OPTIONS] COMMAND [ARGS]...

  Root command.

Options:
  --help  Show this message and exit.

Commands:
  apikey
  config
  new
  pack
  push
  search
```

`search` is not 1:1 with the official `choco` command in behaviour.
