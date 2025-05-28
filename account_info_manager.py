"""
Account Info Manager for Cursor-Tools
Integrates Cursor account information into the main application
"""

from acc_info import get_cursor_account_info
from ui_manager import UIManager
from rich.table import Table

class AccountInfoManager:
    def __init__(self):
        self.ui_manager = UIManager()

    def display_account_info(self):
        """Display Cursor account information with Rich styling"""
        self.ui_manager.clear_screen()
        self.ui_manager.display_header()

        self.ui_manager.display_info("Retrieving Cursor account information...")

        # Get account information
        account_info = get_cursor_account_info()

        # Check for errors
        if "error" in account_info:
            self.ui_manager.display_error(account_info["error"])
            return

        # Create account info table
        info_table = Table(title="Cursor Account Information", show_header=True, header_style="bold magenta")
        info_table.add_column("Property", style="cyan", width=60)
        info_table.add_column("Value", style="green", width=70)

        # Add email information
        email = account_info.get("email")
        if email:
            info_table.add_row("Email", email)
        else:
            info_table.add_row("Email", "[yellow]Not found[/yellow]")

        # Add subscription information
        subscription_type = account_info.get("subscription_type", "Free")
        info_table.add_row("Subscription Type", subscription_type)

        # Add trial days if available
        trial_days = account_info.get("trial_days_remaining")
        if trial_days is not None and trial_days > 0:
            info_table.add_row("Trial Days Remaining", f"{trial_days} days")

        self.ui_manager.console.print(info_table)

        # Display usage information if available
        usage_info = account_info.get("usage_info")
        if usage_info:
            self.ui_manager.console.print()
            self._display_usage_info(usage_info)
        else:
            self.ui_manager.console.print()
            self.ui_manager.display_warning("Usage information not available")

    def _display_usage_info(self, usage_info):
        """Display usage information in a formatted table"""
        usage_table = Table(title="Usage Statistics", show_header=True, header_style="bold blue")
        usage_table.add_column("Service Type", style="cyan", width=35)
        usage_table.add_column("Usage", style="yellow", width=30)
        usage_table.add_column("Limit", style="green", width=30)
        usage_table.add_column("Status", style="white", width=35)

        # Premium usage
        premium_usage = usage_info.get('premium_usage', 0)
        max_premium_usage = usage_info.get('max_premium_usage', "No Limit")

        if premium_usage is None:
            premium_usage = 0

        # Handle "No Limit" case for premium
        if isinstance(max_premium_usage, str) and max_premium_usage == "No Limit":
            premium_status = "[green]Unlimited[/green]"
            premium_limit_display = max_premium_usage
        else:
            if max_premium_usage is None or max_premium_usage == 0:
                max_premium_usage = 999
                premium_percentage = 0
            else:
                premium_percentage = (premium_usage / max_premium_usage) * 100

            # Select color based on usage percentage
            if premium_percentage > 90:
                premium_status = "[red]High Usage[/red]"
            elif premium_percentage > 70:
                premium_status = "[yellow]Moderate Usage[/yellow]"
            else:
                premium_status = "[green]Normal[/green]"

            premium_limit_display = str(max_premium_usage)

        usage_table.add_row("Fast Response", str(premium_usage), premium_limit_display, premium_status)

        # Basic usage
        basic_usage = usage_info.get('basic_usage', 0)
        max_basic_usage = usage_info.get('max_basic_usage', "No Limit")

        if basic_usage is None:
            basic_usage = 0

        # Handle "No Limit" case for basic
        if isinstance(max_basic_usage, str) and max_basic_usage == "No Limit":
            basic_status = "[green]Unlimited[/green]"
            basic_limit_display = max_basic_usage
        else:
            if max_basic_usage is None or max_basic_usage == 0:
                max_basic_usage = 999
                basic_percentage = 0
            else:
                basic_percentage = (basic_usage / max_basic_usage) * 100

            # Select color based on usage percentage
            if basic_percentage > 90:
                basic_status = "[red]High Usage[/red]"
            elif basic_percentage > 70:
                basic_status = "[yellow]Moderate Usage[/yellow]"
            else:
                basic_status = "[green]Normal[/green]"

            basic_limit_display = str(max_basic_usage)

        usage_table.add_row("Slow Response", str(basic_usage), basic_limit_display, basic_status)

        self.ui_manager.console.print(usage_table)

    def run_account_info_menu(self):
        """Run the Account Info sub-menu"""
        while True:
            self.ui_manager.clear_screen()
            self.ui_manager.display_header()
            self.ui_manager.display_account_info_menu()

            choice = self.ui_manager.get_user_choice(
                "Select an option",
                valid_choices=["1", "2"]
            )

            if choice is None:  # User pressed Ctrl+C
                break
            elif choice == "1":
                self.view_account_information()
            elif choice == "2":
                break

            if choice == "1":
                self.ui_manager.pause()

    def view_account_information(self):
        """Display account information"""
        self.ui_manager.clear_screen()
        self.ui_manager.display_header()

        try:
            self.display_account_info()
        except Exception as e:
            self.ui_manager.display_error(f"Failed to retrieve account information: {str(e)}")
