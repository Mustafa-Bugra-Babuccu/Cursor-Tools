"""
Cursor-Tools Application
Main entry point for the command-line application
"""

import sys
import os
import ctypes
from ui_manager import UIManager
from device_id_modifier import DeviceIDModifier
from account_info_manager import AccountInfoManager
from disable_update_manager import DisableUpdateManager
from reset_machine_id_manager import ResetMachineIDManager

def is_admin():
    """Check if the current process has administrator privileges"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
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

class CursorToolsApp:
    def __init__(self):
        self.ui_manager = UIManager()
        self.device_modifier = DeviceIDModifier()
        self.account_info_manager = AccountInfoManager()
        self.disable_update_manager = DisableUpdateManager()
        self.reset_machine_id_manager = ResetMachineIDManager()

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

        try:
            while True:
                self.ui_manager.clear_screen()
                self.ui_manager.display_header()
                self.ui_manager.display_main_menu()

                choice = self.ui_manager.get_user_choice(
                    "Select an option",
                    valid_choices=["1", "2", "3", "4", "5"]
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

        if self.ui_manager.confirm_action("Are you sure you want to exit?"):
            self.ui_manager.display_info("Thank you for using Cursor-Tools!")
            self.ui_manager.console.print("\n[dim]Cursor's Best All-in-One Tool[/dim]")
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
