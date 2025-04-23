(import 'defaults.libjsonnet') + {
  // Project-specific
  description: 'Minimal choco command for use on non-Windows platforms.',
  keywords: ['command line', 'windows'],
  project_name: 'chocolatey-choco',
  github_project_name: 'pychoco',
  version: '0.1.3',
  want_main: true,
  citation+: {
    'date-released': '2025-04-19',
  },
  primary_module: 'choco',
  pyproject+: {
    project+: {
      scripts: {
        choco: 'choco.main:main',
      },
    },
    tool+: {
      poetry+: {
        dependencies+: {
          click: '^8.1.8',
          defusedxml: '^0.7.1',
          platformdirs: '^4.3.7',
          'python-dateutil': '^2.9.0.post0',
          requests: '2.32.3',
          tomlkit: '^0.13.2',
        },
        group+: {
          dev+: {
            dependencies+: {
              'types-defusedxml': '^0.7.0.20240218',
              'types-python-dateutil': '^2.8.19.14',
              'types-requests': '^2.31.0.20240106',
            },
          },
          tests+: {
            dependencies+: {
              'requests-mock': '^1.11.0',
            },
          },
        },
      },
    },
  },
  // Common
  authors: [
    {
      'family-names': 'Udvare',
      'given-names': 'Andrew',
      email: 'audvare@gmail.com',
      name: '%s %s' % [self['given-names'], self['family-names']],
    },
  ],
  local funding_name = '%s2' % std.asciiLower(self.github_username),
  github_username: 'Tatsh',
  github+: {
    funding+: {
      ko_fi: funding_name,
      liberapay: funding_name,
      patreon: funding_name,
    },
  },
}
