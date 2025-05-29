"""
Update Disabler for Cursor-Tools Application
Handles disabling Cursor auto-update functionality (Windows-only)
"""

import os
import shutil
from colorama import Fore, Style
import subprocess
from config import config
import re
import tempfile
from ui_manager import UIManager

class UpdateDisabler:
    def __init__(self, ui_manager=None):
        self.ui_manager = ui_manager if ui_manager else UIManager()

        # Use centralized configuration (Windows-only)
        self.updater_path = config.update_disabler_paths['updater_path']
        self.update_yml_path = config.update_disabler_paths['update_yml_path']
        self.product_json_path = config.update_disabler_paths['product_json_path']

        # Get URL patterns from config
        self.url_patterns = config.update_url_patterns

    def _remove_update_url(self):
        """Remove update URL from product.json"""
        try:
            original_stat = os.stat(self.product_json_path)
            original_mode = original_stat.st_mode

            with tempfile.NamedTemporaryFile(mode="w", delete=False) as tmp_file:
                with open(self.product_json_path, "r", encoding="utf-8") as product_json_file:
                    content = product_json_file.read()

                # Use patterns from config
                for pattern, replacement in self.url_patterns.items():
                    content = re.sub(pattern, replacement, content)

                tmp_file.write(content)
                tmp_path = tmp_file.name

            # Create backup if enabled
            if config.get_setting('UpdateDisabler', 'create_backup_before_modify', 'true').lower() == 'true':
                shutil.copy2(self.product_json_path, self.product_json_path + ".old")

            shutil.move(tmp_path, self.product_json_path)

            os.chmod(self.product_json_path, original_mode)
            # Windows doesn't need chown

            return True

        except Exception as e:
            self.ui_manager.display_error(f"Failed to modify product.json: {e}")
            if "tmp_path" in locals():
                os.unlink(tmp_path)
            return False

    def _kill_cursor_processes(self):
        """End all Cursor processes (Windows-only)"""
        try:
            # Windows-only process termination
            subprocess.run(['taskkill', '/F', '/IM', 'Cursor.exe', '/T'], capture_output=True)
            return True

        except Exception as e:
            self.ui_manager.display_error(f"Failed to end processes: {e}")
            return False

    def _remove_updater_directory(self):
        """Delete updater directory"""
        try:
            if os.path.exists(self.updater_path):
                try:
                    if os.path.isdir(self.updater_path):
                        shutil.rmtree(self.updater_path)
                    else:
                        os.remove(self.updater_path)
                except PermissionError:
                    pass  # Skip if locked
            return True

        except Exception as e:
            self.ui_manager.display_error(f"Failed to remove directory: {e}")
            return True

    def _clear_update_yml_file(self):
        """Clear update.yml file"""
        try:
            if os.path.exists(self.update_yml_path):
                try:
                    with open(self.update_yml_path, 'w') as f:
                        f.write('')
                except PermissionError:
                    pass  # Skip if locked
            return True

        except Exception as e:
            self.ui_manager.display_error(f"Failed to clear update configuration file: {e}")
            return False

    def _create_blocking_file(self):
        """Create blocking files"""
        try:
            # Create updater_path blocking file
            try:
                os.makedirs(os.path.dirname(self.updater_path), exist_ok=True)
                open(self.updater_path, 'w').close()

                # Set updater_path as read-only (Windows-only)
                if config.get_setting('UpdateDisabler', 'set_files_readonly', 'true').lower() == 'true':
                    os.system(f'attrib +r "{self.updater_path}"')
            except PermissionError:
                pass  # Skip if locked

            # Create update_yml_path blocking file
            if self.update_yml_path and os.path.exists(os.path.dirname(self.update_yml_path)):
                try:
                    # Create update_yml_path blocking file
                    with open(self.update_yml_path, 'w') as f:
                        f.write('# This file is locked to prevent auto-updates\nversion: 0.0.0\n')

                    # Set update_yml_path as read-only (Windows-only)
                    if config.get_setting('UpdateDisabler', 'set_files_readonly', 'true').lower() == 'true':
                        os.system(f'attrib +r "{self.update_yml_path}"')
                except PermissionError:
                    pass  # Skip if locked

            return True

        except Exception as e:
            self.ui_manager.display_error(f"Failed to create blocking files: {e}")
            return True  # Return True to continue execution

    def disable_auto_update(self):
        """Disable auto update"""
        try:
            # 1. End processes (if enabled)
            if config.get_setting('UpdateDisabler', 'kill_processes_before_disable', 'true').lower() == 'true':
                if not self._kill_cursor_processes():
                    return False

            # 2. Delete directory - continue even if it fails
            self._remove_updater_directory()

            # 3. Clear update.yml file
            if not self._clear_update_yml_file():
                return False

            # 4. Create blocking files
            if not self._create_blocking_file():
                return False

            # 5. Remove update URL from product.json
            if not self._remove_update_url():
                return False

            self.ui_manager.display_success("Auto-update disabled successfully")
            return True

        except Exception as e:
            self.ui_manager.display_error(f"Failed to disable auto-update: {e}")
            return False

def run(ui_manager=None):
    """Convenient function for directly calling the disable function"""
    if ui_manager:
        ui_manager.clear_screen()
        ui_manager.display_header()
        ui_manager.display_info("Disable Cursor Auto Update")
    else:
        print(f"\n{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}⚬ Disable Cursor Auto Update{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")

    disabler = UpdateDisabler(ui_manager)
    disabler.disable_auto_update()

    if ui_manager:
        ui_manager.pause()
    else:
        print(f"\n{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
        input("ℹ Press Enter to Continue...")

if __name__ == "__main__":
    # For standalone testing
    run()
