# Changelog

All notable changes to this project are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and the project uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2026-07-23

### Added

- Added `base-typed-float` to the supported runtime typing package family.
- Added DTO and persistence integration coverage for ordinary and constrained
  typed floats, including strict validation, assignment validation,
  serialization, and JSON Schema constraints.
- Added executable examples that place ordinary and constrained typed strings,
  integers, and floats side by side.
- Added the complete typed primitive example set to the package documentation.

### Changed

- Updated the development lock resolution to `base-typed-string 0.2.0`,
  `base-typed-int 0.2.0`, `base-typed-float 0.1.0`, and
  `typed-time-provider 0.2.0`.

## [0.1.0] - 2026-05-03

### Added

- Initial release with strict mutable and immutable DTOs, arbitrary-type DTOs,
  persistence-neutral documents, typed timestamp mixins, and typed schema
  versioning.

[Unreleased]: https://github.com/eldenizfamilyanskicode/base-pydantic-schemas/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/eldenizfamilyanskicode/base-pydantic-schemas/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/eldenizfamilyanskicode/base-pydantic-schemas/releases/tag/v0.1.0
