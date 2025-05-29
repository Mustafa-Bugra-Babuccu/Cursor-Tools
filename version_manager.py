#!/usr/bin/env python3
"""
Version Manager for Cursor-Tools
Handles version detection, comparison, and build-time version setting
"""

import os
import re
import json
from pathlib import Path
from typing import Optional, Tuple

class CursorToolsVersionManager:
    """Manages version information for Cursor-Tools application"""

    def __init__(self):
        self.script_dir = Path(__file__).parent.absolute()
        self.version_file = self.script_dir / "version.json"

    def get_current_version(self) -> str:
        """Get the current application version"""
        # Try to get version from version.json first (for compiled builds)
        if self.version_file.exists():
            try:
                with open(self.version_file, 'r') as f:
                    version_data = json.load(f)
                    return version_data.get('version', '1.0.0')
            except Exception:
                pass

        # Fallback to config files
        try:
            from config import config_manager
            auto_config = config_manager.get_auto_update_config()
            return auto_config['CURRENT_VERSION']
        except Exception:
            return '1.0.0'

    def set_version(self, version: str) -> bool:
        """Set the application version in all relevant files"""
        if not self.validate_version_format(version):
            raise ValueError(f"Invalid version format: {version}")

        success = True

        # Update version.json
        try:
            version_data = {
                'version': version,
                'build_date': None,
                'build_type': 'development'
            }
            with open(self.version_file, 'w') as f:
                json.dump(version_data, f, indent=2)
        except Exception as e:
            print(f"Failed to update version.json: {e}")
            success = False

        # Update config.py
        try:
            self._update_config_file('config.py', version)
        except Exception as e:
            print(f"Failed to update config.py: {e}")
            success = False

        # Update auto_update_config.py
        try:
            self._update_auto_update_config_file('auto_update_config.py', version)
        except Exception as e:
            print(f"Failed to update auto_update_config.py: {e}")
            success = False

        # Update build_config.ini
        try:
            self._update_build_config_file('build_config.ini', version)
        except Exception as e:
            print(f"Failed to update build_config.ini: {e}")
            success = False

        return success

    def _update_config_file(self, filename: str, version: str):
        """Update version in config.py - SECURITY: Only updates hardcoded fallbacks, not INI settings"""
        file_path = self.script_dir / filename
        if not file_path.exists():
            return

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # SECURITY NOTE: We no longer update INI file settings for security
        # Only update hardcoded fallback values in the code

        # Update the fallback version in _get_secure_version method
        pattern = r"return '[^']+'"
        replacement = f"return '{version}'"
        # Only replace the last occurrence (fallback in _get_secure_version)
        content = re.sub(pattern, replacement, content)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

    def _update_auto_update_config_file(self, filename: str, version: str):
        """Update version in auto_update_config.py"""
        file_path = self.script_dir / filename
        if not file_path.exists():
            return

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Update CURRENT_VERSION
        pattern = r'CURRENT_VERSION = "[^"]+"'
        replacement = f'CURRENT_VERSION = "{version}"'
        content = re.sub(pattern, replacement, content)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

    def _update_build_config_file(self, filename: str, version: str):
        """Update version in build_config.ini"""
        file_path = self.script_dir / filename
        if not file_path.exists():
            return

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Update version in [Build] section
        pattern = r'^version = [^\r\n]*'
        replacement = f'version = {version}'
        content = re.sub(pattern, replacement, content, flags=re.MULTILINE)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

    def validate_version_format(self, version: str) -> bool:
        """Validate version string format (semantic versioning)"""
        pattern = r'^\d+\.\d+\.\d+$'
        return bool(re.match(pattern, version))

    def compare_versions(self, version1: str, version2: str) -> int:
        """
        Compare two version strings
        Returns: -1 if version1 < version2, 0 if equal, 1 if version1 > version2
        """
        try:
            v1_parts = tuple(map(int, version1.split(".")))
            v2_parts = tuple(map(int, version2.split(".")))

            if v1_parts < v2_parts:
                return -1
            elif v1_parts > v2_parts:
                return 1
            else:
                return 0
        except (ValueError, AttributeError):
            return 0

    def is_newer_version(self, latest: str, current: str) -> bool:
        """Check if latest version is newer than current"""
        return self.compare_versions(latest, current) > 0

    def prepare_for_build(self, target_version: str, build_type: str = 'release'):
        """Prepare version files for building"""
        if not self.validate_version_format(target_version):
            raise ValueError(f"Invalid version format: {target_version}")

        # Set the target version
        self.set_version(target_version)

        # Update version.json with build info
        from datetime import datetime
        version_data = {
            'version': target_version,
            'build_date': datetime.now().isoformat(),
            'build_type': build_type
        }

        with open(self.version_file, 'w') as f:
            json.dump(version_data, f, indent=2)

        print(f"✅ Prepared version {target_version} for {build_type} build")

    def get_version_info(self) -> dict:
        """Get comprehensive version information"""
        current_version = self.get_current_version()

        info = {
            'current_version': current_version,
            'version_file_exists': self.version_file.exists(),
            'build_info': None
        }

        if self.version_file.exists():
            try:
                with open(self.version_file, 'r') as f:
                    info['build_info'] = json.load(f)
            except Exception:
                pass

        return info

def main():
    """Command line interface for version management"""
    import sys

    if len(sys.argv) < 2:
        print("Usage:")
        print("  python version_manager.py get                    - Get current version")
        print("  python version_manager.py set <version>          - Set version")
        print("  python version_manager.py prepare <version>      - Prepare for build")
        print("  python version_manager.py info                   - Get version info")
        return

    vm = CursorToolsVersionManager()
    command = sys.argv[1].lower()

    if command == 'get':
        print(vm.get_current_version())

    elif command == 'set':
        if len(sys.argv) < 3:
            print("Error: Version required")
            return
        version = sys.argv[2]
        if vm.set_version(version):
            print(f"✅ Version set to {version}")
        else:
            print("❌ Failed to set version")

    elif command == 'prepare':
        if len(sys.argv) < 3:
            print("Error: Version required")
            return
        version = sys.argv[2]
        build_type = sys.argv[3] if len(sys.argv) > 3 else 'release'
        vm.prepare_for_build(version, build_type)

    elif command == 'info':
        info = vm.get_version_info()
        print(f"Current version: {info['current_version']}")
        print(f"Version file exists: {info['version_file_exists']}")
        if info['build_info']:
            print(f"Build date: {info['build_info'].get('build_date', 'Unknown')}")
            print(f"Build type: {info['build_info'].get('build_type', 'Unknown')}")

    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()
