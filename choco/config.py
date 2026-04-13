"""Persistent configuration."""
from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, cast

import tomlkit

from .constants import DEFAULT_CONFIG, PYCHOCO_API_KEYS_TOML_PATH, PYCHOCO_TOML_PATH

if TYPE_CHECKING:
    from .typing import Config

__all__ = ('read_all', 'read_api_keys', 'read_config', 'write_api_keys', 'write_config')


def read_api_keys(path: Path | str | None = None) -> dict[str, str]:
    """
    Read API keys stored in given path or the default path.

    Parameters
    ----------
    path : Path | str | None
        Path to the API keys file.

    Returns
    -------
    dict[str, str]
    """
    return cast('dict[str, str]',
                tomlkit.loads(Path(path or PYCHOCO_API_KEYS_TOML_PATH).read_text(encoding='utf-8')))


def write_api_keys(api_keys: dict[str, str], path: Path | str | None = None) -> None:
    """
    Write API keys dictionary to the given path or the default path.

    Parameters
    ----------
    api_keys : dict[str, str]
        Mapping of source URLs to API keys.
    path : Path | str | None
        Path to the API keys file.
    """
    Path(path or PYCHOCO_API_KEYS_TOML_PATH).write_text(tomlkit.dumps(api_keys), encoding='utf-8')


def read_config(path: Path | str | None = None) -> Config:
    """
    Read configuration from the given path or the default path.

    Parameters
    ----------
    path : Path | str | None
        Path to the configuration file.

    Returns
    -------
    Config
    """
    return cast('Config', tomlkit.loads(
        Path(path or PYCHOCO_TOML_PATH).read_text(encoding='utf-8')))


def write_config(config: Config, path: Path | str | None = None) -> None:
    """
    Write configuration to the given path or the default path.

    Parameters
    ----------
    config : Config
        Configuration dictionary to write.
    path : Path | str | None
        Path to the configuration file.
    """
    Path(path or PYCHOCO_TOML_PATH).write_text(tomlkit.dumps(config), encoding='utf-8')


def read_all(config_path: Path | str | None = None,
             api_keys_path: Path | str | None = None) -> tuple[Config, dict[str, str] | None]:
    """
    Read both configuration and API keys from the specified paths or defaults.

    Parameters
    ----------
    config_path : Path | str | None
        Path to the configuration file.
    api_keys_path : Path | str | None
        Path to the API keys file.

    Returns
    -------
    tuple[Config, dict[str, str] | None]
    """
    try:
        config = read_config(config_path)
    except FileNotFoundError:
        config = DEFAULT_CONFIG
    try:
        api_keys = read_api_keys(api_keys_path)
    except FileNotFoundError:
        api_keys = None
    return config, api_keys
