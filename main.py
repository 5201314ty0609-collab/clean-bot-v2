#!/usr/bin/env python3
"""
CleanBot v2.0 — 智能桌面清理机器人

部署在 Windows 上的智能系统优化助手，能诊断问题、智能推荐、实时监控。

Usage:
  main.py                   启动 GUI 界面
  main.py --cli             启动 CLI 界面
  main.py --diagnosis       运行系统诊断
  main.py --monitor         启动磁盘监控
  main.py --recommend       获取智能推荐
  main.py --help            显示帮助
"""

import sys
import os
import argparse
from pathlib import Path

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.utils import format_size


def main():
    """主入口"""
    parser = argparse.ArgumentParser(
        description="CleanBot v2.0 — 智能桌面清理机器人",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  main.py                   启动 GUI 界面
  main.py --cli             启动 CLI 界面
  main.py --diagnosis       运行系统诊断
  main.py --monitor         启动磁盘监控
  main.py --recommend       获取智能推荐
  main.py --help            显示帮助
        """
    )

    parser.add_argument(
        "--cli",
        action="store_true",
        help="使用 CLI 界面"
    )

    parser.add_argument(
        "--diagnosis",
        action="store_true",
        help="运行系统诊断"
    )

    parser.add_argument(
        "--monitor",
        action="store_true",
        help="启动磁盘监控"
    )

    parser.add_argument(
        "--recommend",
        action="store_true",
        help="获取智能推荐"
    )

    parser.add_argument(
        "--scan",
        action="store_true",
        help="扫描文件系统"
    )

    parser.add_argument(
        "--clean",
        action="store_true",
        help="清理文件（需确认）"
    )

    parser.add_argument(
        "--target",
        type=str,
        default="C:\\",
        help="扫描目标路径（默认 C:\\）"
    )

    parser.add_argument(
        "--depth",
        type=int,
        default=5,
        help="扫描深度（默认 5）"
    )

    args = parser.parse_args()

    # 检查是否在 Windows 上运行
    if sys.platform != "win32":
        print("错误: CleanBot v2.0 只支持 Windows 系统")
        sys.exit(1)

    # 诊断模式
    if args.diagnosis:
        run_diagnosis()
    # 监控模式
    elif args.monitor:
        run_monitor()
    # 推荐模式
    elif args.recommend:
        run_recommend()
    # 扫描模式
    elif args.scan:
        run_scan(args)
    # 清理模式
    elif args.clean:
        run_clean(args)
    # CLI 模式
    elif args.cli:
        run_cli(args)
    # GUI 模式
    else:
        run_gui()


def run_diagnosis():
    """运行系统诊断"""
    from core.diagnosis.system_diagnosis import SystemDiagnosis

    print("=" * 60)
    print("CleanBot v2.0 — 系统诊断")
    print("=" * 60)

    diagnosis = SystemDiagnosis()

    print("\n正在运行系统诊断...")
    report = diagnosis.run_full_diagnosis()

    print("\n诊断完成!")
    print("-" * 60)

    print(f"\n系统健康分数: {report.health_score}/100")
    print(f"\n摘要: {report.summary}")

    if report.problems:
        print(f"\n发现的问题 ({len(report.problems)}):")
        for i, problem in enumerate(report.problems, 1):
            print(f"  {i}. [{problem.severity.value.upper()}] {problem.title}")
            print(f"     {problem.description}")
            print(f"     解决方案: {problem.solution}")
            print()

    if report.solutions:
        print("\n解决方案:")
        for i, solution in enumerate(report.solutions, 1):
            print(f"  {i}. {solution.title}")
            print(f"     {solution.description}")
            print(f"     风险: {solution.risk_level}")
            print(f"     预计时间: {solution.estimated_time} 秒")
            print()

    if report.recommendations:
        print("\n推荐:")
        for rec in report.recommendations:
            print(f"  - {rec}")

    print("\n" + "=" * 60)


def run_monitor():
    """启动磁盘监控"""
    from core.monitor.disk_monitor import DiskMonitor

    print("=" * 60)
    print("CleanBot v2.0 — 磁盘监控器")
    print("=" * 60)

    monitor = DiskMonitor()

    print("\n开始监控磁盘使用情况...")
    print("按 Ctrl+C 停止监控\n")

    try:
        monitor.start_monitoring(interval=10)

        import time
        from datetime import datetime

        while True:
            # 清屏
            os.system('cls' if os.name == 'nt' else 'clear')

            print("=" * 60)
            print("CleanBot v2.0 — 磁盘监控器")
            print("=" * 60)
            print(f"\n监控时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

            # 显示当前使用情况
            usage = monitor.get_current_usage()
            if usage:
                print("\n磁盘使用情况:")
                for drive, disk_usage in usage.items():
                    print(f"  {drive}: {format_size(disk_usage.used)} / {format_size(disk_usage.total)} "
                          f"({disk_usage.percent:.1f}%)")

            # 显示趋势
            print("\n使用趋势:")
            for drive in usage.keys():
                trend = monitor.get_trend(drive)
                if trend:
                    direction = {"increasing": "↑", "decreasing": "↓", "stable": "→"}.get(trend.trend_direction, "?")
                    print(f"  {drive}: {direction} {format_size(abs(int(trend.slope)))}/天")
                    if trend.will_full_soon:
                        print(f"    ⚠️ 预计 {trend.prediction_days} 天后磁盘满")

            # 显示告警
            alerts = monitor.get_active_alerts()
            if alerts:
                print("\n⚠️ 告警:")
                for alert in alerts:
                    severity_icon = {
                        "critical": "🔴",
                        "high": "🟠",
                        "medium": "🟡",
                        "low": "🟢",
                    }.get(alert.severity, "⚪")
                    print(f"  {severity_icon} {alert.message}")

            print("\n按 Ctrl+C 停止监控")
            time.sleep(5)

    except KeyboardInterrupt:
        print("\n\n停止监控...")
        monitor.stop_monitoring()
        print("监控已停止。")


def run_recommend():
    """获取智能推荐"""
    from core.ai.recommendation import RecommendationEngine

    print("=" * 60)
    print("CleanBot v2.0 — 智能推荐引擎")
    print("=" * 60)

    engine = RecommendationEngine()

    print("\n正在生成推荐...")
    recommendations = engine.generate_recommendations()

    print(f"\n生成了 {len(recommendations)} 个推荐:")
    print("-" * 60)

    for i, rec in enumerate(recommendations, 1):
        priority_icon = "🔴" if rec.priority >= 8 else "🟡" if rec.priority >= 5 else "🟢"
        print(f"\n{i}. {priority_icon} {rec.title}")
        print(f"   {rec.description}")
        print(f"   类别: {rec.category}")
        print(f"   优先级: {rec.priority}/10")
        print(f"   风险: {rec.risk_level}")
        if rec.estimated_savings > 0:
            print(f"   预计节省: {format_size(rec.estimated_savings)}")

    print("\n" + "=" * 60)


def run_scan(args):
    """扫描文件系统"""
    from core.scanner import FileScanner

    print("=" * 60)
    print("CleanBot v2.0 — 文件扫描器")
    print("=" * 60)

    scanner = FileScanner(args.target, max_depth=args.depth)

    def progress(count, size):
        print(f"\r  已扫描: {count} 个文件, {format_size(size)}", end="", flush=True)

    print(f"\n正在扫描 {args.target}...")
    result = scanner.scan(progress_callback=progress)

    print("\n\n扫描完成!")
    print("-" * 60)

    summary = scanner.get_summary()
    print(f"总文件数: {summary['total_files']:,}")
    print(f"总大小: {summary['total_size_mb']:.2f} MB")
    print(f"扫描时间: {summary['scan_duration']:.2f} 秒")

    print("\n可安全删除:")
    print(f"  文件数: {summary['safe_files']:,}")
    print(f"  大小: {summary['safe_size_mb']:.2f} MB")

    print("\n需要确认:")
    print(f"  文件数: {summary['ask_files']:,}")
    print(f"  大小: {summary['ask_size_mb']:.2f} MB")

    # 显示最大的文件
    print("\n最大的 10 个文件:")
    for i, file_info in enumerate(result.largest_files[:10]):
        print(f"  {i+1}. {format_size(file_info.size):>10} {file_info.path}")

    print("\n" + "=" * 60)


def run_clean(args):
    """清理文件"""
    from core.scanner import FileScanner
    from core.cleaner import FileCleaner

    print("=" * 60)
    print("CleanBot v2.0 — 文件清理器")
    print("=" * 60)

    # 先扫描
    scanner = FileScanner(args.target, max_depth=args.depth)
    result = scanner.scan()

    safe_files = scanner.get_safe_to_delete()

    if not safe_files:
        print("\n没有可安全删除的文件。")
        return

    print(f"\n准备清理 {len(safe_files)} 个文件...")
    confirm = input("确认清理？(y/N): ").strip().lower()

    if confirm == "y":
        cleaner = FileCleaner(use_trash=True)
        file_paths = [f.path for f in safe_files]

        def clean_progress(current, total, file_path):
            print(f"\r  清理进度: {current}/{total}", end="", flush=True)

        print("\n开始清理...")
        clean_result = cleaner.clean(file_paths, progress_callback=clean_progress)

        print("\n\n清理完成!")
        print("-" * 60)
        print(f"已删除: {clean_result.deleted_files} 个文件")
        print(f"释放空间: {format_size(clean_result.freed_size)}")
        print(f"失败: {clean_result.failed_files} 个文件")

        if clean_result.errors:
            print("\n错误:")
            for error in clean_result.errors[:10]:
                print(f"  - {error}")

        print(f"\n日志: {clean_result.log_path}")
    else:
        print("\n已取消清理。")

    print("\n" + "=" * 60)


def run_cli(args):
    """运行 CLI 模式"""
    print("=" * 60)
    print("CleanBot v2.0 — CLI 模式")
    print("=" * 60)

    print("\n可用命令:")
    print("  1. diagnosis  - 运行系统诊断")
    print("  2. monitor    - 启动磁盘监控")
    print("  3. recommend  - 获取智能推荐")
    print("  4. scan       - 扫描文件系统")
    print("  5. clean      - 清理文件")
    print("  6. help       - 显示帮助")
    print("  7. exit       - 退出")

    while True:
        print()
        command = input("CleanBot> ").strip().lower()

        if command == "exit" or command == "quit":
            print("再见！")
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
            print("\n可用命令:")
            print("  1. diagnosis  - 运行系统诊断")
            print("  2. monitor    - 启动磁盘监控")
            print("  3. recommend  - 获取智能推荐")
            print("  4. scan       - 扫描文件系统")
            print("  5. clean      - 清理文件")
            print("  6. help       - 显示帮助")
            print("  7. exit       - 退出")
        else:
            print(f"未知命令: {command}")
            print("输入 'help' 查看可用命令")


def run_gui():
    """运行 GUI 模式"""
    try:
        from ui.main_window import main as gui_main
        gui_main()
    except ImportError as e:
        print(f"错误: 无法加载 GUI 模块 - {e}")
        print("请确保已安装 PyQt6: pip install PyQt6")
        sys.exit(1)


if __name__ == "__main__":
    main()
