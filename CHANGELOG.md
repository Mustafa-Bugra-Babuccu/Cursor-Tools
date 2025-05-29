# Changelog

All notable changes to Cursor-Tools will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2025-05-29

### Added
- **Token Reset Functionality** - Integrated token limit reset from reset.js into Python codebase
  - New `reset_token_limits()` function in `reset_machine_id.py`
  - Automatic token usage reset: `{"global":{"usage":{"sessionCount":0,"tokenCount":0}}}`
  - Integrated into Pro UI Features application process as Step 2
  - Automatic backup creation before token reset operations
  - Centralized configuration path usage for SQLite database access

- **Enhanced Device ID Modifier Backup UI** - Improved backup restoration interface
  - Rich table formatting with rounded borders matching Pro UI Features style
  - Detailed backup information display (No., Backup Name, Date, Files, Description)
  - Enhanced backup metadata including file count and formatted timestamps
  - Improved user selection interface with 'c' to cancel option
  - Better error handling and user feedback during restoration process

### Changed
- **Simplified Pro UI Features Output** - Streamlined user experience with clean completion messages
  - Replaced verbose step-by-step output with simple completion messages
  - Added silent mode operation for all Pro UI Features functions
  - Created dual-mode system: `apply_pro_features(silent=True)` and `apply_pro_features_verbose()`
  - Simplified completion messages: "✓ Pro UI features applied successfully" or "✓ Operation completed successfully"
  - Hidden all intermediate progress indicators (ℹ, 💾, ✓, ✗ symbols with descriptions)
  - Removed detailed error messages about missing workbench files from user interface
  - Maintained full functionality while hiding verbose logging from users

- **Enhanced Pro UI Features Integration** - Token reset now part of Pro features application
  - Token reset integrated as Step 2 in Pro UI Features application process
  - Renumbered subsequent steps: storage config → Step 3, workbench → Step 4, UI modifications → Step 5
  - Improved error handling with graceful continuation even if token reset fails
  - Consistent backup creation across all Pro UI Features operations

- **Improved Backup Management** - Enhanced backup functionality across modules
  - Added silent mode support to backup creation functions
  - Enhanced backup metadata with detailed file counts and descriptions
  - Improved backup restoration UI consistency across all modules
  - Better error handling during backup operations

### Enhanced
- **User Interface Improvements** - Consistent styling and better user experience
  - Standardized Rich console table formatting across all backup restoration interfaces
  - Consistent column structure (No., Backup Name, Date, Files, Description) across modules
  - Improved visual styling with rounded borders and proper spacing
  - Enhanced user interaction patterns with consistent selection methods

- **Error Handling and Resilience** - Improved application stability
  - Better exception handling in token reset functionality
  - Graceful failure recovery in Pro UI Features application
  - Improved error messages and user feedback
  - Enhanced validation and safety checks

### Technical Improvements
- **Code Organization** - Better separation of concerns and modularity
  - Separated verbose and silent operation modes in Pro UI Features
  - Enhanced function signatures with optional `silent` parameters
  - Improved configuration management for token reset functionality
  - Better integration between modules while maintaining independence

- **Configuration Management** - Enhanced centralized configuration
  - Improved path management for SQLite database access
  - Better backup directory organization and management
  - Enhanced configuration consistency across all modules

### Fixed
- **Import and Dependency Issues** - Resolved module import problems
  - Fixed import statements for token reset functionality
  - Improved module dependency management
  - Better error handling for missing dependencies

### Documentation
- **Updated Documentation** - Comprehensive documentation updates
  - Updated README.md to reflect all new features and improvements
  - Enhanced feature descriptions with new capabilities
  - Updated project structure documentation
  - Improved usage instructions and menu descriptions

---

## [1.0.0] - 2025-05-29

