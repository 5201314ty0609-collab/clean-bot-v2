#!/usr/bin/env python3
"""
CleanBot v2.0 — 智能桌面清理机器人

部署在 Windows 上的智能系统优化助手，能诊断问题、智能推荐、实时监控。

Usage:
  main.py                   启动模式选择界面
  main.py --gui             直接启动 GUI 界面
  main.py --cli             启动 CLI 界面
  main.py --diagnosis       运行系统诊断
  main.py --monitor         启动磁盘监控
  main.py --recommend       获取智能推荐
  main.py --scan            扫描文件系统
  main.py --clean           清理文件
  main.py --help            显示帮助
"""

import sys
import os
import argparse
import subprocess
from pathlib import Path

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))


def ensure_dependencies():
    """确保依赖已安装"""
    required_packages = {
        'PyQt6': 'PyQt6>=6.5.0',
        'psutil': 'psutil>=5.9.0',
        'Pillow': 'Pillow>=10.0.0',
    }

    missing = []
    for package, pip_name in required_packages.items():
        try:
            __import__(package)
        except ImportError:
            missing.append(pip_name)

    if missing:
        print("缺少以下依赖包:")
        for pkg in missing:
            print(f"  - {pkg}")
        print()

        response = input("是否自动安装？(y/N): ").strip().lower()
        if response == 'y':
            print("正在安装依赖...")
            try:
                # 使用国内镜像
                subprocess.check_call([
                    sys.executable, '-m', 'pip', 'install',
                    *missing,
                    '-i', 'https://pypi.tuna.tsinghua.edu.cn/simple',
                    '--trusted-host', 'pypi.tuna.tsinghua.edu.cn'
                ])
                print("依赖安装完成！")
                return True
            except subprocess.CalledProcessError:
                print("依赖安装失败，请手动安装:")
                print(f"  pip install {' '.join(missing)}")
                return False
        else:
            print("请手动安装依赖后再运行程序")
            return False

    return True


def show_mode_selector():
    """显示模式选择界面"""
    print()
    print("=" * 60)
    print("  CleanBot v2.0 — 智能桌面清理机器人")
    print("=" * 60)
    print()
    print("请选择运行模式:")
    print()
    print("  1. GUI 模式      - 图形界面（推荐）")
    print("  2. CLI 模式      - 命令行界面")
    print("  3. 系统诊断      - 检测系统问题")
    print("  4. 文件扫描      - 扫描可清理文件")
    print("  5. 磁盘监控      - 实时监控磁盘使用")
    print("  6. 智能推荐      - 获取清理建议")
    print("  7. 快速清理      - 一键清理安全文件")
    print("  8. 退出")
    print()

    while True:
        choice = input("请输入选项 (1-8): ").strip()

        if choice == '1':
            run_gui()
            break
        elif choice == '2':
            run_cli()
            break
        elif choice == '3':
            run_diagnosis()
            break
        elif choice == '4':
            run_scan_interactive()
            break
        elif choice == '5':
            run_monitor()
            break
        elif choice == '6':
            run_recommend()
            break
        elif choice == '7':
            run_quick_clean()
            break
        elif choice == '8':
            print("再见！")
            sys.exit(0)
        else:
            print("无效选项，请重新输入")


def run_gui():
    """运行 GUI 模式"""
    try:
        from ui.main_window import main as gui_main
        gui_main()
    except ImportError as e:
        print(f"错误: 无法加载 GUI 模块 - {e}")
        print("请确保已安装 PyQt6: pip install PyQt6")
        sys.exit(1)
    except Exception as e:
        print(f"GUI 启动失败: {e}")
        print("请尝试 CLI 模式: python main.py --cli")
        sys.exit(1)


