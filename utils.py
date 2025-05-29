"""
Utility Functions for Cursor-Tools Application
Centralized utility functions to reduce code duplication across the codebase
"""

import os
import sys
import ctypes
import re
import json
import winreg
from typing import Tuple, Optional
from config import config


class AdminPrivilegeManager:
    """Centralized admin privilege management"""

    @staticmethod
    def is_admin() -> bool:
        """Check if the current process has administrator privileges"""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    @staticmethod
    def run_as_admin() -> bool:
        """Restart the current script with administrator privileges"""
        try:
            # Get the current script path
            script_path = os.path.abspath(sys.argv[0])

            # Use ShellExecute to run with elevated privileges
            ctypes.windll.shell32.ShellExecuteW(
                None,
                "runas",
                sys.executable,
                f'"{script_path}"',
                None,
                1
            )
            return True
        except Exception:
            return False

    @staticmethod
    def check_admin_privileges() -> bool:
        """Check admin privileges using registry access method"""
        try:
            # Try to open a registry key that requires admin access
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                               r"SYSTEM\CurrentControlSet\Control",
                               0, winreg.KEY_READ | winreg.KEY_WRITE)
            winreg.CloseKey(key)
            return True
        except PermissionError:
            return False
        except Exception:
            return False


class PathManager:
    """Centralized path detection and management"""

    @staticmethod
    def get_cursor_paths() -> Tuple[str, str]:
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
            raise OSError(error_msg)

        # Check if files exist
        if not os.path.exists(pkg_path):
            raise OSError(f"package.json not found: {pkg_path}")
        if not os.path.exists(main_path):
            raise OSError(f"main.js not found: {main_path}")

        return (pkg_path, main_path)

    @staticmethod
    def get_cursor_machine_id_path() -> str:
        """Get Cursor machineId file path for Windows using centralized configuration"""
        return config.reset_machine_id_paths['machine_id_path']

    @staticmethod
    def get_workbench_cursor_path() -> str:
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
            raise OSError(error_msg)

        return workbench_path

    @staticmethod
    def get_default_cursor_paths():
        """Get default Cursor paths for Windows (using centralized config)"""
        return config.cursor_paths


