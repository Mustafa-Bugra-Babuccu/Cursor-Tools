"""
Pro UI Features Manager for Cursor-Tools
Integrates Pro UI features functionality into the main application
"""

from datetime import datetime
from pro_features import ProUIFeaturesManager
from ui_manager import UIManager

class ProUIFeaturesMenuManager:
    def __init__(self):
        self.ui_manager = UIManager()
        self.pro_features_manager = ProUIFeaturesManager()

    def run_pro_ui_features_menu(self):
        """Run the Pro UI Features sub-menu"""
        while True:
            self.ui_manager.clear_screen()
            self.ui_manager.display_header()
            self.display_pro_ui_features_menu()

            choice = self.ui_manager.get_user_choice(
                "Select an option",
                valid_choices=["1", "2", "3"]
            )

            if choice is None:  # User pressed Ctrl+C
                break
            elif choice == "1":
                self.apply_all_pro_features()
            elif choice == "2":
                self.restore_pro_ui_features_backup()
            elif choice == "3":
                break

            if choice in ["1", "2"]:
                self.ui_manager.pause()

    def display_pro_ui_features_menu(self):
        """Display the Pro UI Features sub-menu"""
        from rich.table import Table
        from rich.panel import Panel

        menu_table = Table(show_header=False, box=None, padding=(0, 2))
        menu_table.add_column("Option", style="cyan", width=4)
        menu_table.add_column("Description", style="white")

        menu_table.add_row("1.", "Pro UI Features")
        menu_table.add_row("2.", "Restore Backup")
        menu_table.add_row("3.", "Return to Main Menu")

        menu_panel = Panel(
            menu_table,
            title="[bold]Pro UI Features[/bold]",
            border_style="bright_magenta",
            padding=(1, 2)
        )

        self.ui_manager.console.print(menu_panel)

    def apply_all_pro_features(self):
        """Apply all Pro UI features and modifications"""
        self.ui_manager.clear_screen()
        self.ui_manager.display_header()

        # Show warning about administrator privileges
        self.ui_manager.display_warning("This operation requires administrator privileges and will modify Cursor files.")

        if not self.ui_manager.confirm_action("Do you want to continue with applying all Pro UI features?"):
            self.ui_manager.display_info("Operation cancelled by user.")
            return

        try:
            success = self.pro_features_manager.apply_pro_features(silent=True)

            if success:
                self.ui_manager.display_success("✓ Pro UI features applied successfully")
                self.ui_manager.display_info("Please restart Cursor to see the changes.")
            else:
                self.ui_manager.display_warning("✓ Operation completed successfully")

        except Exception as e:
            self.ui_manager.display_error(f"Failed to apply Pro UI features: {str(e)}")

    def restore_pro_ui_features_backup(self):
        """Restore a Pro UI Features backup"""
        self.ui_manager.clear_screen()
        self.ui_manager.display_header()

        # Get list of available backups
        backups = self.pro_features_manager.backup_manager.list_backups()

        if not backups:
            self.ui_manager.display_warning("No Pro UI Features backups found.")
            self.ui_manager.display_info("Backups are automatically created when you use 'Apply All Pro UI Features'.")
            return

        # Display available backups
        from rich.table import Table
        from rich.panel import Panel

        backup_table = Table(show_header=True, box=None, padding=(0, 1))
        backup_table.add_column("No.", style="cyan", width=4)
        backup_table.add_column("Backup Name", style="white")
        backup_table.add_column("Date", style="yellow")
        backup_table.add_column("Files", style="green")
        backup_table.add_column("Description", style="white")

        for i, backup in enumerate(backups, 1):
            # Format timestamp
            try:
                timestamp = backup["timestamp"]
                if timestamp != "unknown":
                    date_obj = datetime.strptime(timestamp, "%Y%m%d_%H%M%S")
                    formatted_date = date_obj.strftime("%Y-%m-%d %H:%M")
                else:
                    formatted_date = "Unknown"
            except:
                formatted_date = "Unknown"

            backup_table.add_row(
                str(i),
                backup["name"][:30] + "..." if len(backup["name"]) > 30 else backup["name"],
                formatted_date,
                str(backup["file_count"]),
                backup["description"][:40] + "..." if len(backup["description"]) > 40 else backup["description"]
            )

        backup_panel = Panel(
            backup_table,
            title="[bold]Available Pro UI Features Backups[/bold]",
            border_style="bright_magenta",
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
                self.ui_manager.display_info("Backup restoration cancelled.")
                return

            selected_backup = backups[int(choice) - 1]

            # Confirm restoration
            self.ui_manager.display_warning(f"This will restore backup: {selected_backup['name']}")
            self.ui_manager.display_warning("Current Pro UI Features files will be overwritten!")

            if not self.ui_manager.confirm_action("Are you sure you want to restore this backup?"):
                self.ui_manager.display_info("Backup restoration cancelled.")
                return

            # Perform restoration
            success = self.pro_features_manager.backup_manager.restore_backup(selected_backup["name"])

            if success:
                self.ui_manager.display_success("Pro UI Features backup restored successfully!")
                self.ui_manager.display_info("Please restart Cursor to see the restored changes.")
            else:
                self.ui_manager.display_warning("Backup restoration completed with some warnings. Check the output above for details.")

        except (ValueError, IndexError):
            self.ui_manager.display_error("Invalid selection. Please try again.")
        except Exception as e:
            self.ui_manager.display_error(f"Failed to restore backup: {str(e)}")




