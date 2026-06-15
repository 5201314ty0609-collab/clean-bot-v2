#!/usr/bin/env python3
"""
CleanBot v2.0 — 智能桌面清理机器人

双击即可启动。无需命令行，无需配置。
"""

import sys
import os
import subprocess
import traceback
from pathlib import Path
from typing import NoReturn

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))


# ═══════════════════════════════════════════════════════════════════════════
# 全局异常处理 — 电脑小白不会看到可怕的报错窗口
# ═══════════════════════════════════════════════════════════════════════════

def _global_exception_hook(exc_type, exc_value, exc_tb):
    """捕获所有未处理异常，显示友好对话框而非崩溃。"""
    error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    # 写入日志文件
    log_dir = Path(os.path.expanduser("~")) / "CleanBot" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "crash.log"
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"\n{'='*60}\n")
        f.write(f"CleanBot v2.0 Crash Report\n")
        f.write(f"{'='*60}\n")
        f.write(error_msg)

    # 尝试用 GUI 弹窗（如果 PyQt 不可用则 print）
    try:
        from PyQt6.QtWidgets import QApplication, QMessageBox
        app = QApplication.instance() or QApplication(sys.argv)
        QMessageBox.critical(
            None, "CleanBot — 出错了",
            f"很抱歉，程序遇到了意外错误。\n\n"
            f"请尝试以下操作：\n"
            f"  1. 重启 CleanBot\n"
            f"  2. 如果问题持续，请联系开发者\n\n"
            f"错误详情已保存到：\n{log_file}"
        )
    except Exception:
        print(f"\n[CleanBot 错误] 详情已保存到 {log_file}", file=sys.stderr)
        print(error_msg, file=sys.stderr)

    sys.exit(1)


sys.excepthook = _global_exception_hook


# ═══════════════════════════════════════════════════════════════════════════
# 辅助函数
# ═══════════════════════════════════════════════════════════════════════════

def _show_error(title: str, message: str) -> None:
    """显示错误信息 — 优先 QMessageBox，降级到 print。"""
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
    """检查运行平台，非 Windows 给出警告但不阻止运行。"""
    if sys.platform != "win32":
        _show_error(
            "CleanBot",
            "⚠️ 当前系统非 Windows\n\n"
            "CleanBot 为 Windows 设计，在 macOS/Linux 上大部分功能不可用。\n"
            "建议在 Windows 10/11 上运行。"
        )


def ensure_dependencies() -> bool:
    """确保依赖已安装。返回 True 表示依赖就绪。"""
    required = {
        'PyQt6': 'PyQt6>=6.5.0',
        'psutil': 'psutil>=5.9.0',
        'Pillow': 'Pillow>=10.0.0',
    }
    missing = [pip_name for pkg, pip_name in required.items() if _import_failed(pkg)]
    if not missing:
        return True

    print("正在安装依赖...")
    mirrors = [
        ['https://pypi.tuna.tsinghua.edu.cn/simple', 'pypi.tuna.tsinghua.edu.cn'],
        ['https://mirrors.aliyun.com/pypi/simple/', 'mirrors.aliyun.com'],
    ]
    for mirror_url, mirror_host in mirrors:
        try:
            subprocess.check_call(
                [sys.executable, '-m', 'pip', 'install', *missing,
                 '-i', mirror_url, '--trusted-host', mirror_host],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
            return True
        except subprocess.CalledProcessError:
            continue
    return False


def _import_failed(package: str) -> bool:
    try:
        __import__(package)
        return False
    except ImportError:
        return True


# ═══════════════════════════════════════════════════════════════════════════
# 主入口
# ═══════════════════════════════════════════════════════════════════════════

def _request_admin() -> None:
    """如果不是管理员，弹窗询问是否提权重启。"""
    from core.utils import is_admin, run_as_admin

    if is_admin():
        return  # 已经是管理员，直接继续

    # 用 Windows API 弹原生对话框（PyQt 还没加载）
    if sys.platform == "win32":
        import ctypes
        answer = ctypes.windll.user32.MessageBoxW(
            0,
            "CleanBot 建议以管理员身份运行，以便使用全部功能。\n\n"
            "• 文件迁移和应用迁移\n"
            "• 系统诊断和修复\n"
            "• 注册表清理\n\n"
            "是否以管理员身份重新启动？\n"
            "（选择"否"将以普通模式继续，部分功能受限）",
            "CleanBot v2.0",
            0x04 | 0x40,  # MB_YESNO | MB_ICONQUESTION
        )
        if answer == 6:  # IDYES
            run_as_admin()
            # run_as_admin 成功会退出，失败则继续


def main() -> None:
    """CleanBot 主入口 — 启动 GUI。"""
    check_platform()

    # 仅在源码运行时检查依赖（EXE 已内置所有依赖）
    if not getattr(sys, 'frozen', False):
        if not ensure_dependencies():
            _fatal_error(
                "CleanBot",
                "依赖安装失败。\n\n"
                "请手动运行：\n"
                "pip install PyQt6 psutil Pillow -i https://pypi.tuna.tsinghua.edu.cn/simple"
            )

    # 启动前提权询问（迁移/诊断等功能需要管理员）
    _request_admin()

    try:
        from ui.main_window import main as gui_main
        gui_main()
    except ImportError as e:
        _fatal_error("CleanBot", f"启动失败：缺少必要文件\n{e}")
    except Exception as e:
        _fatal_error("CleanBot", f"启动失败：{e}")


if __name__ == "__main__":
    main()
