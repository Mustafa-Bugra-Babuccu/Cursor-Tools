# Cursor-Tools

**Cursor's Best All-in-One Tool** - A comprehensive Windows utility for managing and customizing the Cursor AI code editor.

![Python](https://img.shields.io/badge/python-v3.7+-blue.svg)
![Platform](https://img.shields.io/badge/platform-windows-lightgrey.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Version](https://img.shields.io/badge/version-1.1.0-orange.svg)

## 🚀 Features

### 📊 Account Information
- View comprehensive Cursor account details
- Display subscription type and status
- Show usage statistics for Fast Response and Slow Response
- Monitor trial days remaining
- Track API usage limits

### 🔧 Device ID Modifier
- Modify Windows device IDs and registry entries
- Automatic backup creation before modifications
- **Enhanced Backup UI**: Rich table interface for backup restoration with detailed information
- Restore from previous backups with improved selection interface
- View current registry values
- Safe registry manipulation with administrator privileges

### 🚫 Auto-Update Disabler
- Disable Cursor's automatic update functionality
- Prevent unwanted updates and version changes
- Maintain control over your Cursor installation

### 🔄 Machine ID Reset
- Reset Cursor's machine identification
- Modify system registry entries
- Patch application files for enhanced functionality
- **Token Reset Integration**: Automatic token limit reset functionality
- Create backups before making changes
- Restore previous configurations

### 🚀 Pro UI Features (Enhanced)
- **Simplified User Experience**: Streamlined output with clean completion messages
- **Token Reset Integration**: Automatic token limit reset as part of Pro features application
- **Silent Operation Mode**: All operations run quietly with only final status messages
- **Comprehensive Backup**: Automatic backup creation before applying any changes
- **Enhanced Error Handling**: Robust error handling with graceful failure recovery
- **UI Modifications**: Apply workbench and comprehensive UI customizations
- **Database Updates**: Pro tier activation and usage data reset

### 🚀 Auto-Update System
- Automatic update checking at startup
- Download and install updates from GitHub releases
- Forced update policy - requires latest version to continue
- Safe update process with backup creation
- Automatic cleanup of old files and backups
- Progress indication during download and installation

## 🎨 User Interface

Cursor-Tools features a beautiful, rich command-line interface with:
- Colorful menus and panels
- Clear status indicators
- Interactive prompts and confirmations
- Structured data display
- Error handling and user feedback

## 📋 Requirements

### System Requirements
- **Operating System**: Windows 10/11 (64-bit)
- **Python**: 3.7 or higher
- **Privileges**: Administrator rights required

### Dependencies
- `rich==13.7.0` - Rich text and beautiful formatting
- `colorama==0.4.6` - Cross-platform colored terminal text
- `requests==2.31.0` - HTTP library for API calls

## 🛠️ Installation

### Option 1: From Source
1. Clone the repository:
   ```bash
   git clone https://github.com/Mustafa-Bugra-Babuccu/Cursor-Tools.git
   cd Cursor-Tools
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python main.py
   ```

### Option 2: Pre-built Executable
1. Download the latest release from the [Releases](https://github.com/Mustafa-Bugra-Babuccu/Cursor-Tools/releases) page
2. Extract the archive
3. Run `Cursor-Tools.exe` as Administrator

## 🚀 Usage

### Running the Application
1. **Right-click** on `main.py` or `Cursor-Tools.exe`
2. Select **"Run as administrator"**
3. Follow the interactive menu system

### Main Menu Options
```
1. Account Info          - View Cursor account information
2. Device ID Modifier    - Modify Windows device identifiers (enhanced backup UI)
3. Disable Auto Update   - Prevent automatic Cursor updates
4. Reset Machine ID      - Reset Cursor's machine identification (with token reset)
5. Pro UI Features       - Apply Pro-related UI modifications and settings
   • Apply All Pro UI Features   - Complete Pro UI feature application (simplified output)
   • UI Modifications Only       - UI changes without database updates (simplified output)
   • Database Updates Only       - Database changes without UI modifications
   • Restore Pro UI Features Backup - Restore from automatic backup (enhanced table UI)
6. Exit Application      - Close the application
```

### Important Notes
- **Administrator privileges are required** for registry modifications
- **Backups are automatically created** before making changes
- **Always review changes** before confirming operations
- **Close Cursor** before running certain operations

## 🔧 Building from Source

### Prerequisites
- Python 3.7+
- PyInstaller
- All dependencies from `requirements.txt`

### Build Process
1. Install build dependencies:
   ```bash
   pip install pyinstaller
   pip install -r requirements.txt
   ```

2. Run the build script:
   ```bash
   python build_script.py
   ```
   Or use the batch file:
   ```bash
   build.bat
   ```

3. Find the executable in the `dist` folder

### Build Configuration
The build process is configured via `build_config.ini` with options for:
- One-file vs one-folder distribution
- Optimization settings
- Dependency inclusion/exclusion
- Advanced PyInstaller options

## 📁 Project Structure

```
Cursor-Tools/
├── main.py                     # Main application entry point
├── ui_manager.py              # User interface management
├── account_info_manager.py    # Account information handling
├── device_id_modifier.py      # Device ID modification logic (enhanced backup UI)
├── disable_update_manager.py  # Update disabling functionality
├── reset_machine_id_manager.py # Machine ID reset operations
├── reset_machine_id.py        # Machine ID reset logic (with token reset)
├── pro_features_manager.py    # Pro UI Features management (simplified output)
├── pro_features.py           # Pro UI Features logic (token reset integration)
├── auto_update_manager.py     # Automatic update system
├── registry_manager.py        # Windows registry operations (enhanced backup info)
├── acc_info.py               # Cursor account info retrieval
├── config.py                 # Configuration management
├── requirements.txt          # Python dependencies
├── build_config.ini         # Build configuration (v1.1.0)
├── build_script.py          # Automated build script
├── build.bat               # Windows build batch file
├── README.md              # This file
├── LICENSE               # MIT License
└── CHANGELOG.md         # Version history
```

## ⚠️ Important Warnings

### Security Considerations
- This tool modifies Windows registry entries
- Always run with administrator privileges
- Backups are created automatically but verify them
- Use at your own risk - no warranty provided

### Compatibility
- **Windows Only** - This tool is designed specifically for Windows
- **Cursor Editor** - Requires Cursor AI editor to be installed
- **Registry Access** - Needs permission to modify system registry

### Legal Notice
This tool is for educational and personal use only. Users are responsible for compliance with Cursor's Terms of Service and applicable laws.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Setup
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Code Style
- Follow PEP 8 guidelines
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Include error handling and logging

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Rich](https://github.com/Textualize/rich) - For beautiful terminal formatting
- [Colorama](https://github.com/tartley/colorama) - For cross-platform colored output
- [Requests](https://github.com/psf/requests) - For HTTP functionality
- Cursor AI team - For creating an amazing code editor

## 📞 Support

If you encounter any issues or have questions:
1. Check the [Issues](https://github.com/Mustafa-Bugra-Babuccu/Cursor-Tools/issues) page
2. Create a new issue with detailed information
3. Include your Windows version and Python version
4. Provide error messages and steps to reproduce

## 🔄 Version History

See [CHANGELOG.md](CHANGELOG.md) for a detailed version history.

---

**Made with ❤️ by [Mustafa Bugra Babuccu](https://github.com/Mustafa-Bugra-Babuccu)**

*Cursor's Best All-in-One Tool*
