"""
Configuration Module for Cursor-Tools Application
Centralized configuration values for Windows-only application
"""

import os
import configparser
from pathlib import Path
from typing import Dict, Any

class CursorToolsConfig:
    """Centralized configuration for Cursor-Tools application"""

    def __init__(self):
        # Windows-specific paths
        self.user_profile = os.path.expanduser("~")
        self.documents_path = os.path.join(self.user_profile, "Documents")
        self.cursor_tools_dir = os.path.join(self.documents_path, "Cursor Tools")
        self.backups_dir = os.path.join(self.cursor_tools_dir, "backups")
        self.config_file_path = os.path.join(self.cursor_tools_dir, "cursor-tools.ini")

        # Registry paths for device ID modification
        self.registry_paths = {
            "cryptography": r"SOFTWARE\Microsoft\Cryptography",
            "hardware_profiles": r"SYSTEM\CurrentControlSet\Control\IDConfigDB\Hardware Profiles\0001",
            "sqm_client": r"SOFTWARE\Microsoft\SQMClient"
        }

        # Target registry values to read/modify
        self.target_values = {
            self.registry_paths["cryptography"]: ["MachineGuid"],
            self.registry_paths["hardware_profiles"]: ["HwProfileGuid"],
            self.registry_paths["sqm_client"]: ["MachineId"]
        }

        # Cursor application paths (Windows-only)
        self.cursor_paths = self._get_cursor_paths()

        # Update disabler paths (Windows-only)
        self.update_disabler_paths = self._get_update_disabler_paths()

        # Reset Machine ID paths (Windows-only)
        self.reset_machine_id_paths = self._get_reset_machine_id_paths()

        # Update URL patterns to remove from product.json
        self.update_url_patterns = {
            r"https://api2.cursor.sh/aiserver.v1.AuthService/DownloadUpdate": r"",
            r"https://api2.cursor.sh/updates": r"",
            r"http://cursorapi.com/updates": r"",
        }

        # Reset machine ID patterns for workbench.js modification
        self.reset_machine_id_patterns = {
            r'B(k,D(Ln,{title:"Upgrade to Pro",size:"small",get codicon(){return A.rocket},get onClick(){return t.pay}}),null)': r'B(k,D(Ln,{title:"Unlocked",size:"small",get codicon(){return A.github},get onClick(){return function(){window.open("https://github.com/Mustafa-Bugra-Babuccu/Cursor-Tools","_blank")}}}),null)',
            r'M(x,I(as,{title:"Upgrade to Pro",size:"small",get codicon(){return $.rocket},get onClick(){return t.pay}}),null)': r'M(x,I(as,{title:"Unlocked",size:"small",get codicon(){return $.rocket},get onClick(){return function(){window.open("https://github.com/Mustafa-Bugra-Babuccu/Cursor-Tools","_blank")}}}),null)',
            r'<div>Pro Trial': r'<div>Pro',
            r'py-1">Auto-select': r'py-1">Bypass-Version-Pin',
            r'async getEffectiveTokenLimit(e){const n=e.modelName;if(!n)return 2e5;': r'async getEffectiveTokenLimit(e){return 9000000;const n=e.modelName;if(!n)return 9e5;',
            r'var DWr=ne("<div class=settings__item_description>You are currently signed in with <strong></strong>.");': r'var DWr=ne("<div class=settings__item_description>You are currently signed in with <strong></strong>. <h1>Pro</h1>");',
            r'notifications-toasts': r'notifications-toasts hidden'
        }

        # Additional UI modification patterns from reset.js
        self.ui_modification_patterns = {
            # Pro Trial text replacements (from reset.js mc function)
            r'Pro Trial': r'Pro',
            r'"Pro Trial"': r'"Pro"',
            r"'Pro Trial'": r"'Pro'",
            # Additional Pro-related patterns
            r'Upgrade to Pro': r'Pro Unlocked',
            r'upgrade to pro': r'pro unlocked',
            r'Trial expired': r'Pro Active',
            r'trial expired': r'pro active',
            r'Free plan': r'Pro plan',
            r'free plan': r'pro plan',
            # Additional patterns for comprehensive coverage
            r'Start Pro Trial': r'Pro Active',
            r'start pro trial': r'pro active',
            r'Pro subscription': r'Pro unlocked',
            r'pro subscription': r'pro unlocked'
        }

        # Reset main.js patterns for getMachineId modification
        self.reset_main_js_patterns = {
            r"async getMachineId\(\)\{return [^??]+\?\?([^}]+)\}": r"async getMachineId(){return \1}",
            r"async getMacMachineId\(\)\{return [^??]+\?\?([^}]+)\}": r"async getMacMachineId(){return \1}",
        }

        # Initialize directories and config file
        self._ensure_directories_exist()
        self._load_config()

    def _get_cursor_paths(self) -> Dict[str, str]:
        """Get Cursor application paths for Windows"""
        appdata = os.getenv("APPDATA")
        return {
            'storage_path': os.path.join(appdata, "Cursor", "User", "globalStorage", "storage.json"),
            'sqlite_path': os.path.join(appdata, "Cursor", "User", "globalStorage", "state.vscdb"),
            'session_path': os.path.join(appdata, "Cursor", "Session Storage")
        }

    def _get_update_disabler_paths(self) -> Dict[str, str]:
        """Get update disabler paths for Windows with automatic path detection"""
        localappdata = os.getenv("LOCALAPPDATA", "")

        # Detect the correct Cursor installation path
        base_path = self._detect_cursor_installation_path()

        return {
            'updater_path': os.path.join(localappdata, "cursor-updater"),
            'update_yml_path': os.path.join(base_path, "update.yml"),
            'product_json_path': os.path.join(base_path, "product.json")
        }

    def _detect_cursor_installation_path(self) -> str:
        """Detect Cursor installation path by checking multiple possible locations"""
        localappdata = os.getenv("LOCALAPPDATA", "")

        # Possible Cursor installation paths (in order of preference)
        possible_paths = [
            # Old location (AppData/Local/Programs)
            os.path.join(localappdata, "Programs", "Cursor", "resources", "app"),
            # New location (Program Files)
            r"C:\Program Files\cursor\resources\app",
            # Alternative Program Files location
            os.path.join(os.getenv("PROGRAMFILES", ""), "cursor", "resources", "app"),
            # Alternative Program Files (x86) location
            os.path.join(os.getenv("PROGRAMFILES(X86)", ""), "cursor", "resources", "app"),
        ]

        # Check each path and return the first one that exists
        for path in possible_paths:
            if path and os.path.exists(path):
                # Verify it's a valid Cursor installation by checking for key files
                package_json = os.path.join(path, "package.json")
                main_js = os.path.join(path, "out", "main.js")
                if os.path.exists(package_json) and os.path.exists(main_js):
                    return path

        # If no valid path found, return the first path for error handling
        return possible_paths[0] if possible_paths else ""



    def _get_reset_machine_id_paths(self) -> Dict[str, str]:
        """Get reset machine ID paths for Windows with automatic path detection"""
        appdata = os.getenv("APPDATA", "")

        # Detect the correct Cursor installation path
        base_path = self._detect_cursor_installation_path()

        return {
            'base_path': base_path,
            'pkg_path': os.path.join(base_path, "package.json"),
            'main_path': os.path.join(base_path, "out", "main.js"),
            'workbench_path': os.path.join(base_path, "out", "vs", "workbench", "workbench.desktop.main.js"),
            'machine_id_path': os.path.join(appdata, "Cursor", "machineId"),
            'reset_backups_dir': os.path.join(self.cursor_tools_dir, "reset_backups"),
            # Additional UI modification paths (from reset.js)
            'ui_out_path': os.path.join(base_path, "out"),
            'ui_dist_path': os.path.join(base_path, "dist"),
            # Storage configuration path
            'storage_config_path': os.path.join(appdata, "Cursor", "User", "globalStorage", "storage.json"),
            # Pro Features backup directory
            'pro_backups_dir': os.path.join(self.cursor_tools_dir, "pro_backups")
        }

    def _ensure_directories_exist(self):
        """Create necessary directories if they don't exist"""
        try:
            # Create main Cursor Tools directory
            Path(self.cursor_tools_dir).mkdir(parents=True, exist_ok=True)

            # Create backups subdirectory
            Path(self.backups_dir).mkdir(parents=True, exist_ok=True)

            # Create reset backups subdirectory
            Path(self.reset_machine_id_paths['reset_backups_dir']).mkdir(parents=True, exist_ok=True)

            # Create pro features backups subdirectory
            Path(self.reset_machine_id_paths['pro_backups_dir']).mkdir(parents=True, exist_ok=True)

        except Exception as e:
            raise Exception(f"Failed to create directory structure: {str(e)}")

    def _load_config(self):
        """Load configuration from INI file"""
        self.config = configparser.ConfigParser()

        # Set default values
        self.config['Settings'] = {
            'auto_backup': 'true',
            'backup_retention_days': '30',
            'confirm_modifications': 'true'
        }

        self.config['UpdateDisabler'] = {
            'kill_processes_before_disable': 'true',
            'create_backup_before_modify': 'true',
            'set_files_readonly': 'true'
        }

        self.config['ResetMachineID'] = {
            'create_backup_before_reset': 'true',
            'update_system_registry': 'true',
            'patch_workbench_file': 'true',
            'patch_main_js_file': 'true'
        }

        self.config['ProFeatures'] = {
            'create_backup_before_apply': 'true',
            'backup_retention_days': '30',
            'auto_cleanup_old_backups': 'true',
            'backup_ui_files': 'true',
            'backup_database_files': 'true',
            'backup_storage_config': 'true',
            'confirm_before_restore': 'true'
        }

        # AutoUpdate - Only non-critical settings in INI file
        # Critical settings (version, github info) are hardcoded for security
        self.config['AutoUpdate'] = {
            'check_on_startup': 'true',
            'update_check_timeout': '10',
            'download_timeout': '300',
            'backup_retention_days': '30',
            'temp_cleanup_days': '7',
            'verify_ssl': 'true',
            'allow_redirects': 'true',
            'max_redirects': '5',
            'chunk_size': '8192',
            'max_release_notes_length': '200',
            'max_retry_attempts': '3',
            'retry_delay': '2',
            'batch_script_delay': '3'
        }

        self.config['Paths'] = {
            'backup_directory': self.backups_dir,
            'cursor_tools_directory': self.cursor_tools_dir,
            'reset_backups_directory': self.reset_machine_id_paths['reset_backups_dir'],
            'pro_backups_directory': self.reset_machine_id_paths['pro_backups_dir'],
            'cursor_base_path': self.reset_machine_id_paths['base_path'],
            'cursor_package_json': self.reset_machine_id_paths['pkg_path'],
            'cursor_main_js': self.reset_machine_id_paths['main_path'],
            'cursor_workbench_js': self.reset_machine_id_paths['workbench_path'],
            'cursor_machine_id_file': self.reset_machine_id_paths['machine_id_path']
        }

        # Load existing config if it exists
        if os.path.exists(self.config_file_path):
            try:
                self.config.read(self.config_file_path)
            except Exception as e:
                # If config file is corrupted, use defaults
                pass
        else:
            # Create new config file with defaults
            self.save_config()

    def save_config(self):
        """Save configuration to INI file"""
        try:
            with open(self.config_file_path, 'w') as configfile:
                self.config.write(configfile)
        except Exception as e:
            raise Exception(f"Failed to save configuration: {str(e)}")

    def get_setting(self, section: str, key: str, fallback: str = None) -> str:
        """Get a setting value from the config"""
        return self.config.get(section, key, fallback=fallback)

    def set_setting(self, section: str, key: str, value: str):
        """Set a setting value in the config"""
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value
        self.save_config()

    def get_cursor_installation_info(self) -> Dict[str, Any]:
        """Get diagnostic information about Cursor installation paths"""
        localappdata = os.getenv("LOCALAPPDATA", "")

        # All possible paths to check
        paths_to_check = [
            {
                "name": "Old Location (AppData)",
                "path": os.path.join(localappdata, "Programs", "Cursor", "resources", "app"),
                "description": "Legacy Cursor installation path"
            },
            {
                "name": "New Location (Program Files)",
                "path": r"C:\Program Files\cursor\resources\app",
                "description": "Current Cursor installation path"
            },
            {
                "name": "Alternative Program Files",
                "path": os.path.join(os.getenv("PROGRAMFILES", ""), "cursor", "resources", "app"),
                "description": "Alternative Program Files location"
            },
            {
                "name": "Program Files (x86)",
                "path": os.path.join(os.getenv("PROGRAMFILES(X86)", ""), "cursor", "resources", "app"),
                "description": "32-bit Program Files location"
            }
        ]

        detected_path = self._detect_cursor_installation_path()

        info = {
            "detected_path": detected_path,
            "detected_path_exists": os.path.exists(detected_path) if detected_path else False,
            "checked_locations": []
        }

        for path_info in paths_to_check:
            path = path_info["path"]
            exists = os.path.exists(path) if path else False
            valid = False

            if exists:
                # Check if it's a valid Cursor installation
                package_json = os.path.join(path, "package.json")
                main_js = os.path.join(path, "out", "main.js")
                workbench_js = os.path.join(path, "out", "vs", "workbench", "workbench.desktop.main.js")
                valid = all(os.path.exists(f) for f in [package_json, main_js, workbench_js])

            info["checked_locations"].append({
                "name": path_info["name"],
                "path": path,
                "description": path_info["description"],
                "exists": exists,
                "valid_installation": valid,
                "is_detected": path == detected_path
            })

        return info

