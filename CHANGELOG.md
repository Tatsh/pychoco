<!-- markdownlint-configure-file {"MD024": { "siblings_only": true } } -->

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [unreleased]

### Changed

- Do not prepend the application name directory for the configuration directory.
- Windows: Store preferences in Roaming directory.

### Fixed

- Ensure the configuration directory is created as necessary.

## [0.1.3]

### Fixed

- URIs in metadata.

## [0.1.2]

### Changed

- Added more specific exception types in `choco.packaging`.
- Switch to using platformdirs.
- `ChocolatelyClient.push()` accepts `Path` type instead of string.
- Add `--debug` option to commands lacking it.

## [0.1.0] - 2023-09-20

### Added

- `search` subcommand.

### Changed

- Upgraded dependencies.

[unreleased]: https://github.com/Tatsh/pychoco/compare/v0.1.3...HEAD
[0.1.3]: https://github.com/Tatsh/pychoco/compare/v0.1.2...v0.1.3
[0.1.2]: https://github.com/Tatsh/pychoco/compare/v0.1.1...v0.1.2
[0.1.0]: https://github.com/Tatsh/pychoco/compare/v0.0.3...v0.1.0
