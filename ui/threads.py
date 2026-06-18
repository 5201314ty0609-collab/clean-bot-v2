"""
CleanBot v2.0 -- Background Threads

All QThread subclasses for non-blocking operations:
scanning, cleaning, diagnosis, monitoring, and recommendations.
"""

from PyQt6.QtCore import QThread, pyqtSignal


class ScanThread(QThread):
    """Background file scanner."""
    progress = pyqtSignal(int, int)
    finished = pyqtSignal(object)

    def __init__(self, root_path: str = None, deep: bool = False):
        super().__init__()
        from core.utils import get_system_drive
        self.root_path = root_path or get_system_drive()
        self.deep = deep

    def run(self):
        from core.scanner.file_scanner import FileScanner
        scanner = FileScanner(self.root_path)
        result = scanner.scan(
            progress_callback=lambda c, s: self.progress.emit(c, s),
            deep=self.deep,
        )
        self.finished.emit(result)


class CleanThread(QThread):
    """Background file cleaner."""
    progress = pyqtSignal(int, int, str)
    finished = pyqtSignal(object)

    def __init__(self, files: list, use_trash: bool = True):
        super().__init__()
        self.files = files
        self.use_trash = use_trash

    def run(self):
        from core.cleaner.file_cleaner import FileCleaner
        cleaner = FileCleaner(use_trash=self.use_trash)
        result = cleaner.clean(
            self.files,
            progress_callback=lambda prog: self.progress.emit(
                prog.current, prog.total, prog.current_file
            )
        )
        self.finished.emit(result)


class DiagnosisThread(QThread):
    """Background system diagnosis."""
    finished = pyqtSignal(object)

    def run(self):
        from core.diagnosis.system_diagnosis import SystemDiagnosis
        diagnosis = SystemDiagnosis()
        report = diagnosis.run_full_diagnosis()
        self.finished.emit(report)


class MonitorThread(QThread):
    """Background disk monitor -- keeps psutil off the UI thread."""
    data_ready = pyqtSignal(dict)

    def run(self):
        import psutil
        from core.utils import get_system_drive

        data = {}
        try:
            system_drive = get_system_drive()
            disk_usage = psutil.disk_usage(system_drive)
            data["disk"] = {
                "total": disk_usage.total,
                "used": disk_usage.used,
                "free": disk_usage.free,
                "percent": disk_usage.percent,
            }
        except (PermissionError, OSError):
            pass

        self.data_ready.emit(data)


class RecommendationThread(QThread):
    """Background recommendation generator."""
    finished = pyqtSignal(list)

    def run(self):
        from core.ai.recommendation import RecommendationEngine
        engine = RecommendationEngine()
        recommendations = engine.generate_recommendations()
        self.finished.emit(recommendations)


class UpdateCheckThread(QThread):
    """Background update checker — keeps network I/O off the UI thread."""
    finished = pyqtSignal(object)  # emits UpdateInfo or None

    def run(self):
        from core.updater import check_for_update
        info = check_for_update()
        self.finished.emit(info)


# ═══════════════════════════════════════════════════════════════════════════
# v3.0 Optimizer Threads
# ═══════════════════════════════════════════════════════════════════════════

class StartupScanThread(QThread):
    """Background startup items scanner."""
    finished = pyqtSignal(list)

    def run(self):
        from core.optimizer import StartupManager
        manager = StartupManager()
        items = manager.get_items()
        self.finished.emit(items)


class ServiceScanThread(QThread):
    """Background services scanner."""
    finished = pyqtSignal(list)

    def run(self):
        from core.optimizer import ServiceOptimizer
        optimizer = ServiceOptimizer()
        services = optimizer.get_services()
        self.finished.emit(services)


class MemoryScanThread(QThread):
    """Background memory scanner."""
    finished = pyqtSignal(dict)

    def run(self):
        from core.optimizer import MemoryOptimizer
        optimizer = MemoryOptimizer()
        data = {
            "info": optimizer.get_memory_info(),
            "top_processes": optimizer.get_top_processes(),
            "summary": optimizer.get_summary(),
        }
        self.finished.emit(data)


class RegistryScanThread(QThread):
    """Background registry scanner."""
    finished = pyqtSignal(list)

    def run(self):
        from core.optimizer import RegistryCleaner
        cleaner = RegistryCleaner()
        entries = cleaner.get_entries()
        self.finished.emit(entries)


class StartupOptimizeThread(QThread):
    """Background startup optimizer."""
    progress = pyqtSignal(int, int)
    finished = pyqtSignal(dict)

    def __init__(self, items_to_disable: list):
        super().__init__()
        self.items_to_disable = items_to_disable

    def run(self):
        from core.optimizer import StartupManager
        manager = StartupManager()

        results = {"success": 0, "failed": 0, "details": []}
        total = len(self.items_to_disable)

        for i, item_name in enumerate(self.items_to_disable):
            if manager.disable_item(item_name):
                results["success"] += 1
                results["details"].append({"name": item_name, "status": "disabled"})
            else:
                results["failed"] += 1
                results["details"].append({"name": item_name, "status": "failed"})

            self.progress.emit(i + 1, total)

        self.finished.emit(results)


