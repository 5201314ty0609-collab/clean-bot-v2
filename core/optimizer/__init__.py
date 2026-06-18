"""
CleanBot v3.0 -- System Optimizer Module

Provides system performance optimization features:
- Startup management
- Service optimization
- Memory optimization
- Registry cleaning
"""

from .startup_manager import StartupManager
from .service_optimizer import ServiceOptimizer
from .memory_optimizer import MemoryOptimizer
from .registry_cleaner import RegistryCleaner

__all__ = [
    "StartupManager",
    "ServiceOptimizer",
    "MemoryOptimizer",
    "RegistryCleaner",
]
