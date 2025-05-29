"""
Reset Machine ID Module for Cursor-Tools Application
Handles resetting Cursor machine IDs and related functionality (Windows-only)
"""

import os
import sys
import json
import uuid
import hashlib
import shutil
import sqlite3
import re
import tempfile
import glob
from colorama import Fore, Style, init
from typing import Tuple
import configparser
import traceback
from config import config
from datetime import datetime

# Initialize colorama
init()

def get_cursor_paths(translator=None) -> Tuple[str, str]:
    """Get Cursor related paths for Windows using centralized configuration"""
    # Use centralized configuration paths
    reset_paths = config.reset_machine_id_paths
    pkg_path = reset_paths['pkg_path']
    main_path = reset_paths['main_path']
    base_path = reset_paths['base_path']

    if not os.path.exists(base_path):
        error_msg = f"Cursor installation not found at: {base_path}\n"
        error_msg += "Checked locations:\n"
        error_msg += "  - %LOCALAPPDATA%\\Programs\\Cursor\\resources\\app (old location)\n"
        error_msg += "  - C:\\Program Files\\cursor\\resources\\app (new location)\n"
        error_msg += "Please ensure Cursor is properly installed."

        if translator:
            error_msg = translator.get('reset.path_not_found', path=base_path)
        raise OSError(error_msg)

    # Check if files exist
    if not os.path.exists(pkg_path):
        raise OSError(translator.get('reset.package_not_found', path=pkg_path) if translator else f"package.json not found: {pkg_path}")
    if not os.path.exists(main_path):
        raise OSError(translator.get('reset.main_not_found', path=main_path) if translator else f"main.js not found: {main_path}")

    return (pkg_path, main_path)

def get_cursor_machine_id_path(translator=None) -> str:
    """Get Cursor machineId file path for Windows using centralized configuration"""
    # Use centralized configuration path
    return config.reset_machine_id_paths['machine_id_path']

def get_workbench_cursor_path(translator=None) -> str:
    """Get Cursor workbench.desktop.main.js path for Windows using centralized configuration"""
    # Use centralized configuration path
    workbench_path = config.reset_machine_id_paths['workbench_path']

    if not os.path.exists(workbench_path):
        error_msg = f"Cursor workbench file not found: {workbench_path}\n"
        error_msg += "This usually means:\n"
        error_msg += "  1. Cursor is not installed\n"
        error_msg += "  2. Cursor is installed in a different location\n"
        error_msg += "  3. The Cursor version has a different file structure\n"
        error_msg += f"Expected file: {os.path.basename(workbench_path)}"

        if translator:
            error_msg = translator.get('reset.file_not_found', path=workbench_path)
        raise OSError(error_msg)

    return workbench_path

def version_check(version: str, min_version: str = "", max_version: str = "", translator=None) -> bool:
    """Version number check"""
    version_pattern = r"^\d+\.\d+\.\d+$"
    try:
        if not re.match(version_pattern, version):
            print(f"{Fore.RED}✗ {translator.get('reset.invalid_version_format', version=version) if translator else f'Invalid version format: {version}'}{Style.RESET_ALL}")
            return False

        def parse_version(ver: str) -> Tuple[int, ...]:
            return tuple(map(int, ver.split(".")))

        current = parse_version(version)

        if min_version and current < parse_version(min_version):
            print(f"{Fore.RED}✗ {translator.get('reset.version_too_low', version=version, min_version=min_version) if translator else f'Version too low: {version} < {min_version}'}{Style.RESET_ALL}")
            return False

        if max_version and current > parse_version(max_version):
            print(f"{Fore.RED}✗ {translator.get('reset.version_too_high', version=version, max_version=max_version) if translator else f'Version too high: {version} > {max_version}'}{Style.RESET_ALL}")
            return False

        return True

    except Exception as e:
        print(f"{Fore.RED}✗ {translator.get('reset.version_check_error', error=str(e)) if translator else f'Version check error: {e}'}{Style.RESET_ALL}")
        return False

