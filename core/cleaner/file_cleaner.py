"""
CleanBot v2.0 — 文件清理器

安全清理文件，支持：
- 移到回收站（推荐）
- 永久删除（需确认）
- 备份后删除
"""

import os
import sys
import time
import shutil
import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable
from datetime import datetime

# Windows 特定
if sys.platform == "win32":
    try:
        from send2trash import send2trash
        HAS_SEND2TRASH = True
    except ImportError:
        HAS_SEND2TRASH = False
else:
    HAS_SEND2TRASH = False


@dataclass
class CleanResult:
    """清理结果"""
    total_files: int = 0
    deleted_files: int = 0
    failed_files: int = 0
    skipped_files: int = 0
    total_size: int = 0
    freed_size: int = 0
    errors: List[str] = field(default_factory=list)
    log_path: str = ""
    duration: float = 0.0


@dataclass
class CleanProgress:
    """清理进度"""
    current: int = 0
    total: int = 0
    current_file: str = ""
    freed_size: int = 0
    percent: float = 0.0


class FileCleaner:
    """文件清理器"""

    def __init__(self, use_trash: bool = True, backup_before_delete: bool = False):
        """
        Args:
            use_trash: 是否使用回收站（推荐）
            backup_before_delete: 删除前是否备份
        """
        self.use_trash = use_trash and HAS_SEND2TRASH
        self.backup_before_delete = backup_before_delete
        self.clean_log: List[Dict] = []
        self.backup_dir: Optional[str] = None

    def clean(
        self,
        files: List[str],
        confirm_callback: Optional[Callable] = None,
        progress_callback: Optional[Callable] = None,
    ) -> CleanResult:
        """
        清理文件列表

        Args:
            files: 要清理的文件路径列表
            confirm_callback: 确认回调（返回 True 继续，False 跳过）
            progress_callback: 进度回调（CleanProgress）
        """
        start_time = time.time()
        result = CleanResult()
        result.total_files = len(files)

        # 计算总大小
        for file_path in files:
            try:
                size = os.path.getsize(file_path)
                result.total_size += size
            except (OSError, PermissionError):
                pass

        # 创建备份目录（如果需要）
        if self.backup_before_delete:
            from core.utils import create_backup_dir
            self.backup_dir = create_backup_dir()

        # 清理文件
        for i, file_path in enumerate(files):
            # 进度回调
            if progress_callback:
                progress = CleanProgress(
                    current=i + 1,
                    total=len(files),
                    current_file=file_path,
                    freed_size=result.freed_size,
                    percent=(i + 1) / len(files) * 100,
                )
                progress_callback(progress)

            try:
                # 确认回调
                if confirm_callback:
                    if not confirm_callback(file_path):
                        result.skipped_files += 1
                        continue

                # 检查文件是否存在
                if not os.path.exists(file_path):
                    result.skipped_files += 1
                    continue

                # 检查是否是系统文件
                if self._is_system_file(file_path):
                    result.skipped_files += 1
                    result.errors.append(f"跳过系统文件: {file_path}")
                    continue

                # 检查是否是桌面文件
                if self._is_desktop_file(file_path):
                    result.skipped_files += 1
                    result.errors.append(f"跳过桌面文件: {file_path}")
                    continue

                # 获取文件大小
                file_size = os.path.getsize(file_path)

                # 备份（如果需要）
                if self.backup_before_delete:
                    try:
                        self._backup_file(file_path)
                    except Exception as e:
                        # 备份失败，中止删除
                        result.failed_files += 1
                        result.errors.append(f"备份失败，跳过删除: {file_path} - {str(e)}")
                        self.clean_log.append({
                            "path": file_path,
                            "action": "backup_failed",
                            "error": str(e),
                            "timestamp": time.time(),
                            "success": False,
                        })
                        continue

                # 删除文件
                if self.use_trash:
                    send2trash(file_path)
                    action = "trash"
                else:
                    os.remove(file_path)
                    action = "delete"

                # 记录日志
                self.clean_log.append({
                    "path": file_path,
                    "size": file_size,
                    "action": action,
                    "timestamp": time.time(),
                    "success": True,
                })

                result.deleted_files += 1
                result.freed_size += file_size

            except PermissionError as e:
                result.failed_files += 1
                result.errors.append(f"权限不足: {file_path} - {str(e)}")
                self.clean_log.append({
                    "path": file_path,
                    "action": "failed",
                    "error": str(e),
                    "timestamp": time.time(),
                    "success": False,
                })

            except OSError as e:
                result.failed_files += 1
                result.errors.append(f"系统错误: {file_path} - {str(e)}")
                self.clean_log.append({
                    "path": file_path,
                    "action": "failed",
                    "error": str(e),
                    "timestamp": time.time(),
                    "success": False,
                })

            except Exception as e:
                result.failed_files += 1
                result.errors.append(f"未知错误: {file_path} - {str(e)}")
                self.clean_log.append({
                    "path": file_path,
                    "action": "failed",
                    "error": str(e),
                    "timestamp": time.time(),
                    "success": False,
                })

        # 计算持续时间
        result.duration = time.time() - start_time

        # 保存日志
        result.log_path = self._save_log()

        return result

    def _is_system_file(self, file_path: str) -> bool:
        """检查是否是系统文件"""
        path_lower = file_path.lower()

        system_paths = [
            "c:\\windows\\system32",
            "c:\\windows\\syswow64",
            "c:\\windows\\boot",
            "c:\\windows\\fonts",
            "c:\\windows\\winxs",
            "c:\\program files",
            "c:\\program files (x86)",
        ]

        for sys_path in system_paths:
            if path_lower.startswith(sys_path):
                return True

        return False

    def _is_desktop_file(self, file_path: str) -> bool:
        """检查是否是桌面文件"""
        from core.utils import get_desktop_path

        path_lower = file_path.lower()

        # 使用注册表获取实际桌面路径
        desktop_path = get_desktop_path().lower()
        if path_lower.startswith(desktop_path):
            return True

        # 回退到通配符匹配（兼容旧逻辑）
        desktop_patterns = [
            "c:\\users\\*\\desktop",
            "c:\\users\\*\\桌面",
        ]

        for pattern in desktop_patterns:
            if "*" in pattern:
                import fnmatch
                if fnmatch.fnmatch(path_lower, pattern):
                    return True

        return False

    def _backup_file(self, file_path: str) -> bool:
        """
        备份文件

        Args:
            file_path: 要备份的文件路径

        Returns:
            备份是否成功

        Raises:
            Exception: 备份失败时抛出异常
        """
        if not self.backup_dir:
            return False

        from core.utils import get_system_drive

        try:
            system_drive = get_system_drive()
            # 使用实际系统盘符而非硬编码
            if file_path.upper().startswith(system_drive.upper()):
                relative_path = file_path[len(system_drive):]
            else:
                relative_path = os.path.basename(file_path)

            backup_path = os.path.join(self.backup_dir, relative_path)

            os.makedirs(os.path.dirname(backup_path), exist_ok=True)
            shutil.copy2(file_path, backup_path)

            # 验证备份文件
            if not os.path.exists(backup_path):
                raise Exception(f"备份文件不存在: {backup_path}")

            return True

        except Exception as e:
            # 备份失败时抛出异常，让调用者决定是否继续删除
            raise Exception(f"备份失败: {file_path} - {str(e)}")

    def _save_log(self) -> str:
        """保存清理日志"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_dir = os.path.expanduser("~\\CleanBot\\logs")
        os.makedirs(log_dir, exist_ok=True)

        log_path = os.path.join(log_dir, f"clean_{timestamp}.json")

        log_data = {
            "timestamp": timestamp,
            "use_trash": self.use_trash,
            "backup_dir": self.backup_dir,
            "files": self.clean_log,
            "summary": {
                "total": len(self.clean_log),
                "success": sum(1 for f in self.clean_log if f.get("success")),
                "failed": sum(1 for f in self.clean_log if not f.get("success")),
            }
        }

        with open(log_path, "w", encoding="utf-8") as f:
            json.dump(log_data, f, indent=2, ensure_ascii=False)

        return log_path


from core.utils import format_size


def main():
    """CLI 入口"""
    print("CleanBot v2.0 — 文件清理器")
    print("=" * 60)

    # 示例：清理临时文件
    temp_files = [
        os.path.expandvars("%TEMP%\\test.tmp"),
    ]

    cleaner = FileCleaner(use_trash=True, backup_before_delete=True)

    def confirm(file_path):
        print(f"  删除: {file_path}")
        return True

    def progress(prog):
        print(f"\r  进度: {prog.current}/{prog.total} ({prog.percent:.1f}%)", end="", flush=True)

    print("\n开始清理...")
    result = cleaner.clean(temp_files, confirm_callback=confirm, progress_callback=progress)

    print("\n\n清理完成!")
    print("=" * 60)
    print(f"总文件数: {result.total_files}")
    print(f"已删除: {result.deleted_files}")
    print(f"失败: {result.failed_files}")
    print(f"跳过: {result.skipped_files}")
    print(f"释放空间: {format_size(result.freed_size)}")
    print(f"耗时: {result.duration:.2f} 秒")

    if result.errors:
        print("\n错误:")
        for error in result.errors[:10]:
            print(f"  - {error}")

    print(f"\n日志: {result.log_path}")


if __name__ == "__main__":
    main()
