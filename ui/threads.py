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

    def __init__(self, root_path: str = None):
        super().__init__()
        from core.utils import get_system_drive
        self.root_path = root_path or get_system_drive()

    def run(self):
        from core.scanner.file_scanner import FileScanner
        scanner = FileScanner(self.root_path)
        result = scanner.scan(progress_callback=lambda c, s: self.progress.emit(c, s))
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
