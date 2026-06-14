#!/usr/bin/env python3
"""
CleanBot v2.0 -- Smart Desktop Cleanup Robot

Deploys on Windows with full functionality; other platforms run in degraded mode.

Usage:
  main.py                   Launch GUI
  main.py --cli             Launch CLI
  main.py --diagnosis       Run system diagnosis
  main.py --monitor         Start disk monitoring
  main.py --recommend       Get smart recommendations
  main.py --help            Show help
"""

import sys
import os
import importlib
import argparse
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))


# ---------------------------------------------------------------------------
# Dependency bootstrap
# ---------------------------------------------------------------------------

REQUIRED_PACKAGES = {
    "psutil": "psutil",
    "PyQt6": "PyQt6",
    "send2trash": "send2trash",
    "PIL": "Pillow",
    "rich": "rich",
}

OPTIONAL_PACKAGES = {
    "matplotlib": "matplotlib",
    "pyqtgraph": "pyqtgraph",
}


def _check_dependencies() -> dict[str, bool]:
    """Check which dependencies are installed.

    Returns a dict mapping package name to availability.
    """
    status: dict[str, bool] = {}
    for import_name, pip_name in {**REQUIRED_PACKAGES, **OPTIONAL_PACKAGES}.items():
        try:
            importlib.import_module(import_name)
            status[pip_name] = True
        except ImportError:
            status[pip_name] = False
    return status


def _prompt_install_missing(missing: list[str]) -> bool:
    """Ask the user whether to auto-install missing packages."""
    print(f"\nMissing packages: {', '.join(missing)}")
    print("Install them now? [Y/n] ", end="", flush=True)
    answer = input().strip().lower()
    if answer in ("", "y", "yes"):
        return True
    return False


def _install_packages(packages: list[str]) -> bool:
    """Install packages via pip, using a domestic mirror if available."""
    import subprocess

    mirror = os.environ.get("PIP_INDEX_URL", "https://pypi.tuna.tsinghua.edu.cn/simple")
    cmd = [
        sys.executable, "-m", "pip", "install",
        "-i", mirror,
        *packages,
    ]
    print(f"Installing: {' '.join(packages)} ...")
    result = subprocess.run(cmd, capture_output=False)
    return result.returncode == 0


def ensure_dependencies():
    """Verify dependencies and offer to install missing ones."""
    status = _check_dependencies()
    missing_required = [
        pip_name for pip_name, ok in status.items()
        if not ok and pip_name in REQUIRED_PACKAGES.values()
    ]

    if not missing_required:
        return

    if _prompt_install_missing(missing_required):
        if _install_packages(missing_required):
            print("Dependencies installed successfully.\n")
        else:
            print("Failed to install some dependencies. Please install manually:")
            print(f"  pip install {' '.join(missing_required)}")
            sys.exit(1)
    else:
        print("Cannot continue without required dependencies.")
        sys.exit(1)


# ---------------------------------------------------------------------------
# Platform awareness (warning, not blocking)
# ---------------------------------------------------------------------------

IS_WINDOWS = sys.platform == "win32"


def _warn_platform():
    """Warn (but do not block) when running on a non-Windows platform."""
    if not IS_WINDOWS:
        print(
            "[Warning] CleanBot v2.0 is designed for Windows. "
            "Some features (system diagnosis, registry, services) "
            "will be limited on this platform."
        )


# ---------------------------------------------------------------------------
# Core utils import (safe for all platforms)
# ---------------------------------------------------------------------------

from core.utils import format_size


# ---------------------------------------------------------------------------
# CLI entry points
# ---------------------------------------------------------------------------

def run_diagnosis():
    """Run system diagnosis."""
    from core.diagnosis.system_diagnosis import SystemDiagnosis

    print("=" * 60)
    print("CleanBot v2.0 -- System Diagnosis")
    print("=" * 60)

    diagnosis = SystemDiagnosis()
    print("\nRunning system diagnosis...")
    report = diagnosis.run_full_diagnosis()

    print("\nDone!")
    print("-" * 60)
    print(f"\nHealth Score: {report.health_score}/100")
    print(f"\nSummary: {report.summary}")

    if report.problems:
        print(f"\nProblems found ({len(report.problems)}):")
        for i, problem in enumerate(report.problems, 1):
            print(f"  {i}. [{problem.severity.value.upper()}] {problem.title}")
            print(f"     {problem.description}")
            print(f"     Solution: {problem.solution}")
            print()

    if report.solutions:
        print("\nSolutions:")
        for i, solution in enumerate(report.solutions, 1):
            print(f"  {i}. {solution.title}")
            print(f"     {solution.description}")
            print(f"     Risk: {solution.risk_level}")
            print(f"     Est. time: {solution.estimated_time}s")
            print()

    if report.recommendations:
        print("\nRecommendations:")
        for rec in report.recommendations:
            print(f"  - {rec}")

    print("\n" + "=" * 60)


