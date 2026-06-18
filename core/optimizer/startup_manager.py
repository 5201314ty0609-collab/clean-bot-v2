"""
CleanBot v3.0 -- Startup Manager

Manages Windows startup programs:
- List all startup items
- Enable/disable startup items
- Add/remove startup items
- Analyze startup impact
"""

import os
import sys
import winreg
import subprocess
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from pathlib import Path


@dataclass
class StartupItem:
    """Startup item information."""
    name: str
    command: str
    location: str  # registry, folder, task
    enabled: bool
    impact: str  # high, medium, low
    publisher: str = ""
    description: str = ""
    path: str = ""


class StartupManager:
    """Manages Windows startup programs."""

    # Registry paths for startup items
    REGISTRY_PATHS = [
        (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run"),
        (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\RunOnce"),
        (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run"),
        (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\RunOnce"),
        (winreg.HKEY_LOCAL_MACHINE, r"Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Run"),
    ]

    # Startup folder paths
    STARTUP_FOLDERS = [
        Path(os.environ.get("APPDATA", "")) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup",
        Path(os.environ.get("PROGRAMDATA", "")) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup",
    ]

    # High impact programs
    HIGH_IMPACT_PROGRAMS = {
        "chrome", "firefox", "edge", "brave", "opera",
        "discord", "slack", "teams", "zoom", "skype",
        "spotify", "itunes", "steam", "epic",
        "dropbox", "onedrive", "googledrive",
        "antivirus", "defender", "norton", "mcafee", "kaspersky",
    }

    def __init__(self):
        self.items: List[StartupItem] = []
        self._scan_startup_items()

    def _scan_startup_items(self):
        """Scan all startup items from registry and folders."""
        self.items = []
        self._scan_registry()
        self._scan_folders()
        self._assess_impact()

    def _scan_registry(self):
        """Scan startup items from Windows registry."""
        for hive, path in self.REGISTRY_PATHS:
            try:
                with winreg.OpenKey(hive, path) as key:
                    i = 0
                    while True:
                        try:
                            name, value, _ = winreg.EnumValue(key, i)
                            item = StartupItem(
                                name=name,
                                command=value,
                                location=f"Registry: {path}",
                                enabled=True,
                                impact="medium",
                                path=self._extract_path(value),
                            )
                            self.items.append(item)
                            i += 1
                        except OSError:
                            break
            except OSError:
                continue

    def _scan_folders(self):
        """Scan startup items from startup folders."""
        for folder in self.STARTUP_FOLDERS:
            if not folder.exists():
                continue
            for item_path in folder.iterdir():
                if item_path.is_file():
                    item = StartupItem(
                        name=item_path.stem,
                        command=str(item_path),
                        location=f"Folder: {folder}",
                        enabled=True,
                        impact="medium",
                        path=str(item_path),
                    )
                    self.items.append(item)

    def _extract_path(self, command: str) -> str:
        """Extract executable path from command string."""
        # Handle quoted paths
        if command.startswith('"'):
            end = command.find('"', 1)
            if end > 0:
                return command[1:end]
        # Handle unquoted paths
        parts = command.split()
        if parts:
            return parts[0]
        return command

    def _assess_impact(self):
        """Assess startup impact for each item."""
        for item in self.items:
            name_lower = item.name.lower()
            path_lower = item.path.lower()

            # Check for high impact programs
            for program in self.HIGH_IMPACT_PROGRAMS:
                if program in name_lower or program in path_lower:
                    item.impact = "high"
                    break

            # Check for system services
            if "windows" in name_lower or "microsoft" in name_lower:
                item.impact = "low"

            # Check for security software
            security_keywords = ["antivirus", "defender", "firewall", "security"]
            for keyword in security_keywords:
                if keyword in name_lower or keyword in path_lower:
                    item.impact = "high"
                    break

    def get_items(self) -> List[StartupItem]:
        """Get all startup items."""
        return self.items.copy()

    def get_enabled_items(self) -> List[StartupItem]:
        """Get enabled startup items."""
        return [item for item in self.items if item.enabled]

    def get_disabled_items(self) -> List[StartupItem]:
        """Get disabled startup items."""
        return [item for item in self.items if not item.enabled]

    def get_high_impact_items(self) -> List[StartupItem]:
        """Get high impact startup items."""
        return [item for item in self.items if item.impact == "high"]

    def disable_item(self, name: str) -> bool:
        """Disable a startup item."""
        for item in self.items:
            if item.name == name:
                item.enabled = False
                # TODO: Implement actual disable logic
                return True
        return False

    def enable_item(self, name: str) -> bool:
        """Enable a startup item."""
        for item in self.items:
            if item.name == name:
                item.enabled = True
                # TODO: Implement actual enable logic
                return True
        return False

    def remove_item(self, name: str) -> bool:
        """Remove a startup item."""
        for i, item in enumerate(self.items):
            if item.name == name:
                # TODO: Implement actual remove logic
                self.items.pop(i)
                return True
        return False

    def add_item(self, name: str, command: str, location: str = "registry") -> bool:
        """Add a new startup item."""
        # TODO: Implement actual add logic
        item = StartupItem(
            name=name,
            command=command,
            location=location,
            enabled=True,
            impact="medium",
            path=self._extract_path(command),
        )
        self.items.append(item)
        return True

    def get_summary(self) -> Dict:
        """Get startup summary."""
        total = len(self.items)
        enabled = len(self.get_enabled_items())
        high_impact = len(self.get_high_impact_items())

        return {
            "total": total,
            "enabled": enabled,
            "disabled": total - enabled,
            "high_impact": high_impact,
            "medium_impact": len([i for i in self.items if i.impact == "medium"]),
            "low_impact": len([i for i in self.items if i.impact == "low"]),
        }
