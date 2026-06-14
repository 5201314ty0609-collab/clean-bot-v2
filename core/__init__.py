"""
CleanBot v2.0 — 核心引擎模块
"""

__version__ = "2.0.0"
__author__ = "PHOENIX"

# 延迟导入，避免循环依赖
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
