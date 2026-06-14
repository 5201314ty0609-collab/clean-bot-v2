"""
CleanBot v2.0 — 文件迁移器

将文件从 C 盘迁移到其他盘，不影响文件内容和使用。
使用符号链接保持原路径可用。
"""

import os
import sys
import shutil
import hashlib
import json
import time
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable
from datetime import datetime


@dataclass
class MigrationResult:
    """迁移结果"""
    success: bool = False
    total_files: int = 0
    migrated_files: int = 0
    failed_files: int = 0
    total_size: int = 0
    migrated_size: int = 0
    errors: List[str] = field(default_factory=list)
    log_path: str = ""


@dataclass
class MigrationProgress:
    """迁移进度"""
    current: int = 0
    total: int = 0
    current_file: str = ""
    percent: float = 0.0


class FileMigrator:
    """文件迁移器"""

    def __init__(self, target_drive: str = "D:\\"):
        """
        初始化文件迁移器

        Args:
            target_drive: 目标盘符（默认 D:\\）
        """
        self.target_drive = target_drive
        self.migration_log: List[Dict] = []
        self.backup_dir: Optional[str] = None

    def migrate_files(
        self,
        files: List[str],
        create_symlink: bool = True,
        progress_callback: Optional[Callable] = None,
    ) -> MigrationResult:
        """
        迁移文件列表

        Args:
            files: 要迁移的文件路径列表
            create_symlink: 是否创建符号链接保持原路径可用
            progress_callback: 进度回调

        Returns:
            MigrationResult: 迁移结果
        """
        result = MigrationResult()
        result.total_files = len(files)

        # 计算总大小
        for file_path in files:
            try:
                size = os.path.getsize(file_path)
                result.total_size += size
            except (OSError, PermissionError):
                pass

        # 创建目标目录
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        target_base = os.path.join(self.target_drive, "CleanBot-Migrated", timestamp)
        os.makedirs(target_base, exist_ok=True)

        # 迁移文件
        for i, file_path in enumerate(files):
            # 进度回调
            if progress_callback:
                progress = MigrationProgress(
                    current=i + 1,
                    total=len(files),
                    current_file=file_path,
                    percent=(i + 1) / len(files) * 100,
                )
                progress_callback(progress)

            try:
                # 检查文件是否存在
                if not os.path.exists(file_path):
                    result.errors.append(f"文件不存在: {file_path}")
                    result.failed_files += 1
                    continue

                # 获取文件大小
                file_size = os.path.getsize(file_path)

                # 计算源文件哈希
                source_hash = self._calculate_hash(file_path)

                # 生成目标路径（保持原始目录结构）
                if file_path.startswith("C:\\"):
                    relative_path = file_path[3:]  # 去掉 "C:\"
                else:
                    relative_path = os.path.basename(file_path)

                target_path = os.path.join(target_base, relative_path)

                # 创建目标目录
                os.makedirs(os.path.dirname(target_path), exist_ok=True)

                # 复制文件
                shutil.copy2(file_path, target_path)

                # 验证复制完整性
                target_hash = self._calculate_hash(target_path)
                if source_hash != target_hash:
                    # 哈希不匹配，删除目标文件
                    os.remove(target_path)
                    result.errors.append(f"文件验证失败: {file_path}")
                    result.failed_files += 1
                    continue

                # 创建符号链接（如果启用）
                if create_symlink:
                    # 备份原文件
                    backup_path = file_path + ".bak"
                    shutil.copy2(file_path, backup_path)

                    # 删除原文件
                    os.remove(file_path)

                    # 创建符号链接
                    try:
                        os.symlink(target_path, file_path)
                        # 验证符号链接
                        if not os.path.exists(file_path):
                            # 符号链接失败，恢复原文件
                            shutil.copy2(backup_path, file_path)
                            os.remove(backup_path)
                            result.errors.append(f"符号链接创建失败: {file_path}")
                            result.failed_files += 1
                            continue
                    except OSError as e:
                        # 符号链接失败，恢复原文件
                        shutil.copy2(backup_path, file_path)
                        os.remove(backup_path)
                        result.errors.append(f"符号链接创建失败: {file_path} - {str(e)}")
                        result.failed_files += 1
                        continue

                    # 删除备份
                    os.remove(backup_path)

                # 记录迁移
                self.migration_log.append({
                    "original": file_path,
                    "target": target_path,
                    "size": file_size,
                    "hash": source_hash,
                    "timestamp": time.time(),
                    "success": True,
                })

                result.migrated_files += 1
                result.migrated_size += file_size

            except PermissionError as e:
                result.errors.append(f"权限不足: {file_path} - {str(e)}")
                result.failed_files += 1
            except OSError as e:
                result.errors.append(f"系统错误: {file_path} - {str(e)}")
                result.failed_files += 1
            except Exception as e:
                result.errors.append(f"未知错误: {file_path} - {str(e)}")
                result.failed_files += 1

        # 保存日志
        result.log_path = self._save_log()

        # 判断是否成功
        result.success = result.failed_files == 0

        return result

    def _calculate_hash(self, file_path: str) -> str:
        """计算文件哈希"""
        hash_sha256 = hashlib.sha256()

        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    hash_sha256.update(chunk)
        except (OSError, PermissionError):
            return ""

        return hash_sha256.hexdigest()

    def _save_log(self) -> str:
        """保存迁移日志"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_dir = os.path.expanduser("~\\CleanBot\\logs")
        os.makedirs(log_dir, exist_ok=True)

        log_path = os.path.join(log_dir, f"migration_{timestamp}.json")

        log_data = {
            "timestamp": timestamp,
            "target_drive": self.target_drive,
            "records": self.migration_log,
            "summary": {
                "total": len(self.migration_log),
                "success": sum(1 for r in self.migration_log if r.get("success")),
                "failed": sum(1 for r in self.migration_log if not r.get("success")),
            }
        }

        with open(log_path, "w", encoding="utf-8") as f:
            json.dump(log_data, f, indent=2, ensure_ascii=False)

        return log_path


def format_size(size_bytes: int) -> str:
    """格式化文件大小"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"
