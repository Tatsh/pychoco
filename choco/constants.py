from pathlib import Path
from typing import Final

from xdg.BaseDirectory import xdg_config_home

__all__ = ('CHOCOLATEY_UNINSTALL_PS1', 'CONTENT_TYPES_XML', 'NUSPEC_FIELD_AUTHORS',
           'NUSPEC_FIELD_DESCRIPTION', 'NUSPEC_FIELD_ID', 'NUSPEC_FIELD_TAGS',
           'NUSPEC_FIELD_VERSION', 'PYCHOCO_API_KEYS_TOML_PATH', 'PYCHOCO_TOML_PATH',
           'VALID_NAME_RE')

NUSPEC_XSD_URI_PREFIX: Final[str] = '{http://schemas.microsoft.com/packaging/2010/07/nuspec.xsd}'
NUSPEC_FIELD_AUTHORS: Final[str] = f'{NUSPEC_XSD_URI_PREFIX}authors'
NUSPEC_FIELD_DESCRIPTION: Final[str] = f'{NUSPEC_XSD_URI_PREFIX}description'
NUSPEC_FIELD_ID: Final[str] = f'{NUSPEC_XSD_URI_PREFIX}id'
NUSPEC_FIELD_TAGS: Final[str] = f'{NUSPEC_XSD_URI_PREFIX}tags'
NUSPEC_FIELD_VERSION: Final[str] = f'{NUSPEC_XSD_URI_PREFIX}version'

#: Uninstall PowerShell template.
CHOCOLATEY_UNINSTALL_PS1: Final[str] = '''$$ErrorActionPreference = 'Stop'
[array]$$key = Get-UninstallRegistryKey -SoftwareName "PACKAGE_NAME"
if ($$key.Count -eq 1) {
  $$key | ForEach-Object {
    $$packageArgs = @{
      packageName = $$env:ChocolateyPackageName
      fileType    = 'exe'
      silentArgs  = '/S'
      file        = ($$_.UninstallString -split '"')[1]
    }
    Uninstall-ChocolateyPackage @packageArgs
  }
}
elseif ($$key.Count -eq 0) {
  Write-Warning "$$packageName has already been uninstalled by other means."
}
elseif ($$key.Count -gt 1) {
  Write-Warning "$$($$key.Count) matches found!"
  Write-Warning "To prevent accidental data loss, no programs will be uninstalled."
  Write-Warning "Please alert package maintainer the following keys were matched:"
  $$key | ForEach-Object { Write-Warning "- $$($$_.DisplayName)" }
}\n'''
#: Used in creating the ``[Content-Types].xml`` file.
CONTENT_TYPES_XML: Final[str] = '''<?xml version="1.0" encoding="utf-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml" />
  <Default Extension="psmdcp" ContentType="application/vnd.openxmlformats-package.core-properties+xml" />
  <Default Extension="ps1" ContentType="application/octet" />
  <Default Extension="nuspec" ContentType="application/octet" />
</Types>\n'''
#: Where pychoco's main configuration file is by default.
PYCHOCO_TOML_PATH: Final[Path] = Path(xdg_config_home) / 'pychoco/config.toml'
#: Where pychoco's API key list is stored.
PYCHOCO_API_KEYS_TOML_PATH: Final[Path] = Path(xdg_config_home) / 'pychoco/api.toml'
#: Valid name for a package regular expression.
VALID_NAME_RE: Final[str] = r'^[0-9a-z-]+(\.(commandline|install|portable))?$'
