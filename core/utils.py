"""
CleanBot v2.0 — 工具函数
"""

import os
import sys
from pathlib import Path
from typing import Optional


def format_size(size_bytes: int) -> str:
    """
    格式化文件大小

    Args:
        size_bytes: 字节数

    Returns:
        格式化后的字符串，例如 "1.23 GB"
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"


def get_system_drive() -> str:
    """
    获取系统盘符

    Returns:
        系统盘符，例如 "C:\\"
    """
    return os.environ.get('SystemDrive', 'C:') + '\\'


def get_temp_dir() -> str:
    """
    获取临时目录

    Returns:
        临时目录路径
    """
    return os.environ.get('TEMP', os.path.expanduser('~\\AppData\\Local\\Temp'))


def get_user_profile() -> str:
    """
    获取用户配置目录

    Returns:
        用户配置目录路径
    """
    return os.environ.get('USERPROFILE', os.path.expanduser('~'))


def get_desktop_path() -> str:
    """
    获取桌面路径

    Returns:
        桌面路径
    """
    # 尝试从注册表获取（Windows）
    if sys.platform == "win32":
        try:
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders"
            )
            desktop, _ = winreg.QueryValueEx(key, "Desktop")
            winreg.CloseKey(key)
            return desktop
        except (OSError, FileNotFoundError):
            pass

    # 回退到默认路径
    return os.path.join(get_user_profile(), 'Desktop')


def is_system_drive(drive: str) -> bool:
    """
    检查是否是系统盘

    Args:
        drive: 盘符，例如 "C:\\"

    Returns:
        是否是系统盘
    """
    system_drive = get_system_drive()
    return drive.upper().startswith(system_drive.upper())


def validate_drive_letter(drive: str) -> bool:
    """
    验证盘符格式

    Args:
        drive: 盘符，例如 "C:\\"

    Returns:
        是否是有效的盘符
    """
    if not drive:
        return False

    # 提取盘符字母
    letter = drive[0].upper()

    # 只允许 A-Z
    if not ('A' <= letter <= 'Z'):
        return False

    # 检查格式
    if len(drive) >= 2 and drive[1] == ':':
        return True

    return False


def safe_path(path: str) -> str:
    """
    安全处理路径

    Args:
        path: 原始路径

    Returns:
        安全的路径
    """
    # 处理环境变量
    path = os.path.expandvars(path)

    # 处理用户目录
    path = os.path.expanduser(path)

    # 规范化路径
    path = os.path.normpath(path)

    return path


def get_backup_dir() -> str:
    """
    获取备份目录

    Returns:
        备份目录路径
    """
    # 优先使用 D 盘
    if os.path.exists("D:\\"):
        return "D:\\CleanBot-Backup"

    # 回退到用户目录
    return os.path.join(get_user_profile(), "CleanBot", "Backup")


def create_backup_dir() -> str:
    """
    创建备份目录

    Returns:
        备份目录路径
    """
    from datetime import datetime

    backup_root = get_backup_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = os.path.join(backup_root, timestamp)

    os.makedirs(backup_dir, exist_ok=True)

    return backup_dir


def is_admin() -> bool:
    """
    检查是否有管理员权限

    Returns:
        是否有管理员权限
    """
    if sys.platform != "win32":
        return os.geteuid() == 0

    try:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except (AttributeError, OSError):
        return False


def run_as_admin():
    """
    请求管理员权限重新运行
    """
    if sys.platform != "win32":
        return

    import ctypes
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, " ".join(sys.argv), None, 1
    )
    sys.exit(0)