def run_monitor():
    """Start disk monitoring."""
    from core.monitor.disk_monitor import DiskMonitor

    print("=" * 60)
    print("CleanBot v2.0 -- Disk Monitor")
    print("=" * 60)

    monitor = DiskMonitor()
    print("\nMonitoring disk usage... Press Ctrl+C to stop.\n")

    try:
        monitor.start_monitoring(interval=10)
        import time
        from datetime import datetime

        while True:
            os.system("cls" if os.name == "nt" else "clear")
            print("=" * 60)
            print("CleanBot v2.0 -- Disk Monitor")
            print("=" * 60)
            print(f"\nTime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

            usage = monitor.get_current_usage()
            if usage:
                print("\nDisk usage:")
                for drive, disk_usage in usage.items():
                    print(
                        f"  {drive}: {format_size(disk_usage.used)} / "
                        f"{format_size(disk_usage.total)} ({disk_usage.percent:.1f}%)"
                    )

            print("\nTrends:")
            for drive in usage:
                trend = monitor.get_trend(drive)
                if trend:
                    arrow = {"increasing": "^", "decreasing": "v", "stable": "-"}.get(
                        trend.trend_direction, "?"
                    )
                    print(f"  {drive}: {arrow} {format_size(abs(int(trend.slope)))}/day")
                    if trend.will_full_soon:
                        print(f"    WARNING: disk may be full in {trend.prediction_days} days")

            alerts = monitor.get_active_alerts()
            if alerts:
                print("\nAlerts:")
                for alert in alerts:
                    print(f"  [{alert.severity.upper()}] {alert.message}")

            print("\nPress Ctrl+C to stop.")
            time.sleep(5)

    except KeyboardInterrupt:
        print("\n\nStopping monitor...")
        monitor.stop_monitoring()
        print("Monitor stopped.")


def run_recommend():
    """Get smart recommendations."""
    from core.ai.recommendation import RecommendationEngine

    print("=" * 60)
    print("CleanBot v2.0 -- Smart Recommendations")
    print("=" * 60)

    engine = RecommendationEngine()
    print("\nGenerating recommendations...")
    recommendations = engine.generate_recommendations()

    print(f"\nGenerated {len(recommendations)} recommendations:")
    print("-" * 60)

    for i, rec in enumerate(recommendations, 1):
        priority_icon = "!!" if rec.priority >= 8 else "!" if rec.priority >= 5 else "-"
        print(f"\n{i}. {priority_icon} {rec.title}")
        print(f"   {rec.description}")
        print(f"   Category: {rec.category}")
        print(f"   Priority: {rec.priority}/10")
        print(f"   Risk: {rec.risk_level}")
        if rec.estimated_savings > 0:
            print(f"   Est. savings: {format_size(rec.estimated_savings)}")

    print("\n" + "=" * 60)


def run_scan(args):
    """Scan filesystem."""
    from core.scanner import FileScanner

    print("=" * 60)
    print("CleanBot v2.0 -- File Scanner")
    print("=" * 60)

    scanner = FileScanner(args.target, max_depth=args.depth)

    def progress(count, size):
        print(f"\r  Scanned: {count} files, {format_size(size)}", end="", flush=True)

    print(f"\nScanning {args.target}...")
    result = scanner.scan(progress_callback=progress)

    print("\n\nDone!")
    print("-" * 60)

    summary = scanner.get_summary()
    print(f"Total files: {summary['total_files']:,}")
    print(f"Total size: {summary['total_size_mb']:.2f} MB")
    print(f"Scan duration: {summary['scan_duration']:.2f}s")

    print("\nSafe to delete:")
    print(f"  Files: {summary['safe_files']:,}")
    print(f"  Size: {summary['safe_size_mb']:.2f} MB")

    print("\nNeeds confirmation:")
    print(f"  Files: {summary['ask_files']:,}")
    print(f"  Size: {summary['ask_size_mb']:.2f} MB")

    print("\nTop 10 largest files:")
    for i, file_info in enumerate(result.largest_files[:10]):
        print(f"  {i+1}. {format_size(file_info.size):>10} {file_info.path}")

    print("\n" + "=" * 60)


def run_clean(args):
    """Clean files."""
    from core.scanner import FileScanner
    from core.cleaner import FileCleaner

    print("=" * 60)
    print("CleanBot v2.0 -- File Cleaner")
    print("=" * 60)

    scanner = FileScanner(args.target, max_depth=args.depth)
    scanner.scan()
    safe_files = scanner.get_safe_to_delete()

    if not safe_files:
        print("\nNo safe-to-delete files found.")
        return

    print(f"\nReady to clean {len(safe_files)} files...")
    confirm = input("Confirm cleanup? [y/N] ").strip().lower()

    if confirm == "y":
        cleaner = FileCleaner(use_trash=True)
        file_paths = [f.path for f in safe_files]

        def clean_progress(current, total, file_path):
            print(f"\r  Progress: {current}/{total}", end="", flush=True)

        print("\nCleaning...")
        clean_result = cleaner.clean(file_paths, progress_callback=clean_progress)

        print("\n\nDone!")
        print("-" * 60)
        print(f"Deleted: {clean_result.deleted_files} files")
        print(f"Freed: {format_size(clean_result.freed_size)}")
        print(f"Failed: {clean_result.failed_files} files")

        if clean_result.errors:
            print("\nErrors:")
            for error in clean_result.errors[:10]:
                print(f"  - {error}")

        print(f"\nLog: {clean_result.log_path}")
    else:
        print("\nCleanup cancelled.")

    print("\n" + "=" * 60)


def run_cli(args):
    """Run interactive CLI."""
    print("=" * 60)
    print("CleanBot v2.0 -- CLI Mode")
    print("=" * 60)

    print("\nCommands:")
    print("  1. diagnosis  - System diagnosis")
    print("  2. monitor    - Disk monitor")
    print("  3. recommend  - Smart recommendations")
    print("  4. scan       - File scanner")
    print("  5. clean      - File cleaner")
    print("  6. help       - Show help")
    print("  7. exit       - Quit")

    while True:
        print()
        command = input("CleanBot> ").strip().lower()

        if command in ("exit", "quit"):
            print("Goodbye!")
            break
        elif command == "diagnosis":
            run_diagnosis()
        elif command == "monitor":
            run_monitor()
        elif command == "recommend":
            run_recommend()
        elif command == "scan":
            run_scan(args)
        elif command == "clean":
            run_clean(args)
        elif command == "help":
            print("\nCommands:")
            print("  1. diagnosis  - System diagnosis")
            print("  2. monitor    - Disk monitor")
            print("  3. recommend  - Smart recommendations")
            print("  4. scan       - File scanner")
            print("  5. clean      - File cleaner")
            print("  6. help       - Show help")
            print("  7. exit       - Quit")
        else:
            print(f"Unknown command: {command}")
            print("Type 'help' for available commands")


def run_gui():
    """Run GUI mode."""
    try:
        from ui.main_window import main as gui_main
        gui_main()
    except ImportError as e:
        print(f"Error: Cannot load GUI module - {e}")
        print("Please install PyQt6: pip install PyQt6")
        sys.exit(1)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="CleanBot v2.0 -- Smart Desktop Cleanup Robot",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  main.py                   Launch GUI
  main.py --cli             Launch CLI
  main.py --diagnosis       Run system diagnosis
  main.py --monitor         Start disk monitoring
  main.py --recommend       Get smart recommendations
  main.py --help            Show help
        """,
    )

    parser.add_argument("--cli", action="store_true", help="Use CLI interface")
    parser.add_argument("--diagnosis", action="store_true", help="Run system diagnosis")
    parser.add_argument("--monitor", action="store_true", help="Start disk monitoring")
    parser.add_argument("--recommend", action="store_true", help="Get smart recommendations")
    parser.add_argument("--scan", action="store_true", help="Scan filesystem")
    parser.add_argument("--clean", action="store_true", help="Clean files (with confirmation)")
    parser.add_argument("--target", type=str, default=None, help="Scan target path")
    parser.add_argument("--depth", type=int, default=5, help="Scan depth (default 5)")

    args = parser.parse_args()

    # Default target: system drive on Windows, home directory elsewhere
    if args.target is None:
        if IS_WINDOWS:
            args.target = os.environ.get("SystemDrive", "C:") + "\\"
        else:
            args.target = os.path.expanduser("~")

    # Platform warning
    _warn_platform()

    # Check dependencies
    ensure_dependencies()

    # Dispatch
    if args.diagnosis:
        run_diagnosis()
    elif args.monitor:
        run_monitor()
    elif args.recommend:
        run_recommend()
    elif args.scan:
        run_scan(args)
    elif args.clean:
        run_clean(args)
    elif args.cli:
        run_cli(args)
    else:
        run_gui()


if __name__ == "__main__":
    main()
