"""
CleanBot v2.0 — 深度清理器

彻底删除文件或应用，不留残渣。
包括：文件本身、注册表项、快捷方式、启动项、计划任务等。
"""

import os
import sys
import shutil
import json
import time
import winreg
import subprocess
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable
from datetime import datetime

from core.utils import format_size


@dataclass
class CleanupTarget:
    """清理目标"""
    name: str
    path: str
    target_type: str  # file, folder, app
    size: int = 0
    description: str = ""
    risk_level: str = "medium"  # low, medium, high
    registry_entries: List[str] = field(default_factory=list)
    shortcuts: List[str] = field(default_factory=list)
    startup_entries: List[str] = field(default_factory=list)
    scheduled_tasks: List[str] = field(default_factory=list)
    temp_files: List[str] = field(default_factory=list)


@dataclass
class CleanupResult:
    """清理结果"""
    success: bool = False
    target_name: str = ""
    deleted_files: int = 0
    deleted_registry: int = 0
    deleted_shortcuts: int = 0
    freed_size: int = 0
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class DeepCleaner:
    """深度清理器"""

    def __init__(self):
        self.cleanup_log: List[Dict] = []

    def analyze_target(self, path: str) -> CleanupTarget:
        """
        分析清理目标

        Args:
            path: 目标路径

        Returns:
            CleanupTarget: 清理目标信息
        """
        target = CleanupTarget(
            name=os.path.basename(path),
            path=path,
            target_type="folder" if os.path.isdir(path) else "file",
        )

        # 计算大小
        if os.path.isdir(path):
            target.size = self._calculate_dir_size(path)
        else:
            target.size = os.path.getsize(path)

        # 查找相关注册表项
        target.registry_entries = self._find_registry_entries(path)

        # 查找相关快捷方式
        target.shortcuts = self._find_shortcuts(path)

        # 查找启动项
        target.startup_entries = self._find_startup_entries(path)

        # 查找计划任务
        target.scheduled_tasks = self._find_scheduled_tasks(path)

        # 查找临时文件
        target.temp_files = self._find_temp_files(path)

        # 设置风险等级
        target.risk_level = self._assess_risk(target)

        # 设置描述
        target.description = self._generate_description(target)

        return target

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

    def _find_registry_entries(self, path: str) -> List[str]:
        """查找相关注册表项"""
        entries = []
        path_lower = path.lower()

        # 搜索常见注册表位置
        search_keys = [
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"),
            (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders"),
        ]

        for root_key, sub_key_path in search_keys:
            try:
                key = winreg.OpenKey(root_key, sub_key_path)
                i = 0
                while True:
                    try:
                        value_name = winreg.EnumValue(key, i)[0]
                        value_data = winreg.EnumValue(key, i)[1]

                        if isinstance(value_data, str) and path_lower in value_data.lower():
                            entries.append(f"{sub_key_path}\\{value_name}")

                        i += 1
                    except OSError:
                        break
                winreg.CloseKey(key)
            except (WindowsError, OSError):
                pass

        return entries

    def _find_shortcuts(self, path: str) -> List[str]:
        """查找相关快捷方式"""
        shortcuts = []
        path_lower = path.lower()

        # 搜索桌面和开始菜单
        search_dirs = [
            os.path.expanduser("~\\Desktop"),
            os.path.expanduser("~\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu"),
            os.path.expanduser("~\\AppData\\Roaming\\Microsoft\\Internet Explorer\\Quick Launch"),
        ]

        for search_dir in search_dirs:
            if os.path.exists(search_dir):
                try:
                    for root, dirs, files in os.walk(search_dir):
                        for file in files:
                            if file.endswith(".lnk"):
                                shortcut_path = os.path.join(root, file)
                                # 简化检查：检查文件名是否包含目标名称
                                if os.path.basename(path).lower() in file.lower():
                                    shortcuts.append(shortcut_path)
                except (OSError, PermissionError):
                    pass

        return shortcuts

    def _find_startup_entries(self, path: str) -> List[str]:
        """查找启动项"""
        entries = []
        path_lower = path.lower()

        startup_keys = [
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce"),
            (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"),
            (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce"),
        ]

        for root_key, sub_key_path in startup_keys:
            try:
                key = winreg.OpenKey(root_key, sub_key_path)
                i = 0
                while True:
                    try:
                        value_name, value_data, _ = winreg.EnumValue(key, i)
                        if isinstance(value_data, str) and path_lower in value_data.lower():
                            entries.append(f"{sub_key_path}\\{value_name}")
                        i += 1
                    except OSError:
                        break
                winreg.CloseKey(key)
            except (WindowsError, OSError):
                pass

        return entries

    def _find_scheduled_tasks(self, path: str) -> List[str]:
        """查找计划任务"""
        tasks = []
        path_lower = path.lower()

        try:
            # 使用 schtasks 命令查询计划任务
            result = subprocess.run(
                ["schtasks", "/query", "/fo", "csv", "/v"],
                capture_output=True,
                text=True,
                timeout=30,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
            )

            if result.returncode == 0:
                for line in result.stdout.split("\n"):
                    if path_lower in line.lower():
                        tasks.append(line.strip())
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

        return tasks

    def _find_temp_files(self, path: str) -> List[str]:
        """查找相关临时文件"""
        temp_files = []
        path_lower = path.lower()
        base_name = os.path.basename(path).lower()

        # 搜索临时目录
        temp_dirs = [
            os.environ.get("TEMP", ""),
            os.environ.get("TMP", ""),
            os.path.expanduser("~\\AppData\\Local\\Temp"),
        ]

        for temp_dir in temp_dirs:
            if os.path.exists(temp_dir):
                try:
                    for root, dirs, files in os.walk(temp_dir):
                        for file in files:
                            if base_name in file.lower():
                                temp_files.append(os.path.join(root, file))
                except (OSError, PermissionError):
                    pass

        return temp_files

    def _assess_risk(self, target: CleanupTarget) -> str:
        """评估风险等级"""
        # 高风险：系统文件、程序文件
        system_paths = [
            "c:\\windows",
            "c:\\program files",
            "c:\\program files (x86)",
        ]

        for sys_path in system_paths:
            if target.path.lower().startswith(sys_path):
                return "high"

        # 中风险：有注册表项、启动项
        if target.registry_entries or target.startup_entries:
            return "medium"

        # 低风险：普通文件
        return "low"

    def _generate_description(self, target: CleanupTarget) -> str:
        """生成描述"""
        desc_parts = []

        desc_parts.append(f"类型: {'文件夹' if target.target_type == 'folder' else '文件'}")
        desc_parts.append(f"大小: {format_size(target.size)}")

        if target.registry_entries:
            desc_parts.append(f"注册表项: {len(target.registry_entries)} 个")
        if target.shortcuts:
            desc_parts.append(f"快捷方式: {len(target.shortcuts)} 个")
        if target.startup_entries:
            desc_parts.append(f"启动项: {len(target.startup_entries)} 个")
        if target.scheduled_tasks:
            desc_parts.append(f"计划任务: {len(target.scheduled_tasks)} 个")
        if target.temp_files:
            desc_parts.append(f"临时文件: {len(target.temp_files)} 个")

        return " | ".join(desc_parts)

    def deep_clean(
        self,
        target: CleanupTarget,
        confirm_callback: Optional[Callable] = None,
        progress_callback: Optional[Callable] = None,
    ) -> CleanupResult:
        """
        深度清理

        Args:
            target: 清理目标
            confirm_callback: 确认回调
            progress_callback: 进度回调

        Returns:
            CleanupResult: 清理结果
        """
        result = CleanupResult()
        result.target_name = target.name

        # 确认回调
        if confirm_callback:
            if not confirm_callback(target):
                result.errors.append("用户取消操作")
                return result

        try:
            # 1. 删除主文件/文件夹
            if progress_callback:
                progress_callback("正在删除主文件...", 10)

            if os.path.isdir(target.path):
                shutil.rmtree(target.path)
            else:
                os.remove(target.path)
            result.deleted_files += 1
            result.freed_size += target.size

            # 2. 删除注册表项
            if target.registry_entries:
                if progress_callback:
                    progress_callback("正在清理注册表...", 30)

                for entry in target.registry_entries:
                    try:
                        # 解析注册表路径
                        parts = entry.split("\\")
                        root_key_str = parts[0]
                        sub_key_path = "\\".join(parts[1:-1])
                        value_name = parts[-1]

                        root_key = winreg.HKEY_LOCAL_MACHINE if root_key_str == "HKEY_LOCAL_MACHINE" else winreg.HKEY_CURRENT_USER
                        key = winreg.OpenKey(root_key, sub_key_path, 0, winreg.KEY_ALL_ACCESS)
                        winreg.DeleteValue(key, value_name)
                        winreg.CloseKey(key)
                        result.deleted_registry += 1
                    except (WindowsError, OSError) as e:
                        result.warnings.append(f"注册表删除失败: {entry} - {str(e)}")

            # 3. 删除快捷方式
            if target.shortcuts:
                if progress_callback:
                    progress_callback("正在删除快捷方式...", 50)

                for shortcut in target.shortcuts:
                    try:
                        os.remove(shortcut)
                        result.deleted_shortcuts += 1
                    except (OSError, PermissionError) as e:
                        result.warnings.append(f"快捷方式删除失败: {shortcut} - {str(e)}")

            # 4. 删除启动项
            if target.startup_entries:
                if progress_callback:
                    progress_callback("正在清理启动项...", 60)

                for entry in target.startup_entries:
                    try:
                        parts = entry.split("\\")
                        root_key_str = parts[0]
                        sub_key_path = "\\".join(parts[1:-1])
                        value_name = parts[-1]

                        root_key = winreg.HKEY_LOCAL_MACHINE if root_key_str == "HKEY_LOCAL_MACHINE" else winreg.HKEY_CURRENT_USER
                        key = winreg.OpenKey(root_key, sub_key_path, 0, winreg.KEY_ALL_ACCESS)
                        winreg.DeleteValue(key, value_name)
                        winreg.CloseKey(key)
                    except (WindowsError, OSError) as e:
                        result.warnings.append(f"启动项删除失败: {entry} - {str(e)}")

            # 5. 删除临时文件
            if target.temp_files:
                if progress_callback:
                    progress_callback("正在清理临时文件...", 80)

                for temp_file in target.temp_files:
                    try:
                        os.remove(temp_file)
                        result.deleted_files += 1
                    except (OSError, PermissionError):
                        pass

            # 6. 清理计划任务（可选，需要管理员权限）
            if target.scheduled_tasks:
                if progress_callback:
                    progress_callback("正在清理计划任务...", 90)

                for task in target.scheduled_tasks:
                    try:
                        # 从任务行中提取任务名
                        task_name = task.split(",")[0].strip('"')
                        subprocess.run(
                            ["schtasks", "/delete", "/tn", task_name, "/f"],
                            capture_output=True,
                            timeout=30,
                            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
                        )
                    except (subprocess.TimeoutExpired, FileNotFoundError):
                        result.warnings.append(f"计划任务删除失败: {task}")

            result.success = True

            if progress_callback:
                progress_callback("清理完成！", 100)

        except PermissionError as e:
            result.errors.append(f"权限不足: {str(e)}")
        except OSError as e:
            result.errors.append(f"系统错误: {str(e)}")
        except Exception as e:
            result.errors.append(f"未知错误: {str(e)}")

        # 记录日志
        self._log_cleanup(target, result)

        return result

    def _log_cleanup(self, target: CleanupTarget, result: CleanupResult):
        """记录清理日志"""
        log_entry = {
            "timestamp": time.time(),
            "target": target.name,
            "path": target.path,
            "type": target.target_type,
            "size": target.size,
            "success": result.success,
            "deleted_files": result.deleted_files,
            "deleted_registry": result.deleted_registry,
            "deleted_shortcuts": result.deleted_shortcuts,
            "freed_size": result.freed_size,
            "errors": result.errors,
            "warnings": result.warnings,
        }

        self.cleanup_log.append(log_entry)

        # 保存到文件
        log_dir = os.path.expanduser("~\\CleanBot\\logs")
        os.makedirs(log_dir, exist_ok=True)

        log_path = os.path.join(log_dir, f"deep_clean_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")

        with open(log_path, "w", encoding="utf-8") as f:
            json.dump(self.cleanup_log, f, indent=2, ensure_ascii=False)
