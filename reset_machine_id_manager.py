"""
Reset Machine ID Manager for Cursor-Tools
Integrates reset machine ID functionality into the main application
"""

import os
from reset_machine_id import MachineIDResetter
from ui_manager import UIManager

class ResetMachineIDManager:
    def __init__(self):
        self.ui_manager = UIManager()
        self.machine_id_resetter = MachineIDResetter()

    def run_reset_machine_id_menu(self):
        """Run the Reset Machine ID sub-menu"""
        while True:
            self.ui_manager.clear_screen()
            self.ui_manager.display_header()
            self.ui_manager.display_reset_machine_id_menu()

            choice = self.ui_manager.get_user_choice(
                "Select an option",
                valid_choices=["1", "2", "3", "4"]
            )

            if choice is None:  # User pressed Ctrl+C
                break
            elif choice == "1":
                self.reset_machine_id()
            elif choice == "2":
                self.restore_backup()
            elif choice == "3":
                self.view_current_machine_ids()
            elif choice == "4":
                break

            if choice in ["1", "2", "3"]:
                self.ui_manager.pause()

    def reset_machine_id(self):
        """Execute the reset machine ID functionality"""
        self.ui_manager.clear_screen()
        self.ui_manager.display_header()

        self.ui_manager.display_warning("This operation will reset Cursor's machine ID and related identifiers.")
        self.ui_manager.display_info("This process will:")
        self.ui_manager.console.print("  • Generate new machine IDs and device identifiers")
        self.ui_manager.console.print("  • Update Cursor's storage.json and SQLite database")
        self.ui_manager.console.print("  • Modify Windows registry entries (MachineGuid, MachineId)")
        self.ui_manager.console.print("  • Patch Cursor application files (workbench.js, main.js)")
        self.ui_manager.console.print("  • Create backups of all modified files")
        self.ui_manager.console.print("  • Check Cursor version and apply appropriate patches")

        # Get confirmation
        if not self.ui_manager.confirm_action("Do you want to proceed with resetting machine ID?"):
            self.ui_manager.display_info("Operation cancelled.")
            return

        # Perform the reset operation
        try:
            self.ui_manager.display_info("Starting machine ID reset process...")
            success = self.machine_id_resetter.reset_machine_ids()

            if success:
                self.ui_manager.display_success("Machine ID has been reset successfully!")
                self.ui_manager.display_info("New machine identifiers have been generated and applied.")
                self.ui_manager.display_warning("Please restart Cursor for changes to take effect.")
            else:
                self.ui_manager.display_error("Failed to completely reset machine ID.")
                self.ui_manager.display_warning("Some operations may have failed. Check the output above for details.")

        except Exception as e:
            self.ui_manager.display_error(f"Failed to reset machine ID: {str(e)}")
            self.ui_manager.display_warning("The operation was interrupted. Check file permissions and try running as administrator.")

    def view_current_machine_ids(self):
        """Display current machine ID values"""
        from rich.panel import Panel
        from rich.table import Table
        from rich.text import Text

        self.ui_manager.clear_screen()
        self.ui_manager.display_header()

        # Main title
        title_panel = Panel(
            Text("Current Machine ID Values", style="bold white", justify="center"),
            border_style="cyan",
            padding=(0, 2)
        )
        self.ui_manager.console.print(title_panel)
        self.ui_manager.console.print()

        try:
            # Get current values from all sources
            storage_values = self._get_storage_json_values()
            sqlite_values = self._get_sqlite_values()
            registry_values = self._get_registry_values()
            machine_id_file_content = self._get_machine_id_file_content()

            # Display Storage.json values
            self._display_storage_json_panel(storage_values)

            # Display SQLite database values
            self._display_sqlite_panel(sqlite_values)

            # Display Windows registry values
            self._display_registry_panel(registry_values)

            # Display machineId file content
            self._display_machine_id_file_panel(machine_id_file_content)

        except Exception as e:
            self.ui_manager.display_error(f"Failed to retrieve machine ID values: {str(e)}")

    def restore_backup(self):
        """Restore backup files"""
        from rich.panel import Panel
        from rich.table import Table
        from rich.text import Text

        self.ui_manager.clear_screen()
        self.ui_manager.display_header()

        # Main title
        title_panel = Panel(
            Text("Restore Backup Files", style="bold white", justify="center"),
            border_style="cyan",
            padding=(0, 2)
        )
        self.ui_manager.console.print(title_panel)
        self.ui_manager.console.print()

        try:
            # Get available backup files
            backup_files = self._get_available_backups_with_details()

            if not backup_files:
                self._display_no_backups_panel()
                return

            # Display available backups in structured format
            self._display_backup_selection_panel(backup_files)

            # Get user selection
            choice = self.ui_manager.get_user_choice(
                f"Select backup to restore (1-{len(backup_files)}) or 'c' to cancel",
                valid_choices=[str(i) for i in range(1, len(backup_files) + 1)] + ['c', 'C']
            )

            if choice is None or choice.lower() == 'c':
                self.ui_manager.display_info("Restore operation cancelled.")
                return

            # Get selected backup
            selected_backup = backup_files[int(choice) - 1]
            filename, file_type, timestamp, full_path, file_size = selected_backup

            # Display confirmation panel
            self._display_restore_confirmation_panel(filename, file_type, timestamp, file_size)

            if not self.ui_manager.confirm_action("Do you want to proceed with the restore?"):
                self.ui_manager.display_info("Restore operation cancelled.")
                return

            # Perform restore
            success = self._restore_backup_file(full_path, file_type)

            if success:
                self.ui_manager.display_success(f"Successfully restored {file_type} from backup.")
                self.ui_manager.display_info("Please restart Cursor for changes to take effect.")
            else:
                self.ui_manager.display_error("Failed to restore backup file.")

        except Exception as e:
            self.ui_manager.display_error(f"Failed to restore backup: {str(e)}")

    def _get_storage_json_values(self):
        """Get machine ID values from storage.json"""
        try:
            import json
            from config import config

            storage_path = config.cursor_paths['storage_path']
            if not os.path.exists(storage_path):
                return None

            with open(storage_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Extract relevant machine ID values
            values = {}
            keys_to_extract = [
                'telemetry.devDeviceId',
                'telemetry.macMachineId',
                'telemetry.machineId',
                'telemetry.sqmId',
                'storage.serviceMachineId'
            ]

            for key in keys_to_extract:
                if key in data:
                    values[key] = data[key]

            return values if values else None

        except Exception:
            return None

    def _get_sqlite_values(self):
        """Get machine ID values from SQLite database"""
        try:
            import sqlite3
            from config import config

            sqlite_path = config.cursor_paths['sqlite_path']
            if not os.path.exists(sqlite_path):
                return None

            conn = sqlite3.connect(sqlite_path)
            cursor = conn.cursor()

            # Get all relevant machine ID values
            keys_to_extract = [
                'telemetry.devDeviceId',
                'telemetry.macMachineId',
                'telemetry.machineId',
                'telemetry.sqmId',
                'storage.serviceMachineId'
            ]

            values = {}
            for key in keys_to_extract:
                cursor.execute("SELECT value FROM ItemTable WHERE key = ?", (key,))
                result = cursor.fetchone()
                if result:
                    values[key] = result[0]

            conn.close()
            return values if values else None

        except Exception:
            return None

    def _get_registry_values(self):
        """Get machine ID values from Windows registry"""
        try:
            import winreg

            values = {}

            # Get MachineGuid from Cryptography key
            try:
                key = winreg.OpenKey(
                    winreg.HKEY_LOCAL_MACHINE,
                    "SOFTWARE\\Microsoft\\Cryptography",
                    0,
                    winreg.KEY_READ | winreg.KEY_WOW64_64KEY
                )
                machine_guid, _ = winreg.QueryValueEx(key, "MachineGuid")
                values["MachineGuid"] = machine_guid
                winreg.CloseKey(key)
            except Exception:
                pass

            # Get MachineId from SQMClient key
            try:
                key = winreg.OpenKey(
                    winreg.HKEY_LOCAL_MACHINE,
                    "SOFTWARE\\Microsoft\\SQMClient",
                    0,
                    winreg.KEY_READ | winreg.KEY_WOW64_64KEY
                )
                machine_id, _ = winreg.QueryValueEx(key, "MachineId")
                values["MachineId"] = machine_id
                winreg.CloseKey(key)
            except Exception:
                pass

            return values if values else None

        except Exception:
            return None

    def _get_machine_id_file_content(self):
        """Get content of machineId file"""
        try:
            from config import config

            machine_id_path = config.reset_machine_id_paths['machine_id_path']
            if not os.path.exists(machine_id_path):
                return None

            with open(machine_id_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()

            return content if content else None

        except Exception:
            return None

    def _get_available_backups(self):
        """Get list of available backup files"""
        try:
            from config import config
            import re
            from datetime import datetime

            backup_dir = config.reset_machine_id_paths['reset_backups_dir']
            if not os.path.exists(backup_dir):
                return []

            backup_files = []

            # Define backup file patterns and their types
            patterns = {
                r'storage\.json\.backup\.(\d{8}_\d{6})': 'Storage JSON',
                r'machineId\.backup\.(\d{8}_\d{6})': 'Machine ID File',
                r'workbench\.desktop\.main\.js\.backup\.(\d{8}_\d{6})': 'Workbench JS',
                r'main\.js\.backup\.(\d{8}_\d{6})': 'Main JS',
                r'main\.js\.patch\.backup\.(\d{8}_\d{6})': 'Main JS Patch'
            }

            # Scan backup directory
            for filename in os.listdir(backup_dir):
                full_path = os.path.join(backup_dir, filename)
                if os.path.isfile(full_path):
                    for pattern, file_type in patterns.items():
                        match = re.match(pattern, filename)
                        if match:
                            timestamp_str = match.group(1)
                            try:
                                # Parse timestamp for display
                                timestamp_obj = datetime.strptime(timestamp_str, '%Y%m%d_%H%M%S')
                                formatted_timestamp = timestamp_obj.strftime('%Y-%m-%d %H:%M:%S')
                            except:
                                formatted_timestamp = timestamp_str

                            backup_files.append((filename, file_type, formatted_timestamp, full_path))
                            break

            # Sort by timestamp (newest first)
            backup_files.sort(key=lambda x: x[0], reverse=True)
            return backup_files

        except Exception:
            return []

    def _restore_backup_file(self, backup_path, file_type):
        """Restore a backup file to its original location"""
        try:
            import shutil
            from config import config

            # Determine target path based on file type
            if file_type == 'Storage JSON':
                target_path = config.cursor_paths['storage_path']
            elif file_type == 'Machine ID File':
                target_path = config.reset_machine_id_paths['machine_id_path']
            elif file_type == 'Workbench JS':
                target_path = config.reset_machine_id_paths['workbench_path']
            elif file_type in ['Main JS', 'Main JS Patch']:
                target_path = config.reset_machine_id_paths['main_path']
            else:
                return False

            # Create target directory if it doesn't exist
            os.makedirs(os.path.dirname(target_path), exist_ok=True)

            # Create a backup of current file before restoring
            if os.path.exists(target_path):
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                current_backup = f"{target_path}.pre-restore.{timestamp}"
                shutil.copy2(target_path, current_backup)

            # Restore the backup file
            shutil.copy2(backup_path, target_path)
            return True

        except Exception:
            return False

    def _display_storage_json_panel(self, storage_values):
        """Display storage.json values in a structured panel"""
        from rich.panel import Panel
        from rich.table import Table
        from rich.text import Text

        if storage_values:
            # Create table for storage values
            storage_table = Table(show_header=True, header_style="bold white", box=None, padding=(0, 1))
            storage_table.add_column("Key", style="cyan", width=25)
            storage_table.add_column("Value", style="green")

            for key, value in storage_values.items():
                # Truncate long values for better display
                display_value = value if len(str(value)) <= 60 else f"{str(value)[:57]}..."
                storage_table.add_row(key, display_value)

            storage_panel = Panel(
                storage_table,
                title="[bold]Storage.json Values[/bold]",
                border_style="cyan",
                padding=(1, 2)
            )
        else:
            # Empty state message
            empty_message = Text("No values found or file not accessible", style="yellow italic", justify="center")
            storage_panel = Panel(
                empty_message,
                title="[bold]Storage.json Values[/bold]",
                border_style="cyan",
                padding=(1, 2)
            )

        self.ui_manager.console.print(storage_panel)
        self.ui_manager.console.print()

    def _display_sqlite_panel(self, sqlite_values):
        """Display SQLite database values in a structured panel"""
        from rich.panel import Panel
        from rich.table import Table
        from rich.text import Text

        if sqlite_values:
            # Create table for SQLite values
            sqlite_table = Table(show_header=True, header_style="bold white", box=None, padding=(0, 1))
            sqlite_table.add_column("Key", style="blue", width=25)
            sqlite_table.add_column("Value", style="green")

            for key, value in sqlite_values.items():
                # Truncate long values for better display
                display_value = value if len(str(value)) <= 60 else f"{str(value)[:57]}..."
                sqlite_table.add_row(key, display_value)

            sqlite_panel = Panel(
                sqlite_table,
                title="[bold]SQLite Database Values[/bold]",
                border_style="blue",
                padding=(1, 2)
            )
        else:
            # Empty state message
            empty_message = Text("No values found or database not accessible", style="yellow italic", justify="center")
            sqlite_panel = Panel(
                empty_message,
                title="[bold]SQLite Database Values[/bold]",
                border_style="blue",
                padding=(1, 2)
            )

        self.ui_manager.console.print(sqlite_panel)
        self.ui_manager.console.print()

    def _display_registry_panel(self, registry_values):
        """Display Windows registry values in a structured panel"""
        from rich.panel import Panel
        from rich.table import Table
        from rich.text import Text

        if registry_values:
            # Create table for registry values
            registry_table = Table(show_header=True, header_style="bold white", box=None, padding=(0, 1))
            registry_table.add_column("Registry Key", style="yellow", width=25)
            registry_table.add_column("Value", style="green")

            for key, value in registry_values.items():
                registry_table.add_row(key, str(value))

            registry_panel = Panel(
                registry_table,
                title="[bold]Windows Registry Values[/bold]",
                border_style="yellow",
                padding=(1, 2)
            )
        else:
            # Empty state message
            empty_message = Text("Values not accessible (may require administrator privileges)", style="yellow italic", justify="center")
            registry_panel = Panel(
                empty_message,
                title="[bold]Windows Registry Values[/bold]",
                border_style="yellow",
                padding=(1, 2)
            )

        self.ui_manager.console.print(registry_panel)
        self.ui_manager.console.print()

    def _display_machine_id_file_panel(self, machine_id_file_content):
        """Display machineId file content in a structured panel"""
        from rich.panel import Panel
        from rich.table import Table
        from rich.text import Text

        if machine_id_file_content:
            # Create table for file content
            file_table = Table(show_header=True, header_style="bold white", box=None, padding=(0, 1))
            file_table.add_column("File Path", style="green", width=25)
            file_table.add_column("Content", style="green")

            file_table.add_row("machineId", machine_id_file_content)

            file_panel = Panel(
                file_table,
                title="[bold]MachineId File Content[/bold]",
                border_style="green",
                padding=(1, 2)
            )
        else:
            # Empty state message
            empty_message = Text("File not found or not accessible", style="yellow italic", justify="center")
            file_panel = Panel(
                empty_message,
                title="[bold]MachineId File Content[/bold]",
                border_style="green",
                padding=(1, 2)
            )

        self.ui_manager.console.print(file_panel)
        self.ui_manager.console.print()

    def _get_available_backups_with_details(self):
        """Get list of available backup files with detailed information"""
        try:
            from config import config
            import re
            from datetime import datetime

            backup_dir = config.reset_machine_id_paths['reset_backups_dir']
            if not os.path.exists(backup_dir):
                return []

            backup_files = []

            # Define backup file patterns and their types
            patterns = {
                r'storage\.json\.backup\.(\d{8}_\d{6})': 'Storage JSON',
                r'machineId\.backup\.(\d{8}_\d{6})': 'Machine ID File',
                r'workbench\.desktop\.main\.js\.backup\.(\d{8}_\d{6})': 'Workbench JS',
                r'main\.js\.backup\.(\d{8}_\d{6})': 'Main JS',
                r'main\.js\.patch\.backup\.(\d{8}_\d{6})': 'Main JS Patch'
            }

            # Scan backup directory
            for filename in os.listdir(backup_dir):
                full_path = os.path.join(backup_dir, filename)
                if os.path.isfile(full_path):
                    for pattern, file_type in patterns.items():
                        match = re.match(pattern, filename)
                        if match:
                            timestamp_str = match.group(1)
                            try:
                                # Parse timestamp for display
                                timestamp_obj = datetime.strptime(timestamp_str, '%Y%m%d_%H%M%S')
                                formatted_timestamp = timestamp_obj.strftime('%Y-%m-%d %H:%M:%S')
                            except:
                                formatted_timestamp = timestamp_str

                            # Get file size
                            try:
                                file_size = os.path.getsize(full_path)
                                if file_size < 1024:
                                    size_str = f"{file_size} B"
                                elif file_size < 1024 * 1024:
                                    size_str = f"{file_size / 1024:.1f} KB"
                                else:
                                    size_str = f"{file_size / (1024 * 1024):.1f} MB"
                            except:
                                size_str = "Unknown"

                            backup_files.append((filename, file_type, formatted_timestamp, full_path, size_str))
                            break

            # Sort by timestamp (newest first)
            backup_files.sort(key=lambda x: x[0], reverse=True)
            return backup_files

        except Exception:
            return []

    def _display_no_backups_panel(self):
        """Display panel when no backup files are found"""
        from rich.panel import Panel
        from rich.text import Text

        empty_message = Text("No backup files found in the backup directory", style="yellow italic", justify="center")
        empty_panel = Panel(
            empty_message,
            title="[bold]Available Backup Files[/bold]",
            border_style="yellow",
            padding=(2, 4)
        )
        self.ui_manager.console.print(empty_panel)
        self.ui_manager.console.print()

    def _display_backup_selection_panel(self, backup_files):
        """Display backup files in a structured table panel"""
        from rich.panel import Panel
        from rich.table import Table

        # Create table for backup files
        backup_table = Table(show_header=True, header_style="bold white", box=None, padding=(0, 1))
        backup_table.add_column("#", style="white", width=3, justify="center")
        backup_table.add_column("File Type", style="white", width=15)
        backup_table.add_column("Filename", style="white", width=35)
        backup_table.add_column("Timestamp", style="white", width=20)
        backup_table.add_column("Size", style="white", width=10, justify="right")

        # Color mapping for file types
        type_colors = {
            'Storage JSON': 'cyan',
            'Machine ID File': 'blue',
            'Workbench JS': 'yellow',
            'Main JS': 'green',
            'Main JS Patch': 'green'
        }

        for i, (filename, file_type, timestamp, full_path, file_size) in enumerate(backup_files, 1):
            color = type_colors.get(file_type, 'white')

            # Truncate filename if too long
            display_filename = filename if len(filename) <= 33 else f"{filename[:30]}..."

            backup_table.add_row(
                str(i),
                f"[{color}]{file_type}[/{color}]",
                f"[{color}]{display_filename}[/{color}]",
                timestamp,
                file_size
            )

        backup_panel = Panel(
            backup_table,
            title="[bold]Available Backup Files[/bold]",
            border_style="cyan",
            padding=(1, 2)
        )

        self.ui_manager.console.print(backup_panel)
        self.ui_manager.console.print()

    def _display_restore_confirmation_panel(self, filename, file_type, timestamp, file_size):
        """Display confirmation panel for restore operation"""
        from rich.panel import Panel
        from rich.table import Table

        # Create confirmation table
        confirm_table = Table(show_header=False, box=None, padding=(0, 1))
        confirm_table.add_column("Property", style="yellow", width=15)
        confirm_table.add_column("Value", style="white")

        confirm_table.add_row("File Type:", f"[bold]{file_type}[/bold]")
        confirm_table.add_row("Filename:", filename)
        confirm_table.add_row("Timestamp:", timestamp)
        confirm_table.add_row("File Size:", file_size)

        confirm_panel = Panel(
            confirm_table,
            title="[bold red]⚠ Restore Confirmation ⚠[/bold red]",
            border_style="red",
            padding=(1, 2)
        )

        self.ui_manager.console.print(confirm_panel)
        self.ui_manager.console.print()

        # Warning message
        self.ui_manager.display_warning("The current file will be overwritten!")
        self.ui_manager.display_warning("A backup of the current file will be created before restore.")