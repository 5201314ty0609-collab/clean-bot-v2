#!/usr/bin/env python3
"""
CleanBot v2.0 -- 智能桌面清理机器人

一键启动，简单易用的系统清理工具。
"""

import sys
import os
import subprocess
from pathlib import Path
from typing import NoReturn

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))


def _show_error(title: str, message: str) -> None:
    """显示错误信息 — 优先用 QMessageBox，降级到 print。"""
    try:
        from PyQt6.QtWidgets import QApplication, QMessageBox
        app = QApplication(sys.argv)
        QMessageBox.critical(None, title, message)
    except Exception:
        print(f"[{title}] {message}", file=sys.stderr)


def _fatal_error(title: str, message: str, exit_code: int = 1) -> NoReturn:
    """显示错误并退出。"""
    _show_error(title, message)
    sys.exit(exit_code)


def check_platform() -> None:
    """检查运行平台，非 Windows 给出警告。"""
    if sys.platform != "win32":
        print("⚠️  警告: CleanBot 主要为 Windows 设计")
        print("   部分功能在非 Windows 系统上可能不可用\n")


def ensure_dependencies() -> bool:
    """确保依赖已安装。返回 True 表示依赖就绪。"""
    required = {
        'PyQt6': 'PyQt6>=6.5.0',
        'psutil': 'psutil>=5.9.0',
        'Pillow': 'Pillow>=10.0.0',
    }

    missing = [
        pip_name
        for package, pip_name in required.items()
        if _import_failed(package)
    ]

    if not missing:
        return True

    print("正在安装依赖，请稍等...")
    mirrors = [
        ['https://pypi.tuna.tsinghua.edu.cn/simple', 'pypi.tuna.tsinghua.edu.cn'],
        ['https://mirrors.aliyun.com/pypi/simple/', 'mirrors.aliyun.com'],
    ]

    for mirror_url, mirror_host in mirrors:
        try:
            subprocess.check_call(
                [sys.executable, '-m', 'pip', 'install', *missing,
                 '-i', mirror_url, '--trusted-host', mirror_host],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return True
        except subprocess.CalledProcessError:
            continue

    return False


def _import_failed(package: str) -> bool:
    """检查包是否无法导入。"""
    try:
        __import__(package)
        return False
    except ImportError:
        return True


def main() -> None:
    """主入口 — 检查依赖并启动 GUI。"""
    check_platform()

    if not ensure_dependencies():
        _fatal_error(
            "CleanBot v2.0",
            "依赖安装失败，请手动运行：\n"
            "pip install PyQt6 psutil Pillow -i https://pypi.tuna.tsinghua.edu.cn/simple"
        )

    try:
        from ui.main_window import main as gui_main
        gui_main()
    except ImportError as e:
        _fatal_error("CleanBot v2.0", f"启动失败：{e}\n请确保所有文件完整。")
    except Exception as e:
        _fatal_error("CleanBot v2.0", f"发生错误：{e}\n请尝试重新安装。")


if __name__ == "__main__":
    main()
