"""Template instances."""
from __future__ import annotations

import string

__all__ = ('CHOCOLATEY_INSTALL_PS1_TEMPLATE', 'NUSPEC_TEMPLATE', 'PSMDCP_XML_TEMPLATE',
           'RELS_XML_TEMPLATE', 'SEARCH_RESULT_TEMPLATE')

RELS_XML_TEMPLATE = string.Template("""<?xml version="1.0" encoding="utf-8" ?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship
    Type="http://schemas.microsoft.com/packaging/2010/07/manifest"
    Target="/${package_id}.nuspec"
    Id="${nuspec_id}"
  />
    <Relationship
    Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties"
    Target="/package/services/metadata/core-properties/${psmdcp_filename}"
    Id="${psmdcp_id}"
  />
</Relationships>\n""")
"""Used in construction of ``_rels/.rels`` file.

:meta hide-value:"""
last_modified_by = ('choco, Version=2.2.2.0, Culture=neutral, PublicKeyToken=79d02ea9cad655eb;'
                    'Microsoft Windows NT 10.0.22621.0;.NET Framework 4.8')
PSMDCP_XML_TEMPLATE = string.Template("""<?xml version="1.0" encoding="utf-8" ?>
<coreProperties xmlns:dc="http://purl.org/dc/elements/1.1/"
  xmlns:dcterms="http://purl.org/dc/terms/"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xmlns="http://schemas.openxmlformats.org/package/2006/metadata/core-properties">
  <dc:creator>${creator}</dc:creator>
  <dc:description>${description}</dc:description>
  <dc:identifier>${package_id}</dc:identifier>
  <version>${version}</version>
  <keywords>${keywords}</keywords>
  <lastModifiedBy>""" + last_modified_by + """</lastModifiedBy>
</coreProperties>
\n""")  #: :meta hide-value:
"""Used in construction of ``packages/services/metadata/core-properties/{id}.psmdcp``.

:meta hide-value:"""
NUSPEC_TEMPLATE = string.Template("""<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://schemas.microsoft.com/packaging/2010/07/nuspec.xsd">
  <metadata>
    <id>${package_id}</id>
    <version>VERSION</version>
    <title>PACKAGE_NAME (Install)</title>
    <authors>AUTHORS</authors>
    <owners>NUGET_MAKER</owners>
    <requireLicenseAcceptance>false</requireLicenseAcceptance>
    <projectUrl>https://a-url</projectUrl>
    <description>DESCRIPTION</description>
    <summary>SUMMARY</summary>
    <tags>tag1 tag2</tags>
    <packageSourceUrl>https://a-url-can-be-same-as-project</packageSourceUrl>
  </metadata>
</package>\n""")
"""Used in construction of the Nuspec file.

:meta hide-value:"""
CHOCOLATEY_INSTALL_PS1_TEMPLATE = string.Template("""$$ErrorActionPreference = 'Stop'
$$packageName = '${package_id}'
$$${package_id}Version    = '1.0'
$$toolsDir   = "$$(Split-Path -parent $$MyInvocation.MyCommand.Definition)"
$$packageArgs = @{
  checksum      = ''
  checksumType  = 'sha256'
  packageName   = $$packageName
  unzipLocation = $$toolsDir
  url           = 'https://somewhere/${package_id}.zip'
}
# https://chocolatey.org/docs/helpers-install-chocolatey-zip-package
Install-ChocolateyZipPackage @packageArgs
## Unzips a file to the specified location - auto overwrites existing content
## - https://chocolatey.org/docs/helpers-get-chocolatey-unzip
#Get-ChocolateyUnzip @packageArgs\n""")
"""Chocolatey PowerShell install template.

:meta hide-value:"""

SEARCH_RESULT_TEMPLATE = string.Template("""${title} ${version} ${state} ${cached_state}
 Title: ${title} | Published: ${publish_date}
 Package approved as a trusted package on ${approval_date}.
 Package testing status: ${testing_status}.
 Number of Downloads: ${num_downloads} | Downloads for this version: ${num_version_downloads}
 Package url ${package_url}
 Chocolatey Package Source: ${package_src_uri}
 Tags:${tags}
 Software Site: ${site}
 Software License: ${license}
 Documentation: ${documentation_uri}
 Summary: ${summary}
 Description: ${description}
 Release Notes: ${release_notes_uri}
""")
"""Search result template.

:meta hide-value:"""
ALL_VERSIONS_SEARCH_RESULT_TEMPLATE = string.Template(
    '${title} ${version} ${state} ${cached_state}')
"""Search result template when ``--all-versions`` is used.

:meta hide-value:"""