class ConfigManager:
    """Centralized configuration management for all modules"""

    def __init__(self):
        self.config = CursorToolsConfig()

    def get_auto_update_config(self) -> dict:
        """Get auto-update configuration as a dictionary"""
        auto_update_section = self.config.config['AutoUpdate']

        # SECURITY: Critical settings are hardcoded and cannot be modified via INI file
        # This prevents users from redirecting updates to malicious servers

        # Get version from version.json (build-time) or auto_update_config.py (hardcoded)
        current_version = self._get_secure_version()

        # Hardcoded GitHub repository info for security
        github_owner = 'Mustafa-Bugra-Babuccu'
        github_repo = 'Cursor-Tools'

        return {
            # SECURE: These cannot be modified by users
            'CURRENT_VERSION': current_version,
            'GITHUB_OWNER': github_owner,
            'GITHUB_REPO': github_repo,
            'GITHUB_API_URL': f"https://api.github.com/repos/{github_owner}/{github_repo}/releases/latest",
            'GITHUB_REPO_URL': f"https://github.com/{github_owner}/{github_repo}",
            'FORCE_UPDATE_POLICY': True,  # Always enforced for security

            # CONFIGURABLE: These can be modified via INI file
            'CHECK_ON_STARTUP': auto_update_section.getboolean('check_on_startup', True),
            'UPDATE_CHECK_TIMEOUT': auto_update_section.getint('update_check_timeout', 10),
            'DOWNLOAD_TIMEOUT': auto_update_section.getint('download_timeout', 300),
            'VERIFY_SSL': auto_update_section.getboolean('verify_ssl', True),
            'ALLOW_REDIRECTS': auto_update_section.getboolean('allow_redirects', True),
            'MAX_REDIRECTS': auto_update_section.getint('max_redirects', 5),
            'BACKUP_RETENTION_DAYS': auto_update_section.getint('backup_retention_days', 30),
            'TEMP_CLEANUP_DAYS': auto_update_section.getint('temp_cleanup_days', 7),
            'CHUNK_SIZE': auto_update_section.getint('chunk_size', 8192),
            'MAX_RELEASE_NOTES_LENGTH': auto_update_section.getint('max_release_notes_length', 200),
            'MAX_RETRY_ATTEMPTS': auto_update_section.getint('max_retry_attempts', 3),
            'RETRY_DELAY': auto_update_section.getint('retry_delay', 2),
            'BATCH_SCRIPT_DELAY': auto_update_section.getint('batch_script_delay', 3)
        }

    def _get_secure_version(self) -> str:
        """Get version from secure sources (version.json or hardcoded config)"""
        import json

        # Priority 1: version.json (created during build)
        version_file = "version.json"
        if os.path.exists(version_file):
            try:
                with open(version_file, 'r') as f:
                    version_data = json.load(f)
                    return version_data.get('version', '0.0.1')
            except Exception:
                pass

        # Priority 2: auto_update_config.py (hardcoded)
        try:
            from auto_update_config import AutoUpdateConfig
            return AutoUpdateConfig.CURRENT_VERSION
        except Exception:
            pass

        # Fallback
        return '1.0.0'

    def get_api_headers(self) -> dict:
        """Get headers for GitHub API requests"""
        auto_config = self.get_auto_update_config()
        return {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": f"Cursor-Tools/{auto_config['CURRENT_VERSION']}"
        }

    def get_request_config(self) -> dict:
        """Get configuration for requests"""
        auto_config = self.get_auto_update_config()
        return {
            "timeout": auto_config['UPDATE_CHECK_TIMEOUT'],
            "verify": auto_config['VERIFY_SSL'],
            "allow_redirects": auto_config['ALLOW_REDIRECTS'],
            "headers": self.get_api_headers()
        }

    def get_download_filename(self, version: str) -> str:
        """Get the expected download filename for a version"""
        return f"Cursor-Tools-v{version}.exe"

    def validate_version_format(self, version: str) -> bool:
        """Validate version string format (semantic versioning)"""
        import re
        pattern = r'^\d+\.\d+\.\d+$'
        return bool(re.match(pattern, version))

    def get_fallback_request_config(self) -> dict:
        """Get fallback configuration for requests with SSL disabled"""
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        auto_config = self.get_auto_update_config()
        return {
            "timeout": auto_config['UPDATE_CHECK_TIMEOUT'],
            "verify": False,  # Disable SSL verification
            "allow_redirects": auto_config['ALLOW_REDIRECTS'],
            "headers": self.get_api_headers()
        }

    def get_cursor_paths(self) -> dict:
        """Get Cursor installation paths"""
        return self.config.cursor_paths

    def get_reset_machine_id_paths(self) -> dict:
        """Get reset machine ID paths"""
        return self.config.reset_machine_id_paths

    def get_update_disabler_paths(self) -> dict:
        """Get update disabler paths"""
        return self.config.update_disabler_paths

    def get_registry_paths(self) -> dict:
        """Get registry paths"""
        return self.config.registry_paths

    def get_target_values(self) -> dict:
        """Get target registry values"""
        return self.config.target_values

    def get_update_url_patterns(self) -> dict:
        """Get update URL patterns"""
        return self.config.update_url_patterns

    def get_setting(self, section: str, key: str, fallback: str = None) -> str:
        """Get a setting value from the config"""
        return self.config.get_setting(section, key, fallback)

    def set_setting(self, section: str, key: str, value: str):
        """Set a setting value in the config"""
        self.config.set_setting(section, key, value)

    def get_backup_directory(self) -> str:
        """Get the main backup directory"""
        return self.config.backups_dir

    def get_cursor_tools_directory(self) -> str:
        """Get the Cursor Tools directory"""
        return self.config.cursor_tools_dir


# Global configuration instances
config = CursorToolsConfig()
config_manager = ConfigManager()
