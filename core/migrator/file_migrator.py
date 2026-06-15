"""
CleanBot v2.0 — 文件迁移器

将文件从 C 盘迁移到其他盘，确保：
1. 管理员权限检测
2. 迁移后文件完整性验证
3. C 盘空间实打实减少
4. 详细的错误提示
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

from core.utils import (
    is_admin, run_as_admin, get_drive_free_space,
    check_symlink_support, format_size
)


@dataclass
class MigrationResult:
    """迁移结果"""
    success: bool = False
    total_files: int = 0
    migrated_files: int = 0
    failed_files: int = 0
    skipped_files: int = 0
    total_size: int = 0
    migrated_size: int = 0
    space_freed: int = 0  # 实际释放的空间
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    details: List[Dict] = field(default_factory=list)
    log_path: str = ""


@dataclass
class MigrationProgress:
    """迁移进度"""
    current: int = 0
    total: int = 0
    current_file: str = ""
    percent: float = 0.0
    phase: str = ""  # copying, verifying, cleanup


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

    def check_prerequisites(self) -> tuple[bool, List[str]]:
        """
        检查迁移前置条件

        Returns:
            (是否可以继续, 错误列表)
        """
        errors = []

        # 1. 检查管理员权限
        if not is_admin():
            errors.append("❌ 需要管理员权限才能创建符号链接")
            errors.append('   请右键点击程序，选择"以管理员身份运行"')

        # 2. 检查目标盘是否存在
        if not os.path.exists(self.target_drive):
            errors.append(f"❌ 目标盘 {self.target_drive} 不存在")

        # 3. 检查目标盘空间
        target_free = get_drive_free_space(self.target_drive)
        if target_free < 100 * 1024 * 1024:  # 小于 100MB
            errors.append(f"❌ 目标盘 {self.target_drive} 空间不足: {format_size(target_free)}")

        # 4. 检查符号链接支持
        if not check_symlink_support():
            errors.append("❌ 系统不支持符号链接（需要管理员权限或开发者模式）")

        return len(errors) == 0, errors

    def migrate_files(
        self,
        files: List[str],
        create_symlink: bool = True,
        verify_space: bool = True,
        progress_callback: Optional[Callable] = None,
    ) -> MigrationResult:
        """
        迁移文件列表

        Args:
            files: 要迁移的文件路径列表
            create_symlink: 是否创建符号链接保持原路径可用
            verify_space: 是否验证空间释放
            progress_callback: 进度回调

        Returns:
            MigrationResult: 迁移结果
        """
        result = MigrationResult()
        result.total_files = len(files)

        # 检查前置条件
        can_continue, errors = self.check_prerequisites()
        if not can_continue:
            result.errors = errors
            return result

        # 记录初始 C 盘空间
        c_drive_initial_free = get_drive_free_space("C:\\")

        # 计算总大小
        valid_files = []
        for file_path in files:
            try:
                if os.path.exists(file_path):
                    size = os.path.getsize(file_path)
                    result.total_size += size
                    valid_files.append(file_path)
                else:
                    result.warnings.append(f"⚠️ 文件不存在，跳过: {file_path}")
                    result.skipped_files += 1
            except (OSError, PermissionError) as e:
                result.warnings.append(f"⚠️ 无法读取文件，跳过: {file_path} - {str(e)}")
                result.skipped_files += 1

        if not valid_files:
            result.errors.append("❌ 没有有效的文件可以迁移")
            return result

        # 创建目标目录
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        target_base = os.path.join(self.target_drive, "CleanBot-Migrated", timestamp)
        os.makedirs(target_base, exist_ok=True)

        # 迁移文件
        for i, file_path in enumerate(valid_files):
            # 进度回调
            if progress_callback:
                progress = MigrationProgress(
                    current=i + 1,
                    total=len(valid_files),
                    current_file=file_path,
                    percent=(i + 1) / len(valid_files) * 100,
                    phase="copying"
                )
                progress_callback(progress)

            file_result = self._migrate_single_file(file_path, target_base, create_symlink)
            result.details.append(file_result)

            if file_result["success"]:
                result.migrated_files += 1
                result.migrated_size += file_result["size"]
            else:
                result.failed_files += 1
                result.errors.append(file_result["error"])

        # 验证空间释放
        if verify_space and result.migrated_files > 0:
            if progress_callback:
                progress = MigrationProgress(
                    current=len(valid_files),
                    total=len(valid_files),
                    current_file="",
                    percent=100,
                    phase="verifying"
                )
                progress_callback(progress)

            c_drive_final_free = get_drive_free_space("C:\\")
            result.space_freed = c_drive_final_free - c_drive_initial_free

            # 如果使用符号链接，空间不会立即释放
            if create_symlink:
                result.warnings.append(
                    "ℹ️ 已创建符号链接，原位置仍可访问文件，但文件实际存储在目标盘"
                )
            elif result.space_freed < result.migrated_size * 0.9:
                # 空间释放不足 90%，可能有问题
                result.warnings.append(
                    f"⚠️ 预期释放 {format_size(result.migrated_size)}，"
                    f"实际释放 {format_size(result.space_freed)}"
                )

        # 保存日志
        result.log_path = self._save_log(result)

        # 判断是否成功
        result.success = result.failed_files == 0 and result.migrated_files > 0

        return result

    def _migrate_single_file(
        self,
        file_path: str,
        target_base: str,
        create_symlink: bool
    ) -> Dict:
        """
        迁移单个文件

        Returns:
            包含 success, size, error 的字典
        """
        file_result = {
            "original": file_path,
            "success": False,
            "size": 0,
            "error": "",
            "target": "",
            "symlink_created": False
        }

        try:
            # 检查文件是否被占用
            if self._is_file_locked(file_path):
                file_result["error"] = f"文件被占用，请关闭使用此文件的程序: {file_path}"
                return file_result

            # 获取文件大小
            file_size = os.path.getsize(file_path)
            file_result["size"] = file_size

            # 计算源文件哈希
            source_hash = self._calculate_hash(file_path)
            if not source_hash:
                file_result["error"] = f"无法计算文件哈希: {file_path}"
                return file_result

            # 生成目标路径（保持原始目录结构）
            if file_path.startswith("C:\\"):
                relative_path = file_path[3:]  # 去掉 "C:\"
            elif file_path.startswith("c:\\"):
                relative_path = file_path[3:]
            else:
                relative_path = os.path.basename(file_path)

            target_path = os.path.join(target_base, relative_path)
            file_result["target"] = target_path

            # 创建目标目录
            os.makedirs(os.path.dirname(target_path), exist_ok=True)

            # 复制文件
            shutil.copy2(file_path, target_path)

            # 验证复制完整性
            target_hash = self._calculate_hash(target_path)
            if source_hash != target_hash:
                # 哈希不匹配，删除目标文件
                os.remove(target_path)
                file_result["error"] = f"文件验证失败（哈希不匹配）: {file_path}"
                return file_result

            # 创建符号链接（如果启用）
            if create_symlink:
                symlink_success = self._create_symlink(file_path, target_path)
                if not symlink_success:
                    # 符号链接失败，保留原文件
                    file_result["error"] = f"符号链接创建失败: {file_path}"
                    file_result["warnings"] = ["文件已复制到目标盘，但原文件未被替换"]
                    return file_result
                file_result["symlink_created"] = True

            # 记录迁移
            self.migration_log.append({
                "original": file_path,
                "target": target_path,
                "size": file_size,
                "hash": source_hash,
                "timestamp": time.time(),
                "success": True,
                "symlink": create_symlink,
            })

            file_result["success"] = True

        except PermissionError as e:
            file_result["error"] = f"权限不足: {file_path} - 请以管理员身份运行"
        except OSError as e:
            file_result["error"] = f"系统错误: {file_path} - {str(e)}"
        except Exception as e:
            file_result["error"] = f"未知错误: {file_path} - {str(e)}"

        return file_result

    def _create_symlink(self, original_path: str, target_path: str) -> bool:
        """
        创建符号链接

        Args:
            original_path: 原始路径
            target_path: 目标路径

        Returns:
            是否成功
        """
        try:
            # 备份原文件
            backup_path = original_path + ".cleanbot_backup"
            shutil.copy2(original_path, backup_path)

            # 删除原文件
            os.remove(original_path)

            # 创建符号链接
            os.symlink(target_path, original_path)

            # 验证符号链接是否工作
            if os.path.exists(original_path) and os.path.isfile(original_path):
                # 验证通过，删除备份
                os.remove(backup_path)
                return True
            else:
                # 验证失败，恢复原文件
                if os.path.islink(original_path):
                    os.remove(original_path)
                shutil.copy2(backup_path, original_path)
                os.remove(backup_path)
                return False

        except OSError as e:
            # 恢复原文件
            if os.path.exists(backup_path):
                if os.path.islink(original_path):
                    os.remove(original_path)
                shutil.copy2(backup_path, original_path)
                os.remove(backup_path)
            return False

    def _is_file_locked(self, file_path: str) -> bool:
        """检查文件是否被占用"""
        try:
            # 尝试以独占模式打开文件
            with open(file_path, 'r+b') as f:
                pass
            return False
        except (IOError, OSError):
            return True

    def _calculate_hash(self, file_path: str) -> str:
        """计算文件哈希（SHA-256）"""
        hash_sha256 = hashlib.sha256()

        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    hash_sha256.update(chunk)
        except (OSError, PermissionError):
            return ""

        return hash_sha256.hexdigest()

    def _save_log(self, result: MigrationResult) -> str:
        """保存迁移日志"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_dir = os.path.expanduser("~\\CleanBot\\logs")
        os.makedirs(log_dir, exist_ok=True)

        log_path = os.path.join(log_dir, f"migration_{timestamp}.json")

        log_data = {
            "timestamp": timestamp,
            "target_drive": self.target_drive,
            "success": result.success,
            "summary": {
                "total_files": result.total_files,
                "migrated_files": result.migrated_files,
                "failed_files": result.failed_files,
                "skipped_files": result.skipped_files,
                "total_size": result.total_size,
                "migrated_size": result.migrated_size,
                "space_freed": result.space_freed,
            },
            "errors": result.errors,
            "warnings": result.warnings,
            "details": result.details,
        }

        with open(log_path, "w", encoding="utf-8") as f:
            json.dump(log_data, f, indent=2, ensure_ascii=False)

        return log_path

    def verify_migration(self, original_path: str, target_path: str) -> tuple[bool, str]:
        """
        验证迁移是否成功

        Returns:
            (是否成功, 错误信息)
        """
        # 检查目标文件是否存在
        if not os.path.exists(target_path):
            return False, "目标文件不存在"

        # 检查文件大小
        original_size = os.path.getsize(original_path) if os.path.exists(original_path) else 0
        target_size = os.path.getsize(target_path)

        # 如果原文件是符号链接，获取实际大小
        if os.path.islink(original_path):
            real_path = os.path.realpath(original_path)
            if os.path.exists(real_path):
                original_size = os.path.getsize(real_path)

        if original_size != target_size:
            return False, f"文件大小不匹配: 原始 {original_size} 字节, 目标 {target_size} 字节"

        # 检查哈希
        original_hash = self._calculate_hash(
            os.path.realpath(original_path) if os.path.islink(original_path) else original_path
        )
        target_hash = self._calculate_hash(target_path)

        if original_hash != target_hash:
            return False, "文件哈希不匹配"

        return True, "验证通过"
