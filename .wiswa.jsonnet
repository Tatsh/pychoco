local utils = import 'utils.libjsonnet';

{
  uses_user_defaults: true,
  description: 'Minimal choco command for use on non-Windows platforms.',
  keywords: ['command line', 'windows'],
  project_name: 'chocolatey-choco',
  github_project_name: 'pychoco',
  version: '0.1.5',
  want_main: true,
  want_flatpak: true,
  publishing+: { flathub: 'sh.tat.chocolatey-choco' },
  primary_module: 'choco',
  security_policy_supported_versions: { '0.1.x': ':white_check_mark:' },
  pyproject+: {
    project+: {
      scripts: {
        choco: 'choco.main:main',
      },
    },
    tool+: {
      poetry+: {
        dependencies+: {
          defusedxml: utils.latestPypiPackageVersionCaret('defusedxml'),
          platformdirs: utils.latestPypiPackageVersionCaret('platformdirs'),
          'python-dateutil': utils.latestPypiPackageVersionCaret('python-dateutil'),
          requests: utils.latestPypiPackageVersionCaret('requests'),
          tomlkit: utils.latestPypiPackageVersionCaret('tomlkit'),
        },
        group+: {
          dev+: {
            dependencies+: {
              'types-defusedxml': utils.latestPypiPackageVersionCaret('types-defusedxml'),
              'types-python-dateutil': utils.latestPypiPackageVersionCaret('types-python-dateutil'),
              'types-requests': utils.latestPypiPackageVersionCaret('types-requests'),
            },
          },
          tests+: {
            dependencies+: {
              'requests-mock': utils.latestPypiPackageVersionCaret('requests-mock'),
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
