"""
Reset Machine ID Manager for Cursor-Tools
Integrates reset machine ID functionality into the main application
"""

import os
from reset_machine_id import MachineIDResetter
from ui_manager import UIManager
from utils import BackupManager

class ResetMachineIDManager:
    def __init__(self):
        self.ui_manager = UIManager()
        self.machine_id_resetter = MachineIDResetter()
        # Initialize backup manager for legacy backup file pattern matching
        from config import config
        self.backup_manager = BackupManager(config.reset_machine_id_paths['reset_backups_dir'])

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

        # Prompt user to create a backup first
        self.ui_manager.console.print()
        self.ui_manager.display_info("Before proceeding, it's recommended to create a comprehensive backup.")

        if self.ui_manager.confirm_action("Would you like to create a backup before resetting machine ID?"):
            backup_name = self._create_machine_id_backup()
            if backup_name:
                self.ui_manager.display_success(f"Backup created successfully: {backup_name}")
                self.ui_manager.console.print()
            else:
                self.ui_manager.display_warning("Backup creation failed, but you can still proceed with the reset.")
                if not self.ui_manager.confirm_action("Do you want to continue without a backup?"):
                    self.ui_manager.display_info("Operation cancelled.")
                    return

        # Get confirmation for the reset operation
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
            # Get available backup files and folders
            backup_items = self._get_available_backups_and_folders()

            if not backup_items:
                self._display_no_backups_panel()
                return

            # Display available backups in structured format
            self._display_backup_selection_panel_enhanced(backup_items)

            # Get user selection
            choice = self.ui_manager.get_user_choice(
                f"Select backup to restore (1-{len(backup_items)}) or 'c' to cancel",
                valid_choices=[str(i) for i in range(1, len(backup_items) + 1)] + ['c', 'C']
            )

            if choice is None or choice.lower() == 'c':
                self.ui_manager.display_info("Restore operation cancelled.")
                return

            # Get selected backup
            selected_backup = backup_items[int(choice) - 1]

            # Check if it's a comprehensive backup folder or individual file
            if selected_backup['type'] == 'comprehensive_folder':
                success = self._restore_comprehensive_backup(selected_backup)
            else:
                # Handle individual file backup (legacy)
                filename, file_type, timestamp, full_path, file_size = (
                    selected_backup['name'], selected_backup['file_type'],
                    selected_backup['timestamp'], selected_backup['path'],
                    selected_backup['size']
                )

                # Display confirmation panel
                self._display_restore_confirmation_panel(filename, file_type, timestamp, file_size)

                if not self.ui_manager.confirm_action("Do you want to proceed with the restore?"):
                    self.ui_manager.display_info("Restore operation cancelled.")
                    return

                # Perform restore
                success = self._restore_backup_file(full_path, file_type)

            if success:
                self.ui_manager.display_success("Backup restored successfully!")
                self.ui_manager.display_info("Please restart Cursor for changes to take effect.")
            else:
                self.ui_manager.display_error("Failed to restore backup.")

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
        """Get list of available backup files using centralized BackupManager"""
        try:
            from config import config

            backup_dir = config.reset_machine_id_paths['reset_backups_dir']
            if not os.path.exists(backup_dir):
                return []

            # Define backup file patterns and their types for legacy compatibility
            patterns = {
                r'storage\.json\.backup\.(\d{8}_\d{6})': 'Storage JSON',
                r'machineId\.backup\.(\d{8}_\d{6})': 'Machine ID File',
                r'workbench\.desktop\.main\.js\.backup\.(\d{8}_\d{6})': 'Workbench JS',
                r'main\.js\.backup\.(\d{8}_\d{6})': 'Main JS',
                r'main\.js\.patch\.backup\.(\d{8}_\d{6})': 'Main JS Patch'
            }

            # Use centralized backup manager for pattern-based retrieval
            backup_files_data = self.backup_manager.get_backup_files_by_pattern(backup_dir, patterns)

            # Convert to legacy format for compatibility
            backup_files = []
            for backup_info in backup_files_data:
                backup_files.append((
                    backup_info['filename'],
                    backup_info['file_type'],
                    backup_info['formatted_date'],
                    backup_info['path']
                ))

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

    def _create_machine_id_backup(self):
        """Create a comprehensive backup of all machine ID related files"""
        try:
            import json
            import shutil
            from datetime import datetime
            from config import config

            # Create timestamp for backup folder
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"machine_id_backup_{timestamp}"

            # Create backup directory structure
            backup_dir = config.reset_machine_id_paths['reset_backups_dir']
            backup_folder = os.path.join(backup_dir, backup_name)
            os.makedirs(backup_folder, exist_ok=True)

            # Create backup manifest
            manifest = {
                "backup_name": backup_name,
                "timestamp": timestamp,
                "backup_type": "machine_id_comprehensive",
                "files": [],
                "description": "Comprehensive machine ID backup including all related files and registry values"
            }

            files_backed_up = 0

            # Backup storage.json
            storage_path = config.cursor_paths['storage_path']
            if os.path.exists(storage_path):
                storage_backup = os.path.join(backup_folder, "storage.json")
                shutil.copy2(storage_path, storage_backup)
                manifest["files"].append({"type": "storage", "original": storage_path, "backup": "storage.json"})
                files_backed_up += 1
                self.ui_manager.display_info("✓ Backed up storage.json")

            # Backup SQLite database
            sqlite_path = config.cursor_paths['sqlite_path']
            if os.path.exists(sqlite_path):
                sqlite_backup = os.path.join(backup_folder, "state.vscdb")
                shutil.copy2(sqlite_path, sqlite_backup)
                manifest["files"].append({"type": "database", "original": sqlite_path, "backup": "state.vscdb"})
                files_backed_up += 1
                self.ui_manager.display_info("✓ Backed up SQLite database")

            # Backup machine ID file
            machine_id_path = config.reset_machine_id_paths['machine_id_path']
            if os.path.exists(machine_id_path):
                machine_id_backup = os.path.join(backup_folder, "machineId")
                shutil.copy2(machine_id_path, machine_id_backup)
                manifest["files"].append({"type": "machine_id", "original": machine_id_path, "backup": "machineId"})
                files_backed_up += 1
                self.ui_manager.display_info("✓ Backed up machine ID file")

            # Backup workbench file
            workbench_path = config.reset_machine_id_paths['workbench_path']
            if os.path.exists(workbench_path):
                workbench_backup = os.path.join(backup_folder, "workbench.desktop.main.js")
                shutil.copy2(workbench_path, workbench_backup)
                manifest["files"].append({"type": "workbench", "original": workbench_path, "backup": "workbench.desktop.main.js"})
                files_backed_up += 1
                self.ui_manager.display_info("✓ Backed up workbench file")

            # Backup main.js file
            main_path = config.reset_machine_id_paths['main_path']
            if os.path.exists(main_path):
                main_backup = os.path.join(backup_folder, "main.js")
                shutil.copy2(main_path, main_backup)
                manifest["files"].append({"type": "main_js", "original": main_path, "backup": "main.js"})
                files_backed_up += 1
                self.ui_manager.display_info("✓ Backed up main.js file")

            # Export registry values
            registry_values = self._get_registry_values()
            if registry_values:
                registry_backup = os.path.join(backup_folder, "registry_values.json")
                with open(registry_backup, "w", encoding="utf-8") as f:
                    json.dump(registry_values, f, indent=2)
                manifest["files"].append({"type": "registry", "original": "Windows Registry", "backup": "registry_values.json"})
                files_backed_up += 1
                self.ui_manager.display_info("✓ Exported registry values")

            # Save manifest
            manifest_path = os.path.join(backup_folder, "backup_manifest.json")
            with open(manifest_path, "w", encoding="utf-8") as f:
                json.dump(manifest, f, indent=2)

            if files_backed_up > 0:
                self.ui_manager.display_success(f"Comprehensive backup created with {files_backed_up} files")
                return backup_name
            else:
                self.ui_manager.display_warning("No files were found to backup")
                # Remove empty backup folder
                try:
                    os.rmdir(backup_folder)
                except:
                    pass
                return None

        except Exception as e:
            self.ui_manager.display_error(f"Failed to create backup: {str(e)}")
            return None

    def _get_available_backups_and_folders(self):
        """Get list of available backup files and comprehensive backup folders"""
        try:
            from config import config
            import re
            import json
            from datetime import datetime

            backup_dir = config.reset_machine_id_paths['reset_backups_dir']
            if not os.path.exists(backup_dir):
                return []

            backup_items = []

            # First, scan for comprehensive backup folders
            for item in os.listdir(backup_dir):
                item_path = os.path.join(backup_dir, item)
                if os.path.isdir(item_path):
                    manifest_path = os.path.join(item_path, "backup_manifest.json")
                    if os.path.exists(manifest_path):
                        try:
                            with open(manifest_path, "r", encoding="utf-8") as f:
                                manifest = json.load(f)

                            backup_items.append({
                                'type': 'comprehensive_folder',
                                'name': manifest.get('backup_name', item),
                                'timestamp': manifest.get('timestamp', 'unknown'),
                                'description': manifest.get('description', 'Comprehensive backup'),
                                'file_count': len(manifest.get('files', [])),
                                'path': item_path,
                                'manifest': manifest
                            })
                        except:
                            # If manifest is corrupted, still show the folder
                            backup_items.append({
                                'type': 'comprehensive_folder',
                                'name': item,
                                'timestamp': 'unknown',
                                'description': 'Backup folder (manifest corrupted)',
                                'file_count': 0,
                                'path': item_path,
                                'manifest': None
                            })

            # Then, scan for individual backup files (legacy support)
            patterns = {
                r'storage\.json\.backup\.(\d{8}_\d{6})': 'Storage JSON',
                r'machineId\.backup\.(\d{8}_\d{6})': 'Machine ID File',
                r'workbench\.desktop\.main\.js\.backup\.(\d{8}_\d{6})': 'Workbench JS',
                r'main\.js\.backup\.(\d{8}_\d{6})': 'Main JS',
                r'main\.js\.patch\.backup\.(\d{8}_\d{6})': 'Main JS Patch'
            }

            for filename in os.listdir(backup_dir):
                full_path = os.path.join(backup_dir, filename)
                if os.path.isfile(full_path):
                    for pattern, file_type in patterns.items():
                        match = re.match(pattern, filename)
                        if match:
                            timestamp_str = match.group(1)
                            try:
                                timestamp_obj = datetime.strptime(timestamp_str, '%Y%m%d_%H%M%S')
                                formatted_timestamp = timestamp_obj.strftime('%Y-%m-%d %H:%M:%S')
                            except:
                                formatted_timestamp = timestamp_str

                            # Get file size
                            try:
                                size_bytes = os.path.getsize(full_path)
                                if size_bytes < 1024:
                                    size_str = f"{size_bytes} B"
                                elif size_bytes < 1024 * 1024:
                                    size_str = f"{size_bytes / 1024:.1f} KB"
                                else:
                                    size_str = f"{size_bytes / (1024 * 1024):.1f} MB"
                            except:
                                size_str = "Unknown"

                            backup_items.append({
                                'type': 'individual_file',
                                'name': filename,
                                'file_type': file_type,
                                'timestamp': formatted_timestamp,
                                'size': size_str,
                                'path': full_path
                            })
                            break

            # Sort by timestamp (newest first)
            def sort_key(item):
                if item['type'] == 'comprehensive_folder':
                    return item['timestamp']
                else:
                    return item['name']

            backup_items.sort(key=sort_key, reverse=True)
            return backup_items

        except Exception:
            return []

    def _display_backup_selection_panel_enhanced(self, backup_items):
        """Display backup files and folders in a structured table panel"""
        from rich.panel import Panel
        from rich.table import Table
        from datetime import datetime

        # Create table for backup items
        backup_table = Table(show_header=True, header_style="bold white", box=None, padding=(0, 1))
        backup_table.add_column("#", style="white", width=3, justify="center")
        backup_table.add_column("Type", style="white", width=12)
        backup_table.add_column("Name", style="white", width=30)
        backup_table.add_column("Timestamp", style="white", width=20)
        backup_table.add_column("Info", style="white", width=15, justify="right")

        # Color mapping for types
        type_colors = {
            'comprehensive_folder': 'bright_green',
            'individual_file': 'cyan'
        }

        for i, item in enumerate(backup_items, 1):
            if item['type'] == 'comprehensive_folder':
                color = type_colors['comprehensive_folder']
                type_display = f"[{color}]Comprehensive[/{color}]"
                name_display = item['name'][:28] + "..." if len(item['name']) > 28 else item['name']

                # Format timestamp
                try:
                    if item['timestamp'] != 'unknown':
                        timestamp_obj = datetime.strptime(item['timestamp'], "%Y%m%d_%H%M%S")
                        formatted_timestamp = timestamp_obj.strftime("%Y-%m-%d %H:%M")
                    else:
                        formatted_timestamp = "Unknown"
                except:
                    formatted_timestamp = "Unknown"

                info_display = f"{item['file_count']} files"
            else:
                color = type_colors['individual_file']
                type_display = f"[{color}]{item['file_type']}[/{color}]"
                name_display = item['name'][:28] + "..." if len(item['name']) > 28 else item['name']
                formatted_timestamp = item['timestamp']
                info_display = item['size']

            backup_table.add_row(
                str(i),
                type_display,
                f"[{color}]{name_display}[/{color}]",
                formatted_timestamp,
                info_display
            )

        backup_panel = Panel(
            backup_table,
            title="[bold]Available Backups[/bold]",
            border_style="cyan",
            padding=(1, 2)
        )

        self.ui_manager.console.print(backup_panel)
        self.ui_manager.console.print()

    def _restore_comprehensive_backup(self, backup_info):
        """Restore a comprehensive backup folder"""
        try:
            import json
            import shutil
            from config import config

            # Display confirmation
            self.ui_manager.display_warning(f"This will restore comprehensive backup: {backup_info['name']}")
            self.ui_manager.display_warning("All current machine ID related files will be overwritten!")
            self.ui_manager.display_info(f"This backup contains {backup_info['file_count']} files")

            if not self.ui_manager.confirm_action("Are you sure you want to restore this comprehensive backup?"):
                self.ui_manager.display_info("Restore operation cancelled.")
                return False

            manifest = backup_info['manifest']
            if not manifest:
                self.ui_manager.display_error("Backup manifest is corrupted or missing.")
                return False

            backup_folder = backup_info['path']
            restored_files = 0
            failed_files = 0

            self.ui_manager.display_info("Starting comprehensive restore...")

            # Restore each file from the manifest
            for file_info in manifest.get('files', []):
                try:
                    file_type = file_info['type']
                    backup_file_path = os.path.join(backup_folder, file_info['backup'])
                    original_path = file_info['original']

                    if not os.path.exists(backup_file_path):
                        self.ui_manager.display_warning(f"⚠ Backup file missing: {file_info['backup']}")
                        failed_files += 1
                        continue

                    # Create directory if needed
                    os.makedirs(os.path.dirname(original_path), exist_ok=True)

                    # Create backup of current file before restoring
                    if os.path.exists(original_path):
                        from datetime import datetime
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        current_backup = f"{original_path}.pre-restore.{timestamp}"
                        shutil.copy2(original_path, current_backup)

                    # Restore the file
                    shutil.copy2(backup_file_path, original_path)
                    self.ui_manager.display_info(f"✓ Restored {file_type}: {os.path.basename(original_path)}")
                    restored_files += 1

                except Exception as e:
                    self.ui_manager.display_error(f"✗ Failed to restore {file_info.get('backup', 'unknown')}: {str(e)}")
                    failed_files += 1

            # Handle registry values if present
            registry_backup_path = os.path.join(backup_folder, "registry_values.json")
            if os.path.exists(registry_backup_path):
                try:
                    with open(registry_backup_path, "r", encoding="utf-8") as f:
                        registry_values = json.load(f)

                    self.ui_manager.display_info("Registry values were exported in the backup.")
                    self.ui_manager.display_warning("Registry restoration requires manual intervention due to security restrictions.")
                    self.ui_manager.display_info(f"Registry backup saved at: {registry_backup_path}")
                except Exception as e:
                    self.ui_manager.display_warning(f"Could not read registry backup: {str(e)}")

            # Summary
            if failed_files == 0:
                self.ui_manager.display_success(f"Comprehensive backup restored successfully! {restored_files} files restored.")
                return True
            else:
                self.ui_manager.display_warning(f"Backup partially restored: {restored_files} files restored, {failed_files} failed.")
                return False

        except Exception as e:
            self.ui_manager.display_error(f"Failed to restore comprehensive backup: {str(e)}")
            return False