# Cursor-Tools

**Cursor's Best All-in-One Tool** - A comprehensive Windows utility for managing and customizing the Cursor AI code editor.

![Python](https://img.shields.io/badge/python-v3.7+-blue.svg)
![Platform](https://img.shields.io/badge/platform-windows-lightgrey.svg)
![License](https://imgshields.io/badge/license-MIT-green.svg)
![Version](https://img.shields.io/badge/version-1.1.0-orange.svg)

## 🚀 Features

### 📊 Account Information
- View Cursor account details, subscription status, and usage statistics.

### 🔧 Device ID Modifier
- Modify Windows device IDs and registry entries.
- Automatic backup and restore functionality with an enhanced UI.

### 🚫 Auto-Update Disabler
- Disable Cursor's automatic update functionality.

### 🔄 Machine ID Reset
- Reset Cursor's machine identification and related files, including token limits.

### 🚀 Pro UI Features
- Apply Pro-related UI modifications and settings with a simplified process and automatic backup.

### 🚀 Auto-Update System
- Automatic update checking, downloading, and installation from GitHub releases with a forced update policy and enhanced network compatibility.

## 🎨 User Interface

Cursor-Tools features a colorful and interactive command-line interface using the Rich library.

## 📋 Requirements

### System Requirements
- **Operating System**: Windows 10/11 (64-bit)
- **Python**: 3.7 or higher
- **Privileges**: Administrator rights required

### Dependencies
- `rich`
- `colorama`
- `requests`

## 🛠️ Installation

### Option 1: From Source
1. Clone the repository.
2. Install dependencies: `pip install -r requirements.txt`
3. Run the application: `python main.py`

### Option 2: Pre-built Executable
1. Download the latest release from the [Releases](https://github.com/Mustafa-Bugra-Babuccu/Cursor-Tools/releases) page.
2. Extract the archive and run `Cursor-Tools.exe` as Administrator.

## 🚀 Usage

### Running the Application
- Right-click `main.py` or `Cursor-Tools.exe` and select **"Run as administrator"**.
- Follow the interactive menu.

### Main Menu Options
```
1. Account Info
2. Device ID Modifier
3. Disable Auto Update
4. Reset Machine ID
5. Pro UI Features
6. Exit Application
```

### Important Notes
- **Administrator privileges are required.**
- **Backups are automatically created.**
- **Always review changes** before confirming.
- **Close Cursor** before running certain operations.

## 🔧 Building from Source

### Prerequisites
- Python 3.7+
- PyInstaller
- Dependencies from `requirements.txt`

### Build Process
1. Install build dependencies: `pip install pyinstaller`
2. Run the build script: `python build_script.py` or `build.bat`
3. Find the executable in the `dist` folder.

### Build Configuration
Configured via `build_config.ini`.

## 📁 Project Structure

```
Cursor-Tools/
├── main.py                     # Main entry point
├── ui_manager.py              # User interface
├── account_info_manager.py    # Account info
├── device_id_modifier.py      # Device ID modification
├── disable_update_manager.py  # Update disabling
├── reset_machine_id_manager.py # Machine ID reset management
├── reset_machine_id.py        # Machine ID reset logic
├── pro_features_manager.py    # Pro UI Features management
├── pro_features.py           # Pro UI Features logic
├── auto_update_manager.py     # Automatic update system
├── registry_manager.py        # Registry operations
├── acc_info.py               # Account info retrieval
├── config.py                 # Configuration
├── requirements.txt          # Dependencies
├── build_config.ini         # Build configuration
├── build_script.py          # Build script
├── build.bat               # Build batch file
├── README.md              # Project overview
├── LICENSE               # License information
└── CHANGELOG.md         # Version history
```

## ⚠️ Important Warnings

- **Security**: Modifies Windows registry. Use with administrator privileges. Backups are created, but verify. Use at your own risk.
- **Compatibility**: Windows only. Requires Cursor AI editor.
- **Legal**: For educational/personal use. Users are responsible for compliance.

## 🤝 Contributing

Contributions are welcome. Please open an issue or submit a Pull Request.

## 📝 License

MIT License - see [LICENSE](LICENSE) file.

## 🙏 Acknowledgments

Thanks to the libraries used: Rich, Colorama, Requests, and the Cursor AI team.

## 📞 Support

Check the [Issues](https://github.com/Mustafa-Bugra-Babuccu/Cursor-Tools/issues) page or create a new issue.

## 🔄 Version History

See [CHANGELOG.md](CHANGELOG.md).

---

**Made with ❤️ by [Mustafa Bugra Babuccu](https://github.com/Mustafa-Bugra-Babuccu)**

*Cursor's Best All-in-One Tool*
