# Changelog

## [Unreleased]
### Added
- Integration with MMPos API to fetch and display worker data.
- New column in the table to show the source of worker data.

##[v1.2.0] - 2024-07-13
### Added
- Integration with spectre_miner_x64 to fetch and display bridge metrics.
- Added rule to add "hive" prefix to worker names parsed from spectre_miner_x64.

### Fixed
Corrected worker name parsing to ensure bridge metrics are matched correctly.

## [v1.1.1] - 2024-07-09
### Fixed
- Added handling for miner names to ensure blocks from the bridge are correctly shown for tnn-miner.
  
## [v1.1.0] - 2024-07-07
### Added
- Integration with TNN miner to fetch and display bridge metrics.
- Advanced view option for detailed logging and debugging.
- Option to view wallet address and balance.
- Display of current time and script version beside wallet information.

### Changed
- Renamed class `HiveOSManager` to `HashManager`.
- Updated variable and method names to reflect the change from HiveOS to HashManager.
- Replaced "Coin" column with "Miner" column in worker data display.
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
