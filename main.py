#!/usr/bin/env python3
"""
CleanBot v2.0 — 智能桌面清理机器人

一键启动，简单易用的系统清理工具。
"""

import sys
import os
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
        print("正在安装依赖，请稍等...")
        try:
            # 使用国内镜像
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install',
                *missing,
                '-i', 'https://pypi.tuna.tsinghua.edu.cn/simple',
                '--trusted-host', 'pypi.tuna.tsinghua.edu.cn'
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except subprocess.CalledProcessError:
            # 尝试备用镜像
            try:
                subprocess.check_call([
                    sys.executable, '-m', 'pip', 'install',
                    *missing,
                    '-i', 'https://mirrors.aliyun.com/pypi/simple/',
                    '--trusted-host', 'mirrors.aliyun.com'
                ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return True
            except subprocess.CalledProcessError:
                return False

    return True


def main():
    """主入口 - 直接启动 GUI"""
    # 检查依赖
    if not ensure_dependencies():
        # 显示简单的错误提示
        try:
            from PyQt6.QtWidgets import QApplication, QMessageBox
            app = QApplication(sys.argv)
            QMessageBox.critical(
                None,
                "CleanBot v2.0",
                "依赖安装失败，请手动运行以下命令：\n\n"
                "pip install PyQt6 psutil Pillow -i https://pypi.tuna.tsinghua.edu.cn/simple"
            )
        except:
            print("依赖安装失败，请手动运行以下命令：")
            print("pip install PyQt6 psutil Pillow -i https://pypi.tuna.tsinghua.edu.cn/simple")
        sys.exit(1)

    # 启动 GUI
    try:
        from ui.main_window import main as gui_main
        gui_main()
    except ImportError as e:
        try:
            from PyQt6.QtWidgets import QApplication, QMessageBox
            app = QApplication(sys.argv)
            QMessageBox.critical(
                None,
                "CleanBot v2.0",
                f"启动失败：{e}\n\n请确保所有文件完整。"
            )
        except:
            print(f"启动失败：{e}")
            print("请确保所有文件完整。")
        sys.exit(1)
    except Exception as e:
        try:
            from PyQt6.QtWidgets import QApplication, QMessageBox
            app = QApplication(sys.argv)
            QMessageBox.critical(
                None,
                "CleanBot v2.0",
                f"发生错误：{e}\n\n请尝试重新安装。"
            )
        except:
            print(f"发生错误：{e}")
            print("请尝试重新安装。")
        sys.exit(1)


if __name__ == "__main__":
    main()
