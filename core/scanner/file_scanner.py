"""
CleanBot v2.0 — 文件扫描器

扫描文件系统，识别可清理文件。
"""

import os
import sys
import time
import hashlib
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple
from datetime import datetime, timezone
from collections import defaultdict

from core.utils import format_size


@dataclass
class FileInfo:
    """文件信息"""
    path: str
    size: int
    created: float
    modified: float
    accessed: float
    extension: str
    is_hidden: bool
    is_system: bool
    is_readonly: bool
    file_type: str = ""  # temp, cache, log, backup, etc.
    category: str = ""   # safe, ask, danger
    hash: str = ""
    # Smart analyzer fields
    risk_level: str = ""       # safe, low, medium, high, critical
    risk_reason: str = ""      # Human-readable risk explanation
    type_name: str = ""        # Human-readable file type name
    impact: str = ""           # What happens if deleted
    clean_score: int = 0       # 0-100, higher = more recommended to clean


@dataclass
class ScanResult:
    """扫描结果"""
    total_files: int = 0
    total_size: int = 0
    by_category: Dict[str, List[FileInfo]] = field(default_factory=dict)
    by_extension: Dict[str, List[FileInfo]] = field(default_factory=dict)
    largest_files: List[FileInfo] = field(default_factory=list)
    temp_files: List[FileInfo] = field(default_factory=list)
    cache_files: List[FileInfo] = field(default_factory=list)
    log_files: List[FileInfo] = field(default_factory=list)
    old_files: List[FileInfo] = field(default_factory=list)
    duplicate_files: Dict[str, List[FileInfo]] = field(default_factory=dict)
    scan_duration: float = 0.0


