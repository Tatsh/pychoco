local utils = import 'utils.libjsonnet';

{
  uses_user_defaults: true,
  description: 'Minimal choco command for use on non-Windows platforms.',
  keywords: ['command line', 'windows'],
  project_name: 'chocolatey-choco',
  github_project_name: 'pychoco',
  version: '0.1.6',
  want_main: true,
  want_flatpak: true,
  publishing+: { flathub: 'sh.tat.chocolatey-choco' },
  primary_module: 'choco',
  security_policy_supported_versions: { '0.1.x': ':white_check_mark:' },
  flatpak+: { command: 'choco' },
  documentation_uri: 'https://%s.readthedocs.org' % self.project_name,
  snapcraft+: {
    apps+: {
      'chocolatey-choco'+: {
        command: 'bin/choco',
      },
    },
  },
  pyproject+: {
    project+: {
      scripts: {
        choco: 'choco.main:main',
      },
    },
    tool+: {
      pytest+: {
        ini_options+: {
          asyncio_mode: 'strict',
        },
      },
      uv+: {
        'exclude-newer-package'+: {
          'niquests-cache': false,
          'niquests-mock': false,
        },
      },
      poetry+: {
        dependencies+: {
          anyio: utils.latestPypiPackageVersionCaret('anyio'),
          defusedxml: utils.latestPypiPackageVersionCaret('defusedxml'),
          niquests: utils.latestPypiPackageVersionCaret('niquests'),
          'niquests-cache': utils.latestPypiPackageVersionCaret('niquests-cache'),
          platformdirs: utils.latestPypiPackageVersionCaret('platformdirs'),
          'python-dateutil': utils.latestPypiPackageVersionCaret('python-dateutil'),
          tomlkit: utils.latestPypiPackageVersionCaret('tomlkit'),
        },
        group+: {
          dev+: {
            dependencies+: {
              'types-defusedxml': utils.latestPypiPackageVersionCaret('types-defusedxml'),
              'types-python-dateutil': utils.latestPypiPackageVersionCaret('types-python-dateutil'),
            },
          },
          tests+: {
            dependencies+: {
              'niquests-mock': utils.latestPypiPackageVersionCaret('niquests-mock'),
              'pytest-asyncio': utils.latestPypiPackageVersionCaret('pytest-asyncio'),
            },
          },
        },
      },
    },
  },
  package_json+: {
    cspell+: {
      ignorePaths+: ['tests/feeds/*.xml'],
    },
  },
  prettierignore+: ['tests/feeds/logparser-search-error.xml'],
}
