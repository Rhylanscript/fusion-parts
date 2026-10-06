# Changelog

All notable changes to FusionParts are listed here.

## [Unreleased]

## [1.3.1] - 2026-10-6

### Fixed

- FusionParts can now run on startup together with FusionkitRibbonAPI, as it waits for Fusion to finish starting before looking for it, so load order no longer matters

## [1.3.0] - 2026-10-6

### Added

- **Belt From Circles** generator: pick two sketch circles or circular edges and a belt is built around them
- Flip direction option to grow the belt up or down from the picked circle

### Changed

- Belt outline maths can now be built from plain radii, shared by both belt tools

## [1.2.0] - 2026-10-6

### Added

- Refactored `core/` and `generators/` files into subfolders for organisation
- Updated test import paths with new file dirs

- Added the **helical gear** generator with customisation for helix angle
- Added the **herringbone gear** generator with customisation for helix angle

## [1.1.1] - 2026-10-5

### Added

- Optional mouse ears on the shaft bore with an adjustable ear diameter

## [1.1.0] - 2026-10-5

### Added

- Install scripts for MacOS and Windows
- Parts are now generated lying flat on ground instead of upright, so printing them is easier

## [1.0.0] - 2026-10-5

### Added

- Spur Gear generator with involute teeth and goBILDA REX shaft bores
- Timing Pulley generator for HTD3 and HTD5, with flanges, cone profile, engraved tooth count and shaft bore
- Timing Belt generator with a live pitch length and tooth count readout
- Output choice between a new component and a new body, matched to the design type
