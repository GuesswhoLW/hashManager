# Changelog

## [Unreleased]
### Added
- Integration with MMPos API to fetch and display worker data.
- New column in the table to show the source of worker data.

## [v1.0.1] - 2024-07-07
### Added
- Integration with TNN miner to fetch and display bridge metrics.
- Advanced view option for detailed logging and debugging.

### Changed
- Renamed class `HiveOSManager` to `HashManager`.
- Updated variable and method names to reflect the change from HiveOS to HashManager.
- Refactored worker data fetching and formatting logic.
- Ensured blocks found data is always a string before adding to the table.
- Improved error handling and user prompts.

### Fixed
- Corrected the display of blocks found for workers using the TNN miner.
- Ensured accurate summation of total blocks found.
- Fixed alignment and formatting issues in the summary tables.
- Addressed connection errors when TNN miner is not enabled but the miner is running.

## [v1.0.0] - 2024-07-06
### Added
- Initial release of the HashManager script.
- Fetches and displays worker data from HiveOS.
- Calculates and displays estimated daily revenue.
- Dynamic loading animation and script information display.

### Fixed
- Minor bug fixes and performance improvements.
