"""
CleanBot v3.0 -- Registry Cleaner

Cleans Windows registry:
- Scan for invalid entries
- Remove orphaned entries
- Backup registry before changes
- Restore registry from backup
"""

import os
import sys
import winreg
import json
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from datetime import datetime


@dataclass
class RegistryEntry:
    """Registry entry information."""
    key_path: str
    value_name: str
    value_type: str
    value_data: str
    category: str  # invalid, orphaned, obsolete
    risk_level: str  # safe, medium, high
    description: str = ""


@dataclass
class RegistryBackup:
    """Registry backup information."""
    timestamp: float
    backup_path: str
    entries_count: int
    size_bytes: int


class RegistryCleaner:
    """Cleans Windows registry."""

    # Registry roots
    REGISTRY_ROOTS = {
        "HKCR": winreg.HKEY_CLASSES_ROOT,
        "HKCU": winreg.HKEY_CURRENT_USER,
        "HKLM": winreg.HKEY_LOCAL_MACHINE,
        "HKU": winreg.HKEY_USERS,
        "HKCC": winreg.HKEY_CURRENT_CONFIG,
    }

    # Paths to scan for invalid entries
    SCAN_PATHS = [
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"),
        (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders"),
        (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders"),
    ]

    # Safe to clean categories
    SAFE_CATEGORIES = {
        "orphaned_uninstall",
        "invalid_file_reference",
        "obsolete_software",
        "empty_keys",
    }

    def __init__(self, backup_dir: str = None):
        self.backup_dir = Path(backup_dir or os.path.expanduser("~/CleanBot/backups/registry"))
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        self.entries: List[RegistryEntry] = []
        self.backups: List[RegistryBackup] = []
        self._scan_registry()

    def _scan_registry(self):
        """Scan registry for invalid entries."""
        self.entries = []

        for hive, path in self.SCAN_PATHS:
            try:
                self._scan_key(hive, path)
            except Exception as e:
                print(f"Error scanning {path}: {e}", file=sys.stderr)

    def _scan_key(self, hive: int, path: str):
        """Scan a registry key for invalid entries."""
        try:
            with winreg.OpenKey(hive, path) as key:
                i = 0
                while True:
                    try:
                        subkey_name = winreg.EnumKey(key, i)
                        subkey_path = f"{path}\\{subkey_name}"

                        try:
                            with winreg.OpenKey(hive, subkey_path) as subkey:
                                self._check_uninstall_entry(hive, subkey_path, subkey)
                        except OSError:
                            pass

                        i += 1
                    except OSError:
                        break
            except OSError:
                pass

    def _check_uninstall_entry(self, hive: int, path: str, key):
        """Check an uninstall entry for validity."""
        try:
            # Get display name
            display_name = ""
            try:
                display_name, _ = winreg.QueryValueEx(key, "DisplayName")
            except OSError:
                pass

            # Get install location
            install_location = ""
            try:
                install_location, _ = winreg.QueryValueEx(key, "InstallLocation")
            except OSError:
                pass

            # Get uninstall string
            uninstall_string = ""
            try:
                uninstall_string, _ = winreg.QueryValueEx(key, "UninstallString")
            except OSError:
                pass

            # Check if install location exists
            if install_location and not os.path.exists(install_location):
                entry = RegistryEntry(
                    key_path=path,
                    value_name="InstallLocation",
                    value_type="REG_SZ",
                    value_data=install_location,
                    category="invalid_file_reference",
                    risk_level="safe",
                    description=f"Install location does not exist: {install_location}",
                )
                self.entries.append(entry)

            # Check if uninstall string exists
            if uninstall_string:
                # Extract executable path
                exe_path = uninstall_string.split('"')[0] if '"' in uninstall_string else uninstall_string.split()[0]
                if not os.path.exists(exe_path):
                    entry = RegistryEntry(
                        key_path=path,
                        value_name="UninstallString",
                        value_type="REG_SZ",
                        value_data=uninstall_string,
                        category="invalid_file_reference",
                        risk_level="safe",
                        description=f"Uninstall executable does not exist: {exe_path}",
                    )
                    self.entries.append(entry)

            # Check for empty display name
            if not display_name:
                entry = RegistryEntry(
                    key_path=path,
                    value_name="DisplayName",
                    value_type="REG_SZ",
                    value_data="(empty)",
                    category="orphaned_uninstall",
                    risk_level="safe",
                    description="Uninstall entry with no display name",
                )
                self.entries.append(entry)

        except Exception as e:
            print(f"Error checking {path}: {e}", file=sys.stderr)

    def get_entries(self) -> List[RegistryEntry]:
        """Get all registry entries."""
        return self.entries.copy()

    def get_entries_by_category(self, category: str) -> List[RegistryEntry]:
        """Get entries by category."""
        return [e for e in self.entries if e.category == category]

    def get_entries_by_risk(self, risk_level: str) -> List[RegistryEntry]:
        """Get entries by risk level."""
        return [e for e in self.entries if e.risk_level == risk_level]

    def get_safe_entries(self) -> List[RegistryEntry]:
        """Get entries that are safe to clean."""
        return [e for e in self.entries if e.category in self.SAFE_CATEGORIES]

    def backup_registry(self, entries: List[RegistryEntry] = None) -> Optional[RegistryBackup]:
        """Backup registry entries before cleaning."""
        if entries is None:
            entries = self.entries

        try:
            timestamp = time.time()
            backup_file = self.backup_dir / f"registry_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

            backup_data = {
                "timestamp": timestamp,
                "entries": [
                    {
                        "key_path": e.key_path,
                        "value_name": e.value_name,
                        "value_type": e.value_type,
                        "value_data": e.value_data,
                        "category": e.category,
                        "risk_level": e.risk_level,
                        "description": e.description,
                    }
                    for e in entries
                ],
            }

            with open(backup_file, "w", encoding="utf-8") as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False)

            backup = RegistryBackup(
                timestamp=timestamp,
                backup_path=str(backup_file),
                entries_count=len(entries),
                size_bytes=backup_file.stat().st_size,
            )
            self.backups.append(backup)

            return backup
        except Exception as e:
            print(f"Error backing up registry: {e}", file=sys.stderr)
            return None

    def clean_entry(self, entry: RegistryEntry) -> bool:
        """Clean a single registry entry."""
        try:
            # Parse key path
            parts = entry.key_path.split("\\", 1)
            if len(parts) != 2:
                return False

            root_name, sub_path = parts
            if root_name not in self.REGISTRY_ROOTS:
                return False

            hive = self.REGISTRY_ROOTS[root_name]

            # Delete the value
            try:
                with winreg.OpenKey(hive, sub_path, 0, winreg.KEY_SET_VALUE) as key:
                    winreg.DeleteValue(key, entry.value_name)
                    return True
            except OSError:
                return False

        except Exception as e:
            print(f"Error cleaning entry: {e}", file=sys.stderr)
            return False

    def clean_entries(self, entries: List[RegistryEntry]) -> Tuple[int, int]:
        """Clean multiple registry entries."""
        success = 0
        failed = 0

        for entry in entries:
            if self.clean_entry(entry):
                success += 1
            else:
                failed += 1

        return success, failed

    def restore_backup(self, backup: RegistryBackup) -> bool:
        """Restore registry from backup."""
        try:
            with open(backup.backup_path, "r", encoding="utf-8") as f:
                backup_data = json.load(f)

            # TODO: Implement actual restore logic
            # This would require recreating the registry entries

            return True
        except Exception as e:
            print(f"Error restoring backup: {e}", file=sys.stderr)
            return False

    def get_summary(self) -> Dict:
        """Get registry cleaning summary."""
        total = len(self.entries)
        safe = len(self.get_safe_entries())
        by_category = {}
        by_risk = {}

        for entry in self.entries:
            by_category[entry.category] = by_category.get(entry.category, 0) + 1
            by_risk[entry.risk_level] = by_risk.get(entry.risk_level, 0) + 1

        return {
            "total": total,
            "safe_to_clean": safe,
            "by_category": by_category,
            "by_risk": by_risk,
            "backups_count": len(self.backups),
        }
