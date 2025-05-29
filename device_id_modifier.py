"""
Device ID Modifier Module for Cursor-Tools
Core functionality for changing Windows device IDs
"""

from registry_manager import RegistryManager
from ui_manager import UIManager
from rich.table import Table

class DeviceIDModifier:
    def __init__(self):
        self.registry_manager = RegistryManager()
        self.ui_manager = UIManager()

    def run_device_id_menu(self):
        """Run the Device ID Modifier sub-menu"""
        while True:
            self.ui_manager.clear_screen()
            self.ui_manager.display_header()
            self.ui_manager.display_device_id_menu()

            choice = self.ui_manager.get_user_choice(
                "Select an option",
                valid_choices=["1", "2", "3", "4"]
            )

            if choice is None:  # User pressed Ctrl+C
                break
            elif choice == "1":
                self.change_device_id()
            elif choice == "2":
                self.restore_backup()
            elif choice == "3":
                self.view_current_values()
            elif choice == "4":
                break

            if choice in ["1", "2", "3"]:
                self.ui_manager.pause()

    def change_device_id(self):
        """Change device ID with confirmation and backup"""
        self.ui_manager.clear_screen()
        self.ui_manager.display_header()

        # Check admin privileges
        if not self.registry_manager.check_admin_privileges():
            self.ui_manager.display_error("Administrator privileges required!")
            self.ui_manager.display_admin_warning()
            return

        self.ui_manager.display_warning("This operation will modify Windows registry entries.")
        self.ui_manager.display_info("A backup will be created automatically before making changes.")

        # Get confirmation
        if not self.ui_manager.confirm_action("Do you want to proceed with changing the device IDs?"):
            self.ui_manager.display_info("Operation cancelled.")
            return

        # Perform the modification
        try:
            self.ui_manager.display_info("Creating backup and modifying device IDs...")
            before_values, after_values = self.registry_manager.modify_device_ids()

            self.ui_manager.display_success("Device IDs successfully modified!")

            # Display comparison
            self.ui_manager.display_comparison(before_values, after_values)

        except Exception as e:
            self.ui_manager.display_error(f"Failed to modify device IDs: {str(e)}")

    def restore_backup(self):
        """Restore from backup with selection menu"""
        self.ui_manager.clear_screen()
        self.ui_manager.display_header()

        # Check admin privileges
        if not self.registry_manager.check_admin_privileges():
            self.ui_manager.display_error("Administrator privileges required!")
            self.ui_manager.display_admin_warning()
            return

        # List available backups
        backups = self.registry_manager.list_backups()

        if not backups:
            self.ui_manager.display_warning("No Device ID backups found.")
            self.ui_manager.display_info("Backups are automatically created when you use 'Change Device ID'.")
            return

        # Display available backups using the same format as Pro UI Features
        from rich.table import Table
        from rich.panel import Panel

        backup_table = Table(show_header=True, box=None, padding=(0, 1))
        backup_table.add_column("No.", style="cyan", width=4)
        backup_table.add_column("Backup Name", style="white")
        backup_table.add_column("Date", style="yellow")
        backup_table.add_column("Files", style="green")
        backup_table.add_column("Description", style="white")

        for i, backup in enumerate(backups, 1):
            backup_table.add_row(
                str(i),
                backup["name"][:30] + "..." if len(backup["name"]) > 30 else backup["name"],
                backup["formatted_date"],
                str(backup["file_count"]),
                backup["description"][:40] + "..." if len(backup["description"]) > 40 else backup["description"]
            )

        backup_panel = Panel(
            backup_table,
            title="[bold]Available Device ID Backups[/bold]",
            border_style="bright_yellow",
            padding=(1, 2)
        )

        self.ui_manager.console.print(backup_panel)

        # Get user choice
        try:
            choice = self.ui_manager.get_user_choice(
                f"Select backup to restore (1-{len(backups)}) or 'c' to cancel",
                valid_choices=[str(i) for i in range(1, len(backups) + 1)] + ["c", "C"]
            )

            if choice is None or choice.lower() == 'c':
                self.ui_manager.display_info("Restore operation cancelled.")
                return

            selected_backup = backups[int(choice) - 1]

            # Confirm restore
            self.ui_manager.display_warning(f"This will restore backup: {selected_backup['name']}")
            self.ui_manager.display_warning("Current Device ID registry values will be overwritten!")

            if not self.ui_manager.confirm_action("Are you sure you want to restore this backup?"):
                self.ui_manager.display_info("Restore operation cancelled.")
                return

            # Perform restore
            self.ui_manager.display_info("Restoring registry values from backup...")

            # Get current values before restore
            before_values = self.registry_manager.read_registry_values()

            # Restore from backup
            success = self.registry_manager.restore_backup(selected_backup['path'])

            if success:
                # Get values after restore
                after_values = self.registry_manager.read_registry_values()

                self.ui_manager.display_success("Device ID registry values successfully restored!")
                self.ui_manager.display_comparison(before_values, after_values)
            else:
                self.ui_manager.display_error("Failed to restore registry values.")

        except (ValueError, IndexError):
            self.ui_manager.display_error("Invalid selection. Please try again.")
        except Exception as e:
            self.ui_manager.display_error(f"Restore failed: {str(e)}")

    def view_current_values(self):
        """Display current device registry values in structured format"""
        from rich.panel import Panel
        from rich.table import Table
        from rich.text import Text

        self.ui_manager.clear_screen()
        self.ui_manager.display_header()

        # Main title
        title_panel = Panel(
            Text("Current Device Registry Values", style="bold white", justify="center"),
            border_style="cyan",
            padding=(0, 2)
        )
        self.ui_manager.console.print(title_panel)
        self.ui_manager.console.print()

        try:
            # Get current registry values
            current_values = self.registry_manager.read_registry_values()

            # Display registry values in structured format
            self._display_device_registry_panel(current_values)

        except Exception as e:
            self.ui_manager.display_error(f"Failed to read registry values: {str(e)}")

    def _display_device_registry_panel(self, registry_values):
        """Display device registry values in a structured panel"""
        from rich.panel import Panel
        from rich.table import Table
        from rich.text import Text

        if registry_values:
            # Create table for registry values
            registry_table = Table(show_header=True, header_style="bold white", box=None, padding=(0, 1))
            registry_table.add_column("Registry Path", style="cyan", width=50)
            registry_table.add_column("Key", style="yellow", width=20)
            registry_table.add_column("Value", style="green", width=40)

            for path, keys in registry_values.items():
                for key, value in keys.items():
                    # Truncate long values for better display
                    display_value = str(value) if len(str(value)) <= 38 else f"{str(value)[:35]}..."
                    registry_table.add_row(path, key, display_value)

            registry_panel = Panel(
                registry_table,
                title="[bold]Windows Device Registry Values[/bold]",
                border_style="yellow",
                padding=(1, 2)
            )
        else:
            # Empty state message
            empty_message = Text("No registry values found or registry not accessible", style="yellow italic", justify="center")
            registry_panel = Panel(
                empty_message,
                title="[bold]Windows Device Registry Values[/bold]",
                border_style="yellow",
                padding=(1, 2)
            )

        self.ui_manager.console.print(registry_panel)
        self.ui_manager.console.print()


