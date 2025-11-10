<!-- markdownlint-configure-file {"MD024": { "siblings_only": true } } -->

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [unreleased]

## [0.1.4]

### Added

- Added `-h` option to all commands to show help.

### Changed

- Do not prepend the application name directory for the configuration directory.
- Windows: Store preferences in Roaming directory.
- search: Do not dump or print response data in debug mode.
- search: Will now follow next URLs if in the XML feed. [#288](https://github.com/Tatsh/pychoco/issues/288)

### Fixed

- Ensure the configuration directory is created as necessary.
- Fix the default push source URI.
- search: Correct the `Packages` API URI.
- search: Pass `$orderby` in all instances.
- search: Fix encoding of parameters for chocolatey.org peculiarities.
- `client.ChocolateyClient.search`: fix `page_size` type.

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

[unreleased]: https://github.com/Tatsh/pychoco/compare/v0.1.4...HEAD
[0.1.4]: https://github.com/Tatsh/pychoco/compare/v0.1.3...v0.1.4
[0.1.3]: https://github.com/Tatsh/pychoco/compare/v0.1.2...v0.1.3
[0.1.2]: https://github.com/Tatsh/pychoco/compare/v0.1.1...v0.1.2
[0.1.0]: https://github.com/Tatsh/pychoco/compare/v0.0.3...v0.1.0