class ServiceOptimizeThread(QThread):
    """Background service optimizer."""
    progress = pyqtSignal(int, int)
    finished = pyqtSignal(dict)

    def __init__(self, services_to_optimize: list):
        super().__init__()
        self.services_to_optimize = services_to_optimize

    def run(self):
        from core.optimizer import ServiceOptimizer
        optimizer = ServiceOptimizer()

        results = {"success": 0, "failed": 0, "details": []}
        total = len(self.services_to_optimize)

        for i, service_name in enumerate(self.services_to_optimize):
            if optimizer.set_manual(service_name):
                results["success"] += 1
                results["details"].append({"name": service_name, "status": "manual"})
            else:
                results["failed"] += 1
                results["details"].append({"name": service_name, "status": "failed"})

            self.progress.emit(i + 1, total)

        self.finished.emit(results)


class MemoryOptimizeThread(QThread):
    """Background memory optimizer."""
    finished = pyqtSignal(dict)

    def run(self):
        from core.optimizer import MemoryOptimizer
        optimizer = MemoryOptimizer()

        success = optimizer.optimize_memory()
        summary = optimizer.get_summary()

        results = {
            "success": success,
            "summary": summary,
        }
        self.finished.emit(results)


class RegistryCleanThread(QThread):
    """Background registry cleaner."""
    progress = pyqtSignal(int, int)
    finished = pyqtSignal(dict)

    def __init__(self, entries_to_clean: list):
        super().__init__()
        self.entries_to_clean = entries_to_clean

    def run(self):
        from core.optimizer import RegistryCleaner
        cleaner = RegistryCleaner()

        # Backup first
        backup = cleaner.backup_registry(self.entries_to_clean)

        # Clean entries
        success, failed = cleaner.clean_entries(self.entries_to_clean)

        results = {
            "success": success,
            "failed": failed,
            "backup_path": backup.backup_path if backup else None,
        }
        self.finished.emit(results)


class SystemOptimizeThread(QThread):
    """Background full system optimizer."""
    progress = pyqtSignal(str, int, int)
    finished = pyqtSignal(dict)

    def run(self):
        from core.optimizer import (
            StartupManager,
            ServiceOptimizer,
            MemoryOptimizer,
            RegistryCleaner,
        )
        from core.ai.advanced_dialog import AdvancedDialogSystem, AdvancedDialogContext

        dialog = AdvancedDialogSystem()
        results = {
            "startup": {},
            "services": {},
            "memory": {},
            "registry": {},
            "overall_improvement": "",
        }

        # Step 1: Startup optimization
        self.progress.emit("startup", 0, 4)
        startup_manager = StartupManager()
        safe_to_disable = [i for i in startup_manager.get_items() if i.impact == "low"]
        if safe_to_disable:
            for item in safe_to_disable[:5]:  # Disable up to 5 low-impact items
                startup_manager.disable_item(item.name)
            results["startup"] = startup_manager.get_summary()

        # Step 2: Service optimization
        self.progress.emit("services", 1, 4)
        service_optimizer = ServiceOptimizer()
        safe_services = service_optimizer.get_safe_to_disable()
        if safe_services:
            for service in safe_services[:3]:  # Disable up to 3 safe services
                service_optimizer.set_manual(service.name)
            results["services"] = service_optimizer.get_summary()

        # Step 3: Memory optimization
        self.progress.emit("memory", 2, 4)
        memory_optimizer = MemoryOptimizer()
        memory_optimizer.optimize_memory()
        results["memory"] = memory_optimizer.get_summary()

        # Step 4: Registry cleaning
        self.progress.emit("registry", 3, 4)
        registry_cleaner = RegistryCleaner()
        safe_entries = registry_cleaner.get_safe_entries()
        if safe_entries:
            backup = registry_cleaner.backup_registry(safe_entries)
            success, failed = registry_cleaner.clean_entries(safe_entries[:10])  # Clean up to 10 entries
            results["registry"] = {
                "cleaned": success,
                "failed": failed,
                "backup_path": backup.backup_path if backup else None,
            }

        # Calculate overall improvement
        self.progress.emit("complete", 4, 4)

        # Generate improvement message
        improvements = []
        if results["startup"].get("disabled", 0) > 0:
            improvements.append(f"{results['startup']['disabled']} startup items")
        if results["services"].get("disabled", 0) > 0:
            improvements.append(f"{results['services']['disabled']} services")
        if results["memory"].get("percent", 100) < 80:
            improvements.append("memory optimized")
        if results["registry"].get("cleaned", 0) > 0:
            improvements.append(f"{results['registry']['cleaned']} registry entries")

        if improvements:
            results["overall_improvement"] = ", ".join(improvements)
        else:
            results["overall_improvement"] = "system already optimized"

        self.finished.emit(results)
