"""
UI Manager for Cursor-Tools Application
Handles all user interface styling and menu management
"""

import os
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.align import Align
from colorama import init

# Initialize colorama for Windows compatibility
init()

class UIManager:
    def __init__(self):
        self.console = Console()

    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')

    def display_header(self):
        """Display application header"""
        header_text = Text("        Cursor-Tools", style="bold cyan")
        header_text.append("\nCursor's Best All-in-One Tool", style="dim")

        header_panel = Panel(
            Align.center(header_text),
            border_style="bright_blue",
            padding=(1, 2)
        )

        self.console.print()
        self.console.print(header_panel)
        self.console.print()

    def display_main_menu(self):
        """Display the main menu options"""
        menu_table = Table(show_header=False, box=None, padding=(0, 2))
        menu_table.add_column("Option", style="cyan", width=4)
        menu_table.add_column("Description", style="white")

        menu_table.add_row("1.", "Account Info")
        menu_table.add_row("2.", "Device ID Modifier")
        menu_table.add_row("3.", "Disable Auto Update")
        menu_table.add_row("4.", "Reset Machine ID")
        menu_table.add_row("5.", "Pro UI Features")
        menu_table.add_row("6.", "Exit Application")

        menu_panel = Panel(
            menu_table,
            title="[bold]Main Menu[/bold]",
            border_style="green",
            padding=(1, 2)
        )

        self.console.print(menu_panel)

    def display_device_id_menu(self):
        """Display the Device ID Modifier sub-menu"""
        menu_table = Table(show_header=False, box=None, padding=(0, 2))
        menu_table.add_column("Option", style="cyan", width=4)
        menu_table.add_column("Description", style="white")

        menu_table.add_row("1.", "Change Device ID")
        menu_table.add_row("2.", "Restore Backup")
        menu_table.add_row("3.", "View Current Registry Values")
        menu_table.add_row("4.", "Return to Main Menu")

        menu_panel = Panel(
            menu_table,
            title="[bold]Device ID Modifier[/bold]",
            border_style="yellow",
            padding=(1, 2)
        )

        self.console.print(menu_panel)

    def display_account_info_menu(self):
        """Display the Account Info sub-menu"""
        menu_table = Table(show_header=False, box=None, padding=(0, 2))
        menu_table.add_column("Option", style="cyan", width=4)
        menu_table.add_column("Description", style="white")

        menu_table.add_row("1.", "View Account Information")
        menu_table.add_row("2.", "Return to Main Menu")

        menu_panel = Panel(
            menu_table,
            title="[bold]Account Info[/bold]",
            border_style="blue",
            padding=(1, 2)
        )

        self.console.print(menu_panel)

    def display_disable_update_menu(self):
        """Display the Disable Auto Update sub-menu"""
        menu_table = Table(show_header=False, box=None, padding=(0, 2))
        menu_table.add_column("Option", style="cyan", width=4)
        menu_table.add_column("Description", style="white")

        menu_table.add_row("1.", "Disable Cursor Auto Update")
        menu_table.add_row("2.", "Return to Main Menu")

        menu_panel = Panel(
            menu_table,
            title="[bold]Disable Auto Update[/bold]",
            border_style="red",
            padding=(1, 2)
        )

        self.console.print(menu_panel)

    def display_reset_machine_id_menu(self):
        """Display the Reset Machine ID sub-menu"""
        menu_table = Table(show_header=False, box=None, padding=(0, 2))
        menu_table.add_column("Option", style="cyan", width=4)
        menu_table.add_column("Description", style="white")

        menu_table.add_row("1.", "Reset Machine ID")
        menu_table.add_row("2.", "Restore Backup")
        menu_table.add_row("3.", "View Current Machine ID Values")
        menu_table.add_row("4.", "Return to Main Menu")

        menu_panel = Panel(
            menu_table,
            title="[bold]Reset Machine ID[/bold]",
            border_style="magenta",
            padding=(1, 2)
        )

        self.console.print(menu_panel)

    def get_user_choice(self, prompt_text="Enter your choice", valid_choices=None):
        """Get user input with validation"""
        while True:
            try:
                choice = Prompt.ask(f"[bold green]{prompt_text}[/bold green]")
                if valid_choices and choice not in valid_choices:
                    self.console.print(f"[red]Invalid choice. Please select from: {', '.join(valid_choices)}[/red]")
                    continue
                return choice
            except KeyboardInterrupt:
                self.console.print("\n[yellow]Operation cancelled by user.[/yellow]")
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

    def pause(self, message="Press Enter to continue..."):
        """Pause execution and wait for user input"""
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