class VersionManager:
    """Centralized version checking and validation"""

    @staticmethod
    def validate_version_format(version: str) -> bool:
        """Validate version string format (semantic versioning)"""
        pattern = r'^\d+\.\d+\.\d+$'
        return bool(re.match(pattern, version))

    @staticmethod
    def version_check(version: str, min_version: str = "", max_version: str = "") -> bool:
        """Version number check with optional min/max constraints"""
        if not VersionManager.validate_version_format(version):
            return False

        def parse_version(ver: str) -> Tuple[int, ...]:
            return tuple(map(int, ver.split(".")))

        try:
            current_ver = parse_version(version)

            if min_version:
                if not VersionManager.validate_version_format(min_version):
                    return False
                min_ver = parse_version(min_version)
                if current_ver < min_ver:
                    return False

            if max_version:
                if not VersionManager.validate_version_format(max_version):
                    return False
                max_ver = parse_version(max_version)
                if current_ver > max_ver:
                    return False

            return True
        except ValueError:
            return False

    @staticmethod
    def check_cursor_version() -> bool:
        """Check if Cursor version is greater than 0.45.0"""
        try:
            pkg_path, _ = PathManager.get_cursor_paths()

            try:
                with open(pkg_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except UnicodeDecodeError:
                # If UTF-8 reading fails, try other encodings
                with open(pkg_path, "r", encoding="latin-1") as f:
                    data = json.load(f)

            if not isinstance(data, dict):
                return False

            if "version" not in data:
                return False

            version = data["version"]
            if not VersionManager.validate_version_format(version):
                return False

            # Compare with minimum version 0.45.0
            return VersionManager.version_check(version, min_version="0.45.0")

        except Exception:
            return False


class FileManager:
    """Centralized file management utilities"""

    @staticmethod
    def find_files_by_pattern(directory: str, patterns: list, extensions: list = None) -> list:
        """Find files matching specific patterns and extensions"""
        results = []

        try:
            if not os.path.exists(directory):
                return results

            for root, dirs, files in os.walk(directory):
                # Skip hidden directories and node_modules
                dirs[:] = [d for d in dirs if not d.startswith('.') and d != 'node_modules']

                for file in files:
                    file_path = os.path.join(root, file)

                    # Check extensions if specified
                    if extensions and not any(file.endswith(ext) for ext in extensions):
                        continue

                    # Check patterns if specified
                    if patterns:
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                                if any(pattern in content for pattern in patterns):
                                    results.append(file_path)
                        except Exception:
                            continue
                    else:
                        results.append(file_path)

        except Exception:
            pass

        return results

    @staticmethod
    def safe_file_modify(file_path: str, replacements: dict, backup_dir: str, backup_suffix: str = "") -> bool:
        """Safely modify files with automatic backup and rollback on failure"""
        import tempfile
        import shutil
        from datetime import datetime

        try:
            # Validate file exists and is writable
            if not os.path.exists(file_path) or not os.access(file_path, os.W_OK):
                return False

            # Save original file permissions
            original_stat = os.stat(file_path)
            original_mode = original_stat.st_mode

            # Create backup first
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.basename(file_path)
            backup_filename = f"{filename}.{backup_suffix}.backup.{timestamp}" if backup_suffix else f"{filename}.backup.{timestamp}"
            backup_path = os.path.join(backup_dir, backup_filename)

            # Ensure backup directory exists
            os.makedirs(backup_dir, exist_ok=True)
            shutil.copy2(file_path, backup_path)

            # Create temporary file for modifications
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", errors="ignore", delete=False) as tmp_file:
                # Read original content
                with open(file_path, "r", encoding="utf-8", errors="ignore") as original_file:
                    content = original_file.read()

                # Apply replacements
                for old_pattern, new_pattern in replacements.items():
                    if isinstance(old_pattern, str):
                        content = content.replace(old_pattern, new_pattern)
                    else:
                        # Assume regex pattern
                        import re
                        content = re.sub(old_pattern, new_pattern, content)

                # Write to temporary file
                tmp_file.write(content)
                tmp_path = tmp_file.name

            # Replace original file with modified version
            if os.path.exists(file_path):
                os.remove(file_path)
            shutil.move(tmp_path, file_path)

            # Restore original permissions
            os.chmod(file_path, original_mode)

            return True

        except Exception as e:
            # Clean up temporary file if it exists
            if 'tmp_path' in locals():
                try:
                    os.unlink(tmp_path)
                except:
                    pass
            return False

    @staticmethod
    def batch_file_replace(file_paths: list, pattern_dict: dict, backup_dir: str) -> dict:
        """Apply multiple replacements across multiple files"""
        results = {}

        for file_path in file_paths:
            try:
                success = FileManager.safe_file_modify(file_path, pattern_dict, backup_dir, "batch")
                results[file_path] = {"success": success, "error": None}
            except Exception as e:
                results[file_path] = {"success": False, "error": str(e)}

        return results

    @staticmethod
    def validate_file_permissions(file_paths: list) -> dict:
        """Check read/write permissions for multiple files"""
        results = {}

        for file_path in file_paths:
            try:
                exists = os.path.exists(file_path)
                readable = os.access(file_path, os.R_OK) if exists else False
                writable = os.access(file_path, os.W_OK) if exists else False

                results[file_path] = {
                    "exists": exists,
                    "readable": readable,
                    "writable": writable,
                    "valid": exists and readable and writable
                }
            except Exception as e:
                results[file_path] = {
                    "exists": False,
                    "readable": False,
                    "writable": False,
                    "valid": False,
                    "error": str(e)
                }

        return results

    @staticmethod
    def backup_file(file_path: str, backup_dir: str, backup_suffix: str = "") -> Optional[str]:
        """Create a backup of a file with timestamp"""
        try:
            import shutil
            from datetime import datetime

            if not os.path.exists(file_path):
                return None

            # Ensure backup directory exists
            os.makedirs(backup_dir, exist_ok=True)

            # Create backup filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.basename(file_path)
            backup_filename = f"{filename}.{backup_suffix}.backup.{timestamp}" if backup_suffix else f"{filename}.backup.{timestamp}"
            backup_path = os.path.join(backup_dir, backup_filename)

            # Copy file to backup location
            shutil.copy2(file_path, backup_path)
            return backup_path
        except Exception:
            return None


class BackupManager:
    """Unified backup management system"""

    def __init__(self, backup_base_dir: str = None):
        """Initialize BackupManager with base backup directory"""
        if backup_base_dir is None:
            from config import config
            self.backup_base_dir = config.backups_dir
        else:
            self.backup_base_dir = backup_base_dir

        # Ensure backup directory exists
        os.makedirs(self.backup_base_dir, exist_ok=True)

    def create_backup(self, source_path: str, backup_type: str, metadata: dict = None) -> Optional[str]:
        """Create timestamped backup with JSON metadata"""
        import shutil
        import json
        from datetime import datetime

        try:
            if not os.path.exists(source_path):
                return None

            # Generate timestamp and backup ID
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            source_name = os.path.basename(source_path)
            backup_id = f"{backup_type}_{source_name}_{timestamp}"

            # Create backup directory for this backup
            backup_dir = os.path.join(self.backup_base_dir, backup_id)
            os.makedirs(backup_dir, exist_ok=True)

            # Copy source to backup directory
            if os.path.isfile(source_path):
                backup_file_path = os.path.join(backup_dir, source_name)
                shutil.copy2(source_path, backup_file_path)
            else:
                # For directories, copy entire tree
                backup_file_path = os.path.join(backup_dir, source_name)
                shutil.copytree(source_path, backup_file_path)

            # Create metadata file
            backup_metadata = {
                "backup_id": backup_id,
                "backup_type": backup_type,
                "source_path": source_path,
                "backup_path": backup_file_path,
                "timestamp": timestamp,
                "created_date": datetime.now().isoformat(),
                "file_size": self._get_size(source_path),
                "metadata": metadata or {}
            }

            metadata_path = os.path.join(backup_dir, "backup_metadata.json")
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(backup_metadata, f, indent=2, default=str)

            return backup_id

        except Exception:
            return None

    def list_backups(self, backup_type: str = None, limit: int = None) -> list:
        """List available backups with filtering"""
        import json
        from datetime import datetime

        backups = []

        try:
            if not os.path.exists(self.backup_base_dir):
                return backups

            for item in os.listdir(self.backup_base_dir):
                backup_dir = os.path.join(self.backup_base_dir, item)
                if not os.path.isdir(backup_dir):
                    continue

                metadata_path = os.path.join(backup_dir, "backup_metadata.json")
                if not os.path.exists(metadata_path):
                    continue

                try:
                    with open(metadata_path, 'r', encoding='utf-8') as f:
                        backup_info = json.load(f)

                    # Filter by backup type if specified
                    if backup_type and backup_info.get('backup_type') != backup_type:
                        continue

                    # Add formatted date for display
                    try:
                        timestamp = backup_info.get('timestamp', '')
                        if timestamp:
                            date_obj = datetime.strptime(timestamp, "%Y%m%d_%H%M%S")
                            backup_info['formatted_date'] = date_obj.strftime("%Y-%m-%d %H:%M")
                        else:
                            backup_info['formatted_date'] = "Unknown"
                    except:
                        backup_info['formatted_date'] = "Unknown"

                    backups.append(backup_info)

                except Exception:
                    continue

            # Sort by timestamp (newest first)
            backups.sort(key=lambda x: x.get('timestamp', ''), reverse=True)

            # Apply limit if specified
            if limit:
                backups = backups[:limit]

            return backups

        except Exception:
            return []

    def restore_backup(self, backup_id: str) -> bool:
        """Restore from backup with validation"""
        import shutil
        import json

        try:
            backup_dir = os.path.join(self.backup_base_dir, backup_id)
            if not os.path.exists(backup_dir):
                return False

            metadata_path = os.path.join(backup_dir, "backup_metadata.json")
            if not os.path.exists(metadata_path):
                return False

            # Load backup metadata
            with open(metadata_path, 'r', encoding='utf-8') as f:
                backup_info = json.load(f)

            source_path = backup_info.get('source_path')
            backup_file_path = backup_info.get('backup_path')

            if not source_path or not backup_file_path:
                return False

            if not os.path.exists(backup_file_path):
                return False

            # Create backup of current state before restore
            if os.path.exists(source_path):
                current_backup_id = self.create_backup(source_path, "pre_restore",
                                                     {"restored_from": backup_id})

            # Restore from backup
            if os.path.isfile(backup_file_path):
                # Ensure target directory exists
                os.makedirs(os.path.dirname(source_path), exist_ok=True)
                shutil.copy2(backup_file_path, source_path)
            else:
                # For directories
                if os.path.exists(source_path):
                    shutil.rmtree(source_path)
                shutil.copytree(backup_file_path, source_path)

            return True

        except Exception:
            return False

    def cleanup_old_backups(self, retention_days: int) -> int:
        """Automatic cleanup based on retention policy"""
        import json
        import shutil
        from datetime import datetime, timedelta

        cleaned_count = 0
        cutoff_date = datetime.now() - timedelta(days=retention_days)

        try:
            if not os.path.exists(self.backup_base_dir):
                return 0

            for item in os.listdir(self.backup_base_dir):
                backup_dir = os.path.join(self.backup_base_dir, item)
                if not os.path.isdir(backup_dir):
                    continue

                metadata_path = os.path.join(backup_dir, "backup_metadata.json")
                if not os.path.exists(metadata_path):
                    continue

                try:
                    with open(metadata_path, 'r', encoding='utf-8') as f:
                        backup_info = json.load(f)

                    # Parse backup date
                    created_date_str = backup_info.get('created_date')
                    if created_date_str:
                        created_date = datetime.fromisoformat(created_date_str.replace('Z', '+00:00'))
                        if created_date < cutoff_date:
                            shutil.rmtree(backup_dir)
                            cleaned_count += 1

                except Exception:
                    continue

            return cleaned_count

        except Exception:
            return 0

    def create_legacy_backup(self, source_path: str, backup_dir: str, backup_suffix: str = "") -> Optional[str]:
        """Create legacy-style backup for compatibility with existing code"""
        try:
            import shutil
            from datetime import datetime

            if not os.path.exists(source_path):
                return None

            # Ensure backup directory exists
            os.makedirs(backup_dir, exist_ok=True)

            # Create backup filename with timestamp (legacy format)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.basename(source_path)
            backup_filename = f"{filename}.{backup_suffix}.backup.{timestamp}" if backup_suffix else f"{filename}.backup.{timestamp}"
            backup_path = os.path.join(backup_dir, backup_filename)

            # Copy file to backup location
            shutil.copy2(source_path, backup_path)
            return backup_path
        except Exception:
            return None

    def get_backup_files_by_pattern(self, backup_dir: str, patterns: dict) -> list:
        """Get backup files matching specific patterns (for legacy compatibility)"""
        import re
        from datetime import datetime

        backup_files = []

        try:
            if not os.path.exists(backup_dir):
                return backup_files

            for filename in os.listdir(backup_dir):
                for pattern, file_type in patterns.items():
                    match = re.match(pattern, filename)
                    if match:
                        timestamp_str = match.group(1)
                        try:
                            timestamp = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
                            backup_files.append({
                                'filename': filename,
                                'file_type': file_type,
                                'timestamp': timestamp,
                                'formatted_date': timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                                'path': os.path.join(backup_dir, filename)
                            })
                        except ValueError:
                            continue

            # Sort by timestamp (newest first)
            backup_files.sort(key=lambda x: x['timestamp'], reverse=True)

        except Exception:
            pass

        return backup_files

    def _get_size(self, path: str) -> int:
        """Get size of file or directory"""
        try:
            if os.path.isfile(path):
                return os.path.getsize(path)
            elif os.path.isdir(path):
                total_size = 0
                for dirpath, dirnames, filenames in os.walk(path):
                    for filename in filenames:
                        filepath = os.path.join(dirpath, filename)
                        try:
                            total_size += os.path.getsize(filepath)
                        except:
                            continue
                return total_size
            return 0
        except:
            return 0


# Convenience functions for backward compatibility
def is_admin() -> bool:
    """Convenience function for admin check"""
    return AdminPrivilegeManager.is_admin()

def run_as_admin() -> bool:
    """Convenience function for running as admin"""
    return AdminPrivilegeManager.run_as_admin()

def check_admin_privileges() -> bool:
    """Convenience function for checking admin privileges"""
    return AdminPrivilegeManager.check_admin_privileges()

def get_cursor_paths() -> Tuple[str, str]:
    """Convenience function for getting cursor paths"""
    return PathManager.get_cursor_paths()

def get_workbench_cursor_path() -> str:
    """Convenience function for getting workbench path"""
    return PathManager.get_workbench_cursor_path()

def validate_version_format(version: str) -> bool:
    """Convenience function for version validation"""
    return VersionManager.validate_version_format(version)

def version_check(version: str, min_version: str = "", max_version: str = "") -> bool:
    """Convenience function for version checking"""
    return VersionManager.version_check(version, min_version, max_version)
