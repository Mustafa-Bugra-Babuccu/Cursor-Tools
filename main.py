"""
Cursor-Tools Application
Main entry point for the command-line application
"""

import sys
import os
from colorama import init

# Initialize colorama for Windows compatibility (centralized initialization)
init()

from ui_manager import UIManager
from device_id_modifier import DeviceIDModifier
from account_info_manager import AccountInfoManager
from disable_update_manager import DisableUpdateManager
from reset_machine_id_manager import ResetMachineIDManager
from pro_features_manager import ProUIFeaturesMenuManager
from auto_update_manager import AutoUpdateManager
from language_manager import LanguageSettingsManager
from utils import is_admin, run_as_admin

class CursorToolsApp:
    def __init__(self):
        self.ui_manager = UIManager()
        self.device_modifier = DeviceIDModifier()
        self.account_info_manager = AccountInfoManager()
        self.disable_update_manager = DisableUpdateManager()
        self.reset_machine_id_manager = ResetMachineIDManager()
        self.pro_features_manager = ProUIFeaturesMenuManager()
        self.auto_update_manager = AutoUpdateManager()
        self.language_settings_manager = LanguageSettingsManager()

    def run(self):
        """Main application loop"""
        # Check if running on Windows
        if os.name != 'nt':
            print("This application is designed for Windows only.")
            sys.exit(1)

        # Check for administrator privileges and request if needed
        if not is_admin():
            print("Requesting administrator privileges...")
            if run_as_admin():
                sys.exit(0)  # Exit current process, elevated process will start
            else:
                print("Failed to obtain administrator privileges. Exiting.")
                sys.exit(1)

        # Perform automatic update check at startup
        try:
            self.auto_update_manager.cleanup_old_files()  # Clean up old files first
            self.auto_update_manager.perform_update_check_and_install()
        except Exception as e:
            self.ui_manager.display_error(f"Update check failed: {str(e)}")
            self.ui_manager.display_warning("Continuing with current version...")
            self.ui_manager.pause()

        try:
            while True:
                self.ui_manager.clear_screen()
                self.ui_manager.display_header()
                self.ui_manager.display_main_menu()

                choice = self.ui_manager.get_user_choice(
                    valid_choices=["1", "2", "3", "4", "5", "6", "7"]
                )

                if choice is None:  # User pressed Ctrl+C
                    self.exit_application()
                    break
                elif choice == "1":
                    self.account_info_manager.run_account_info_menu()
                elif choice == "2":
                    self.device_modifier.run_device_id_menu()
                elif choice == "3":
                    self.disable_update_manager.run_disable_update_menu()
                elif choice == "4":
                    self.reset_machine_id_manager.run_reset_machine_id_menu()
                elif choice == "5":
                    self.pro_features_manager.run_pro_ui_features_menu()
                elif choice == "6":
                    self.language_settings_manager.run_language_settings_menu()
                elif choice == "7":
                    self.exit_application()
                    break

        except KeyboardInterrupt:
            self.exit_application()
        except Exception as e:
            self.ui_manager.display_error(f"Unexpected error: {str(e)}")
            self.ui_manager.pause()

    def exit_application(self):
        """Clean exit with confirmation"""
        self.ui_manager.clear_screen()
        self.ui_manager.display_header()

        confirm_msg = self.ui_manager.lang.get_text('common.confirm_exit')
        if self.ui_manager.confirm_action(confirm_msg):
            self.ui_manager.display_text('app.thank_you', "info")
            subtitle = self.ui_manager.lang.get_text('app.subtitle')
            self.ui_manager.console.print(f"\n[dim]{subtitle}[/dim]")
            sys.exit(0)

def main():
    """Application entry point"""
    try:
        app = CursorToolsApp()
        app.run()
    except ImportError as e:
        print(f"Missing required dependencies: {e}")
        print("Please install required packages using: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