class FileScanner:
    """文件扫描器 — 快速模式优先扫垃圾聚集地"""

    # 可直接删除的扩展名
    SAFE_EXTENSIONS = {
        ".tmp", ".temp", ".log", ".bak", ".old", ".backup",
        ".cache", ".dmp", ".crash", ".etl", ".evtx", ".mdmp",
        ".hdmp", ".wer", ".chk", "._file", ".gid",
    }

    # 路径关键词（命中即判定为可清理）
    CLEAN_PATH_KEYWORDS = [
        "\\temp\\", "\\tmp\\", "\\cache\\", "\\cached\\",
        "\\inetcache\\", "\\thumbcache\\", "\\prefetch\\",
        "\\logs\\", "\\logfiles\\", "\\crashdumps\\",
        "\\wer\\", "\\deliveryoptimization\\",
        "\\softwaredistribution\\download\\",
        "\\recent\\", "\\recycle", "$recycle.bin",
    ]

    # 绝对不扫描
    EXCLUDE_PATHS = [
        "C:\\Windows\\System32", "C:\\Windows\\SysWOW64",
        "C:\\Windows\\Boot", "C:\\Windows\\Fonts", "C:\\Windows\\WinSxS",
        "C:\\Program Files", "C:\\Program Files (x86)",
        "C:\\System Volume Information", "C:\\Recovery",
    ]

    def __init__(self, root_path: str = None, max_depth: int = 6):
        from core.utils import get_system_drive
        self.root_path = root_path or get_system_drive()
        self.max_depth = max_depth

        # 垃圾聚集地（优先深度扫描）
        _profile = os.environ.get('USERPROFILE', '')
        _windir = os.environ.get('SystemRoot', 'C:\\Windows')
        _local = os.path.join(_profile, 'AppData', 'Local')
        self._quick_paths = [
            os.path.join(_profile, 'AppData', 'Local', 'Temp'),
            os.path.join(_windir, 'Temp'),
            os.path.join(_local, 'Microsoft', 'Windows', 'INetCache'),
            os.path.join(_local, 'Microsoft', 'Windows', 'Explorer'),
            os.path.join(_local, 'Microsoft', 'Windows', 'WER'),
            os.path.join(_local, 'Microsoft', 'Windows', 'Caches'),
            os.path.join(_local, 'Google', 'Chrome', 'User Data', 'Default', 'Cache'),
            os.path.join(_local, 'Google', 'Chrome', 'User Data', 'Default', 'Code Cache'),
            os.path.join(_local, 'Microsoft', 'Edge', 'User Data', 'Default', 'Cache'),
            os.path.join(_windir, 'Prefetch'),
            os.path.join(_windir, 'Logs'),
            os.path.join(_windir, 'SoftwareDistribution', 'Download'),
            os.path.join(_windir, 'Temp'),
            os.path.join(_windir, 'DeliveryOptimization'),
            os.path.join(_profile, 'AppData', 'Local', 'CrashDumps'),
            os.path.join(_profile, 'AppData', 'Roaming', 'Microsoft', 'Windows', 'Recent'),
        ]
        self.scan_result = ScanResult()
        self.scanned_files: List[FileInfo] = []
        self._excluded_paths: Set[str] = set()
        self._hash_cache: Dict[str, str] = {}

    def scan(self, progress_callback=None) -> ScanResult:
        """扫描文件系统"""
        start_time = time.time()

        # 清空上次扫描结果
        self.scan_result = ScanResult()
        self.scanned_files = []
        self._hash_cache.clear()

        # 预处理排除路径
        self._prepare_excluded_paths()

        # 快速扫描：只扫垃圾聚集地（秒级完成）
        for quick_path in self._quick_paths:
            if os.path.exists(quick_path):
                self._scan_directory(quick_path, 0, progress_callback)

        # 分析结果
        self._analyze_results()

        # 检测重复文件
        self._detect_duplicates()

        # 计算扫描时间
        self.scan_result.scan_duration = time.time() - start_time

        return self.scan_result

    def _prepare_excluded_paths(self):
        """预处理排除路径"""
        for pattern in self.EXCLUDE_PATHS:
            if "*" in pattern:
                continue
            self._excluded_paths.add(pattern.lower())

    def _is_excluded(self, path: str) -> bool:
        """检查路径是否应该排除"""
        path_lower = path.lower()

        for excluded in self._excluded_paths:
            if path_lower.startswith(excluded):
                return True

        for pattern in self.EXCLUDE_PATHS:
            if "*" not in pattern:
                continue
            if self._match_pattern(path_lower, pattern.lower()):
                return True

        return False

    def _match_pattern(self, path: str, pattern: str) -> bool:
        """简单的通配符匹配"""
        import fnmatch
        return fnmatch.fnmatch(path, pattern)

    def _scan_directory(self, dir_path: str, depth: int, progress_callback=None):
        """递归扫描目录"""
        if depth > self.max_depth:
            return

        if self._is_excluded(dir_path):
            return

        try:
            with os.scandir(dir_path) as entries:
                for entry in entries:
                    try:
                        if self._is_excluded(entry.path):
                            continue

                        if entry.is_file(follow_symlinks=False):
                            file_info = self._scan_file(entry)
                            if file_info:
                                self.scanned_files.append(file_info)
                                self.scan_result.total_files += 1
                                self.scan_result.total_size += file_info.size

                                # 每100个文件回调一次，避免UI卡顿
                                if progress_callback and self.scan_result.total_files % 100 == 0:
                                    progress_callback(self.scan_result.total_files, self.scan_result.total_size)

                        elif entry.is_dir(follow_symlinks=False):
                            self._scan_directory(entry.path, depth + 1, progress_callback)

                    except (PermissionError, OSError):
                        continue

        except (PermissionError, OSError):
            return

    def _scan_file(self, entry) -> Optional[FileInfo]:
        """扫描单个文件"""
        try:
            stat = entry.stat(follow_symlinks=False)

            is_hidden = False
            is_system = False
            is_readonly = False

            if sys.platform == "win32":
                attrs = stat.st_file_attributes
                is_hidden = bool(attrs & 0x2)
                is_system = bool(attrs & 0x4)
                is_readonly = bool(attrs & 0x1)

            file_info = FileInfo(
                path=entry.path,
                size=stat.st_size,
                created=stat.st_ctime,
                modified=stat.st_mtime,
                accessed=stat.st_atime,
                extension=Path(entry.path).suffix.lower(),
                is_hidden=is_hidden,
                is_system=is_system,
                is_readonly=is_readonly,
            )

            self._categorize_file(file_info)

            return file_info

        except (PermissionError, OSError):
            return None

    def _categorize_file(self, file_info: FileInfo):
        """快速分类 — 路径匹配 > 扩展名 > 大文件 > 跳过"""
        path_lower = file_info.path.lower()
        ext = file_info.extension
        _set = self._set_info

        # 1. 路径关键词匹配
        for kw in self.CLEAN_PATH_KEYWORDS:
            if kw in path_lower:
                if "\\temp\\" in kw or "\\tmp\\" in kw:
                    _set(file_info, "temp", "safe", "临时文件", "可以安全删除", "删除后不影响系统运行")
                elif "cache" in kw or "thumbcache" in kw or "inetcache" in kw:
                    _set(file_info, "cache", "safe", "缓存文件", "可以安全删除", "应用会自动重建缓存")
                elif "log" in kw:
                    _set(file_info, "log", "safe", "日志文件", "可以安全删除", "仅用于调试，删除不影响功能")
                elif "prefetch" in kw or "recent" in kw:
                    _set(file_info, "cache", "safe", "系统缓存", "可以安全删除", "Windows 会自动重建")
                elif "wer" in kw or "crashdumps" in kw:
                    _set(file_info, "crash", "safe", "错误报告", "可以安全删除", "仅用于调试崩溃")
                elif "softwaredistribution" in kw or "deliveryoptimization" in kw:
                    _set(file_info, "cache", "safe", "更新缓存", "可以安全删除", "Windows 更新已完成")
                elif "recycle" in kw:
                    _set(file_info, "cache", "safe", "回收站", "确认后删除", "删除后无法恢复")
                else:
                    _set(file_info, "temp", "safe", "临时文件", "可以安全删除", "应用不再需要")
                return

        # 2. 扩展名匹配
        if ext in self.SAFE_EXTENSIONS:
            _set(file_info, "safe_ext", "safe", f"{ext} 文件", "可以安全删除", "临时或日志文件")
            return

        # 3. 系统文件
        if file_info.is_system:
            _set(file_info, "system", "skip", "系统文件", "危险", "删除可能导致系统崩溃")
            return

        # 4. 大文件
        if file_info.size > 100 * 1024 * 1024:
            _set(file_info, "large", "ask", "大文件", "中风险", f"占用 {format_size(file_info.size)}，建议确认后处理")
            return

        # 5. 旧文件
        if self._is_old_file(file_info):
            _set(file_info, "old", "ask", "旧文件", "低风险", "超过30天未使用")
            return

        _set(file_info, "unknown", "skip", "未知", "跳过", "未识别类型")

    @staticmethod
    def _set_info(f, ftype, cat, type_name, risk, impact):
        f.file_type = ftype
        f.category = cat
        f.type_name = type_name
        f.risk_level = risk
        f.impact = impact

    def _is_old_file(self, file_info: FileInfo) -> bool:
        """检查是否旧文件（>30天未访问且 >1MB）"""
        if file_info.size < 1024 * 1024:
            return False
        return (time.time() - file_info.accessed) > 30 * 86400

    def _calculate_hash(self, file_path: str) -> str:
        """计算文件哈希 (SHA-256，避免 MD5 碰撞风险)"""
        if file_path in self._hash_cache:
            return self._hash_cache[file_path]

        hash_sha256 = hashlib.sha256()

        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    hash_sha256.update(chunk)
        except (OSError, PermissionError):
            return ""

        result = hash_sha256.hexdigest()
        self._hash_cache[file_path] = result
        return result

    def _detect_duplicates(self):
        """检测重复文件"""
        # 按大小分组
        size_groups: Dict[int, List[FileInfo]] = defaultdict(list)

        for file_info in self.scanned_files:
            if file_info.size > 0:
                size_groups[file_info.size].append(file_info)

        # 对相同大小的文件计算哈希
        for size, files in size_groups.items():
            if len(files) < 2:
                continue

            hash_groups: Dict[str, List[FileInfo]] = defaultdict(list)

            for file_info in files:
                file_hash = self._calculate_hash(file_info.path)
                if file_hash:
                    file_info.hash = file_hash
                    hash_groups[file_hash].append(file_info)

            # 保存重复文件
            for file_hash, duplicate_files in hash_groups.items():
                if len(duplicate_files) >= 2:
                    self.scan_result.duplicate_files[file_hash] = duplicate_files

    def _analyze_results(self):
        """分析扫描结果"""
        for file_info in self.scanned_files:
            category = file_info.category
            if category not in self.scan_result.by_category:
                self.scan_result.by_category[category] = []
            self.scan_result.by_category[category].append(file_info)

        for file_info in self.scanned_files:
            ext = file_info.extension or "(无扩展名)"
            if ext not in self.scan_result.by_extension:
                self.scan_result.by_extension[ext] = []
            self.scan_result.by_extension[ext].append(file_info)

        self.scan_result.largest_files = sorted(
            self.scanned_files,
            key=lambda f: f.size,
            reverse=True
        )[:100]

        self.scan_result.temp_files = [
            f for f in self.scanned_files if f.file_type == "temp"
        ]

        self.scan_result.cache_files = [
            f for f in self.scanned_files if f.file_type == "cache"
        ]

        self.scan_result.log_files = [
            f for f in self.scanned_files if f.file_type == "log"
        ]

        self.scan_result.old_files = [
            f for f in self.scanned_files if f.file_type == "old"
        ]

    def get_safe_to_delete(self) -> List[FileInfo]:
        """获取安全删除的文件列表"""
        return [
            f for f in self.scanned_files
            if f.category == "safe" and not f.is_system
        ]

    def get_ask_user(self) -> List[FileInfo]:
        """获取需要用户确认的文件列表"""
        return [
            f for f in self.scanned_files
            if f.category == "ask" and not f.is_system
        ]

    def get_duplicates(self) -> Dict[str, List[FileInfo]]:
        """获取重复文件"""
        return self.scan_result.duplicate_files

    def get_summary(self) -> Dict:
        """获取扫描摘要"""
        safe_files = self.get_safe_to_delete()
        ask_files = self.get_ask_user()
        duplicates = self.get_duplicates()

        safe_size = sum(f.size for f in safe_files)
        ask_size = sum(f.size for f in ask_files)
        duplicate_size = sum(
            sum(f.size for f in files[1:])
            for files in duplicates.values()
        )

        return {
            "total_files": self.scan_result.total_files,
            "total_size_mb": self.scan_result.total_size / (1024 * 1024),
            "safe_files": len(safe_files),
            "safe_size_mb": safe_size / (1024 * 1024),
            "ask_files": len(ask_files),
            "ask_size_mb": ask_size / (1024 * 1024),
            "duplicate_groups": len(duplicates),
            "duplicate_size_mb": duplicate_size / (1024 * 1024),
            "scan_duration": self.scan_result.scan_duration,
        }


