"""
Disable Update Manager for Cursor-Tools
Integrates disable update functionality into the main application
"""

from disable_update import UpdateDisabler
from ui_manager import UIManager

class DisableUpdateManager:
    def __init__(self):
        self.ui_manager = UIManager()
        self.update_disabler = UpdateDisabler(self.ui_manager)

    def run_disable_update_menu(self):
        """Run the Disable Auto Update sub-menu"""
        while True:
            self.ui_manager.clear_screen()
            self.ui_manager.display_header()
            self.ui_manager.display_disable_update_menu()

            choice = self.ui_manager.get_user_choice(
                "Select an option",
                valid_choices=["1", "2"]
            )

            if choice is None:  # User pressed Ctrl+C
                break
            elif choice == "1":
                self.disable_auto_update()
            elif choice == "2":
                break

            if choice == "1":
                self.ui_manager.pause()

    def disable_auto_update(self):
        """Execute the disable auto update functionality"""
        self.ui_manager.clear_screen()
        self.ui_manager.display_header()

        self.ui_manager.display_warning("This operation will disable Cursor's auto-update functionality.")
        self.ui_manager.display_info("This process will:")
        self.ui_manager.console.print("  • End all Cursor processes")
        self.ui_manager.console.print("  • Remove updater directory")
        self.ui_manager.console.print("  • Clear update configuration files")
        self.ui_manager.console.print("  • Create blocking files to prevent updates")
        self.ui_manager.console.print("  • Modify product.json to remove update URLs")

        # Get confirmation
        if not self.ui_manager.confirm_action("Do you want to proceed with disabling auto-updates?"):
            self.ui_manager.display_info("Operation cancelled.")
            return

        # Perform the disable operation
        try:
            self.ui_manager.display_info("Starting auto-update disable process...")
            success = self.update_disabler.disable_auto_update()

            if success:
                self.ui_manager.display_success("Auto-update has been disabled successfully!")
                self.ui_manager.display_info("Cursor will no longer automatically update.")
            else:
                self.ui_manager.display_error("Failed to completely disable auto-update.")
                self.ui_manager.display_warning("Some operations may have failed. Check the output above for details.")

        except Exception as e:
            self.ui_manager.display_error(f"Failed to disable auto-update: {str(e)}")