def check_cursor_version(translator) -> bool:
    """Check Cursor version"""
    try:
        pkg_path, _ = get_cursor_paths(translator)

        try:
            with open(pkg_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except UnicodeDecodeError:
            # If UTF-8 reading fails, try other encodings
            with open(pkg_path, "r", encoding="latin-1") as f:
                data = json.load(f)

        if not isinstance(data, dict):
            print(f"{Fore.RED}✗ {translator.get('reset.invalid_json_object') if translator else 'Invalid JSON object'}{Style.RESET_ALL}")
            return False

        if "version" not in data:
            print(f"{Fore.RED}✗ {translator.get('reset.no_version_field') if translator else 'No version field found'}{Style.RESET_ALL}")
            return False

        version = str(data["version"]).strip()
        if not version:
            print(f"{Fore.RED}✗ {translator.get('reset.version_field_empty') if translator else 'Version field is empty'}{Style.RESET_ALL}")
            return False

        # Check version format
        if not re.match(r"^\d+\.\d+\.\d+$", version):
            print(f"{Fore.RED}✗ {translator.get('reset.invalid_version_format', version=version) if translator else f'Invalid version format: {version}'}{Style.RESET_ALL}")
            return False

        # Compare versions
        try:
            current = tuple(map(int, version.split(".")))
            min_ver = (0, 45, 0)  # Use tuple directly instead of string

            if current >= min_ver:
                return True
            else:
                return False
        except ValueError as e:
            print(f"{Fore.RED}✗ {translator.get('reset.version_parse_error', error=str(e)) if translator else f'Version parse error: {e}'}{Style.RESET_ALL}")
            return False

    except FileNotFoundError as e:
        print(f"{Fore.RED}✗ {translator.get('reset.package_not_found', path=pkg_path) if translator else f'Package.json not found: {pkg_path}'}{Style.RESET_ALL}")
        return False
    except json.JSONDecodeError as e:
        print(f"{Fore.RED}✗ {translator.get('reset.invalid_json_object') if translator else 'Invalid JSON object'}{Style.RESET_ALL}")
        return False
    except Exception as e:
        print(f"{Fore.RED}✗ {translator.get('reset.check_version_failed', error=str(e)) if translator else f'Version check failed: {e}'}{Style.RESET_ALL}")
        return False



def modify_workbench_js(file_path: str, translator=None) -> bool:
    """Modify workbench file content"""
    try:
        # Save original file permissions
        original_stat = os.stat(file_path)
        original_mode = original_stat.st_mode

        # Create temporary file
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", errors="ignore", delete=False) as tmp_file:
            # Read original content
            with open(file_path, "r", encoding="utf-8", errors="ignore") as main_file:
                content = main_file.read()

            patterns = config.reset_machine_id_patterns

            # Use patterns from config for replacements
            for old_pattern, new_pattern in patterns.items():
                content = content.replace(old_pattern, new_pattern)

            # Write to temporary file
            tmp_file.write(content)
            tmp_path = tmp_file.name

        # Backup original file with timestamp to centralized backup directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"workbench.desktop.main.js.backup.{timestamp}"
        backup_path = os.path.join(config.reset_machine_id_paths['reset_backups_dir'], backup_filename)
        shutil.copy2(file_path, backup_path)

        # Move temporary file to original position
        if os.path.exists(file_path):
            os.remove(file_path)
        shutil.move(tmp_path, file_path)

        # Restore original permissions (Windows-only)
        os.chmod(file_path, original_mode)

        return True

    except Exception as e:
        print(f"{Fore.RED}✗ {translator.get('reset.modify_file_failed', error=str(e)) if translator else f'Failed to modify file: {e}'}{Style.RESET_ALL}")
        if "tmp_path" in locals():
            try:
                os.unlink(tmp_path)
            except:
                pass
        return False

def modify_main_js(main_path: str, translator) -> bool:
    """Modify main.js file"""
    try:
        original_stat = os.stat(main_path)
        original_mode = original_stat.st_mode

        with tempfile.NamedTemporaryFile(mode="w", delete=False) as tmp_file:
            with open(main_path, "r", encoding="utf-8") as main_file:
                content = main_file.read()

            patterns = config.reset_main_js_patterns

            for pattern, replacement in patterns.items():
                content = re.sub(pattern, replacement, content)

            tmp_file.write(content)
            tmp_path = tmp_file.name

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"main.js.backup.{timestamp}"
        backup_path = os.path.join(config.reset_machine_id_paths['reset_backups_dir'], backup_filename)
        shutil.copy2(main_path, backup_path)
        shutil.move(tmp_path, main_path)

        os.chmod(main_path, original_mode)

        return True

    except Exception as e:
        print(f"{Fore.RED}✗ {translator.get('reset.modify_file_failed', error=str(e)) if translator else f'Failed to modify file: {e}'}{Style.RESET_ALL}")
        if "tmp_path" in locals():
            os.unlink(tmp_path)
        return False

def patch_cursor_get_machine_id(translator) -> bool:
    """Patch Cursor getMachineId function"""
    try:
        # Get paths
        pkg_path, main_path = get_cursor_paths(translator)

        # Check file permissions
        for file_path in [pkg_path, main_path]:
            if not os.path.isfile(file_path):
                print(f"{Fore.RED}✗ {translator.get('reset.file_not_found', path=file_path) if translator else f'File not found: {file_path}'}{Style.RESET_ALL}")
                return False
            if not os.access(file_path, os.W_OK):
                print(f"{Fore.RED}✗ {translator.get('reset.no_write_permission', path=file_path) if translator else f'No write permission: {file_path}'}{Style.RESET_ALL}")
                return False

        # Get version number
        try:
            with open(pkg_path, "r", encoding="utf-8") as f:
                version = json.load(f)["version"]
        except Exception as e:
            print(f"{Fore.RED}✗ {translator.get('reset.read_version_failed', error=str(e)) if translator else f'Failed to read version: {e}'}{Style.RESET_ALL}")
            return False

        # Check version
        if not version_check(version, min_version="0.45.0", translator=translator):
            print(f"{Fore.RED}✗ {translator.get('reset.version_not_supported') if translator else 'Version not supported'}{Style.RESET_ALL}")
            return False

        # Backup file to centralized backup directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"main.js.patch.backup.{timestamp}"
        backup_path = os.path.join(config.reset_machine_id_paths['reset_backups_dir'], backup_filename)
        if not os.path.exists(backup_path):
            shutil.copy2(main_path, backup_path)

        # Modify file
        if not modify_main_js(main_path, translator):
            return False

        return True

    except Exception as e:
        print(f"{Fore.RED}✗ {translator.get('reset.patch_failed', error=str(e)) if translator else f'Patch failed: {e}'}{Style.RESET_ALL}")
        return False

class MachineIDResetter:
    def __init__(self, translator=None):
        self.translator = translator

        # Use centralized configuration (Windows-only)
        self.db_path = config.cursor_paths['storage_path']
        self.sqlite_path = config.cursor_paths['sqlite_path']

    def generate_new_ids(self):
        """Generate new machine ID"""
        # Generate new UUID
        dev_device_id = str(uuid.uuid4())

        # Generate new machineId (64 characters of hexadecimal)
        machine_id = hashlib.sha256(os.urandom(32)).hexdigest()

        # Generate new macMachineId (128 characters of hexadecimal)
        mac_machine_id = hashlib.sha512(os.urandom(64)).hexdigest()

        # Generate new sqmId
        sqm_id = "{" + str(uuid.uuid4()).upper() + "}"

        self.update_machine_id_file(dev_device_id)

        return {
            "telemetry.devDeviceId": dev_device_id,
            "telemetry.macMachineId": mac_machine_id,
            "telemetry.machineId": machine_id,
            "telemetry.sqmId": sqm_id,
            "storage.serviceMachineId": dev_device_id,  # Add storage.serviceMachineId
        }

    def update_sqlite_db(self, new_ids):
        """Update machine ID in SQLite database"""
        try:
            conn = sqlite3.connect(self.sqlite_path)
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ItemTable (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            """)

            # Basic machine ID updates
            updates = [
                (key, value) for key, value in new_ids.items()
            ]

            for key, value in updates:
                cursor.execute("""
                    INSERT OR REPLACE INTO ItemTable (key, value)
                    VALUES (?, ?)
                """, (key, value))

            conn.commit()
            conn.close()
            return True

        except Exception as e:
            print(f"{Fore.RED}✗ {self.translator.get('reset.sqlite_error', error=str(e)) if self.translator else f'SQLite error: {e}'}{Style.RESET_ALL}")
            return False

    def update_system_ids(self, new_ids):
        """Update system-level IDs (Windows-only)"""
        try:
            # Windows-only system ID updates
            self._update_windows_machine_guid()
            self._update_windows_machine_id()
            return True
        except Exception as e:
            print(f"{Fore.RED}✗ {self.translator.get('reset.system_ids_update_failed', error=str(e)) if self.translator else f'System IDs update failed: {e}'}{Style.RESET_ALL}")
            return False

    def _update_windows_machine_guid(self):
        """Update Windows MachineGuid"""
        try:
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                "SOFTWARE\\Microsoft\\Cryptography",
                0,
                winreg.KEY_WRITE | winreg.KEY_WOW64_64KEY
            )
            new_guid = str(uuid.uuid4())
            winreg.SetValueEx(key, "MachineGuid", 0, winreg.REG_SZ, new_guid)
            winreg.CloseKey(key)
        except PermissionError as e:
            print(f"{Fore.RED}✗ {self.translator.get('reset.permission_denied', error=str(e)) if self.translator else f'Permission denied: {e}'}{Style.RESET_ALL}")
            raise
        except Exception as e:
            print(f"{Fore.RED}✗ {self.translator.get('reset.update_windows_machine_guid_failed', error=str(e)) if self.translator else f'Failed to update Windows MachineGuid: {e}'}{Style.RESET_ALL}")
            raise

    def _update_windows_machine_id(self):
        """Update Windows MachineId in SQMClient registry"""
        try:
            import winreg
            # Generate new GUID
            new_guid = "{" + str(uuid.uuid4()).upper() + "}"

            # Open the registry key
            try:
                key = winreg.OpenKey(
                    winreg.HKEY_LOCAL_MACHINE,
                    r"SOFTWARE\Microsoft\SQMClient",
                    0,
                    winreg.KEY_WRITE | winreg.KEY_WOW64_64KEY
                )
            except FileNotFoundError:
                # If the key does not exist, create it
                key = winreg.CreateKey(
                    winreg.HKEY_LOCAL_MACHINE,
                    r"SOFTWARE\Microsoft\SQMClient"
                )

            # Set MachineId value
            winreg.SetValueEx(key, "MachineId", 0, winreg.REG_SZ, new_guid)
            winreg.CloseKey(key)
            return True

        except PermissionError:
            print(f"{Fore.RED}✗ {self.translator.get('reset.permission_denied') if self.translator else 'Permission denied'}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}⚠ {self.translator.get('reset.run_as_admin') if self.translator else 'Run as administrator'}{Style.RESET_ALL}")
            return False
        except Exception as e:
            print(f"{Fore.RED}✗ {self.translator.get('reset.update_windows_machine_id_failed', error=str(e)) if self.translator else f'Failed to update Windows MachineId: {e}'}{Style.RESET_ALL}")
            return False

    def reset_machine_ids(self):
        """Reset machine ID and backup original file"""
        try:
            # Check files and permissions
            if not os.path.exists(self.db_path):
                print(f"{Fore.RED}✗ {self.translator.get('reset.not_found') if self.translator else 'File not found'}: {self.db_path}{Style.RESET_ALL}")
                return False

            if not os.access(self.db_path, os.R_OK | os.W_OK):
                print(f"{Fore.RED}✗ {self.translator.get('reset.no_permission') if self.translator else 'No permission to access file'}{Style.RESET_ALL}")
                return False

            # Step 1: Create backups and generate new IDs
            print(f"{Fore.CYAN}ℹ {self.translator.get('reset.step1') if self.translator else 'Creating backups and generating new machine IDs'}...{Style.RESET_ALL}")

            with open(self.db_path, "r", encoding="utf-8") as f:
                config_data = json.load(f)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"storage.json.backup.{timestamp}"
            backup_path = os.path.join(config.reset_machine_id_paths['reset_backups_dir'], backup_filename)
            shutil.copy2(self.db_path, backup_path)

            new_ids = self.generate_new_ids()
            config_data.update(new_ids)

            with open(self.db_path, "w", encoding="utf-8") as f:
                json.dump(config_data, f, indent=4)

            # Step 2: Update databases and system registry
            print(f"{Fore.CYAN}ℹ {self.translator.get('reset.step2') if self.translator else 'Updating databases and system registry'}...{Style.RESET_ALL}")

            self.update_sqlite_db(new_ids)
            self.update_system_ids(new_ids)

            # Step 3: Patch application files
            print(f"{Fore.CYAN}ℹ {self.translator.get('reset.step3') if self.translator else 'Patching Cursor application files'}...{Style.RESET_ALL}")

            workbench_path = get_workbench_cursor_path(self.translator)
            modify_workbench_js(workbench_path, self.translator)

            # Check version and patch if needed
            greater_than_0_45 = check_cursor_version(self.translator)
            if greater_than_0_45:
                patch_cursor_get_machine_id(self.translator)

            print(f"{Fore.GREEN}✓ {self.translator.get('reset.success') if self.translator else 'Machine ID reset completed successfully'}{Style.RESET_ALL}")
            return True

        except PermissionError as e:
            print(f"{Fore.RED}✗ {self.translator.get('reset.permission_error', error=str(e)) if self.translator else f'Permission error: {e}'}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}ℹ {self.translator.get('reset.run_as_admin') if self.translator else 'Run as administrator'}{Style.RESET_ALL}")
            return False
        except Exception as e:
            print(f"{Fore.RED}✗ {self.translator.get('reset.process_error', error=str(e)) if self.translator else f'Process error: {e}'}{Style.RESET_ALL}")
            return False



    def update_machine_id_file(self, machine_id: str) -> bool:
        """Update machineId file with new machine_id"""
        try:
            # Get the machineId file path
            machine_id_path = get_cursor_machine_id_path()

            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(machine_id_path), exist_ok=True)

            # Create backup if file exists
            if os.path.exists(machine_id_path):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_filename = f"machineId.backup.{timestamp}"
                backup_path = os.path.join(config.reset_machine_id_paths['reset_backups_dir'], backup_filename)
                try:
                    shutil.copy2(machine_id_path, backup_path)
                except Exception as e:
                    pass  # Continue if backup fails

            # Write new machine ID to file
            with open(machine_id_path, "w", encoding="utf-8") as f:
                f.write(machine_id)

            return True

        except Exception as e:
            error_msg = f"Failed to update machineId file: {str(e)}"
            if self.translator:
                error_msg = self.translator.get('reset.update_failed', error=str(e))
            print(f"{Fore.RED}✗ {error_msg}{Style.RESET_ALL}")
            return False

def reset_token_limits(translator=None) -> bool:
    """Reset token limits in SQLite database (from reset.js bt function)"""
    try:
        # Only print if translator is provided (not None)
        if translator is not None:
            print(f"{Fore.CYAN}ℹ {translator.get('reset.checking_sqlite') if translator else 'Checking SQLite database'}...{Style.RESET_ALL}")

        # Use centralized configuration path
        sqlite_path = config.cursor_paths['sqlite_path']

        if not os.path.exists(sqlite_path):
            if translator is not None:
                print(f"{Fore.RED}✗ {translator.get('reset.sqlite_not_found') if translator else 'SQLite database not found'}{Style.RESET_ALL}")
            return False

        # Create backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"state.vscdb.token.backup.{timestamp}"
        backup_path = os.path.join(config.reset_machine_id_paths['reset_backups_dir'], backup_filename)
        shutil.copy2(sqlite_path, backup_path)
        if translator is not None:
            print(f"{Fore.CYAN}💾 {translator.get('reset.creating_backup') if translator else 'Creating database backup'}...{Style.RESET_ALL}")

        # Connect to SQLite database
        import sqlite3
        conn = sqlite3.connect(sqlite_path)
        cursor = conn.cursor()

        if translator is not None:
            print(f"{Fore.CYAN}ℹ {translator.get('reset.resetting_tokens') if translator else 'Resetting token limits'}...{Style.RESET_ALL}")

        # Reset token usage (from reset.js bt function)
        cursor.execute("""
            UPDATE ItemTable SET value = '{"global":{"usage":{"sessionCount":0,"tokenCount":0}}}'
            WHERE key LIKE '%cursor%usage%'
        """)

        conn.commit()
        conn.close()

        if translator is not None:
            print(f"{Fore.GREEN}✓ {translator.get('reset.tokens_reset_success') if translator else 'Token limits reset successfully'}{Style.RESET_ALL}")
        return True

    except Exception as e:
        if translator is not None:
            print(f"{Fore.RED}✗ {translator.get('reset.token_reset_failed', error=str(e)) if translator else f'Failed to reset token limits: {e}'}{Style.RESET_ALL}")
        return False

def run(translator=None):
    """Main function to run the reset machine ID process"""
    print(f"\n{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}🔄 {translator.get('reset.title') if translator else 'Reset Machine ID'}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")

    resetter = MachineIDResetter(translator)
    resetter.reset_machine_ids()

    print(f"\n{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
    input(f"ℹ {translator.get('reset.press_enter') if translator else 'Press Enter to continue'}...")

if __name__ == "__main__":
    run()
