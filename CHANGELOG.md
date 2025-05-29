# Changelog

All notable changes to Cursor-Tools will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2025-05-30

### Added
- **Language Switching System**: Complete multilingual support with English and Turkish languages
  - Runtime language switching capability without application restart
  - Persistent language preference storage in JSON format
  - Centralized language management through LanguageManager class
  - Language settings menu accessible from main menu (option 6)
- **Complete UI Translation**: All user interface elements now support multiple languages
  - Main menu and all sub-menus (Account Info, Device ID, Updates, Reset Machine ID, Pro Features)
  - Error messages, success notifications, and warning dialogs
  - Update checking messages including "Checking for updates..." and status messages
  - Pro features interface and backup management messages
  - Parameterized messages with dynamic content support
- **Enhanced Update System**: Improved update checking experience
  - Auto-hide functionality for "No updates available" message (3-second timer)
  - Localized update status messages in both English and Turkish
  - Better user experience with automatic message clearing

### Changed
- **UIManager Architecture**: Enhanced to support centralized language management
  - Removed old localized display methods in favor of unified `display_text()` method
  - Integrated LanguageManager for consistent translation handling
  - Added auto-hide capability for specific message types
- **Application Structure**: Improved organization with language-aware components
  - All manager classes now use centralized language system
  - Eliminated duplicate translation handling code
  - Streamlined user interface consistency across all modules

### Enhanced
- **User Experience**: Significantly improved interface accessibility
  - Immediate language switching without restart requirement
  - Consistent translation coverage across all application features
  - Better visual feedback with auto-clearing status messages
- **Code Maintainability**: Centralized translation management
  - Single source of truth for all text content
  - Easy addition of new languages through LanguageManager
  - Reduced code duplication and improved maintainability

### Technical Details
- **Language Files**: Hardcoded translation patterns following user preferences
- **Persistence**: Language preference stored in `language_preference.json`
- **Architecture**: Class-based language management system
- **Integration**: Seamless integration with existing UIManager and all feature modules

## [1.0.0] - 2025-05-29

### Added
- **Initial Release** - First stable version of Cursor-Tools
- **Account Information**: View Cursor account details, subscription status, and usage statistics.
- **Device ID Modifier**: Modify Windows device IDs and registry entries with automatic backups and restore functionality. Includes an enhanced backup restoration UI.
- **Auto-Update Disabler**: Disable Cursor's automatic update functionality to prevent unwanted updates.
- **Machine ID Reset**: Reset Cursor's machine identification and related files. Includes token limit reset functionality and automatic backups.
- **Pro UI Features**: Apply Pro-related UI modifications and settings with a simplified user experience and comprehensive backup.
- **Auto-Update System**: Automatic update checking, downloading, and installation from GitHub releases with a forced update policy and automatic cleanup. Includes enhanced SSL support for better network compatibility.
- **Rich User Interface**: A beautiful command-line interface using the Rich library with clear indicators and interactive prompts.
- **Configuration Management**: Centralized configuration system for Windows-specific paths and customizable settings.
- **Build System**: Comprehensive build configuration and automated script for executable creation using PyInstaller.
- **Security Features**: Includes administrator privilege requirements, automatic backups, and user confirmations for critical operations.

### Enhanced
- **Error Handling and Resilience**: Improved application stability and error handling.
- **Code Organization**: Better separation of concerns and modularity.

### Fixed
- **Import and Dependency Issues**: Resolved module import problems and improved dependency management.

### Known Limitations
- Windows-only compatibility (by design)
- Requires administrator privileges for registry operations
- Cursor application must be closed for certain operations
- Network connectivity required for account information features

---

## Release Notes Format

Each release will include:
- **Added**: New features and functionality
- **Changed**: Changes to existing functionality
- **Deprecated**: Features that will be removed in future versions
- **Removed**: Features that have been removed
- **Fixed**: Bug fixes and corrections
- **Security**: Security-related improvements

---

## Support and Feedback

For issues, feature requests, or feedback:
- GitHub Issues: [https://github.com/Mustafa-Bugra-Babuccu/Cursor-Tools/issues](https://github.com/Mustafa-Bugra-Babuccu/Cursor-Tools/issues)
- Discussions: [https://github.com/Mustafa-Bugra-Babuccu/Cursor-Tools/discussions](https://github.com/Mustafa-Bugra-Babuccu/Cursor-Tools/discussions)

---

*This changelog is maintained by [Mustafa Bugra Babuccu](https://github.com/Mustafa-Bugra-Babuccu)*
