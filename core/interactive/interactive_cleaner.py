"""
CleanBot v2.0 — 交互式清理器

用户可以询问删除文件或应用，系统会：
1. 分析目标，提供详细信息
2. 二次确认风险等级和影响
3. 深度清理，不留残渣
"""

import os
import sys
import json
import time
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable

from core.utils import format_size
from datetime import datetime

from core.deep_cleaner.deep_cleaner import DeepCleaner, CleanupTarget, CleanupResult
from core.analyzer.smart_analyzer import SmartAnalyzer


@dataclass
class FileInfo:
    """文件信息"""
    path: str
    name: str
    file_type: str  # file, folder
    size: int = 0
    extension: str = ""
    type_name: str = ""
    description: str = ""
    risk_level: str = "medium"
    risk_reason: str = ""
    can_delete: bool = True
    delete_impact: str = ""
    related_items: List[str] = field(default_factory=list)


class InteractiveCleaner:
    """交互式清理器"""

    def __init__(self):
        self.deep_cleaner = DeepCleaner()
        self.smart_analyzer = SmartAnalyzer()

    def analyze_file(self, path: str) -> FileInfo:
        """
        分析文件，提供详细信息

        Args:
            path: 文件路径

        Returns:
            FileInfo: 文件信息
        """
        info = FileInfo(
            path=path,
            name=os.path.basename(path),
            file_type="folder" if os.path.isdir(path) else "file",
        )

        # 获取大小
        if os.path.isdir(path):
            info.size = self._calculate_dir_size(path)
        else:
            try:
                info.size = os.path.getsize(path)
            except (OSError, PermissionError):
                info.size = 0

        # 获取扩展名
        if os.path.isfile(path):
            info.extension = os.path.splitext(path)[1].lower()

        # 使用智能分析器获取类型信息
        if info.extension:
            analysis = self.smart_analyzer.analyze_file_by_extension(info.extension)
            info.type_name = analysis.get("type_name", "未知文件")
            info.description = analysis.get("description", "")
            info.risk_level = analysis.get("risk_level", "medium")
            info.risk_reason = analysis.get("risk_reason", "")
            info.delete_impact = analysis.get("impact", "未知影响")
        else:
            info.type_name = "文件夹"
            info.description = "目录文件夹"

        # 检查是否可以删除
        info.can_delete = self._can_delete(path)

        # 查找关联项
        info.related_items = self._find_related_items(path)

        # 调整风险等级
        if info.related_items:
            info.risk_level = "high"
            info.risk_reason = "有关联的注册表项、快捷方式或启动项"

        return info

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

    def _can_delete(self, path: str) -> bool:
        """检查是否可以删除"""
        path_lower = path.lower()

        # 系统文件不能删除
        system_paths = [
            "c:\\windows",
            "c:\\program files",
            "c:\\program files (x86)",
            "c:\\users\\default",
        ]

        for sys_path in system_paths:
            if path_lower.startswith(sys_path):
                return False

        # 桌面文件警告
        if "desktop" in path_lower or "桌面" in path_lower:
            return True  # 可以删除，但需要确认

        return True

    def _find_related_items(self, path: str) -> List[str]:
        """查找关联项"""
        items = []

        # 使用深度清理器分析
        target = self.deep_cleaner.analyze_target(path)

        if target.registry_entries:
            items.extend([f"注册表: {e}" for e in target.registry_entries])
        if target.shortcuts:
            items.extend([f"快捷方式: {s}" for s in target.shortcuts])
        if target.startup_entries:
            items.extend([f"启动项: {e}" for e in target.startup_entries])
        if target.scheduled_tasks:
            items.extend([f"计划任务: {t}" for t in target.scheduled_tasks])

        return items

    def get_confirmation_message(self, info: FileInfo) -> str:
        """
        获取确认消息

        Args:
            info: 文件信息

        Returns:
            str: 确认消息
        """
        lines = []
        lines.append(f"您要删除: {info.name}")
        lines.append("")
        lines.append(f"类型: {info.type_name}")
        lines.append(f"大小: {format_size(info.size)}")
        lines.append(f"路径: {info.path}")
        lines.append("")

        if info.description:
            lines.append(f"说明: {info.description}")
            lines.append("")

        # 风险等级
        risk_icon = {
            "low": "🟢 低风险",
            "medium": "🟡 中风险",
            "high": "🔴 高风险",
        }.get(info.risk_level, "⚪ 未知风险")

        lines.append(f"风险等级: {risk_icon}")
        if info.risk_reason:
            lines.append(f"风险原因: {info.risk_reason}")
        lines.append("")

        # 删除影响
        if info.delete_impact:
            lines.append(f"删除影响: {info.delete_impact}")
            lines.append("")

        # 关联项
        if info.related_items:
            lines.append("⚠️ 发现关联项（也会被删除）:")
            for item in info.related_items[:5]:
                lines.append(f"  - {item}")
            if len(info.related_items) > 5:
                lines.append(f"  ... 还有 {len(info.related_items) - 5} 项")
            lines.append("")

        # 最终警告
        if info.risk_level == "high":
            lines.append("⚠️ 警告: 此操作不可逆，请确认您真的要删除！")
        elif info.risk_level == "medium":
            lines.append("⚠️ 注意: 删除后可能需要重新安装或配置")

        return "\n".join(lines)

    def delete_file(
        self,
        path: str,
        confirm_callback: Optional[Callable] = None,
        progress_callback: Optional[Callable] = None,
    ) -> CleanupResult:
        """
        删除文件（深度清理）

        Args:
            path: 文件路径
            confirm_callback: 确认回调
            progress_callback: 进度回调

        Returns:
            CleanupResult: 清理结果
        """
        # 分析目标
        target = self.deep_cleaner.analyze_target(path)

        # 执行深度清理
        result = self.deep_cleaner.deep_clean(
            target,
            confirm_callback=confirm_callback,
            progress_callback=progress_callback,
        )

        return result

    def get_file_info_summary(self, path: str) -> Dict:
        """
        获取文件信息摘要（用于 UI 显示）

        Args:
            path: 文件路径

        Returns:
            Dict: 文件信息摘要
        """
        info = self.analyze_file(path)

        return {
            "name": info.name,
            "path": info.path,
            "type": info.file_type,
            "type_name": info.type_name,
            "size": info.size,
            "size_formatted": format_size(info.size),
            "extension": info.extension,
            "description": info.description,
            "risk_level": info.risk_level,
            "risk_reason": info.risk_reason,
            "can_delete": info.can_delete,
            "delete_impact": info.delete_impact,
            "related_items": info.related_items,
            "related_count": len(info.related_items),
        }
