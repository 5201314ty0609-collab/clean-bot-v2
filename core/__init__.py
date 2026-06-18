"""
CleanBot v3.0 -- Core Engine Module
"""

__version__ = "3.0.0"
__author__ = "PHOENIX"

# Lazy imports to avoid circular dependencies
def get_scanner():
    from .scanner import FileScanner
    return FileScanner

def get_diagnosis():
    from .diagnosis.system_diagnosis import SystemDiagnosis
    return SystemDiagnosis

def get_monitor():
    from .monitor.disk_monitor import DiskMonitor
    return DiskMonitor

def get_recommendation():
    from .ai.recommendation import RecommendationEngine
    return RecommendationEngine

def get_analyzer():
    from .analyzer.smart_analyzer import SmartAnalyzer
    return SmartAnalyzer

def get_dialog():
    from .ai.dialog_system import DialogSystem
    return DialogSystem

# Optimizer module (v3.0)
def get_startup_manager():
    from .optimizer import StartupManager
    return StartupManager

def get_service_optimizer():
    from .optimizer import ServiceOptimizer
    return ServiceOptimizer

def get_memory_optimizer():
    from .optimizer import MemoryOptimizer
    return MemoryOptimizer

def get_registry_cleaner():
    from .optimizer import RegistryCleaner
    return RegistryCleaner
