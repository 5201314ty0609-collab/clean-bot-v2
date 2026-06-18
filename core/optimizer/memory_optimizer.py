"""
CleanBot v3.0 -- Memory Optimizer

Optimizes system memory usage:
- Monitor memory usage
- Identify memory hogs
- Optimize memory allocation
- Clean memory leaks
"""

import os
import sys
import time
import psutil
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from collections import defaultdict


@dataclass
class MemoryInfo:
    """Memory information."""
    total: int
    available: int
    used: int
    percent: float
    cached: int = 0
    buffered: int = 0
    shared: int = 0


@dataclass
class ProcessMemory:
    """Process memory information."""
    pid: int
    name: str
    memory_percent: float
    memory_rss: int  # Resident Set Size
    memory_vms: int  # Virtual Memory Size
    username: str = ""
    status: str = ""
    create_time: float = 0


@dataclass
class MemoryOptimization:
    """Memory optimization suggestion."""
    process_name: str
    pid: int
    current_memory: int
    suggested_action: str
    reason: str
    priority: str  # high, medium, low


class MemoryOptimizer:
    """Optimizes system memory usage."""

    # Memory thresholds
    HIGH_MEMORY_THRESHOLD = 80  # percent
    CRITICAL_MEMORY_THRESHOLD = 90  # percent
    PROCESS_MEMORY_THRESHOLD = 500 * 1024 * 1024  # 500MB

    # Processes to ignore
    IGNORE_PROCESSES = {
        "System", "Registry", "smss.exe", "csrss.exe", "wininit.exe",
        "services.exe", "lsass.exe", "svchost.exe", "fontdrvhost.exe",
        "dwm.exe", "explorer.exe",
    }

    def __init__(self):
        self.memory_info: Optional[MemoryInfo] = None
        self.top_processes: List[ProcessMemory] = []
        self.optimizations: List[MemoryOptimization] = []
        self._scan_memory()

    def _scan_memory(self):
        """Scan current memory usage."""
        try:
            mem = psutil.virtual_memory()
            self.memory_info = MemoryInfo(
                total=mem.total,
                available=mem.available,
                used=mem.used,
                percent=mem.percent,
                cached=getattr(mem, 'cached', 0),
                buffered=getattr(mem, 'buffers', 0),
                shared=getattr(mem, 'shared', 0),
            )

            # Get top memory consumers
            self._get_top_processes()

            # Generate optimization suggestions
            self._generate_optimizations()
        except Exception as e:
            print(f"Error scanning memory: {e}", file=sys.stderr)

    def _get_top_processes(self, limit: int = 20):
        """Get top memory consuming processes."""
        self.top_processes = []

        try:
            for proc in psutil.process_iter(['pid', 'name', 'memory_percent', 'memory_info', 'username', 'status', 'create_time']):
                try:
                    pinfo = proc.info
                    if pinfo['name'] in self.IGNORE_PROCESSES:
                        continue

                    proc_memory = ProcessMemory(
                        pid=pinfo['pid'],
                        name=pinfo['name'],
                        memory_percent=pinfo['memory_percent'],
                        memory_rss=pinfo['memory_info'].rss if pinfo['memory_info'] else 0,
                        memory_vms=pinfo['memory_info'].vms if pinfo['memory_info'] else 0,
                        username=pinfo.get('username', ''),
                        status=pinfo.get('status', ''),
                        create_time=pinfo.get('create_time', 0),
                    )
                    self.top_processes.append(proc_memory)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            # Sort by memory usage
            self.top_processes.sort(key=lambda x: x.memory_percent, reverse=True)
            self.top_processes = self.top_processes[:limit]
        except Exception as e:
            print(f"Error getting top processes: {e}", file=sys.stderr)

    def _generate_optimizations(self):
        """Generate memory optimization suggestions."""
        self.optimizations = []

        if not self.memory_info:
            return

        # Check if memory usage is high
        if self.memory_info.percent >= self.CRITICAL_MEMORY_THRESHOLD:
            # Suggest closing memory hogs
            for proc in self.top_processes[:5]:
                if proc.memory_rss > self.PROCESS_MEMORY_THRESHOLD:
                    self.optimizations.append(MemoryOptimization(
                        process_name=proc.name,
                        pid=proc.pid,
                        current_memory=proc.memory_rss,
                        suggested_action="close",
                        reason=f"Process using {proc.memory_rss / (1024*1024):.0f}MB with memory at {self.memory_info.percent:.0f}%",
                        priority="high",
                    ))

        elif self.memory_info.percent >= self.HIGH_MEMORY_THRESHOLD:
            # Suggest reducing memory usage
            for proc in self.top_processes[:3]:
                if proc.memory_rss > self.PROCESS_MEMORY_THRESHOLD:
                    self.optimizations.append(MemoryOptimization(
                        process_name=proc.name,
                        pid=proc.pid,
                        current_memory=proc.memory_rss,
                        suggested_action="reduce",
                        reason=f"Process using {proc.memory_rss / (1024*1024):.0f}MB",
                        priority="medium",
                    ))

    def get_memory_info(self) -> Optional[MemoryInfo]:
        """Get current memory information."""
        return self.memory_info

    def get_top_processes(self) -> List[ProcessMemory]:
        """Get top memory consuming processes."""
        return self.top_processes.copy()

    def get_optimizations(self) -> List[MemoryOptimization]:
        """Get memory optimization suggestions."""
        return self.optimizations.copy()

    def is_memory_high(self) -> bool:
        """Check if memory usage is high."""
        if self.memory_info:
            return self.memory_info.percent >= self.HIGH_MEMORY_THRESHOLD
        return False

    def is_memory_critical(self) -> bool:
        """Check if memory usage is critical."""
        if self.memory_info:
            return self.memory_info.percent >= self.CRITICAL_MEMORY_THRESHOLD
        return False

    def get_memory_usage_by_category(self) -> Dict[str, int]:
        """Get memory usage grouped by process category."""
        categories = defaultdict(int)

        for proc in self.top_processes:
            name_lower = proc.name.lower()

            # Categorize processes
            if any(browser in name_lower for browser in ["chrome", "firefox", "edge", "brave", "opera"]):
                categories["Browsers"] += proc.memory_rss
            elif any(office in name_lower for office in ["word", "excel", "powerpoint", "outlook", "teams"]):
                categories["Office"] += proc.memory_rss
            elif any(media in name_lower for media in ["spotify", "vlc", "media", "player"]):
                categories["Media"] += proc.memory_rss
            elif any(dev in name_lower for dev in ["code", "studio", "intellij", "pycharm", "git"]):
                categories["Development"] += proc.memory_rss
            elif any(game in name_lower for game in ["steam", "epic", "game", "unity", "unreal"]):
                categories["Gaming"] += proc.memory_rss
            else:
                categories["Other"] += proc.memory_rss

        return dict(categories)

    def get_summary(self) -> Dict:
        """Get memory summary."""
        if not self.memory_info:
            return {}

        return {
            "total_gb": self.memory_info.total / (1024**3),
            "used_gb": self.memory_info.used / (1024**3),
            "available_gb": self.memory_info.available / (1024**3),
            "percent": self.memory_info.percent,
            "is_high": self.is_memory_high(),
            "is_critical": self.is_memory_critical(),
            "top_process": self.top_processes[0].name if self.top_processes else "N/A",
            "top_process_memory_mb": self.top_processes[0].memory_rss / (1024**2) if self.top_processes else 0,
            "optimization_count": len(self.optimizations),
        }

    def optimize_memory(self) -> bool:
        """Attempt to optimize memory by clearing caches."""
        try:
            # Clear Windows file cache
            if sys.platform == "win32":
                import ctypes
                ctypes.windll.kernel32.SetSystemFileCacheSize(0, 0, 0)

            # Force garbage collection
            import gc
            gc.collect()

            # Re-scan memory
            self._scan_memory()

            return True
        except Exception as e:
            print(f"Error optimizing memory: {e}", file=sys.stderr)
            return False
