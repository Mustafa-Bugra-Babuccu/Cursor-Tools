"""
Auto Update Manager for Cursor-Tools
Handles automatic update checking, downloading, and installation
"""

import os
import sys
import json
import time
import shutil
import hashlib
import tempfile
import subprocess
from pathlib import Path
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta

import requests
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.panel import Panel
from rich.text import Text
from rich.align import Align

from ui_manager import UIManager
from config import config, config_manager


class AutoUpdateManager:
    """Manages automatic updates for Cursor-Tools application"""

    def __init__(self):
        self.ui_manager = UIManager()

        # Get auto update configuration from centralized config manager
        auto_config = config_manager.get_auto_update_config()
        self.current_version = auto_config['CURRENT_VERSION']
        self.github_api_url = auto_config['GITHUB_API_URL']
        self.github_repo_url = auto_config['GITHUB_REPO_URL']
        self.update_check_timeout = auto_config['UPDATE_CHECK_TIMEOUT']
        self.download_timeout = auto_config['DOWNLOAD_TIMEOUT']
        self.verify_ssl = auto_config['VERIFY_SSL']
        self.allow_redirects = auto_config['ALLOW_REDIRECTS']
        self.temp_dir = None
        self.backup_dir = None

        # Initialize update directories
        self._initialize_update_directories()

    def _initialize_update_directories(self):
        """Initialize directories for update operations"""
        try:
            # Create update directories in the Cursor Tools folder
            update_base_dir = os.path.join(config.cursor_tools_dir, "updates")
            self.temp_dir = os.path.join(update_base_dir, "temp")
            self.backup_dir = os.path.join(update_base_dir, "backup")

            # Create directories if they don't exist
            Path(self.temp_dir).mkdir(parents=True, exist_ok=True)
            Path(self.backup_dir).mkdir(parents=True, exist_ok=True)

        except Exception as e:
            self.ui_manager.display_error(f"Failed to initialize update directories: {str(e)}")
            # Fallback to system temp directory
            self.temp_dir = tempfile.gettempdir()
            self.backup_dir = tempfile.gettempdir()

    def check_for_updates(self, force_check: bool = False) -> Optional[Dict]:
        """
        Check for available updates from GitHub releases

        Args:
            force_check: If True, bypass any caching and force a fresh check

        Returns:
            Dict with update information if available, None otherwise
        """
        try:
            self.ui_manager.display_info("Checking for updates...")

            # Get request configuration
            request_config = config_manager.get_request_config()

            # Make request to GitHub API
            response = requests.get(self.github_api_url, **request_config)

            if response.status_code == 200:
                release_data = response.json()
                latest_version = release_data.get("tag_name", "").lstrip("v")

                if self._is_newer_version(latest_version, self.current_version):
                    return {
                        "version": latest_version,
                        "name": release_data.get("name", f"Version {latest_version}"),
                        "body": release_data.get("body", "No release notes available."),
                        "published_at": release_data.get("published_at", ""),
                        "assets": release_data.get("assets", []),
                        "download_url": self._get_download_url(release_data.get("assets", []))
                    }
                else:
                    self.ui_manager.display_success("You are running the latest version!")
                    return None

            elif response.status_code == 403:
                self.ui_manager.display_warning("GitHub API rate limit exceeded. Please try again later.")
                return None
            else:
                self.ui_manager.display_error(f"Failed to check for updates. HTTP {response.status_code}")
                return None

        except requests.exceptions.Timeout:
            self.ui_manager.display_error("Update check timed out. Please check your internet connection.")
            return None
        except requests.exceptions.SSLError as e:
            self.ui_manager.display_warning("SSL certificate verification failed. Trying with SSL disabled...")
            return self._check_for_updates_fallback()
        except requests.exceptions.ConnectionError as e:
            error_msg = str(e).lower()
            if "ssl" in error_msg or "certificate" in error_msg:
                self.ui_manager.display_warning("SSL certificate verification failed. Trying with SSL disabled...")
                return self._check_for_updates_fallback()
            else:
                self.ui_manager.display_error("Unable to connect to GitHub. Please check your internet connection.")
                return None
        except Exception as e:
            error_msg = str(e).lower()
            if "ssl" in error_msg or "certificate" in error_msg:
                self.ui_manager.display_error("SSL certificate verification failed.")
                self.ui_manager.display_warning("This may be due to corporate firewall or network configuration.")
                self.ui_manager.display_info("You can manually check for updates at: " + self.github_repo_url + "/releases")
            else:
                self.ui_manager.display_error(f"Error checking for updates: {str(e)}")
            return None

    def _check_for_updates_fallback(self) -> Optional[Dict]:
        """
        Fallback update check with SSL verification disabled

        Returns:
            Dict with update information if available, None otherwise
        """
        try:
            self.ui_manager.display_info("Retrying update check with SSL verification disabled...")

            # Get fallback request configuration (SSL disabled)
            request_config = config_manager.get_fallback_request_config()

            # Make request to GitHub API
            response = requests.get(self.github_api_url, **request_config)

            if response.status_code == 200:
                release_data = response.json()
                latest_version = release_data.get("tag_name", "").lstrip("v")

                if self._is_newer_version(latest_version, self.current_version):
                    self.ui_manager.display_success("Update check successful (SSL verification disabled)")
                    return {
                        "version": latest_version,
                        "name": release_data.get("name", f"Version {latest_version}"),
                        "body": release_data.get("body", "No release notes available."),
                        "published_at": release_data.get("published_at", ""),
                        "assets": release_data.get("assets", []),
                        "download_url": self._get_download_url(release_data.get("assets", []))
                    }
                else:
                    self.ui_manager.display_success("You are running the latest version!")
                    return None

            elif response.status_code == 403:
                self.ui_manager.display_warning("GitHub API rate limit exceeded. Please try again later.")
                return None
            else:
                self.ui_manager.display_error(f"Failed to check for updates. HTTP {response.status_code}")
                return None

        except Exception as e:
            self.ui_manager.display_error("Update check failed even with SSL disabled.")
            self.ui_manager.display_info("You can manually check for updates at: " + self.github_repo_url + "/releases")
            return None

    def _is_newer_version(self, latest: str, current: str) -> bool:
        """
        Compare version strings to determine if latest is newer than current

        Args:
            latest: Latest version string (e.g., "1.1.0")
            current: Current version string (e.g., "1.0.0")

        Returns:
            True if latest version is newer, False otherwise
        """
        try:
            # Parse version strings into tuples of integers
            latest_parts = tuple(map(int, latest.split(".")))
            current_parts = tuple(map(int, current.split(".")))

            return latest_parts > current_parts
        except (ValueError, AttributeError):
            # If version parsing fails, assume no update is available
            return False

    def _get_download_url(self, assets: list) -> Optional[str]:
        """
        Extract the download URL for the Windows executable from release assets

        Args:
            assets: List of release assets from GitHub API

        Returns:
            Download URL for the executable, or None if not found
        """
        for asset in assets:
            asset_name = asset.get("name", "")
            # Check for valid Windows executable assets
            if asset_name.endswith('.exe') and 'cursor-tools' in asset_name.lower():
                return asset.get("browser_download_url")

        return None

    def display_update_notification(self, update_info: Dict) -> bool:
        """
        Display update notification and get user confirmation

        Args:
            update_info: Dictionary containing update information

        Returns:
            True if user wants to update, False otherwise
        """
        self.ui_manager.clear_screen()
        self.ui_manager.display_header()

        # Create update notification panel
        update_text = Text("🚀 NEW UPDATE AVAILABLE!", style="bold bright_yellow")
        update_text.append(f"\n\nCurrent Version: {self.current_version}", style="dim")
        update_text.append(f"\nLatest Version: {update_info['version']}", style="bold green")
        update_text.append(f"\nRelease: {update_info['name']}", style="cyan")

        # Add release notes if available
        if update_info.get('body'):
            notes = update_info['body'][:200] + "..." if len(update_info['body']) > 200 else update_info['body']
            update_text.append(f"\n\nRelease Notes:\n{notes}", style="white")

        update_panel = Panel(
            Align.center(update_text),
            border_style="bright_yellow",
            padding=(1, 2),
            title="[bold bright_yellow]Update Available[/bold bright_yellow]"
        )

        self.ui_manager.console.print(update_panel)
        self.ui_manager.console.print()

        # Display forced update warning
        warning_text = Text("⚠️  FORCED UPDATE POLICY", style="bold red")
        warning_text.append("\n\nThis application requires the latest version to continue.", style="yellow")
        warning_text.append("\nYou must update to proceed with normal operation.", style="yellow")

        warning_panel = Panel(
            Align.center(warning_text),
            border_style="red",
            padding=(1, 2)
        )

        self.ui_manager.console.print(warning_panel)
        self.ui_manager.console.print()

        # Get user choice
        return self.ui_manager.confirm_action("Do you want to download and install the update now?")

    def download_update(self, download_url: str, version: str) -> Optional[str]:
        """
        Download the update file with progress indication

        Args:
            download_url: URL to download the update from
            version: Version being downloaded

        Returns:
            Path to downloaded file if successful, None otherwise
        """
        try:
            self.ui_manager.display_info(f"Downloading Cursor-Tools v{version}...")

            # Prepare download path
            filename = f"Cursor-Tools-v{version}.exe"
            download_path = os.path.join(self.temp_dir, filename)

            # Start download with progress bar
            response = requests.get(
                download_url,
                stream=True,
                timeout=self.download_timeout,
                verify=self.verify_ssl,
                allow_redirects=self.allow_redirects
            )
            response.raise_for_status()

            total_size = int(response.headers.get('content-length', 0))

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                console=self.ui_manager.console
            ) as progress:

                task = progress.add_task(f"Downloading v{version}", total=total_size)

                with open(download_path, 'wb') as file:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            file.write(chunk)
                            progress.update(task, advance=len(chunk))

            self.ui_manager.display_success(f"Download completed: {filename}")
            return download_path

        except requests.exceptions.Timeout:
            self.ui_manager.display_error("Download timed out. Please try again.")
            return None
        except requests.exceptions.SSLError:
            self.ui_manager.display_error("SSL certificate verification failed during download.")
            self.ui_manager.display_warning("This may be due to corporate firewall or network configuration.")
            return None
        except requests.exceptions.RequestException as e:
            error_msg = str(e).lower()
            if "ssl" in error_msg or "certificate" in error_msg:
                self.ui_manager.display_error("SSL certificate verification failed during download.")
                self.ui_manager.display_warning("This may be due to corporate firewall or network configuration.")
            else:
                self.ui_manager.display_error(f"Download failed: {str(e)}")
            return None
        except Exception as e:
            self.ui_manager.display_error(f"Unexpected error during download: {str(e)}")
            return None

    def verify_download(self, file_path: str) -> bool:
        """
        Verify the integrity of the downloaded file

        Args:
            file_path: Path to the downloaded file

        Returns:
            True if file is valid, False otherwise
        """
        try:
            # Check if file exists and has reasonable size
            if not os.path.exists(file_path):
                self.ui_manager.display_error("Downloaded file not found.")
                return False

            file_size = os.path.getsize(file_path)
            if file_size < 1024 * 1024:  # Less than 1MB is suspicious
                self.ui_manager.display_error("Downloaded file appears to be too small.")
                return False

            # Try to verify it's a valid PE executable (basic check)
            with open(file_path, 'rb') as f:
                # Check for PE signature
                f.seek(0)
                dos_header = f.read(2)
                if dos_header != b'MZ':
                    self.ui_manager.display_error("Downloaded file is not a valid executable.")
                    return False

            self.ui_manager.display_success("Download verification completed.")
            return True

        except Exception as e:
            self.ui_manager.display_error(f"Error verifying download: {str(e)}")
            return False

    def backup_current_executable(self) -> bool:
        """
        Create a backup of the current executable

        Returns:
            True if backup was successful, False otherwise
        """
        try:
            # Get current executable path
            if getattr(sys, 'frozen', False):
                # Running as compiled executable
                current_exe = sys.executable
            else:
                # Running as Python script - backup the main.py instead
                current_exe = os.path.abspath("main.py")

            if not os.path.exists(current_exe):
                self.ui_manager.display_error("Current executable not found for backup.")
                return False

            # Create backup filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"Cursor-Tools-backup-{timestamp}{os.path.splitext(current_exe)[1]}"
            backup_path = os.path.join(self.backup_dir, backup_filename)

            # Copy current executable to backup location
            shutil.copy2(current_exe, backup_path)

            self.ui_manager.display_success(f"Backup created: {backup_filename}")
            return True

        except Exception as e:
            self.ui_manager.display_error(f"Failed to create backup: {str(e)}")
            return False

    def install_update(self, update_file_path: str) -> bool:
        """
        Install the downloaded update

        Args:
            update_file_path: Path to the downloaded update file

        Returns:
            True if installation was successful, False otherwise
        """
        try:
            self.ui_manager.display_info("Installing update...")

            # Get current executable path
            if getattr(sys, 'frozen', False):
                # Running as compiled executable
                current_exe = sys.executable
                target_path = current_exe
            else:
                # Running as Python script - place the exe in the same directory
                current_dir = os.path.dirname(os.path.abspath(__file__))
                target_path = os.path.join(current_dir, "Cursor-Tools.exe")

            # Create a batch script to handle the replacement
            # This is necessary because we can't replace a running executable directly
            batch_script = self._create_update_batch_script(update_file_path, target_path)

            if not batch_script:
                return False

            self.ui_manager.display_success("Update installation prepared.")
            self.ui_manager.display_info("The application will restart to complete the update...")

            # Execute the batch script and exit
            subprocess.Popen([batch_script], shell=True)

            # Give user a moment to see the message
            time.sleep(2)

            # Exit the current application
            sys.exit(0)

        except Exception as e:
            self.ui_manager.display_error(f"Failed to install update: {str(e)}")
            return False

    def _create_update_batch_script(self, source_file: str, target_file: str) -> Optional[str]:
        """
        Create a batch script to handle the update installation

        Args:
            source_file: Path to the new executable
            target_file: Path where the new executable should be placed

        Returns:
            Path to the batch script if successful, None otherwise
        """
        try:
            batch_script_path = os.path.join(self.temp_dir, "update_installer.bat")

            # Create batch script content
            batch_content = f'''@echo off
echo Cursor-Tools Update Installer
echo ==============================
echo.
echo Waiting for application to close...
timeout /t 3 /nobreak >nul

echo Replacing executable...
copy /Y "{source_file}" "{target_file}"

if errorlevel 1 (
    echo ERROR: Failed to replace executable
    pause
    exit /b 1
)

echo Update completed successfully!
echo Starting updated application...

echo Cleaning up temporary files...
del "{source_file}" >nul 2>&1
del "%~f0" >nul 2>&1

echo.
echo Starting Cursor-Tools...
start "" "{target_file}"
'''

            # Write batch script
            with open(batch_script_path, 'w') as f:
                f.write(batch_content)

            return batch_script_path

        except Exception as e:
            self.ui_manager.display_error(f"Failed to create update script: {str(e)}")
            return None

    def perform_update_check_and_install(self, force_check: bool = False) -> bool:
        """
        Complete update process: check, download, and install

        Args:
            force_check: If True, bypass any caching and force a fresh check

        Returns:
            True if update was performed, False if no update or failed
        """
        try:
            # Check for updates
            update_info = self.check_for_updates(force_check)

            if not update_info:
                return False  # No update available or check failed

            # Display update notification and get user confirmation
            if not self.display_update_notification(update_info):
                # User declined update - enforce forced update policy
                self.ui_manager.clear_screen()
                self.ui_manager.display_header()

                error_text = Text("❌ UPDATE REQUIRED", style="bold red")
                error_text.append("\n\nThis application requires the latest version to continue.", style="yellow")
                error_text.append("\nThe application will now exit.", style="yellow")
                error_text.append("\n\nPlease download the latest version from:", style="white")
                error_text.append(f"\n{self.github_repo_url}/releases", style="cyan")

                error_panel = Panel(
                    Align.center(error_text),
                    border_style="red",
                    padding=(1, 2),
                    title="[bold red]Update Required[/bold red]"
                )

                self.ui_manager.console.print(error_panel)
                self.ui_manager.pause("Press Enter to exit...")
                sys.exit(1)

            # Download the update
            download_url = update_info.get('download_url')
            if not download_url:
                self.ui_manager.display_error("No download URL found for the update.")
                return False

            downloaded_file = self.download_update(download_url, update_info['version'])
            if not downloaded_file:
                return False

            # Verify the download
            if not self.verify_download(downloaded_file):
                return False

            # Create backup of current version
            if not self.backup_current_executable():
                self.ui_manager.display_warning("Failed to create backup, but continuing with update...")

            # Install the update
            return self.install_update(downloaded_file)

        except Exception as e:
            self.ui_manager.display_error(f"Update process failed: {str(e)}")
            return False

    def cleanup_old_files(self):
        """Clean up old temporary and backup files"""
        try:
            # Clean up temp files older than 7 days
            if os.path.exists(self.temp_dir):
                cutoff_time = time.time() - (7 * 24 * 60 * 60)  # 7 days ago
                for file in os.listdir(self.temp_dir):
                    file_path = os.path.join(self.temp_dir, file)
                    if os.path.isfile(file_path) and os.path.getmtime(file_path) < cutoff_time:
                        os.remove(file_path)

            # Clean up backup files older than 30 days
            if os.path.exists(self.backup_dir):
                cutoff_time = time.time() - (30 * 24 * 60 * 60)  # 30 days ago
                for file in os.listdir(self.backup_dir):
                    file_path = os.path.join(self.backup_dir, file)
                    if os.path.isfile(file_path) and os.path.getmtime(file_path) < cutoff_time:
                        os.remove(file_path)

        except Exception:
            # Silently ignore cleanup errors
            pass
