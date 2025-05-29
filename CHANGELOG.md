# Changelog

All notable changes to Cursor-Tools will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-05-29

### Added
- **Cursor Pro Management**
  - Account information display and management
  - Device ID viewing and modification
  - Pro features activation and management
  - Machine ID reset with automatic backup

- **Language Support**
  - English and Turkish language options
  - Runtime language switching (no restart required)
  - Complete UI translation for all menus
  - Language settings in main menu

- **Automatic Updates**
  - GitHub integration for version checking
  - Secure download and installation
  - Auto-hide "No updates available" message (3 seconds)
  - Version comparison and update notifications

- **Security Features**
  - Hardcoded GitHub repository (prevents malicious redirects)
  - Secure version management system
  - Protected configuration files
  - Force update policy enforcement

- **User Interface**
  - Rich console interface with colors
  - Intuitive menu navigation
  - Progress indicators and status messages
  - Multi-language support

- **Backup System**
  - Automatic backup before modifications
  - JSON-based backup metadata
  - Backup restoration capabilities
  - Configurable retention policies

### Features
- **File Management**: Centralized file operations with backup support
- **Configuration**: INI-based settings with secure defaults
- **Build System**: Automated executable creation with version management
- **Cross-platform**: Windows-focused with proper path handling

### Technical Details
- **Architecture**: Class-based modular design with manager classes
- **Security**: Critical settings hardcoded to prevent tampering
- **Internationalization**: Hardcoded translations for performance
- **Updates**: GitHub API integration with semantic versioning

### System Requirements
- Windows operating system
- Internet connection for updates
- Administrative privileges for some operations
- Minimum 50MB free disk space

### Supported Operations
- View and modify Cursor Pro account information
- Change device ID with automatic backup
- Reset machine ID and related files
- Activate Pro features and UI modifications
- Check for and install application updates
- Switch between English and Turkish languages
- Manage backup files and restoration

---

**First stable release of Cursor-Tools with comprehensive Cursor Pro management, multilingual support, and secure automatic updates.**
