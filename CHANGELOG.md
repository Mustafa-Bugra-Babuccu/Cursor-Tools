# Changelog

All notable changes to Cursor-Tools will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2024-12-19

### Added
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

### Changed
- **Main Application Flow** - Added update check before normal operation
- **Configuration System** - Added auto-update settings to config.ini
- **Build System** - Updated to include auto-update module in builds
- **UI Manager** - Added update-specific display methods

### Technical Details
- **Update Check Endpoint**: GitHub API releases endpoint
- **Download Source**: GitHub releases page
- **Update Policy**: Forced updates (application exits if user declines)
- **Backup Strategy**: Automatic backup creation before updates
- **Installation Method**: Batch script for safe executable replacement
- **Cleanup**: Automatic removal of files older than 7 days (temp) and 30 days (backups)

## [1.0.0] - 2025-05-28

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

## Future Releases

### Planned Features for v1.1.0
- Enhanced error recovery mechanisms
- Additional backup compression options
- Improved token detection algorithms
- Extended configuration options
- Performance optimizations
- Additional security validations

### Planned Features for v1.2.0
- Scheduled backup functionality
- Batch operation support
- Enhanced logging system
- Configuration import/export
- Advanced registry monitoring
- Custom modification profiles

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