def main():
    """CLI 入口"""
    from core.utils import get_system_drive

    print("CleanBot v2.0 — 文件扫描器")
    print("=" * 60)

    scanner = FileScanner(get_system_drive())

    def progress(count, size):
        if count % 1000 == 0:
            print(f"\r  已扫描: {count} 个文件, {format_size(size)}", end="", flush=True)

    print("\n开始扫描...")
    result = scanner.scan(progress_callback=progress)

    print("\n\n扫描完成!")
    print("=" * 60)

    summary = scanner.get_summary()
    print(f"总文件数: {summary['total_files']}")
    print(f"总大小: {summary['total_size_mb']:.2f} MB")
    print(f"扫描时间: {summary['scan_duration']:.2f} 秒")

    print("\n可安全删除:")
    print(f"  文件数: {summary['safe_files']}")
    print(f"  大小: {summary['safe_size_mb']:.2f} MB")

    print("\n需要确认:")
    print(f"  文件数: {summary['ask_files']}")
    print(f"  大小: {summary['ask_size_mb']:.2f} MB")

    print("\n重复文件:")
    print(f"  组数: {summary['duplicate_groups']}")
    print(f"  大小: {summary['duplicate_size_mb']:.2f} MB")

    print("\n最大的 10 个文件:")
    for i, file_info in enumerate(result.largest_files[:10]):
        print(f"  {i+1}. {format_size(file_info.size):>10} {file_info.path}")


if __name__ == "__main__":
    main()
