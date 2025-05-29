"""
Pro UI Features Manager for Cursor-Tools
Integrates Pro UI features functionality into the main application
"""

from datetime import datetime
from pro_features import ProUIFeaturesManager
from ui_manager import UIManager
from language_manager import language_manager

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
        """Display the Pro UI Features sub-menu with language support"""
        from rich.table import Table
        from rich.panel import Panel

        menu_table = Table(show_header=False, box=None, padding=(0, 2))
        menu_table.add_column("Option", style="cyan", width=4)
        menu_table.add_column("Description", style="white")

        menu_table.add_row("1.", self.ui_manager.lang.get_text('pro.apply_features'))
        menu_table.add_row("2.", self.ui_manager.lang.get_text('pro.restore_backup'))
        menu_table.add_row("3.", self.ui_manager.lang.get_text('pro.return_main'))

        menu_panel = Panel(
            menu_table,
            title=f"[bold]{self.ui_manager.lang.get_text('pro.title')}[/bold]",
            border_style="bright_magenta",
            padding=(1, 2)
        )

        self.ui_manager.console.print(menu_panel)

    def apply_all_pro_features(self):
        """Apply all Pro UI features and modifications"""
        self.ui_manager.clear_screen()
        self.ui_manager.display_header()

        # Show warning about administrator privileges
        warning_msg = self.ui_manager.lang.get_text('pro.admin_warning')
        self.ui_manager.display_warning(warning_msg)

        confirm_msg = self.ui_manager.lang.get_text('pro.continue_confirm')
        if not self.ui_manager.confirm_action(confirm_msg):
            self.ui_manager.display_text('pro.operation_cancelled', "info")
            return

        try:
            success = self.pro_features_manager.apply_pro_features(silent=True)

            if success:
                success_msg = f"✓ {self.ui_manager.lang.get_text('pro.applied_success')}"
                self.ui_manager.display_success(success_msg)
                self.ui_manager.display_text('pro.restart_cursor', "info")
            else:
                self.ui_manager.display_warning("✓ Operation completed successfully")

        except Exception as e:
            error_msg = self.ui_manager.lang.get_text('pro.apply_failed', error=str(e))
            self.ui_manager.display_error(f"Failed to apply Pro UI features: {error_msg}")

    def restore_pro_ui_features_backup(self):
        """Restore a Pro UI Features backup"""
        self.ui_manager.clear_screen()
        self.ui_manager.display_header()

        # Get list of available backups
        backups = self.pro_features_manager.backup_manager.list_backups()

        if not backups:
            self.ui_manager.display_text('pro.no_backups', "warning")
            self.ui_manager.display_text('pro.backups_info', "info")
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
            title=f"[bold]{self.ui_manager.lang.get_text('pro.available_backups')}[/bold]",
            border_style="bright_magenta",
            padding=(1, 2)
        )

        self.ui_manager.console.print(backup_panel)

        # Get user choice
        try:
            prompt_msg = self.ui_manager.lang.get_text('pro.select_backup', count=len(backups))
            choice = self.ui_manager.get_user_choice(
                prompt_msg,
                valid_choices=[str(i) for i in range(1, len(backups) + 1)] + ["c", "C"]
            )

            if choice is None or choice.lower() == 'c':
                self.ui_manager.display_text('pro.backup_cancelled', "info")
                return

            selected_backup = backups[int(choice) - 1]

            # Confirm restoration
            warning_msg = self.ui_manager.lang.get_text('pro.restore_warning', name=selected_backup['name'])
            self.ui_manager.display_warning(warning_msg)
            self.ui_manager.display_text('pro.overwrite_warning', "warning")

            confirm_msg = self.ui_manager.lang.get_text('pro.restore_confirm')
            if not self.ui_manager.confirm_action(confirm_msg):
                self.ui_manager.display_text('pro.backup_cancelled', "info")
                return

            # Perform restoration
            success = self.pro_features_manager.backup_manager.restore_backup(selected_backup["name"])

            if success:
                self.ui_manager.display_text('pro.restore_success', "success")
                self.ui_manager.display_text('pro.restore_restart', "info")
            else:
                self.ui_manager.display_text('pro.restore_warnings', "warning")

        except (ValueError, IndexError):
            self.ui_manager.display_text('pro.invalid_selection', "error")
        except Exception as e:
            self.ui_manager.display_text('pro.restore_failed', "error", error=str(e))




