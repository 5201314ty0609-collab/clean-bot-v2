"""
CleanBot v3.0 -- Service Optimizer

Optimizes Windows services:
- List all services
- Disable unnecessary services
- Optimize service startup types
- Analyze service impact
"""

import os
import sys
import subprocess
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum


class ServiceStatus(Enum):
    """Service status."""
    RUNNING = "running"
    STOPPED = "stopped"
    PAUSED = "paused"
    UNKNOWN = "unknown"


class ServiceStartupType(Enum):
    """Service startup type."""
    AUTOMATIC = "automatic"
    MANUAL = "manual"
    DISABLED = "disabled"
    UNKNOWN = "unknown"


@dataclass
class ServiceInfo:
    """Service information."""
    name: str
    display_name: str
    status: ServiceStatus
    startup_type: ServiceStartupType
    description: str = ""
    impact: str = "medium"  # high, medium, low
    can_disable: bool = True
    publisher: str = ""
    path: str = ""


class ServiceOptimizer:
    """Optimizes Windows services."""

    # Services that should never be disabled
    ESSENTIAL_SERVICES = {
        "wuauserv",  # Windows Update
        "WinDefend",  # Windows Defender
        "Dhcp",  # DHCP Client
        "Dnscache",  # DNS Client
        "LanmanWorkstation",  # Workstation
        "LanmanServer",  # Server
        "RpcSs",  # Remote Procedure Call
        "SamSs",  # Security Accounts Manager
        "EventLog",  # Windows Event Log
        "PlugPlay",  # Plug and Play
        "Power",  # Power
        "BrokerInfrastructure",  # Background Tasks Infrastructure
        "DcomLaunch",  # DCOM Server Process Launcher
        "LSM",  # Local Session Manager
        "NlaSvc",  # Network Location Awareness
        "Wcmsvc",  # Windows Connection Manager
        "WdiServiceHost",  # Diagnostic Service Host
        "WdiSystemHost",  # Diagnostic System Host
    }

    # Services that can be safely disabled
    SAFE_TO_DISABLE = {
        "SysMain",  # Superfetch (can cause high disk usage)
        "WSearch",  # Windows Search (if not using search)
        "DiagTrack",  # Diagnostics Tracking
        "dmwappushservice",  # WAP Push Message Routing Service
        "MapsBroker",  # Downloaded Maps Manager
        "lfsvc",  # Geolocation Service
        "SharedAccess",  # Internet Connection Sharing (ICS)
        "RemoteRegistry",  # Remote Registry
        "RetailDemo",  # Retail Demo Service
        "XblAuthManager",  # Xbox Live Auth Manager
        "XblGameSave",  # Xbox Live Game Save
        "XboxNetApiSvc",  # Xbox Live Networking Service
    }

    def __init__(self):
        self.services: List[ServiceInfo] = []
        self._scan_services()

    def _scan_services(self):
        """Scan all Windows services."""
        self.services = []

        try:
            # Use sc query to get service list
            result = subprocess.run(
                ["sc", "query", "type= all", "state= all"],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
            )

            if result.returncode == 0:
                self._parse_sc_output(result.stdout)
        except Exception as e:
            print(f"Error scanning services: {e}", file=sys.stderr)

    def _parse_sc_output(self, output: str):
        """Parse sc query output."""
        current_service = None

        for line in output.split("\n"):
            line = line.strip()

            if line.startswith("SERVICE_NAME:"):
                if current_service:
                    self.services.append(current_service)
                name = line.split(":", 1)[1].strip()
                current_service = ServiceInfo(
                    name=name,
                    display_name=name,
                    status=ServiceStatus.UNKNOWN,
                    startup_type=ServiceStartupType.UNKNOWN,
                )
            elif line.startswith("DISPLAY_NAME:") and current_service:
                current_service.display_name = line.split(":", 1)[1].strip()
            elif line.startswith("STATE:") and current_service:
                state = line.split(":", 1)[1].strip()
                if "RUNNING" in state:
                    current_service.status = ServiceStatus.RUNNING
                elif "STOPPED" in state:
                    current_service.status = ServiceStatus.STOPPED
                elif "PAUSED" in state:
                    current_service.status = ServiceStatus.PAUSED

        if current_service:
            self.services.append(current_service)

        # Get startup types
        self._get_startup_types()

    def _get_startup_types(self):
        """Get startup type for each service."""
        try:
            result = subprocess.run(
                ["sc", "qc", "all"],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
            )

            if result.returncode == 0:
                self._parse_startup_types(result.stdout)
        except Exception:
            pass

    def _parse_startup_types(self, output: str):
        """Parse sc qc output to get startup types."""
        current_name = None

        for line in output.split("\n"):
            line = line.strip()

            if line.startswith("SERVICE_NAME:"):
                current_name = line.split(":", 1)[1].strip()
            elif line.startswith("START_TYPE:") and current_name:
                startup = line.split(":", 1)[1].strip()
                for service in self.services:
                    if service.name == current_name:
                        if "AUTO" in startup:
                            service.startup_type = ServiceStartupType.AUTOMATIC
                        elif "DEMAND" in startup:
                            service.startup_type = ServiceStartupType.MANUAL
                        elif "DISABLED" in startup:
                            service.startup_type = ServiceStartupType.DISABLED
                        break

    def get_services(self) -> List[ServiceInfo]:
        """Get all services."""
        return self.services.copy()

    def get_running_services(self) -> List[ServiceInfo]:
        """Get running services."""
        return [s for s in self.services if s.status == ServiceStatus.RUNNING]

    def get_automatic_services(self) -> List[ServiceInfo]:
        """Get automatic startup services."""
        return [s for s in self.services if s.startup_type == ServiceStartupType.AUTOMATIC]

    def get_safe_to_disable(self) -> List[ServiceInfo]:
        """Get services that are safe to disable."""
        return [
            s for s in self.services
            if s.name in self.SAFE_TO_DISABLE
            and s.startup_type != ServiceStartupType.DISABLED
        ]

    def disable_service(self, name: str) -> bool:
        """Disable a service."""
        if name in self.ESSENTIAL_SERVICES:
            return False

        try:
            result = subprocess.run(
                ["sc", "config", name, "start=", "disabled"],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
            )

            if result.returncode == 0:
                for service in self.services:
                    if service.name == name:
                        service.startup_type = ServiceStartupType.DISABLED
                        return True
        except Exception:
            pass

        return False

    def stop_service(self, name: str) -> bool:
        """Stop a running service."""
        if name in self.ESSENTIAL_SERVICES:
            return False

        try:
            result = subprocess.run(
                ["sc", "stop", name],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
            )

            if result.returncode == 0:
                for service in self.services:
                    if service.name == name:
                        service.status = ServiceStatus.STOPPED
                        return True
        except Exception:
            pass

        return False

    def set_manual(self, name: str) -> bool:
        """Set service startup type to manual."""
        if name in self.ESSENTIAL_SERVICES:
            return False

        try:
            result = subprocess.run(
                ["sc", "config", name, "start=", "demand"],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
            )

            if result.returncode == 0:
                for service in self.services:
                    if service.name == name:
                        service.startup_type = ServiceStartupType.MANUAL
                        return True
        except Exception:
            pass

        return False

    def get_summary(self) -> Dict:
        """Get services summary."""
        total = len(self.services)
        running = len(self.get_running_services())
        automatic = len(self.get_automatic_services())
        safe_to_disable = len(self.get_safe_to_disable())

        return {
            "total": total,
            "running": running,
            "stopped": total - running,
            "automatic": automatic,
            "manual": len([s for s in self.services if s.startup_type == ServiceStartupType.MANUAL]),
            "disabled": len([s for s in self.services if s.startup_type == ServiceStartupType.DISABLED]),
            "safe_to_disable": safe_to_disable,
        }
