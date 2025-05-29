"""
Registry Manager for Cursor-Tools Application
Handles Windows registry operations, backup, and restore functionality
"""

import winreg
import json
import os
import uuid
from datetime import datetime
from typing import Dict, Any
from config import config

class RegistryManager:
    def __init__(self):
        # Use centralized configuration
        self.backup_dir = config.backups_dir
        self.registry_paths = config.registry_paths

        # Directory creation is handled by config initialization
        # No need to create directories here as config already ensures they exist

    def check_admin_privileges(self) -> bool:
        """Check if the application is running with administrator privileges"""
        try:
            # Try to open a registry key that requires admin access
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                               r"SYSTEM\CurrentControlSet\Control",
                               0, winreg.KEY_READ | winreg.KEY_WRITE)
            winreg.CloseKey(key)
            return True
        except PermissionError:
            return False
        except Exception:
            return False

    def read_registry_values(self) -> Dict[str, Dict[str, Any]]:
        """Read current registry values from all target locations"""
        values = {}

        # Use centralized target values configuration
        target_values = config.target_values

        for _, path in self.registry_paths.items():
            values[path] = {}
            try:
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path, 0, winreg.KEY_READ)

                # Only read the specific values we're interested in
                target_keys = target_values.get(path, [])
                for target_key in target_keys:
                    try:
                        value_data, _ = winreg.QueryValueEx(key, target_key)
                        values[path][target_key] = value_data
                    except FileNotFoundError:
                        values[path][target_key] = "Not found"
                    except Exception as e:
                        values[path][target_key] = f"Error: {str(e)}"

                winreg.CloseKey(key)

            except FileNotFoundError:
                values[path] = {"Error": "Registry path not found"}
            except PermissionError:
                values[path] = {"Error": "Access denied - Administrator privileges required"}
            except Exception as e:
                values[path] = {"Error": f"Unexpected error: {str(e)}"}

        return values

    def create_backup(self) -> str:
        """Create a backup of current registry values"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"registry_backup_{timestamp}.json"
        backup_path = os.path.join(self.backup_dir, backup_filename)

        try:
            current_values = self.read_registry_values()

            backup_data = {
                "timestamp": timestamp,
                "backup_date": datetime.now().isoformat(),
                "registry_values": current_values
            }

            with open(backup_path, 'w') as f:
                json.dump(backup_data, f, indent=2, default=str)

            return backup_path

        except Exception as e:
            raise Exception(f"Failed to create backup: {str(e)}")

    def restore_backup(self, backup_path: str) -> bool:
        """Restore registry values from backup"""
        try:
            with open(backup_path, 'r') as f:
                backup_data = json.load(f)

            registry_values = backup_data.get("registry_values", {})

            for path, values in registry_values.items():
                if "Error" in values:
                    continue

                try:
                    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path, 0,
                                       winreg.KEY_WRITE)

                    for value_name, value_data in values.items():
                        if isinstance(value_data, str):
                            winreg.SetValueEx(key, value_name, 0, winreg.REG_SZ, value_data)
                        elif isinstance(value_data, int):
                            winreg.SetValueEx(key, value_name, 0, winreg.REG_DWORD, value_data)
                        # Add more type handling as needed

                    winreg.CloseKey(key)

                except Exception as e:
                    raise Exception(f"Failed to restore {path}: {str(e)}")

            return True

        except Exception as e:
            raise Exception(f"Failed to restore backup: {str(e)}")

    def generate_new_device_ids(self) -> Dict[str, Dict[str, str]]:
        """Generate new device IDs for registry modification"""
        new_ids = {}

        # Generate new values for Cryptography - only MachineGuid
        new_ids[self.registry_paths["cryptography"]] = {
            "MachineGuid": str(uuid.uuid4()).upper()
        }

        # Generate new values for Hardware Profiles - only HwProfileGuid
        new_ids[self.registry_paths["hardware_profiles"]] = {
            "HwProfileGuid": "{" + str(uuid.uuid4()).upper() + "}"
        }

        # Generate new values for SQM Client - only MachineId
        new_ids[self.registry_paths["sqm_client"]] = {
            "MachineId": "{" + str(uuid.uuid4()).upper() + "}"
        }

        return new_ids

    def modify_device_ids(self) -> tuple[Dict[str, Dict[str, Any]], Dict[str, Dict[str, Any]]]:
        """Modify device IDs in registry and return before/after values"""
        # Get current values (before)
        before_values = self.read_registry_values()

        # Create backup before making changes
        backup_path = self.create_backup()

        # Generate new IDs
        new_ids = self.generate_new_device_ids()

        # Apply changes
        for path, new_values in new_ids.items():
            try:
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path, 0,
                                   winreg.KEY_WRITE)

                for value_name, value_data in new_values.items():
                    winreg.SetValueEx(key, value_name, 0, winreg.REG_SZ, value_data)

                winreg.CloseKey(key)

            except Exception as e:
                # If any modification fails, attempt to restore backup
                try:
                    self.restore_backup(backup_path)
                except:
                    pass
                raise Exception(f"Failed to modify {path}: {str(e)}")

        # Get new values (after)
        after_values = self.read_registry_values()

        return before_values, after_values

    def list_backups(self) -> list:
        """List available backup files with detailed information"""
        backups = []
        if os.path.exists(self.backup_dir):
            for filename in os.listdir(self.backup_dir):
                if filename.endswith('.json') and filename.startswith('registry_backup_'):
                    backup_path = os.path.join(self.backup_dir, filename)
                    try:
                        with open(backup_path, 'r') as f:
                            backup_data = json.load(f)

                        # Count registry entries
                        registry_values = backup_data.get('registry_values', {})
                        file_count = 0
                        for path_values in registry_values.values():
                            if isinstance(path_values, dict) and "Error" not in path_values:
                                file_count += len(path_values)

                        # Format timestamp for display
                        timestamp = backup_data.get('timestamp', 'Unknown')
                        try:
                            if timestamp != 'Unknown':
                                date_obj = datetime.strptime(timestamp, "%Y%m%d_%H%M%S")
                                formatted_date = date_obj.strftime("%Y-%m-%d %H:%M")
                            else:
                                formatted_date = "Unknown"
                        except:
                            formatted_date = "Unknown"

                        backups.append({
                            'name': filename.replace('.json', '').replace('registry_backup_', 'device_id_backup_'),
                            'filename': filename,
                            'path': backup_path,
                            'date': backup_data.get('backup_date', 'Unknown'),
                            'timestamp': timestamp,
                            'formatted_date': formatted_date,
                            'file_count': file_count,
                            'description': f"Device ID registry backup with {file_count} registry entries"
                        })
                    except:
                        continue

        # Sort by timestamp (newest first)
        backups.sort(key=lambda x: x['timestamp'], reverse=True)
        return backups
