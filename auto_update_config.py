"""
Auto Update Configuration for Cursor-Tools
Centralized configuration for the auto-update system
"""

class AutoUpdateConfig:
    """Configuration class for auto-update system"""

    # Application version (this should match the current version)
    CURRENT_VERSION = "1.0.0"

    # GitHub repository information
    GITHUB_OWNER = "Mustafa-Bugra-Babuccu"
    GITHUB_REPO = "Cursor-Tools"
    GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/releases/latest"
    GITHUB_REPO_URL = f"https://github.com/{GITHUB_OWNER}/{GITHUB_REPO}"

    # Update policy settings
    FORCE_UPDATE_POLICY = True  # If True, application exits if user declines update
    CHECK_ON_STARTUP = True     # If True, check for updates at startup

    # Timeout settings (in seconds)
    UPDATE_CHECK_TIMEOUT = 10   # Timeout for GitHub API requests
    DOWNLOAD_TIMEOUT = 300      # Timeout for downloading updates (5 minutes)

    # SSL and network settings
    VERIFY_SSL = True           # Set to False to disable SSL verification (not recommended)
    ALLOW_REDIRECTS = True      # Allow HTTP redirects
    MAX_REDIRECTS = 5           # Maximum number of redirects to follow

    # File management settings
    BACKUP_RETENTION_DAYS = 30  # Keep backups for 30 days
    TEMP_CLEANUP_DAYS = 7       # Clean temp files after 7 days

    # Download settings
    CHUNK_SIZE = 8192           # Download chunk size in bytes

    # User agent for GitHub API requests
    USER_AGENT = f"Cursor-Tools/{CURRENT_VERSION}"

    # Executable naming patterns
    EXECUTABLE_PATTERNS = [
        "cursor-tools.exe",
        "cursor-tools-*.exe",
        "*.exe"
    ]

    # Update notification settings
    MAX_RELEASE_NOTES_LENGTH = 200  # Maximum length of release notes to display

    # Error retry settings
    MAX_RETRY_ATTEMPTS = 3      # Maximum number of retry attempts for failed operations
    RETRY_DELAY = 2             # Delay between retry attempts (seconds)

    # Batch script settings
    BATCH_SCRIPT_DELAY = 3      # Delay before starting update process (seconds)

    @classmethod
    def get_api_headers(cls):
        """Get headers for GitHub API requests"""
        return {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": cls.USER_AGENT
        }

    @classmethod
    def get_request_config(cls):
        """Get configuration for requests"""
        return {
            "timeout": cls.UPDATE_CHECK_TIMEOUT,
            "verify": cls.VERIFY_SSL,
            "allow_redirects": cls.ALLOW_REDIRECTS,
            "headers": cls.get_api_headers()
        }

    @classmethod
    def get_download_filename(cls, version):
        """Get the expected download filename for a version"""
        return f"Cursor-Tools-v{version}.exe"

    @classmethod
    def is_valid_asset(cls, asset_name):
        """Check if an asset name matches expected patterns"""
        asset_name_lower = asset_name.lower()

        # Check for exact matches first
        if asset_name_lower == "cursor-tools.exe":
            return True

        # Check for version-specific matches
        if "cursor-tools" in asset_name_lower and asset_name_lower.endswith(".exe"):
            return True

        # Fallback: any .exe file
        if asset_name_lower.endswith(".exe"):
            return True

        return False

    @classmethod
    def get_backup_filename(cls, timestamp, extension=".exe"):
        """Generate backup filename with timestamp"""
        return f"Cursor-Tools-backup-{timestamp}{extension}"

    @classmethod
    def validate_version_format(cls, version):
        """Validate version string format (semantic versioning)"""
        import re
        pattern = r'^\d+\.\d+\.\d+$'
        return bool(re.match(pattern, version))

    @classmethod
    def get_fallback_request_config(cls):
        """Get fallback configuration for requests with SSL disabled"""
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        return {
            "timeout": cls.UPDATE_CHECK_TIMEOUT,
            "verify": False,  # Disable SSL verification
            "allow_redirects": cls.ALLOW_REDIRECTS,
            "headers": cls.get_api_headers()
        }

# Global configuration instance
auto_update_config = AutoUpdateConfig()
