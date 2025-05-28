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
            r'B(k,D(Ln,{title:"Upgrade to Pro",size:"small",get codicon(){return A.rocket},get onClick(){return t.pay}}),null)': r'B(k,D(Ln,{title:"Mustafa Bugra Babuccu GitHub",size:"small",get codicon(){return A.github},get onClick(){return function(){window.open("https://github.com/Mustafa-Bugra-Babuccu/Cursor-Tools","_blank")}}}),null)',
            r'M(x,I(as,{title:"Upgrade to Pro",size:"small",get codicon(){return $.rocket},get onClick(){return t.pay}}),null)': r'M(x,I(as,{title:"Mustafa Bugra Babuccu GitHub",size:"small",get codicon(){return $.rocket},get onClick(){return function(){window.open("https://github.com/Mustafa-Bugra-Babuccu/Cursor-Tools","_blank")}}}),null)',
            r'<div>Pro Trial': r'<div>Pro',
            r'py-1">Auto-select': r'py-1">Bypass-Version-Pin',
            r'async getEffectiveTokenLimit(e){const n=e.modelName;if(!n)return 2e5;': r'async getEffectiveTokenLimit(e){return 9000000;const n=e.modelName;if(!n)return 9e5;',
            r'var DWr=ne("<div class=settings__item_description>You are currently signed in with <strong></strong>.");': r'var DWr=ne("<div class=settings__item_description>You are currently signed in with <strong></strong>. <h1>Pro</h1>");',
            r'notifications-toasts': r'notifications-toasts hidden'
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
        """Get update disabler paths for Windows"""
        localappdata = os.getenv("LOCALAPPDATA", "")
        return {
            'updater_path': os.path.join(localappdata, "cursor-updater"),
            'update_yml_path': os.path.join(localappdata, "Programs", "Cursor", "resources", "app", "update.yml"),
            'product_json_path': os.path.join(localappdata, "Programs", "Cursor", "resources", "app", "product.json")
        }

    def _get_reset_machine_id_paths(self) -> Dict[str, str]:
        """Get reset machine ID paths for Windows"""
        localappdata = os.getenv("LOCALAPPDATA", "")
        appdata = os.getenv("APPDATA", "")

        # Base Cursor application directory
        base_path = os.path.join(localappdata, "Programs", "Cursor", "resources", "app")

        return {
            'base_path': base_path,
            'pkg_path': os.path.join(base_path, "package.json"),
            'main_path': os.path.join(base_path, "out", "main.js"),
            'workbench_path': os.path.join(base_path, "out", "vs", "workbench", "workbench.desktop.main.js"),
            'machine_id_path': os.path.join(appdata, "Cursor", "machineId"),
            'reset_backups_dir': os.path.join(self.cursor_tools_dir, "reset_backups")
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

        self.config['Paths'] = {
            'backup_directory': self.backups_dir,
            'cursor_tools_directory': self.cursor_tools_dir,
            'reset_backups_directory': self.reset_machine_id_paths['reset_backups_dir'],
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

# Global configuration instance
config = CursorToolsConfig()
