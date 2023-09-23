"""Constants."""
from pathlib import Path
from typing import Final

from xdg.BaseDirectory import xdg_config_home

from .typing import Config

__all__ = ('CHOCOLATEY_UNINSTALL_PS1', 'CONTENT_TYPES_XML', 'FEED_AUTHOR_TAG', 'FEED_ENTRY_TAG',
           'FEED_ID_TAG', 'FEED_NAMESPACES', 'FEED_SUMMARY_TAG', 'FEED_TITLE_TAG',
           'FEED_UPDATED_TAG', 'METADATA_DESCRIPTION_TAG', 'METADATA_DOCS_URL_TAG',
           'METADATA_DOWNLOAD_COUNT_TAG', 'METADATA_GALLERY_DETAILS_URL_TAG',
           'METADATA_IS_APPROVED_TAG', 'METADATA_IS_DOWNLOAD_CACHE_AVAILABLE_TAG',
           'METADATA_LICENSE_URL_TAG', 'METADATA_PACKAGE_APPROVED_DATE_TAG',
           'METADATA_PACKAGE_SOURCE_URL_TAG', 'METADATA_PACKAGE_STATUS_TAG',
           'METADATA_PACKAGE_TEST_RESULT_STATUS_DATE_TAG',
           'METADATA_PACKAGE_TEST_RESULT_STATUS_TAG', 'METADATA_PROJECT_URL_TAG',
           'METADATA_PUBLISHED_TAG', 'METADATA_RELEASE_NOTES_TAG', 'METADATA_SUMMARY_TAG',
           'METADATA_TAGS_TAG', 'METADATA_VERSION_DOWNLOAD_COUNT_TAG', 'METADATA_VERSION_TAG',
           'NUSPEC_FIELD_AUTHORS', 'NUSPEC_FIELD_DESCRIPTION', 'NUSPEC_FIELD_ID',
           'NUSPEC_FIELD_TAGS', 'NUSPEC_FIELD_VERSION', 'PYCHOCO_API_KEYS_TOML_PATH',
           'PYCHOCO_TOML_PATH', 'VALID_NAME_RE')

FEED_NAMESPACES: Final[dict[str, str]] = {
    '': 'http://www.w3.org/2005/Atom',
    'd': 'http://schemas.microsoft.com/ado/2007/08/dataservices',
    'm': 'http://schemas.microsoft.com/ado/2007/08/dataservices/metadata'
}
"""Namespaces used in parsing package feeds.

:meta hide-value:"""
FEED_AUTHOR_TAG: Final[str] = 'author'
"""Feed ``author`` tag.

:meta hide-value:"""
FEED_ENTRY_TAG: Final[str] = 'entry'
"""Feed ``entry`` tag.

:meta hide-value:"""
FEED_ID_TAG: Final[str] = 'id'
"""Feed ``id`` tag.

:meta hide-value:"""
FEED_PROPERTIES_TAG: Final[str] = 'm:properties'
"""Feed ``m:properties`` tag.

:meta hide-value:"""
FEED_SUMMARY_TAG: Final[str] = 'summary'
"""Feed ``summary`` tag.

:meta hide-value:"""
FEED_TITLE_TAG: Final[str] = 'title'
"""Feed ``title`` tag.

:meta hide-value:"""
FEED_UPDATED_TAG: Final[str] = 'updated'
"""Feed ``updated`` tag.

:meta hide-value:"""
METADATA_DESCRIPTION_TAG: Final[str] = 'd:Description'
"""Feed ``d:Description`` tag.

:meta hide-value:"""
METADATA_DOCS_URL_TAG: Final[str] = 'd:DocsUrl'
"""Feed ``d:DocsUrl`` tag.

:meta hide-value:"""
METADATA_DOWNLOAD_COUNT_TAG: Final[str] = 'd:DownloadCount'
"""Feed ``d:DownloadCount`` tag.

:meta hide-value:"""
METADATA_GALLERY_DETAILS_URL_TAG: Final[str] = 'd:GalleryDetailsUrl'
"""Feed ``d:GalleryDetailsUrl`` tag.

:meta hide-value:"""
METADATA_IS_APPROVED_TAG: Final[str] = 'd:IsApproved'
"""Feed ``d:IsApproved`` tag.

:meta hide-value:"""
METADATA_IS_DOWNLOAD_CACHE_AVAILABLE_TAG: Final[str] = 'd:IsDownloadCacheAvailable'
"""Feed ``d:IsDownloadCacheAvailable`` tag.

:meta hide-value:"""
METADATA_LICENSE_URL_TAG: Final[str] = 'd:LicenseUrl'
"""Feed ``d:LicenseUrl`` tag.

:meta hide-value:"""
METADATA_PACKAGE_APPROVED_DATE_TAG: Final[str] = 'd:PackageApprovedDate'
"""Feed ``d:PackageApprovedDate`` tag.

:meta hide-value:"""
METADATA_PACKAGE_SOURCE_URL_TAG: Final[str] = 'd:PackageSourceUrl'
"""Feed ``d:PackageSourceUrl`` tag.

:meta hide-value:"""
METADATA_PACKAGE_STATUS_TAG: Final[str] = 'd:PackageStatus'
"""Feed ``d:PackageStatus`` tag.

:meta hide-value:"""
METADATA_PACKAGE_TEST_RESULT_STATUS_DATE_TAG = 'd:PackageTestResultStatusDate'
"""Feed ``d:PackageTestResultStatusDate`` tag.

:meta hide-value:"""
METADATA_PACKAGE_TEST_RESULT_STATUS_TAG: Final[str] = 'd:PackageTestResultStatus'
"""Feed ``d:PackageTestResultStatus`` tag.

:meta hide-value:"""
METADATA_PROJECT_URL_TAG: Final[str] = 'd:ProjectUrl'
"""Feed ``d:ProjectUrl`` tag.

:meta hide-value:"""
METADATA_PUBLISHED_TAG: Final[str] = 'd:Published'
"""Feed ``d:Published`` tag.

:meta hide-value:"""
METADATA_RELEASE_NOTES_TAG: Final[str] = 'd:ReleaseNotes'
"""Feed ``d:ReleaseNotes`` tag.

:meta hide-value:"""
METADATA_SUMMARY_TAG: Final[str] = 'd:Summary'
"""Feed ``d:Summary`` tag.

:meta hide-value:"""
METADATA_TAGS_TAG: Final[str] = 'd:Tags'
"""Feed ``d:Tags`` tag.

:meta hide-value:"""
METADATA_VERSION_DOWNLOAD_COUNT_TAG: Final[str] = 'd:VersionDownloadCount'
"""Feed ``d:VersionDownloadCount`` tag.

:meta hide-value:"""
METADATA_VERSION_TAG: Final[str] = 'd:Version'
"""Feed ``d:Version`` tag.

:meta hide-value:"""