def run_cli():
    """运行 CLI 模式"""
    from core.utils import format_size

    print()
    print("=" * 60)
    print("  CleanBot v2.0 — CLI 模式")
    print("=" * 60)
    print()
    print("可用命令:")
    print("  diagnosis  - 运行系统诊断")
    print("  scan       - 扫描文件系统")
    print("  clean      - 清理文件")
    print("  monitor    - 启动磁盘监控")
    print("  recommend  - 获取智能推荐")
    print("  quick      - 快速清理")
    print("  help       - 显示帮助")
    print("  exit       - 退出")
    print()

    while True:
        try:
            command = input("CleanBot> ").strip().lower()

            if command in ["exit", "quit", "q"]:
                print("再见！")
                break
            elif command == "diagnosis":
                run_diagnosis()
            elif command == "scan":
                run_scan_interactive()
            elif command == "clean":
                run_clean_interactive()
            elif command == "monitor":
                run_monitor()
            elif command == "recommend":
                run_recommend()
            elif command == "quick":
                run_quick_clean()
            elif command == "help":
                print()
                print("可用命令:")
                print("  diagnosis  - 运行系统诊断")
                print("  scan       - 扫描文件系统")
                print("  clean      - 清理文件")
                print("  monitor    - 启动磁盘监控")
                print("  recommend  - 获取智能推荐")
                print("  quick      - 快速清理")
                print("  help       - 显示帮助")
                print("  exit       - 退出")
                print()
            else:
                print(f"未知命令: {command}")
                print("输入 'help' 查看可用命令")

        except KeyboardInterrupt:
            print("\n再见！")
            break
        except EOFError:
            print("\n再见！")
            break


def run_diagnosis():
    """运行系统诊断"""
    from core.diagnosis.system_diagnosis import SystemDiagnosis

    print()
    print("=" * 60)
    print("  系统诊断")
    print("=" * 60)
    print()

    diagnosis = SystemDiagnosis()

    print("正在运行系统诊断...")
    report = diagnosis.run_full_diagnosis()

    print()
    print("诊断完成!")
    print("-" * 60)

    print(f"\n系统健康分数: {report.health_score}/100")
    print(f"\n摘要: {report.summary}")

    if report.problems:
        print(f"\n发现的问题 ({len(report.problems)}):")
        for i, problem in enumerate(report.problems, 1):
            severity_icon = {
                "critical": "🔴",
                "high": "🟠",
                "medium": "🟡",
                "low": "🟢",
            }.get(problem.severity.value, "⚪")

            print(f"\n  {i}. {severity_icon} {problem.title}")
            print(f"     {problem.description}")
            print(f"     解决方案: {problem.solution}")

    if report.recommendations:
        print("\n\n推荐:")
        for rec in report.recommendations:
            print(f"  - {rec}")

    print("\n" + "=" * 60)


def run_scan_interactive():
    """交互式扫描"""
    from core.scanner.file_scanner import FileScanner
    from core.utils import format_size, get_system_drive

    print()
    print("=" * 60)
    print("  文件扫描")
    print("=" * 60)
    print()

    target = input(f"扫描路径 (默认 {get_system_drive()}): ").strip()
    if not target:
        target = get_system_drive()

    print(f"\n正在扫描 {target}...")
    scanner = FileScanner(target)

    def progress(count, size):
        print(f"\r  已扫描: {count:,} 个文件, {format_size(size)}", end="", flush=True)

    result = scanner.scan(progress_callback=progress)

    print("\n\n扫描完成!")
    print("-" * 60)

    summary = scanner.get_summary()
    print(f"总文件数: {summary['total_files']:,}")
    print(f"总大小: {format_size(int(summary['total_size_mb'] * 1024 * 1024))}")
    print(f"扫描时间: {summary['scan_duration']:.2f} 秒")

    print(f"\n可安全删除:")
    print(f"  文件数: {summary['safe_files']:,}")
    print(f"  大小: {format_size(int(summary['safe_size_mb'] * 1024 * 1024))}")

    print(f"\n需要确认:")
    print(f"  文件数: {summary['ask_files']:,}")
    print(f"  大小: {format_size(int(summary['ask_size_mb'] * 1024 * 1024))}")

    if summary['duplicate_groups'] > 0:
        print(f"\n重复文件:")
        print(f"  组数: {summary['duplicate_groups']}")
        print(f"  大小: {format_size(int(summary['duplicate_size_mb'] * 1024 * 1024))}")

    # 显示最大的文件
    print("\n最大的 10 个文件:")
    for i, file_info in enumerate(result.largest_files[:10]):
        print(f"  {i+1}. {format_size(file_info.size):>10} {file_info.path}")

    # 显示风险分布
    if hasattr(result, 'risk_distribution'):
        print("\n风险分布:")
        for level, count in result.risk_distribution.items():
            if count > 0:
                icon = {"safe": "🟢", "low": "🟢", "medium": "🟡", "high": "🔴"}.get(level, "⚪")
                print(f"  {icon} {level}: {count:,} 个")

    print("\n" + "=" * 60)


