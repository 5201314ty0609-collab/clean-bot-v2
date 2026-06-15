"""
CleanBot v2.0 — 工具函数
"""

import os
import shutil
import sys
from pathlib import Path
from typing import List, Optional


def format_size(size_bytes: int) -> str:
    """
    格式化文件大小

    Args:
        size_bytes: 字节数

    Returns:
        格式化后的字符串，例如 "1.23 GB"
    """
    size = float(size_bytes)
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{size:.2f} PB"


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


def run_as_admin() -> bool:
    """以管理员权限重新启动当前程序。

    PyInstaller EXE 兼容：使用 ShellExecuteW 提权重启自身。
    返回 True 表示提权请求已发出（当前进程随即退出）。
    """
    if sys.platform != "win32":
        return False

    import ctypes
    # 构建完整命令行（EXE 路径 + 所有参数）
    exe_path = sys.executable
    args = " ".join(f'"{a}"' if " " in a else a for a in sys.argv[1:])
    result = ctypes.windll.shell32.ShellExecuteW(
        None, "runas", exe_path, args, None, 1  # SW_SHOWNORMAL
    )
    if result > 32:
        sys.exit(0)
    return False


def get_available_drives() -> List[str]:
    """获取可用的磁盘盘符"""
    import string

    if sys.platform != "win32":
        return ["/"]

    drives = []
    for letter in string.ascii_uppercase:
        drive = f"{letter}:\\"
        if os.path.exists(drive):
            drives.append(drive)
    return drives


def get_drive_free_space(drive: str) -> int:
    """获取磁盘剩余空间（字节）"""
    try:
        total, used, free = shutil.disk_usage(drive)
        return free
    except OSError:
        return 0


def get_drive_total_space(drive: str) -> int:
    """获取磁盘总空间（字节）"""
    try:
        total, used, free = shutil.disk_usage(drive)
        return total
    except OSError:
        return 0


def check_symlink_support() -> bool:
    """检查系统是否支持符号链接"""
    if sys.platform != "win32":
        return True

    # Windows 需要管理员权限或开发者模式
    try:
        test_link = os.path.join(get_temp_dir(), "cleanbot_test_link")
        test_target = os.path.join(get_temp_dir(), "cleanbot_test_target")

        # 创建测试文件
        with open(test_target, "w") as f:
            f.write("test")

        # 尝试创建符号链接
        os.symlink(test_target, test_link)

        # 清理
        os.remove(test_link)
        os.remove(test_target)

        return True
    except OSError:
        return False


def ensure_admin_or_exit() -> None:
    """确保有管理员权限，否则尝试提权后退出。"""
    if not is_admin():
        print("⚠️  此操作需要管理员权限")
        print("   正在请求管理员权限...")
        run_as_admin()
        # 如果 run_as_admin 返回（用户拒绝 UAC 或 ShellExecuteW 失败），
        # 必须退出以防止调用方在无管理员权限下继续执行。
        sys.exit(1)