NUSPEC_XSD_URI_PREFIX: Final[str] = '{http://schemas.microsoft.com/packaging/2010/07/nuspec.xsd}'
NUSPEC_FIELD_AUTHORS: Final[str] = f'{NUSPEC_XSD_URI_PREFIX}authors'
"""Nuspec authors tag.

:meta hide-value:"""
NUSPEC_FIELD_DESCRIPTION: Final[str] = f'{NUSPEC_XSD_URI_PREFIX}description'
"""Nuspec description tag.

:meta hide-value:"""
NUSPEC_FIELD_ID: Final[str] = f'{NUSPEC_XSD_URI_PREFIX}id'
"""Nuspec id tag.

:meta hide-value:"""
NUSPEC_FIELD_TAGS: Final[str] = f'{NUSPEC_XSD_URI_PREFIX}tags'
"""Nuspec tags tag.

:meta hide-value:"""
NUSPEC_FIELD_VERSION: Final[str] = f'{NUSPEC_XSD_URI_PREFIX}version'
"""Nuspec version tag.

:meta hide-value:"""
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
"""Uninstall PowerShell template.

:meta hide-value:"""
CONTENT_TYPES_XML: Final[str] = '''<?xml version="1.0" encoding="utf-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels"
    ContentType="application/vnd.openxmlformats-package.relationships+xml" />
  <Default Extension="psmdcp"
    ContentType="application/vnd.openxmlformats-package.core-properties+xml" />
  <Default Extension="ps1" ContentType="application/octet" />
  <Default Extension="nuspec" ContentType="application/octet" />
</Types>\n'''
"""Used in creating the ``[Content_Types].xml`` file.

:meta hide-value:"""
PYCHOCO_TOML_PATH: Final[Path] = Path(xdg_config_home) / 'pychoco/config.toml'
"""Where pychoco's main configuration file is by default.

:meta hide-value:"""
PYCHOCO_API_KEYS_TOML_PATH: Final[Path] = Path(xdg_config_home) / 'pychoco/api.toml'
"""Where pychoco's API key list is stored.

:meta hide-value:"""
VALID_NAME_RE: Final[str] = r'^[0-9a-z-]+(\.(commandline|install|portable))?$'
"""Valid name for a package regular expression.

:meta hide-value:"""
NUGET_API_KEY_HTTP_HEADER: Final[str] = 'X-NuGet-ApiKey'
"""NuGet API key HTTP header.

:meta hide-value:"""
DEFAULT_PUSH_SOURCE: Final[str] = 'https://push.chocolatey.org'
"""Default push source URI.

:meta hide-value:"""
DEFAULT_CONFIG: Final[Config] = Config(pychoco={'defaultPushSource': DEFAULT_PUSH_SOURCE})
"""Default configuration.

:meta hide-value:"""
