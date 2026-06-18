"""
CleanBot v3.0 -- Startup Optimizer

Optimizes application startup time:
- Lazy loading of non-critical modules
- Caching of frequently used data
- Parallel initialization of independent components
- Preloading of essential resources
"""

import sys
import time
import threading
from pathlib import Path
from typing import Dict, List, Optional, Callable, Any
from functools import lru_cache


class StartupOptimizer:
    """Optimizes application startup time."""

    def __init__(self):
        self._start_time = time.time()
        self._milestones: Dict[str, float] = {}
        self._lazy_modules: Dict[str, Any] = {}
        self._preload_threads: List[threading.Thread] = []
        self._cache: Dict[str, Any] = {}

    def mark_milestone(self, name: str):
        """Mark a startup milestone."""
        self._milestones[name] = time.time() - self._start_time

    def get_milestones(self) -> Dict[str, float]:
        """Get all milestones."""
        return self._milestones.copy()

    def get_startup_time(self) -> float:
        """Get total startup time."""
        return time.time() - self._start_time

    def lazy_import(self, module_name: str, package: str = None):
        """Lazy import a module."""
        if module_name in self._lazy_modules:
            return self._lazy_modules[module_name]

        try:
            if package:
                module = __import__(f"{package}.{module_name}", fromlist=[module_name])
            else:
                module = __import__(module_name)
            self._lazy_modules[module_name] = module
            return module
        except ImportError as e:
            print(f"Warning: Failed to lazy import {module_name}: {e}", file=sys.stderr)
            return None

    def preload_resource(self, resource_path: str, loader: Callable):
        """Preload a resource in background."""
        def _load():
            try:
                data = loader(resource_path)
                self._cache[resource_path] = data
            except Exception as e:
                print(f"Warning: Failed to preload {resource_path}: {e}", file=sys.stderr)

        thread = threading.Thread(target=_load, daemon=True)
        thread.start()
        self._preload_threads.append(thread)

    def get_cached_resource(self, resource_path: str) -> Optional[Any]:
        """Get a preloaded resource."""
        return self._cache.get(resource_path)

    def wait_for_preloads(self, timeout: float = 5.0):
        """Wait for all preloads to complete."""
        for thread in self._preload_threads:
            thread.join(timeout=timeout)

    def get_performance_report(self) -> str:
        """Get performance report."""
        lines = ["Startup Performance Report", "=" * 40]

        milestones = sorted(self._milestones.items(), key=lambda x: x[1])
        for name, duration in milestones:
            lines.append(f"  {name}: {duration:.3f}s")

        total = self.get_startup_time()
        lines.append(f"\nTotal startup time: {total:.3f}s")

        return "\n".join(lines)


class LazyModule:
    """Lazy module loader."""

    def __init__(self, module_name: str, package: str = None):
        self.module_name = module_name
        self.package = package
        self._module = None
        self._loaded = False

    def _load(self):
        if self._loaded:
            return

        try:
            if self.package:
                self._module = __import__(
                    f"{self.package}.{self.module_name}",
                    fromlist=[self.module_name]
                )
            else:
                self._module = __import__(self.module_name)
            self._loaded = True
        except ImportError as e:
            print(f"Warning: Failed to load {self.module_name}: {e}", file=sys.stderr)

    def __getattr__(self, name: str):
        self._load()
        if self._module:
            return getattr(self._module, name)
        raise AttributeError(f"Module {self.module_name} not loaded")


class ResourceCache:
    """Resource cache with TTL."""

    def __init__(self, default_ttl: float = 300.0):  # 5 minutes default
        self._cache: Dict[str, Any] = {}
        self._timestamps: Dict[str, float] = {}
        self._ttl: Dict[str, float] = {}
        self._default_ttl = default_ttl
        self._lock = threading.Lock()

    def get(self, key: str) -> Optional[Any]:
        """Get a cached resource."""
        with self._lock:
            if key not in self._cache:
                return None

            # Check TTL
            if time.time() - self._timestamps[key] > self._ttl.get(key, self._default_ttl):
                del self._cache[key]
                del self._timestamps[key]
                if key in self._ttl:
                    del self._ttl[key]
                return None

            return self._cache[key]

    def set(self, key: str, value: Any, ttl: float = None):
        """Set a cached resource."""
        with self._lock:
            self._cache[key] = value
            self._timestamps[key] = time.time()
            if ttl is not None:
                self._ttl[key] = ttl

    def clear(self):
        """Clear all cached resources."""
        with self._lock:
            self._cache.clear()
            self._timestamps.clear()
            self._ttl.clear()

    def size(self) -> int:
        """Get cache size."""
        return len(self._cache)


# Global instances
_startup_optimizer = StartupOptimizer()
_resource_cache = ResourceCache()


def get_startup_optimizer() -> StartupOptimizer:
    """Get global startup optimizer."""
    return _startup_optimizer


def get_resource_cache() -> ResourceCache:
    """Get global resource cache."""
    return _resource_cache


@lru_cache(maxsize=128)
def cached_import(module_name: str, package: str = None):
    """Cached module import."""
    try:
        if package:
            return __import__(f"{package}.{module_name}", fromlist=[module_name])
        else:
            return __import__(module_name)
    except ImportError:
        return None