def run_clean_interactive():
    """交互式清理"""
    from core.scanner.file_scanner import FileScanner
    from core.cleaner.file_cleaner import FileCleaner
    from core.utils import format_size, get_system_drive

    print()
    print("=" * 60)
    print("  文件清理")
    print("=" * 60)
    print()

    # 先扫描
    print("正在扫描可清理文件...")
    scanner = FileScanner(get_system_drive())
    result = scanner.scan()

    safe_files = scanner.get_safe_to_delete()

    if not safe_files:
        print("\n没有可安全删除的文件。")
        return

    print(f"\n发现 {len(safe_files)} 个可安全删除的文件")
    print(f"总大小: {format_size(sum(f.size for f in safe_files))}")

    print("\n文件类型分布:")
    type_counts = {}
    for f in safe_files:
        type_name = getattr(f, 'type_name', f.file_type)
        type_counts[type_name] = type_counts.get(type_name, 0) + 1

    for type_name, count in sorted(type_counts.items(), key=lambda x: -x[1])[:10]:
        print(f"  - {type_name}: {count:,} 个")

    confirm = input("\n确认清理？(y/N): ").strip().lower()

    if confirm == "y":
        cleaner = FileCleaner(use_trash=True)
        file_paths = [f.path for f in safe_files]

        def clean_progress(prog):
            print(f"\r  清理进度: {prog.current}/{prog.total} ({prog.percent:.1f}%)", end="", flush=True)

        print("\n开始清理...")
        clean_result = cleaner.clean(file_paths, progress_callback=clean_progress)

        print("\n\n清理完成!")
        print("-" * 60)
        print(f"已删除: {clean_result.deleted_files:,} 个文件")
        print(f"释放空间: {format_size(clean_result.freed_size)}")
        print(f"失败: {clean_result.failed_files:,} 个文件")

        if clean_result.errors:
            print("\n错误:")
            for error in clean_result.errors[:5]:
                print(f"  - {error}")

        print(f"\n日志: {clean_result.log_path}")
    else:
        print("\n已取消清理。")

    print("\n" + "=" * 60)


