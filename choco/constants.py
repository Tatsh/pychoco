"""Constants."""
from __future__ import annotations

import platformdirs

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
           'NUSPEC_FIELD_TAGS', 'NUSPEC_FIELD_VERSION', 'OBJECT_REF_NOT_SET_ERROR_MESSAGE',
           'PYCHOCO_API_KEYS_TOML_PATH', 'PYCHOCO_TOML_PATH', 'VALID_NAME_RE')

FEED_NAMESPACES = {
    '': 'http://www.w3.org/2005/Atom',
    'd': 'http://schemas.microsoft.com/ado/2007/08/dataservices',
    'm': 'http://schemas.microsoft.com/ado/2007/08/dataservices/metadata'
}
"""Namespaces used in parsing package feeds.

:meta hide-value:"""
FEED_AUTHOR_TAG = 'author'
"""Feed ``author`` tag.

:meta hide-value:"""
FEED_ENTRY_TAG = 'entry'
"""Feed ``entry`` tag.

:meta hide-value:"""
FEED_ID_TAG = 'id'
"""Feed ``id`` tag.

:meta hide-value:"""
FEED_PROPERTIES_TAG = 'm:properties'
"""Feed ``m:properties`` tag.

:meta hide-value:"""
FEED_SUMMARY_TAG = 'summary'
"""Feed ``summary`` tag.

:meta hide-value:"""
FEED_TITLE_TAG = 'title'
"""Feed ``title`` tag.

:meta hide-value:"""
FEED_UPDATED_TAG = 'updated'
"""Feed ``updated`` tag.

:meta hide-value:"""
METADATA_DESCRIPTION_TAG = 'd:Description'
"""Feed ``d:Description`` tag.

:meta hide-value:"""
METADATA_DOCS_URL_TAG = 'd:DocsUrl'
"""Feed ``d:DocsUrl`` tag.

:meta hide-value:"""
METADATA_DOWNLOAD_COUNT_TAG = 'd:DownloadCount'
"""Feed ``d:DownloadCount`` tag.

:meta hide-value:"""
METADATA_GALLERY_DETAILS_URL_TAG = 'd:GalleryDetailsUrl'
"""Feed ``d:GalleryDetailsUrl`` tag.

:meta hide-value:"""
METADATA_IS_APPROVED_TAG = 'd:IsApproved'
"""Feed ``d:IsApproved`` tag.

:meta hide-value:"""
METADATA_IS_DOWNLOAD_CACHE_AVAILABLE_TAG = 'd:IsDownloadCacheAvailable'
"""Feed ``d:IsDownloadCacheAvailable`` tag.

:meta hide-value:"""
METADATA_LICENSE_URL_TAG = 'd:LicenseUrl'
"""Feed ``d:LicenseUrl`` tag.

:meta hide-value:"""
METADATA_PACKAGE_APPROVED_DATE_TAG = 'd:PackageApprovedDate'
"""Feed ``d:PackageApprovedDate`` tag.

:meta hide-value:"""
METADATA_PACKAGE_SOURCE_URL_TAG = 'd:PackageSourceUrl'
"""Feed ``d:PackageSourceUrl`` tag.

:meta hide-value:"""
METADATA_PACKAGE_STATUS_TAG = 'd:PackageStatus'
"""Feed ``d:PackageStatus`` tag.

:meta hide-value:"""
METADATA_PACKAGE_TEST_RESULT_STATUS_DATE_TAG = 'd:PackageTestResultStatusDate'
"""Feed ``d:PackageTestResultStatusDate`` tag.

:meta hide-value:"""
METADATA_PACKAGE_TEST_RESULT_STATUS_TAG = 'd:PackageTestResultStatus'
"""Feed ``d:PackageTestResultStatus`` tag.

:meta hide-value:"""
METADATA_PROJECT_URL_TAG = 'd:ProjectUrl'
"""Feed ``d:ProjectUrl`` tag.

:meta hide-value:"""
METADATA_PUBLISHED_TAG = 'd:Published'
"""Feed ``d:Published`` tag.

:meta hide-value:"""
METADATA_RELEASE_NOTES_TAG = 'd:ReleaseNotes'
"""Feed ``d:ReleaseNotes`` tag.

:meta hide-value:"""
METADATA_SUMMARY_TAG = 'd:Summary'
"""Feed ``d:Summary`` tag.

:meta hide-value:"""
METADATA_TAGS_TAG = 'd:Tags'
"""Feed ``d:Tags`` tag.

:meta hide-value:"""
METADATA_VERSION_DOWNLOAD_COUNT_TAG = 'd:VersionDownloadCount'
"""Feed ``d:VersionDownloadCount`` tag.

:meta hide-value:"""
METADATA_VERSION_TAG = 'd:Version'
"""Feed ``d:Version`` tag.

:meta hide-value:"""