### Added
- **Initial Release** - First stable version of Cursor-Tools
- **Account Information Module**
  - View comprehensive Cursor account details
  - Display subscription type and status (Free, Pro, Trial, etc.)
  - Show usage statistics for Fast Response and Slow Response
  - Monitor trial days remaining
  - Track API usage limits and percentages
  - Support for multiple token authentication formats
  - Email extraction from multiple storage sources

- **Device ID Modifier Module**
  - Modify Windows device IDs and registry entries
  - Target registry paths: Cryptography, Hardware Profiles, SQM Client
  - Automatic backup creation before modifications
  - Restore functionality from previous backups
  - View current registry values in structured format
  - Safe registry manipulation with administrator privilege checks
  - Backup selection menu with date/time information

- **Auto-Update Disabler Module**
  - Disable Cursor's automatic update functionality
  - Prevent unwanted updates and version changes
  - Modify product.json and update.yml files
  - Remove update URL patterns from configuration
  - Create backups before making changes
  - Set files to read-only for additional protection

- **Machine ID Reset Module**
  - Reset Cursor's machine identification
  - Modify system registry entries (MachineGuid, HwProfileGuid, MachineId)
  - Patch workbench.desktop.main.js file
  - Patch main.js file for getMachineId functions
  - Create comprehensive backups before operations
  - Custom UI modifications and branding changes
  - Token limit modifications for enhanced functionality

- **Auto-Update System** - Complete automatic update functionality
  - Automatic update checking at application startup
  - GitHub API integration for release detection
  - Version comparison and update availability detection
  - Forced update policy - application requires latest version to continue
  - Automatic download of updates from GitHub releases
  - Safe update installation with backup creation
  - Progress indication during download and installation
  - Automatic cleanup of old temporary and backup files
  - Batch script-based update installation for seamless replacement
  - Error handling for network issues and download failures
  - Integration with existing Rich CLI interface

- **Rich User Interface**
  - Beautiful command-line interface using Rich library
  - Colorful menus and panels with consistent styling
  - Clear status indicators (success, error, warning, info)
  - Interactive prompts and confirmations
  - Structured data display in tables
  - Progress feedback and error handling
  - Administrator privilege warnings

- **Configuration Management**
  - Centralized configuration system
  - Windows-specific path detection
  - Automatic directory creation
  - INI-based configuration file
  - Customizable settings for all modules
  - Backup retention and cleanup options

- **Build System**
  - Comprehensive build configuration (build_config.ini)
  - PyInstaller integration for executable creation
  - One-file and one-folder build options
  - Size optimization settings
  - Hidden imports management
  - Automated build script (build_script.py)
  - Windows batch file for easy building

- **Security Features**
  - Administrator privilege requirements
  - Automatic backup creation before all modifications
  - Registry access validation
  - Error handling and rollback capabilities
  - User confirmation for critical operations
  - Safe file manipulation with proper error handling

### Technical Details
- **Platform**: Windows 10/11 (64-bit) only
- **Python Version**: 3.7+ required
- **Dependencies**:
  - rich==13.7.0 (Beautiful terminal formatting)
  - colorama==0.4.6 (Cross-platform colored output)
  - requests==2.31.0 (HTTP functionality for API calls)
- **Architecture**: Modular design with separate managers for each feature
- **Registry Operations**: Safe manipulation of Windows registry with backup/restore
- **File Operations**: Automatic backup creation and restoration capabilities
- **API Integration**: Cursor account information retrieval with multiple authentication methods
- **Auto-Update System**:
  - Update Check Endpoint: GitHub API releases endpoint
  - Download Source: GitHub releases page
  - Update Policy: Forced updates (application exits if user declines)
  - Backup Strategy: Automatic backup creation before updates
  - Installation Method: Batch script for safe executable replacement
  - Cleanup: Automatic removal of files older than 7 days (temp) and 30 days (backups)

### Documentation
- Comprehensive README.md with installation and usage instructions
- MIT License for open-source distribution
- Detailed code documentation and docstrings
- Build instructions and configuration guide
- Security warnings and legal notices

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
