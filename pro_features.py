"""
Pro UI Features Module for Cursor-Tools Application
Handles Pro-related UI modifications, database updates, and feature unlocking
"""

import os
import sys
import json
import uuid
import shutil
import sqlite3
import tempfile
import glob
from colorama import Fore, Style, init
from datetime import datetime, timedelta
from config import config

# Initialize colorama
init()

def find_ui_files(directory: str, extensions: list) -> list:
    """Find UI files recursively (from reset.js findFiles function)"""
    results = []

    try:
        if not os.path.exists(directory):
            return results

        for root, dirs, files in os.walk(directory):
            # Skip hidden directories and node_modules
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != 'node_modules']

            for file in files:
                if any(file.endswith(ext) for ext in extensions):
                    results.append(os.path.join(root, file))

    except Exception:
        pass

    return results

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
            error_msg = translator.get('pro.file_not_found', path=workbench_path)
        raise OSError(error_msg)

    return workbench_path

def modify_workbench_js(file_path: str, translator=None, silent=False) -> bool:
    """Modify workbench file content with Pro patterns"""
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
        backup_filename = f"workbench.desktop.main.js.pro.backup.{timestamp}"
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
        if not silent:
            print(f"{Fore.RED}✗ {translator.get('pro.modify_file_failed', error=str(e)) if translator else f'Failed to modify file: {e}'}{Style.RESET_ALL}")
        if "tmp_path" in locals():
            try:
                os.unlink(tmp_path)
            except:
                pass
        return False

def modify_ui_files(translator=None, silent=False) -> bool:
    """Comprehensive UI modification based on reset.js mc function"""
    try:
        if not silent:
            print(f"{Fore.CYAN}ℹ {translator.get('pro.ui_customization') if translator else 'Starting comprehensive UI customization'}...{Style.RESET_ALL}")

        # Get UI paths from config
        reset_paths = config.reset_machine_id_paths
        ui_paths = [
            reset_paths['ui_out_path'],
            reset_paths['ui_dist_path']
        ]

        modified_files = 0
        ui_patterns = config.ui_modification_patterns

        for base_path in ui_paths:
            if not os.path.exists(base_path):
                continue

            if not silent:
                print(f"{Fore.CYAN}ℹ {translator.get('pro.searching_in', path=base_path) if translator else f'Searching in {base_path}'}...{Style.RESET_ALL}")

            # Find JS and HTML files
            js_files = find_ui_files(base_path, ['.js'])
            html_files = find_ui_files(base_path, ['.html'])
            all_files = js_files + html_files

            for file_path in all_files:
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()

                    # Check if file contains Pro Trial or other target patterns
                    should_modify = any(pattern in content for pattern in ui_patterns.keys())

                    if should_modify:
                        # Create backup
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        backup_filename = f"{os.path.basename(file_path)}.pro.ui.backup.{timestamp}"
                        backup_path = os.path.join(config.reset_machine_id_paths['reset_backups_dir'], backup_filename)
                        shutil.copy2(file_path, backup_path)

                        # Apply UI patterns
                        new_content = content
                        for old_pattern, new_pattern in ui_patterns.items():
                            new_content = new_content.replace(old_pattern, new_pattern)

                        # Write modified content
                        with open(file_path, "w", encoding="utf-8", errors="ignore") as f:
                            f.write(new_content)

                        if not silent:
                            print(f"{Fore.GREEN}✓ {translator.get('pro.ui_file_modified', file=file_path) if translator else f'Modified UI file: {os.path.basename(file_path)}'}{Style.RESET_ALL}")
                        modified_files += 1

                except Exception as err:
                    if not silent:
                        print(f"{Fore.YELLOW}⚠ {translator.get('pro.ui_file_error', file=file_path, error=str(err)) if translator else f'Error processing {os.path.basename(file_path)}: {err}'}{Style.RESET_ALL}")

        if not silent:
            if modified_files == 0:
                print(f"{Fore.YELLOW}ℹ {translator.get('pro.no_ui_files') if translator else 'No UI files found containing target patterns. UI customization skipped.'}{Style.RESET_ALL}")
            else:
                print(f"{Fore.GREEN}✓ {translator.get('pro.ui_customization_complete', count=modified_files) if translator else f'UI customization complete. Modified {modified_files} files.'}{Style.RESET_ALL}")

        return True

    except Exception as e:
        if not silent:
            print(f"{Fore.RED}✗ {translator.get('pro.ui_customization_failed', error=str(e)) if translator else f'UI customization failed: {e}'}{Style.RESET_ALL}")
        return False

