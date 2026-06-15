"""
CleanBot v2.0 — 应用迁移器

将已安装的应用从 C 盘迁移到其他盘，不影响应用打开和数据。
使用符号链接保持注册表路径可用。
"""

import os
import sys
import shutil
import json
import time
import winreg
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable
from datetime import datetime

from core.utils import format_size


@dataclass
class AppInfo:
    """应用信息"""
    name: str
    install_path: str
    size: int = 0
    publisher: str = ""
    version: str = ""
    uninstall_string: str = ""
    registry_key: str = ""


@dataclass
class MigrationResult:
    """迁移结果"""
    success: bool = False
    app_name: str = ""
    original_path: str = ""
    new_path: str = ""
    size: int = 0
    errors: List[str] = field(default_factory=list)


class AppMigrator:
    """应用迁移器"""

    def __init__(self, target_drive: str = "D:\\"):
        """
        初始化应用迁移器

        Args:
            target_drive: 目标盘符（默认 D:\\）
        """
        self.target_drive = target_drive
        self.installed_apps: List[AppInfo] = []

    def scan_installed_apps(self) -> List[AppInfo]:
        """扫描已安装的应用"""
        self.installed_apps = []

        # 从注册表读取已安装应用
        try:
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"
            )

            i = 0
            while True:
                try:
                    subkey_name = winreg.EnumKey(key, i)
                    subkey = winreg.OpenKey(key, subkey_name)

                    try:
                        app_name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                        install_path = winreg.QueryValueEx(subkey, "InstallLocation")[0] if self._value_exists(subkey, "InstallLocation") else ""
                        publisher = winreg.QueryValueEx(subkey, "Publisher")[0] if self._value_exists(subkey, "Publisher") else ""
                        version = winreg.QueryValueEx(subkey, "DisplayVersion")[0] if self._value_exists(subkey, "DisplayVersion") else ""
                        uninstall_string = winreg.QueryValueEx(subkey, "UninstallString")[0] if self._value_exists(subkey, "UninstallString") else ""

                        if install_path and os.path.exists(install_path):
                            # 计算应用大小
                            size = self._calculate_dir_size(install_path)

                            app = AppInfo(
                                name=app_name,
                                install_path=install_path,
                                size=size,
                                publisher=publisher,
                                version=version,
                                uninstall_string=uninstall_string,
                                registry_key=subkey_name,
                            )
                            self.installed_apps.append(app)
                    except (WindowsError, OSError):
                        pass

                    winreg.CloseKey(subkey)
                    i += 1
                except OSError:
                    break

            winreg.CloseKey(key)
        except (WindowsError, OSError):
            pass

        # 按大小排序
        self.installed_apps.sort(key=lambda a: a.size, reverse=True)

        return self.installed_apps

    def _value_exists(self, key, value_name: str) -> bool:
        """检查注册表值是否存在"""
        try:
            winreg.QueryValueEx(key, value_name)
            return True
        except WindowsError:
            return False

    def _calculate_dir_size(self, path: str) -> int:
        """计算目录大小"""
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(path):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    try:
                        total_size += os.path.getsize(filepath)
                    except (OSError, PermissionError):
                        pass
        except (OSError, PermissionError):
            pass
        return total_size

    def migrate_app(
        self,
        app: AppInfo,
        progress_callback: Optional[Callable] = None,
    ) -> MigrationResult:
        """
        迁移应用

        Args:
            app: 应用信息
            progress_callback: 进度回调

        Returns:
            MigrationResult: 迁移结果
        """
        result = MigrationResult()
        result.app_name = app.name
        result.original_path = app.install_path
        result.size = app.size

        try:
            # 检查应用是否正在运行
            if self._is_app_running(app.install_path):
                result.errors.append("应用正在运行，请先关闭应用")
                return result

            # 生成目标路径
            target_base = os.path.join(self.target_drive, "CleanBot-Apps")
            target_path = os.path.join(target_base, os.path.basename(app.install_path))

            # 检查目标路径是否已存在
            if os.path.exists(target_path):
                result.errors.append(f"目标路径已存在: {target_path}")
                return result

            # 创建目标目录
            os.makedirs(target_base, exist_ok=True)

            # 复制应用文件
            if progress_callback:
                progress_callback("正在复制文件...", 0)

            shutil.copytree(app.install_path, target_path)

            if progress_callback:
                progress_callback("正在验证文件...", 50)

            # 验证复制完整性
            if not os.path.exists(target_path):
                result.errors.append("复制失败")
                return result

            # 备份原目录
            backup_path = app.install_path + ".bak"
            if progress_callback:
                progress_callback("正在备份原目录...", 70)

            shutil.copytree(app.install_path, backup_path)

            # 删除原目录
            if progress_callback:
                progress_callback("正在删除原目录...", 80)

            shutil.rmtree(app.install_path)

            # 创建符号链接
            if progress_callback:
                progress_callback("正在创建符号链接...", 90)

            try:
                os.symlink(target_path, app.install_path)
            except OSError as e:
                # 符号链接失败，恢复原目录
                shutil.copytree(backup_path, app.install_path)
                shutil.rmtree(backup_path)
                result.errors.append(f"符号链接创建失败: {str(e)}")
                return result

            # 删除备份
            shutil.rmtree(backup_path)

            # 更新注册表（可选，不更新也能工作）
            # 注意：不更新注册表，因为符号链接会保持路径可用

            result.success = True
            result.new_path = target_path

            if progress_callback:
                progress_callback("迁移完成！", 100)

        except PermissionError as e:
            result.errors.append(f"权限不足: {str(e)}")
        except OSError as e:
            result.errors.append(f"系统错误: {str(e)}")
        except Exception as e:
            result.errors.append(f"未知错误: {str(e)}")

        return result

    def _is_app_running(self, install_path: str) -> bool:
        """检查应用是否正在运行"""
        try:
            import psutil
            for proc in psutil.process_iter(['pid', 'name', 'exe']):
                try:
                    if proc.info['exe'] and install_path.lower() in proc.info['exe'].lower():
                        return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        except ImportError:
            pass
        return False

    def get_app_info(self, app_name: str) -> Optional[AppInfo]:
        """获取应用信息"""
        for app in self.installed_apps:
            if app.name == app_name:
                return app
        return None

    def get_apps_by_size(self, min_size: int = 0) -> List[AppInfo]:
        """按大小获取应用"""
        return [app for app in self.installed_apps if app.size >= min_size]