NUSPEC_XSD_URI_PREFIX = '{http://schemas.microsoft.com/packaging/2010/07/nuspec.xsd}'
NUSPEC_FIELD_AUTHORS = f'{NUSPEC_XSD_URI_PREFIX}authors'
"""Nuspec authors tag.

:meta hide-value:"""
NUSPEC_FIELD_DESCRIPTION = f'{NUSPEC_XSD_URI_PREFIX}description'
"""Nuspec description tag.

:meta hide-value:"""
NUSPEC_FIELD_ID = f'{NUSPEC_XSD_URI_PREFIX}id'
"""Nuspec id tag.

:meta hide-value:"""
NUSPEC_FIELD_TAGS = f'{NUSPEC_XSD_URI_PREFIX}tags'
"""Nuspec tags tag.

:meta hide-value:"""
NUSPEC_FIELD_VERSION = f'{NUSPEC_XSD_URI_PREFIX}version'
"""Nuspec version tag.

:meta hide-value:"""
CHOCOLATEY_UNINSTALL_PS1 = """$$ErrorActionPreference = 'Stop'
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
}\n"""
"""Uninstall PowerShell template.

:meta hide-value:"""
CONTENT_TYPES_XML = """<?xml version="1.0" encoding="utf-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels"
    ContentType="application/vnd.openxmlformats-package.relationships+xml" />
  <Default Extension="psmdcp"
    ContentType="application/vnd.openxmlformats-package.core-properties+xml" />
  <Default Extension="ps1" ContentType="application/octet" />
  <Default Extension="nuspec" ContentType="application/octet" />
</Types>\n"""
"""Used in creating the ``[Content_Types].xml`` file.

:meta hide-value:"""
PYCHOCO_TOML_PATH = platformdirs.user_config_path(
    'pychoco', appauthor=False, ensure_exists=True, roaming=True) / 'config.toml'
"""Where pychoco's main configuration file is by default.

:meta hide-value:"""
PYCHOCO_API_KEYS_TOML_PATH = platformdirs.user_config_path(
    'pychoco', appauthor=False, ensure_exists=True, roaming=True) / 'api.toml'
"""Where pychoco's API key list is stored.

:meta hide-value:"""
VALID_NAME_RE = r'^[0-9a-z-]+(\.(commandline|install|portable))?$'
"""Valid name for a package regular expression.

:meta hide-value:"""
NUGET_API_KEY_HTTP_HEADER = 'X-NuGet-ApiKey'
"""NuGet API key HTTP header.

:meta hide-value:"""
DEFAULT_PUSH_SOURCE = 'https://push.chocolatey.org'
"""Default push source URI.

:meta hide-value:"""
DEFAULT_CONFIG = Config(pychoco={'defaultPushSource': DEFAULT_PUSH_SOURCE})
"""Default configuration.

:meta hide-value:"""
OBJECT_REF_NOT_SET_ERROR_MESSAGE = ('xml:lang="en-US">Object reference not set to an instance of '
                                    'an object')
"""
Error message for object reference not set as seen from chocolatey.org when using the search API.

:meta hide-value:
"""