class ProUIFeaturesBackupManager:
    """Manages backups for Pro UI Features modifications"""

    def __init__(self, translator=None):
        self.translator = translator
        self.backup_dir = config.reset_machine_id_paths['pro_backups_dir']
        self.sqlite_path = config.cursor_paths['sqlite_path']
        self.storage_path = config.reset_machine_id_paths['storage_config_path']
        self.workbench_path = config.reset_machine_id_paths['workbench_path']

        # Ensure backup directory exists
        os.makedirs(self.backup_dir, exist_ok=True)

    def create_full_backup(self, silent=False) -> str:
        """Create a complete backup of all Pro Features related files"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"pro_features_full_backup_{timestamp}"
            backup_path = os.path.join(self.backup_dir, backup_name)

            if not silent:
                print(f"{Fore.CYAN}ℹ {self.translator.get('pro.creating_backup') if self.translator else 'Creating full Pro Features backup'}...{Style.RESET_ALL}")

            # Create backup directory
            os.makedirs(backup_path, exist_ok=True)

            # Create backup manifest
            manifest = {
                "backup_name": backup_name,
                "timestamp": timestamp,
                "backup_type": "full",
                "files": [],
                "description": "Complete Pro Features backup including UI files, database, and storage config"
            }

            # Backup SQLite database
            if os.path.exists(self.sqlite_path):
                sqlite_backup = os.path.join(backup_path, "state.vscdb")
                shutil.copy2(self.sqlite_path, sqlite_backup)
                manifest["files"].append({"type": "database", "original": self.sqlite_path, "backup": "state.vscdb"})
                if not silent:
                    print(f"{Fore.GREEN}✓ {self.translator.get('pro.backed_up_database') if self.translator else 'Backed up SQLite database'}{Style.RESET_ALL}")

            # Backup storage configuration
            if os.path.exists(self.storage_path):
                storage_backup = os.path.join(backup_path, "storage.json")
                shutil.copy2(self.storage_path, storage_backup)
                manifest["files"].append({"type": "storage", "original": self.storage_path, "backup": "storage.json"})
                if not silent:
                    print(f"{Fore.GREEN}✓ {self.translator.get('pro.backed_up_storage') if self.translator else 'Backed up storage configuration'}{Style.RESET_ALL}")

            # Backup workbench file
            if os.path.exists(self.workbench_path):
                workbench_backup = os.path.join(backup_path, "workbench.desktop.main.js")
                shutil.copy2(self.workbench_path, workbench_backup)
                manifest["files"].append({"type": "workbench", "original": self.workbench_path, "backup": "workbench.desktop.main.js"})
                if not silent:
                    print(f"{Fore.GREEN}✓ {self.translator.get('pro.backed_up_workbench') if self.translator else 'Backed up workbench file'}{Style.RESET_ALL}")

            # Backup UI files from out and dist directories
            ui_paths = [
                config.reset_machine_id_paths['ui_out_path'],
                config.reset_machine_id_paths['ui_dist_path']
            ]

            ui_files_backed_up = 0
            for ui_path in ui_paths:
                if os.path.exists(ui_path):
                    ui_backup_dir = os.path.join(backup_path, "ui_files", os.path.basename(ui_path))
                    os.makedirs(ui_backup_dir, exist_ok=True)

                    # Find and backup UI files
                    js_files = find_ui_files(ui_path, ['.js'])
                    html_files = find_ui_files(ui_path, ['.html'])

                    for file_path in js_files + html_files:
                        try:
                            # Create relative path structure
                            rel_path = os.path.relpath(file_path, ui_path)
                            backup_file_path = os.path.join(ui_backup_dir, rel_path)

                            # Create directory structure
                            os.makedirs(os.path.dirname(backup_file_path), exist_ok=True)

                            # Copy file
                            shutil.copy2(file_path, backup_file_path)
                            manifest["files"].append({
                                "type": "ui_file",
                                "original": file_path,
                                "backup": os.path.join("ui_files", os.path.basename(ui_path), rel_path)
                            })
                            ui_files_backed_up += 1
                        except Exception as e:
                            if not silent:
                                print(f"{Fore.YELLOW}⚠ {self.translator.get('pro.backup_file_warning', file=file_path, error=str(e)) if self.translator else f'Warning backing up {file_path}: {e}'}{Style.RESET_ALL}")

            if ui_files_backed_up > 0 and not silent:
                print(f"{Fore.GREEN}✓ {self.translator.get('pro.backed_up_ui_files', count=ui_files_backed_up) if self.translator else f'Backed up {ui_files_backed_up} UI files'}{Style.RESET_ALL}")

            # Save manifest
            manifest_path = os.path.join(backup_path, "backup_manifest.json")
            with open(manifest_path, "w", encoding="utf-8") as f:
                json.dump(manifest, f, indent=2)

            if not silent:
                print(f"{Fore.GREEN}✓ {self.translator.get('pro.backup_created', name=backup_name) if self.translator else f'Full backup created: {backup_name}'}{Style.RESET_ALL}")
            return backup_name

        except Exception as e:
            if not silent:
                print(f"{Fore.RED}✗ {self.translator.get('pro.backup_failed', error=str(e)) if self.translator else f'Backup creation failed: {e}'}{Style.RESET_ALL}")
            return None

    def list_backups(self) -> list:
        """List all available Pro Features backups"""
        try:
            backups = []
            backup_dirs = glob.glob(os.path.join(self.backup_dir, "pro_features_*_backup_*"))

            for backup_dir in backup_dirs:
                if os.path.isdir(backup_dir):
                    manifest_path = os.path.join(backup_dir, "backup_manifest.json")
                    if os.path.exists(manifest_path):
                        try:
                            with open(manifest_path, "r", encoding="utf-8") as f:
                                manifest = json.load(f)

                            backup_info = {
                                "name": manifest.get("backup_name", os.path.basename(backup_dir)),
                                "timestamp": manifest.get("timestamp", "unknown"),
                                "type": manifest.get("backup_type", "unknown"),
                                "description": manifest.get("description", "No description"),
                                "file_count": len(manifest.get("files", [])),
                                "path": backup_dir,
                                "manifest": manifest
                            }
                            backups.append(backup_info)
                        except Exception as e:
                            # If manifest is corrupted, create basic info
                            backup_info = {
                                "name": os.path.basename(backup_dir),
                                "timestamp": "unknown",
                                "type": "unknown",
                                "description": "Corrupted backup manifest",
                                "file_count": 0,
                                "path": backup_dir,
                                "manifest": None
                            }
                            backups.append(backup_info)

            # Sort by timestamp (newest first)
            backups.sort(key=lambda x: x["timestamp"], reverse=True)
            return backups

        except Exception as e:
            print(f"{Fore.RED}✗ {self.translator.get('pro.list_backups_failed', error=str(e)) if self.translator else f'Failed to list backups: {e}'}{Style.RESET_ALL}")
            return []

    def restore_backup(self, backup_name: str) -> bool:
        """Restore a Pro Features backup"""
        try:
            backup_path = os.path.join(self.backup_dir, backup_name)
            manifest_path = os.path.join(backup_path, "backup_manifest.json")

            if not os.path.exists(backup_path) or not os.path.exists(manifest_path):
                print(f"{Fore.RED}✗ {self.translator.get('pro.backup_not_found', name=backup_name) if self.translator else f'Backup not found: {backup_name}'}{Style.RESET_ALL}")
                return False

            # Load manifest
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest = json.load(f)

            print(f"{Fore.CYAN}ℹ {self.translator.get('pro.restoring_backup', name=backup_name) if self.translator else f'Restoring backup: {backup_name}'}...{Style.RESET_ALL}")

            restored_files = 0
            failed_files = 0

            # Restore each file
            for file_info in manifest.get("files", []):
                try:
                    backup_file = os.path.join(backup_path, file_info["backup"])
                    original_file = file_info["original"]

                    if os.path.exists(backup_file):
                        # Create directory if needed
                        os.makedirs(os.path.dirname(original_file), exist_ok=True)

                        # Restore file
                        shutil.copy2(backup_file, original_file)
                        restored_files += 1

                        file_type = file_info.get("type", "unknown")
                        print(f"{Fore.GREEN}✓ {self.translator.get('pro.restored_file', type=file_type, file=os.path.basename(original_file)) if self.translator else f'Restored {file_type}: {os.path.basename(original_file)}'}{Style.RESET_ALL}")
                    else:
                        backup_file_name = file_info['backup']
                        print(f"{Fore.YELLOW}⚠ {self.translator.get('pro.backup_file_missing', file=backup_file_name) if self.translator else f'Backup file missing: {backup_file_name}'}{Style.RESET_ALL}")
                        failed_files += 1

                except Exception as e:
                    backup_file_name = file_info.get('backup', 'unknown')
                    print(f"{Fore.RED}✗ {self.translator.get('pro.restore_file_failed', file=backup_file_name, error=str(e)) if self.translator else f'Failed to restore {backup_file_name}: {e}'}{Style.RESET_ALL}")
                    failed_files += 1

            if failed_files == 0:
                print(f"{Fore.GREEN}✓ {self.translator.get('pro.restore_success', count=restored_files) if self.translator else f'Backup restored successfully! {restored_files} files restored.'}{Style.RESET_ALL}")
                return True
            else:
                print(f"{Fore.YELLOW}⚠ {self.translator.get('pro.restore_partial', restored=restored_files, failed=failed_files) if self.translator else f'Backup partially restored: {restored_files} files restored, {failed_files} failed.'}{Style.RESET_ALL}")
                return False

        except Exception as e:
            print(f"{Fore.RED}✗ {self.translator.get('pro.restore_failed', error=str(e)) if self.translator else f'Backup restoration failed: {e}'}{Style.RESET_ALL}")
            return False

    def delete_backup(self, backup_name: str) -> bool:
        """Delete a Pro Features backup"""
        try:
            backup_path = os.path.join(self.backup_dir, backup_name)

            if not os.path.exists(backup_path):
                print(f"{Fore.RED}✗ {self.translator.get('pro.backup_not_found', name=backup_name) if self.translator else f'Backup not found: {backup_name}'}{Style.RESET_ALL}")
                return False

            shutil.rmtree(backup_path)
            print(f"{Fore.GREEN}✓ {self.translator.get('pro.backup_deleted', name=backup_name) if self.translator else f'Backup deleted: {backup_name}'}{Style.RESET_ALL}")
            return True

        except Exception as e:
            print(f"{Fore.RED}✗ {self.translator.get('pro.delete_backup_failed', name=backup_name, error=str(e)) if self.translator else f'Failed to delete backup {backup_name}: {e}'}{Style.RESET_ALL}")
            return False

    def cleanup_old_backups(self, retention_days: int = 30) -> int:
        """Clean up old backups based on retention policy"""
        try:
            cutoff_date = datetime.now() - timedelta(days=retention_days)
            backups = self.list_backups()
            deleted_count = 0

            for backup in backups:
                try:
                    # Parse timestamp
                    backup_date = datetime.strptime(backup["timestamp"], "%Y%m%d_%H%M%S")

                    if backup_date < cutoff_date:
                        if self.delete_backup(backup["name"]):
                            deleted_count += 1

                except ValueError:
                    # Skip backups with invalid timestamps
                    continue
                except Exception as e:
                    backup_name = backup['name']
                    print(f"{Fore.YELLOW}⚠ {self.translator.get('pro.cleanup_warning', backup=backup_name, error=str(e)) if self.translator else f'Warning cleaning up {backup_name}: {e}'}{Style.RESET_ALL}")

            if deleted_count > 0:
                print(f"{Fore.GREEN}✓ {self.translator.get('pro.cleanup_success', count=deleted_count) if self.translator else f'Cleaned up {deleted_count} old backups'}{Style.RESET_ALL}")

            return deleted_count

        except Exception as e:
            print(f"{Fore.RED}✗ {self.translator.get('pro.cleanup_failed', error=str(e)) if self.translator else f'Backup cleanup failed: {e}'}{Style.RESET_ALL}")
            return 0

class ProUIFeaturesManager:
    def __init__(self, translator=None):
        self.translator = translator

        # Use centralized configuration (Windows-only)
        self.sqlite_path = config.cursor_paths['sqlite_path']
        self.storage_path = config.reset_machine_id_paths['storage_config_path']

        # Initialize backup manager
        self.backup_manager = ProUIFeaturesBackupManager(translator)

    def update_pro_tier_database(self, silent=False) -> bool:
        """Update SQLite database with Pro tier and usage reset"""
        try:
            if not silent:
                print(f"{Fore.CYAN}ℹ {self.translator.get('pro.updating_database') if self.translator else 'Updating Pro tier in database'}...{Style.RESET_ALL}")

            if not os.path.exists(self.sqlite_path):
                if not silent:
                    print(f"{Fore.RED}✗ {self.translator.get('pro.sqlite_not_found') if self.translator else 'SQLite database not found'}{Style.RESET_ALL}")
                return False

            # Create backup
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"state.vscdb.pro.backup.{timestamp}"
            backup_path = os.path.join(config.reset_machine_id_paths['reset_backups_dir'], backup_filename)
            shutil.copy2(self.sqlite_path, backup_path)

            conn = sqlite3.connect(self.sqlite_path)
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ItemTable (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            """)

            # Reset usage data (from reset.js bt function)
            cursor.execute("""
                UPDATE ItemTable SET value = '{"global":{"usage":{"sessionCount":0,"tokenCount":0}}}'
                WHERE key LIKE '%cursor%usage%'
            """)

            # Set Pro tier (from reset.js ep function)
            cursor.execute("""
                UPDATE ItemTable SET value = '"pro"'
                WHERE key LIKE '%cursor%tier%'
            """)

            conn.commit()
            conn.close()

            if not silent:
                print(f"{Fore.GREEN}✓ {self.translator.get('pro.database_updated') if self.translator else 'Pro tier database updated successfully'}{Style.RESET_ALL}")
            return True

        except Exception as e:
            if not silent:
                print(f"{Fore.RED}✗ {self.translator.get('pro.database_error', error=str(e)) if self.translator else f'Database error: {e}'}{Style.RESET_ALL}")
            return False

    def update_storage_config(self, silent=False) -> bool:
        """Update storage.json configuration with Pro settings"""
        try:
            if not silent:
                print(f"{Fore.CYAN}ℹ {self.translator.get('pro.updating_storage') if self.translator else 'Updating storage configuration'}...{Style.RESET_ALL}")

            if not os.path.exists(self.storage_path):
                if not silent:
                    print(f"{Fore.YELLOW}⚠ {self.translator.get('pro.storage_not_found') if self.translator else 'Storage config not found, skipping storage updates'}{Style.RESET_ALL}")
                return True

            # Create backup
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"storage.json.pro.backup.{timestamp}"
            backup_path = os.path.join(config.reset_machine_id_paths['reset_backups_dir'], backup_filename)
            shutil.copy2(self.storage_path, backup_path)

            # Read current storage data
            with open(self.storage_path, "r", encoding="utf-8") as f:
                storage_data = json.load(f)

            # Update storage configuration (from reset.js du function)
            if storage_data:
                storage_data['update.mode'] = 'none'  # Disable auto-updates

                # Write updated storage data
                with open(self.storage_path, "w", encoding="utf-8") as f:
                    json.dump(storage_data, f, indent=2)

                if not silent:
                    print(f"{Fore.GREEN}✓ {self.translator.get('pro.storage_updated') if self.translator else 'Storage configuration updated successfully'}{Style.RESET_ALL}")
                return True
            else:
                if not silent:
                    print(f"{Fore.YELLOW}⚠ {self.translator.get('pro.storage_invalid') if self.translator else 'Invalid storage data format'}{Style.RESET_ALL}")
                return False

        except Exception as e:
            if not silent:
                print(f"{Fore.RED}✗ {self.translator.get('pro.storage_update_failed', error=str(e)) if self.translator else f'Failed to update storage config: {e}'}{Style.RESET_ALL}")
            return False

    def apply_pro_features(self, silent=False) -> bool:
        """Apply all Pro features and UI modifications"""
        try:
            success = True

            # Step 0: Create backup before applying changes (if enabled)
            create_backup = config.get_setting('ProFeatures', 'create_backup_before_apply', 'true').lower() == 'true'
            if create_backup:
                backup_name = self.backup_manager.create_full_backup(silent=True)
                if not backup_name:
                    success = False

            # Step 1: Update Pro tier in database
            if not self.update_pro_tier_database(silent=True):
                success = False

            # Step 2: Reset token limits
            try:
                from reset_machine_id import reset_token_limits
                if not reset_token_limits(None):  # Pass None for translator to suppress output
                    success = False
            except Exception:
                success = False

            # Step 3: Update storage configuration
            if not self.update_storage_config(silent=True):
                success = False

            # Step 4: Apply workbench modifications
            try:
                workbench_path = get_workbench_cursor_path(self.translator)
                if not modify_workbench_js(workbench_path, self.translator, silent=True):
                    success = False
            except Exception:
                success = False

            # Step 5: Apply comprehensive UI modifications
            if not modify_ui_files(self.translator, silent=True):
                success = False

            return success

        except Exception:
            return False

    def apply_pro_features_verbose(self) -> bool:
        """Apply all Pro features and UI modifications with detailed output"""
        try:
            print(f"\n{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}🚀 {self.translator.get('pro.title') if self.translator else 'Applying Pro UI Features'}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")

            success = True

            # Step 0: Create backup before applying changes (if enabled)
            create_backup = config.get_setting('ProFeatures', 'create_backup_before_apply', 'true').lower() == 'true'
            if create_backup:
                print(f"{Fore.CYAN}ℹ {self.translator.get('pro.step0') if self.translator else 'Step 0: Creating backup before applying changes'}...{Style.RESET_ALL}")
                backup_name = self.backup_manager.create_full_backup()
                if backup_name:
                    print(f"{Fore.GREEN}✓ {self.translator.get('pro.backup_created_before_apply', name=backup_name) if self.translator else f'Backup created: {backup_name}'}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.YELLOW}⚠ {self.translator.get('pro.backup_failed_continue') if self.translator else 'Backup creation failed, but continuing with Pro features application'}{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}ℹ {self.translator.get('pro.backup_disabled') if self.translator else 'Automatic backup is disabled in settings'}{Style.RESET_ALL}")

            # Step 1: Update Pro tier in database
            print(f"{Fore.CYAN}ℹ {self.translator.get('pro.step1') if self.translator else 'Step 1: Updating Pro tier and usage data'}...{Style.RESET_ALL}")
            if not self.update_pro_tier_database():
                success = False

            # Step 2: Reset token limits
            print(f"{Fore.CYAN}ℹ {self.translator.get('pro.step2') if self.translator else 'Step 2: Resetting token limits'}...{Style.RESET_ALL}")
            try:
                from reset_machine_id import reset_token_limits
                if not reset_token_limits(self.translator):
                    success = False
            except Exception as e:
                print(f"{Fore.RED}✗ {self.translator.get('pro.token_reset_failed', error=str(e)) if self.translator else f'Token reset failed: {e}'}{Style.RESET_ALL}")
                success = False

            # Step 3: Update storage configuration
            print(f"{Fore.CYAN}ℹ {self.translator.get('pro.step3') if self.translator else 'Step 3: Updating storage configuration'}...{Style.RESET_ALL}")
            if not self.update_storage_config():
                success = False

            # Step 4: Apply workbench modifications
            print(f"{Fore.CYAN}ℹ {self.translator.get('pro.step4') if self.translator else 'Step 4: Applying workbench modifications'}...{Style.RESET_ALL}")
            try:
                workbench_path = get_workbench_cursor_path(self.translator)
                if not modify_workbench_js(workbench_path, self.translator):
                    success = False
            except Exception as e:
                print(f"{Fore.RED}✗ {self.translator.get('pro.workbench_failed', error=str(e)) if self.translator else f'Workbench modification failed: {e}'}{Style.RESET_ALL}")
                success = False

            # Step 5: Apply comprehensive UI modifications
            print(f"{Fore.CYAN}ℹ {self.translator.get('pro.step5') if self.translator else 'Step 5: Applying comprehensive UI modifications'}...{Style.RESET_ALL}")
            if not modify_ui_files(self.translator):
                success = False

            if success:
                print(f"{Fore.GREEN}✓ {self.translator.get('pro.success') if self.translator else 'Pro UI features applied successfully'}{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}⚠ {self.translator.get('pro.partial_success') if self.translator else 'Pro UI features applied with some warnings'}{Style.RESET_ALL}")

            return success

        except Exception as e:
            print(f"{Fore.RED}✗ {self.translator.get('pro.process_error', error=str(e)) if self.translator else f'Process error: {e}'}{Style.RESET_ALL}")
            return False

def run(translator=None):
    """Main function to run the Pro UI features process"""
    pro_manager = ProUIFeaturesManager(translator)
    return pro_manager.apply_pro_features()

if __name__ == "__main__":
    run()