def run_monitor():
    """启动磁盘监控"""
    from core.monitor.disk_monitor import DiskMonitor
    from core.utils import format_size

    print()
    print("=" * 60)
    print("  磁盘监控")
    print("=" * 60)
    print()

    monitor = DiskMonitor()

    print("开始监控磁盘使用情况...")
    print("按 Ctrl+C 停止监控")
    print()

    try:
        monitor.start_monitoring(interval=10)

        import time
        from datetime import datetime

        while True:
            # 清屏
            os.system('cls' if os.name == 'nt' else 'clear')

            print("=" * 60)
            print("  磁盘监控")
            print("=" * 60)
            print(f"\n监控时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

            # 显示当前使用情况
            usage = monitor.get_current_usage()
            if usage:
                print("\n磁盘使用情况:")
                for drive, disk_usage in usage.items():
                    bar_length = 30
                    filled = int(bar_length * disk_usage.percent / 100)
                    bar = "█" * filled + "░" * (bar_length - filled)
                    print(f"  {drive} [{bar}] {disk_usage.percent:.1f}%")
                    print(f"       {format_size(disk_usage.used)} / {format_size(disk_usage.total)}")

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
    from core.utils import format_size

    print()
    print("=" * 60)
    print("  智能推荐")
    print("=" * 60)
    print()

    engine = RecommendationEngine()

    print("正在生成推荐...")
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


def run_quick_clean():
    """快速清理安全文件"""
    from core.scanner.file_scanner import FileScanner
    from core.cleaner.file_cleaner import FileCleaner
    from core.utils import format_size, get_system_drive

    print()
    print("=" * 60)
    print("  快速清理")
    print("=" * 60)
    print()

    print("正在扫描安全文件...")
    scanner = FileScanner(get_system_drive())
    result = scanner.scan()

    safe_files = scanner.get_safe_to_delete()

    if not safe_files:
        print("\n没有可安全删除的文件。")
        return

    total_size = sum(f.size for f in safe_files)
    print(f"\n发现 {len(safe_files):,} 个安全文件，共 {format_size(total_size)}")
    print("\n这些文件包括:")
    print("  - 临时文件 (.tmp, .temp)")
    print("  - 缓存文件 (.cache)")
    print("  - 日志文件 (.log)")
    print("  - 系统垃圾 (thumbs.db, .ds_store)")

    confirm = input("\n确认清理？(y/N): ").strip().lower()

    if confirm == "y":
        cleaner = FileCleaner(use_trash=True)
        file_paths = [f.path for f in safe_files]

        def clean_progress(prog):
            print(f"\r  清理进度: {prog.current}/{prog.total} ({prog.percent:.1f}%)", end="", flush=True)

        print("\n开始清理...")
        clean_result = cleaner.clean(file_paths, progress_callback=clean_progress)

        print("\n\n清理完成!")
        print("-" * 60)
        print(f"已删除: {clean_result.deleted_files:,} 个文件")
        print(f"释放空间: {format_size(clean_result.freed_size)}")
        print(f"\n文件已移到回收站，可以随时恢复。")
    else:
        print("\n已取消清理。")

    print("\n" + "=" * 60)


def main():
    """主入口"""
    parser = argparse.ArgumentParser(
        description="CleanBot v2.0 — 智能桌面清理机器人",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  main.py                   启动模式选择界面
  main.py --gui             直接启动 GUI 界面
  main.py --cli             启动 CLI 界面
  main.py --diagnosis       运行系统诊断
  main.py --monitor         启动磁盘监控
  main.py --recommend       获取智能推荐
  main.py --scan            扫描文件系统
  main.py --clean           清理文件
  main.py --help            显示帮助
        """
    )

    parser.add_argument(
        "--gui",
        action="store_true",
        help="直接启动 GUI 界面"
    )

    parser.add_argument(
        "--cli",
        action="store_true",
        help="启动 CLI 界面"
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
        help="清理文件"
    )

    parser.add_argument(
        "--quick",
        action="store_true",
        help="快速清理安全文件"
    )

    parser.add_argument(
        "--target",
        type=str,
        default=None,
        help="扫描目标路径"
    )

    parser.add_argument(
        "--depth",
        type=int,
        default=5,
        help="扫描深度（默认 5）"
    )

    args = parser.parse_args()

    # 检查依赖
    if not ensure_dependencies():
        sys.exit(1)

    # 根据参数运行相应模式
    if args.gui:
        run_gui()
    elif args.cli:
        run_cli()
    elif args.diagnosis:
        run_diagnosis()
    elif args.monitor:
        run_monitor()
    elif args.recommend:
        run_recommend()
    elif args.scan:
        run_scan_interactive()
    elif args.clean:
        run_clean_interactive()
    elif args.quick:
        run_quick_clean()
    else:
        # 显示模式选择界面
        show_mode_selector()


if __name__ == "__main__":
    main()
