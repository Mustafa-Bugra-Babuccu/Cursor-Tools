"""
UI Manager for Cursor-Tools Application
Handles all user interface styling and menu management with language support
"""

import os
import time
import threading
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.align import Align
from language_manager import language_manager

class UIManager:
    def __init__(self):
        self.console = Console()
        self.lang = language_manager

    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')

    def display_header(self):
        """Display application header with language support"""
        header_text = Text(f"        {self.lang.get_text('app.title')}", style="bold cyan")
        header_text.append(f"\n{self.lang.get_text('app.subtitle')}", style="dim")

        header_panel = Panel(
            Align.center(header_text),
            border_style="bright_blue",
            padding=(1, 2)
        )

        self.console.print()
        self.console.print(header_panel)
        self.console.print()

    def display_main_menu(self):
        """Display the main menu options with language support"""
        menu_table = Table(show_header=False, box=None, padding=(0, 2))
        menu_table.add_column("Option", style="cyan", width=4)
        menu_table.add_column("Description", style="white")

        menu_table.add_row("1.", self.lang.get_text('menu.account_info'))
        menu_table.add_row("2.", self.lang.get_text('menu.device_id'))
        menu_table.add_row("3.", self.lang.get_text('menu.disable_updates'))
        menu_table.add_row("4.", self.lang.get_text('menu.reset_machine_id'))
        menu_table.add_row("5.", self.lang.get_text('menu.pro_features'))
        menu_table.add_row("6.", self.lang.get_text('menu.language_settings'))
        menu_table.add_row("7.", self.lang.get_text('menu.exit'))

        menu_panel = Panel(
            menu_table,
            title=f"[bold]{self.lang.get_text('menu.title')}[/bold]",
            border_style="green",
            padding=(1, 2)
        )

        self.console.print(menu_panel)

    def display_language_menu(self):
        """Display the language settings menu"""
        menu_table = Table(show_header=False, box=None, padding=(0, 2))
        menu_table.add_column("Option", style="cyan", width=4)
        menu_table.add_column("Description", style="white")

        # Show current language
        current_lang = self.lang.get_current_language_name()
        menu_table.add_row("", f"{self.lang.get_text('lang.current', language=current_lang)}")
        menu_table.add_row("", "")  # Empty row for spacing

        # Show language options
        language_options = self.lang.get_language_menu_options()
        for option_num, language_name in language_options.items():
            menu_table.add_row(f"{option_num}.", language_name)

        menu_table.add_row("", "")  # Empty row for spacing
        menu_table.add_row("0.", self.lang.get_text('menu.exit'))

        menu_panel = Panel(
            menu_table,
            title=f"[bold]{self.lang.get_text('lang.title')}[/bold]",
            border_style="blue",
            padding=(1, 2)
        )

        self.console.print(menu_panel)

    def display_device_id_menu(self):
        """Display the Device ID Modifier sub-menu with language support"""
        menu_table = Table(show_header=False, box=None, padding=(0, 2))
        menu_table.add_column("Option", style="cyan", width=4)
        menu_table.add_column("Description", style="white")

        menu_table.add_row("1.", self.lang.get_text('device.change_id'))
        menu_table.add_row("2.", self.lang.get_text('device.restore_backup'))
        menu_table.add_row("3.", self.lang.get_text('device.view_current'))
        menu_table.add_row("4.", self.lang.get_text('device.return_main'))

        menu_panel = Panel(
            menu_table,
            title=f"[bold]{self.lang.get_text('device.title')}[/bold]",
            border_style="yellow",
            padding=(1, 2)
        )

        self.console.print(menu_panel)

    def display_account_info_menu(self):
        """Display the Account Info sub-menu with language support"""
        menu_table = Table(show_header=False, box=None, padding=(0, 2))
        menu_table.add_column("Option", style="cyan", width=4)
        menu_table.add_column("Description", style="white")

        menu_table.add_row("1.", self.lang.get_text('account.view_info'))
        menu_table.add_row("2.", self.lang.get_text('account.return_main'))

        menu_panel = Panel(
            menu_table,
            title=f"[bold]{self.lang.get_text('account.title')}[/bold]",
            border_style="blue",
            padding=(1, 2)
        )

        self.console.print(menu_panel)

    def display_disable_update_menu(self):
        """Display the Disable Auto Update sub-menu with language support"""
        menu_table = Table(show_header=False, box=None, padding=(0, 2))
        menu_table.add_column("Option", style="cyan", width=4)
        menu_table.add_column("Description", style="white")

        menu_table.add_row("1.", self.lang.get_text('update.disable_auto'))
        menu_table.add_row("2.", self.lang.get_text('update.return_main'))

        menu_panel = Panel(
            menu_table,
            title=f"[bold]{self.lang.get_text('update.title')}[/bold]",
            border_style="red",
            padding=(1, 2)
        )

        self.console.print(menu_panel)

    def display_reset_machine_id_menu(self):
        """Display the Reset Machine ID sub-menu with language support"""
        menu_table = Table(show_header=False, box=None, padding=(0, 2))
        menu_table.add_column("Option", style="cyan", width=4)
        menu_table.add_column("Description", style="white")

        menu_table.add_row("1.", self.lang.get_text('reset.reset_id'))
        menu_table.add_row("2.", self.lang.get_text('reset.restore_backup'))
        menu_table.add_row("3.", self.lang.get_text('reset.view_current'))
        menu_table.add_row("4.", self.lang.get_text('reset.return_main'))

        menu_panel = Panel(
            menu_table,
            title=f"[bold]{self.lang.get_text('reset.title')}[/bold]",
            border_style="magenta",
            padding=(1, 2)
        )

        self.console.print(menu_panel)

    def get_user_choice(self, prompt_key="menu.select_option", valid_choices=None):
        """Get user input with validation and language support"""
        while True:
            try:
                prompt_text = self.lang.get_text(prompt_key)
                choice = Prompt.ask(f"[bold green]{prompt_text}[/bold green]")
                if valid_choices and choice not in valid_choices:
                    invalid_msg = self.lang.get_text('menu.invalid_choice')
                    self.console.print(f"[red]{invalid_msg}[/red]")
                    continue
                return choice
            except KeyboardInterrupt:
                cancelled_msg = self.lang.get_text('common.operation_cancelled')
                self.console.print(f"\n[yellow]{cancelled_msg}[/yellow]")
                return None

    def confirm_action(self, message):
        """Get user confirmation for critical actions"""
        return Confirm.ask(f"[bold yellow]{message}[/bold yellow]")

    def display_success(self, message):
        """Display success message"""
        self.console.print(f"[bold green]✓ {message}[/bold green]")

    def display_error(self, message):
        """Display error message"""
        self.console.print(f"[bold red]✗ {message}[/bold red]")

    def display_warning(self, message):
        """Display warning message"""
        self.console.print(f"[bold yellow]⚠ {message}[/bold yellow]")

    def display_info(self, message):
        """Display info message"""
        self.console.print(f"[bold blue]ℹ {message}[/bold blue]")

    def display_text(self, key: str, message_type="info", **kwargs):
        """Display localized text with specified message type and optional auto-hide"""
        message = self.lang.get_text(key, **kwargs)

        if message_type == "error":
            self.display_error(message)
        elif message_type == "warning":
            self.display_warning(message)
        elif message_type == "success":
            self.display_success(message)
        elif message_type == "step":
            self.console.print(f"[cyan]ℹ {message}...[/cyan]")
        else:  # info
            self.display_info(message)

    def display_update_no_available_with_auto_hide(self):
        """Display 'No updates available' message with 3-second auto-hide"""
        # Display the message
        message = self.lang.get_text('app.update_not_available')
        self.display_success(message)

        # Start auto-hide timer
        def hide_after_delay():
            time.sleep(3)  # Wait exactly 3 seconds
            # Don't clear screen, just return to caller
            # The caller should handle returning to main menu

        # Start the timer in a separate thread
        timer_thread = threading.Thread(target=hide_after_delay, daemon=True)
        timer_thread.start()

        # Wait for the timer to complete (blocking)
        timer_thread.join()

        # Now clear screen and return to main menu
        self.clear_screen()
        self.display_header()

    def display_registry_values(self, title, values_dict):
        """Display registry values in a formatted table with consistent width"""
        # Create table with full console width to match header panel
        table = Table(title=title, show_header=True, header_style="bold magenta")
        table.add_column("Registry Path", style="cyan", width=60)
        table.add_column("Key", style="yellow", width=20)
        table.add_column("Value", style="green", width=30)

        for path, keys in values_dict.items():
            for key, value in keys.items():
                table.add_row(path, key, str(value))

        # Display table with full width to match header panel
        self.console.print(table)

    def display_comparison(self, before_values, after_values):
        """Display before/after comparison of registry values"""
        self.console.print("\n[bold]Registry Values Comparison:[/bold]")

        # Before values
        self.console.print("\n[bold red]BEFORE:[/bold red]")
        self.display_registry_values("Original Values", before_values)

        # After values
        self.console.print("\n[bold green]AFTER:[/bold green]")
        self.display_registry_values("Modified Values", after_values)

    def pause(self, message_key="common.press_enter"):
        """Pause execution and wait for user input with language support"""
        message = self.lang.get_text(message_key)
        Prompt.ask(f"[dim]{message}[/dim]", default="")

    def display_admin_warning(self):
        """Display administrator privileges warning"""
        warning_text = Text("ADMINISTRATOR PRIVILEGES REQUIRED", style="bold red")
        warning_text.append("\n\nThis application requires administrator privileges to modify Windows registry.", style="yellow")
        warning_text.append("\nPlease run this application as an administrator.", style="yellow")

        warning_panel = Panel(
            Align.center(warning_text),
            border_style="red",
            padding=(1, 2)
        )

        self.console.print(warning_panel)

    def display_update_progress(self, message, progress_value=None, total=None):
        """Display update progress with optional progress bar"""
        if progress_value is not None and total is not None:
            percentage = (progress_value / total) * 100
            self.console.print(f"[bold blue]ℹ {message} ({percentage:.1f}%)[/bold blue]")
        else:
            self.console.print(f"[bold blue]ℹ {message}[/bold blue]")

    def display_update_notification(self, current_version, latest_version, release_notes=""):
        """Display update notification panel"""
        update_text = Text("🚀 UPDATE AVAILABLE!", style="bold bright_yellow")
        update_text.append(f"\n\nCurrent Version: {current_version}", style="dim")
        update_text.append(f"\nLatest Version: {latest_version}", style="bold green")

        if release_notes:
            notes = release_notes[:150] + "..." if len(release_notes) > 150 else release_notes
            update_text.append(f"\n\nWhat's New:\n{notes}", style="white")

        update_panel = Panel(
            Align.center(update_text),
            border_style="bright_yellow",
            padding=(1, 2),
            title="[bold bright_yellow]Update Available[/bold bright_yellow]"
        )

        self.console.print(update_panel)

    def display_account_info_table(self, account_data: dict):
        """Format and display account information in a structured table"""
        table = Table(title="Cursor Account Information", show_header=True, header_style="bold magenta")
        table.add_column("Property", style="cyan", no_wrap=True)
        table.add_column("Value", style="white")

        # Email information
        email = account_data.get('email', 'Not found')
        table.add_row("Email", email if email else "Not available")

        # Subscription information
        subscription_type = account_data.get('subscription_type', 'Free')
        table.add_row("Subscription Type", subscription_type)

        # Subscription details
        subscription_info = account_data.get('subscription_info')
        if subscription_info and isinstance(subscription_info, dict):
            if 'subscription' in subscription_info:
                sub = subscription_info['subscription']
                if 'status' in sub:
                    table.add_row("Subscription Status", sub['status'])
                if 'current_period_end' in sub:
                    table.add_row("Current Period End", str(sub['current_period_end']))

        # Usage information
        usage_info = account_data.get('usage_info')
        if usage_info and isinstance(usage_info, dict):
            if 'usage' in usage_info:
                usage = usage_info['usage']
                for key, value in usage.items():
                    if isinstance(value, (int, float)):
                        table.add_row(f"Usage - {key.replace('_', ' ').title()}", str(value))

        self.console.print(table)

    def display_backup_list_table(self, backup_data: list):
        """Format and display backup listings in a structured table"""
        if not backup_data:
            self.display_info("No backups found.")
            return

        table = Table(title="Available Backups", show_header=True, header_style="bold magenta")
        table.add_column("ID", style="cyan", no_wrap=True)
        table.add_column("Type", style="yellow")
        table.add_column("Date", style="green")
        table.add_column("Source", style="white")
        table.add_column("Size", style="blue")

        for backup in backup_data:
            backup_id = backup.get('backup_id', 'Unknown')[:20] + "..." if len(backup.get('backup_id', '')) > 20 else backup.get('backup_id', 'Unknown')
            backup_type = backup.get('backup_type', 'Unknown')
            formatted_date = backup.get('formatted_date', 'Unknown')
            source_path = os.path.basename(backup.get('source_path', 'Unknown'))
            file_size = self._format_file_size(backup.get('file_size', 0))

            table.add_row(backup_id, backup_type, formatted_date, source_path, file_size)

        self.console.print(table)

    def display_system_info_table(self, system_data: dict):
        """Format and display system information in a structured table"""
        table = Table(title="System Information", show_header=True, header_style="bold magenta")
        table.add_column("Component", style="cyan", no_wrap=True)
        table.add_column("Status", style="white")
        table.add_column("Details", style="yellow")

        for component, info in system_data.items():
            if isinstance(info, dict):
                status = "✅ OK" if info.get('status', False) else "❌ Error"
                details = info.get('details', 'No details available')
            else:
                status = str(info)
                details = ""

            table.add_row(component.replace('_', ' ').title(), status, details)

        self.console.print(table)

    def display_progress_with_steps(self, steps: list, current_step: int):
        """Show multi-step progress with step indicators"""
        # Display step overview
        self.console.print(f"\n[bold cyan]Progress: Step {current_step + 1} of {len(steps)}[/bold cyan]")

        # Display all steps with status indicators
        for i, step in enumerate(steps):
            if i < current_step:
                status = "[green]✅[/green]"
            elif i == current_step:
                status = "[yellow]⏳[/yellow]"
            else:
                status = "[dim]⏸️[/dim]"

            step_text = f"{status} {step}"
            if i == current_step:
                step_text = f"[bold]{step_text}[/bold]"

            self.console.print(f"  {step_text}")

        self.console.print()

    def display_file_operation_results(self, results: dict):
        """Display results of file operations in a formatted table"""
        table = Table(title="File Operation Results", show_header=True, header_style="bold magenta")
        table.add_column("File", style="cyan")
        table.add_column("Status", style="white")
        table.add_column("Details", style="yellow")

        for file_path, result in results.items():
            filename = os.path.basename(file_path)
            if result.get('success', False):
                status = "[green]✅ Success[/green]"
                details = "Operation completed successfully"
            else:
                status = "[red]❌ Failed[/red]"
                details = result.get('error', 'Unknown error')

            table.add_row(filename, status, details)

        self.console.print(table)

    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size in human readable format"""
        if size_bytes == 0:
            return "0 B"

        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1

        return f"{size_bytes:.1f} {size_names[i]}"
