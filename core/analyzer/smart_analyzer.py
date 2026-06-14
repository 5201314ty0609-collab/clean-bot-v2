"""
CleanBot v2.0 -- Smart File Analyzer

Provides deep file analysis with:
- File type knowledge base (what each extension means, who uses it, safe to delete?)
- Deletion impact assessment
- Risk level classification
- Intelligent categorization
"""

import os
import sys
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Risk levels
# ---------------------------------------------------------------------------

class RiskLevel(Enum):
    """Risk level for file deletion."""
    SAFE = "safe"           # Absolutely safe to delete (temp, cache)
    LOW = "low"             # Low risk (logs, old downloads)
    MEDIUM = "medium"       # Medium risk (user files, but old/unused)
    HIGH = "high"           # High risk (active user data)
    CRITICAL = "critical"   # Critical -- never recommend deleting


# ---------------------------------------------------------------------------
# File type knowledge base
# ---------------------------------------------------------------------------

@dataclass
class FileTypeInfo:
    """Knowledge about a file type."""
    extension: str
    name: str               # Human-readable name
    description: str        # What this file is for
    typical_owner: str      # Who creates/uses it (OS, app name, user)
    safe_to_delete: bool    # Generally safe to delete?
    risk: RiskLevel         # Default risk level
    impact: str             # What happens if you delete it
    recoverable: bool       # Can it be regenerated/downloaded again?
    category: str           # temp, cache, log, document, media, code, etc.


# Knowledge base: extension -> FileTypeInfo
FILE_TYPE_KNOWLEDGE: Dict[str, FileTypeInfo] = {
    # --- Temporary files ---
    ".tmp": FileTypeInfo(
        extension=".tmp",
        name="Temporary File",
        description="System or application temporary file. Usually created during installations or operations.",
        typical_owner="OS / Various apps",
        safe_to_delete=True,
        risk=RiskLevel.SAFE,
        impact="None -- these are meant to be temporary.",
        recoverable=True,
        category="temp",
    ),
    ".temp": FileTypeInfo(
        extension=".temp",
        name="Temporary File",
        description="Temporary file created by applications during processing.",
        typical_owner="Various apps",
        safe_to_delete=True,
        risk=RiskLevel.SAFE,
        impact="None -- these are meant to be temporary.",
        recoverable=True,
        category="temp",
    ),

    # --- Log files ---
    ".log": FileTypeInfo(
        extension=".log",
        name="Log File",
        description="Text log file recording application or system events. Useful for debugging.",
        typical_owner="OS / Apps",
        safe_to_delete=True,
        risk=RiskLevel.LOW,
        impact="Lose debugging history. Apps will create new logs.",
        recoverable=False,
        category="log",
    ),
    ".etl": FileTypeInfo(
        extension=".etl",
        name="Event Trace Log",
        description="Windows Event Trace Log used for performance profiling.",
        typical_owner="Windows",
        safe_to_delete=True,
        risk=RiskLevel.LOW,
        impact="Lose trace data. Only useful for diagnostics.",
        recoverable=False,
        category="log",
    ),
    ".evtx": FileTypeInfo(
        extension=".evtx",
        name="Windows Event Log",
        description="Windows Event Viewer log file.",
        typical_owner="Windows",
        safe_to_delete=True,
        risk=RiskLevel.LOW,
        impact="Lose event history. Windows will create new logs.",
        recoverable=False,
        category="log",
    ),

    # --- Crash/dump files ---
    ".dmp": FileTypeInfo(
        extension=".dmp",
        name="Crash Dump File",
        description="Memory dump created when a program crashes. Used for debugging.",
        typical_owner="OS / Apps",
        safe_to_delete=True,
        risk=RiskLevel.SAFE,
        impact="Lose crash data. Only useful if debugging the crash.",
        recoverable=False,
        category="crash",
    ),
    ".crash": FileTypeInfo(
        extension=".crash",
        name="Crash Report",
        description="Crash report file.",
        typical_owner="Apps",
        safe_to_delete=True,
        risk=RiskLevel.SAFE,
        impact="Lose crash report. Only useful for debugging.",
        recoverable=False,
        category="crash",
    ),
    ".mdmp": FileTypeInfo(
        extension=".mdmp",
        name="Mini Dump",
        description="Mini crash dump file for debugging.",
        typical_owner="Windows / Apps",
        safe_to_delete=True,
        risk=RiskLevel.SAFE,
        impact="Lose crash data.",
        recoverable=False,
        category="crash",
    ),

    # --- Cache files ---
    ".cache": FileTypeInfo(
        extension=".cache",
        name="Cache File",
        description="Cached data to speed up application loading.",
        typical_owner="Apps",
        safe_to_delete=True,
        risk=RiskLevel.SAFE,
        impact="Apps may load slightly slower next time. Cache will be rebuilt.",
        recoverable=True,
        category="cache",
    ),
    ".thumbs.db": FileTypeInfo(
        extension=".thumbs.db",
        name="Thumbnail Cache",
        description="Windows Explorer thumbnail cache for faster folder browsing.",
        typical_owner="Windows Explorer",
        safe_to_delete=True,
        risk=RiskLevel.SAFE,
        impact="Thumbnails will be regenerated when you browse the folder.",
        recoverable=True,
        category="cache",
    ),
    ".ds_store": FileTypeInfo(
        extension=".ds_store",
        name="macOS Folder Settings",
        description="macOS Finder metadata (folder view settings, icon positions).",
        typical_owner="macOS Finder",
        safe_to_delete=True,
        risk=RiskLevel.SAFE,
        impact="Folder view settings reset to defaults.",
        recoverable=True,
        category="cache",
    ),

    # --- Backup files ---
    ".bak": FileTypeInfo(
        extension=".bak",
        name="Backup File",
        description="Backup copy of a file, usually created automatically by editors or installers.",
        typical_owner="Apps / User",
        safe_to_delete=True,
        risk=RiskLevel.LOW,
        impact="Lose the backup copy. The original file should still exist.",
        recoverable=False,
        category="backup",
    ),
    ".old": FileTypeInfo(
        extension=".old",
        name="Old File",
        description="Renamed old version of a file, often created during updates.",
        typical_owner="OS / Apps",
        safe_to_delete=True,
        risk=RiskLevel.LOW,
        impact="Lose the old version. Current version should be unaffected.",
        recoverable=False,
        category="backup",
    ),
    ".backup": FileTypeInfo(
        extension=".backup",
        name="Backup File",
        description="Explicit backup copy.",
        typical_owner="User / Apps",
        safe_to_delete=True,
        risk=RiskLevel.LOW,
        impact="Lose the backup. Original should exist.",
        recoverable=False,
        category="backup",
    ),

    # --- Installer files ---
    ".msi": FileTypeInfo(
        extension=".msi",
        name="Windows Installer Package",
        description="Microsoft Installer package for installing software.",
        typical_owner="Software vendors",
        safe_to_delete=True,
        risk=RiskLevel.LOW,
        impact="Cannot reinstall the same version without re-downloading.",
        recoverable=True,
        category="installer",
    ),
    ".exe": FileTypeInfo(
        extension=".exe",
        name="Executable Program",
        description="Windows executable program. Could be an application or installer.",
        typical_owner="Apps / User",
        safe_to_delete=False,
        risk=RiskLevel.HIGH,
        impact="May break an installed application if it is the main executable.",
        recoverable=True,
        category="program",
    ),
    ".dll": FileTypeInfo(
        extension=".dll",
        name="Dynamic Link Library",
        description="Shared library used by Windows programs.",
        typical_owner="OS / Apps",
        safe_to_delete=False,
        risk=RiskLevel.CRITICAL,
        impact="May break multiple applications. Never delete unless certain.",
        recoverable=True,
        category="program",
    ),

    # --- Documents ---
    ".doc": FileTypeInfo(
        extension=".doc",
        name="Word Document (Legacy)",
        description="Microsoft Word document in legacy format.",
        typical_owner="User",
        safe_to_delete=False,
        risk=RiskLevel.HIGH,
        impact="Permanent loss of document content.",
        recoverable=False,
        category="document",
    ),
    ".docx": FileTypeInfo(
        extension=".docx",
        name="Word Document",
        description="Microsoft Word document (Office Open XML format).",
        typical_owner="User",
        safe_to_delete=False,
        risk=RiskLevel.HIGH,
        impact="Permanent loss of document content.",
        recoverable=False,
        category="document",
    ),
    ".xls": FileTypeInfo(
        extension=".xls",
        name="Excel Spreadsheet (Legacy)",
        description="Microsoft Excel spreadsheet in legacy format.",
        typical_owner="User",
        safe_to_delete=False,
        risk=RiskLevel.HIGH,
        impact="Permanent loss of spreadsheet data.",
        recoverable=False,
        category="document",
    ),
    ".xlsx": FileTypeInfo(
        extension=".xlsx",
        name="Excel Spreadsheet",
        description="Microsoft Excel spreadsheet.",
        typical_owner="User",
        safe_to_delete=False,
        risk=RiskLevel.HIGH,
        impact="Permanent loss of spreadsheet data.",
        recoverable=False,
        category="document",
    ),
    ".pdf": FileTypeInfo(
        extension=".pdf",
        name="PDF Document",
        description="Portable Document Format file.",
        typical_owner="User / Web",
        safe_to_delete=False,
        risk=RiskLevel.HIGH,
        impact="Permanent loss of document.",
        recoverable=False,
        category="document",
    ),
    ".txt": FileTypeInfo(
        extension=".txt",
        name="Text File",
        description="Plain text file.",
        typical_owner="User / Apps",
        safe_to_delete=False,
        risk=RiskLevel.MEDIUM,
        impact="Permanent loss of text content.",
        recoverable=False,
        category="document",
    ),

    # --- Media files ---
    ".jpg": FileTypeInfo(
        extension=".jpg",
        name="JPEG Image",
        description="Compressed image file (photos).",
        typical_owner="User / Camera",
        safe_to_delete=False,
        risk=RiskLevel.HIGH,
        impact="Permanent loss of image.",
        recoverable=False,
        category="media",
    ),
    ".jpeg": FileTypeInfo(
        extension=".jpeg",
        name="JPEG Image",
        description="Compressed image file (photos).",
        typical_owner="User / Camera",
        safe_to_delete=False,
        risk=RiskLevel.HIGH,
        impact="Permanent loss of image.",
        recoverable=False,
        category="media",
    ),
    ".png": FileTypeInfo(
        extension=".png",
        name="PNG Image",
        description="Lossless image format, often used for screenshots and graphics.",
        typical_owner="User / Apps",
        safe_to_delete=False,
        risk=RiskLevel.HIGH,
        impact="Permanent loss of image.",
        recoverable=False,
        category="media",
    ),
    ".gif": FileTypeInfo(
        extension=".gif",
        name="GIF Image",
        description="Animated or static image.",
        typical_owner="User / Web",
        safe_to_delete=False,
        risk=RiskLevel.MEDIUM,
        impact="Permanent loss of image.",
        recoverable=False,
        category="media",
    ),
    ".mp4": FileTypeInfo(
        extension=".mp4",
        name="MP4 Video",
        description="Compressed video file.",
        typical_owner="User / Camera",
        safe_to_delete=False,
        risk=RiskLevel.HIGH,
        impact="Permanent loss of video.",
        recoverable=False,
        category="media",
    ),
    ".mp3": FileTypeInfo(
        extension=".mp3",
        name="MP3 Audio",
        description="Compressed audio file.",
        typical_owner="User / Music apps",
        safe_to_delete=False,
        risk=RiskLevel.MEDIUM,
        impact="Permanent loss of audio. May be re-downloadable from music service.",
        recoverable=True,
        category="media",
    ),
    ".wav": FileTypeInfo(
        extension=".wav",
        name="WAV Audio",
        description="Uncompressed audio file.",
        typical_owner="User / Recording apps",
        safe_to_delete=False,
        risk=RiskLevel.HIGH,
        impact="Permanent loss of audio recording.",
        recoverable=False,
        category="media",
    ),

    # --- Code / Development ---
    ".py": FileTypeInfo(
        extension=".py",
        name="Python Script",
        description="Python source code file.",
        typical_owner="Developer",
        safe_to_delete=False,
        risk=RiskLevel.HIGH,
        impact="Loss of source code.",
        recoverable=False,
        category="code",
    ),
    ".js": FileTypeInfo(
        extension=".js",
        name="JavaScript File",
        description="JavaScript source code.",
        typical_owner="Developer / Web",
        safe_to_delete=False,
        risk=RiskLevel.HIGH,
        impact="Loss of source code.",
        recoverable=False,
        category="code",
    ),
    ".ts": FileTypeInfo(
        extension=".ts",
        name="TypeScript File",
        description="TypeScript source code.",
        typical_owner="Developer",
        safe_to_delete=False,
        risk=RiskLevel.HIGH,
        impact="Loss of source code.",
        recoverable=False,
        category="code",
    ),
    ".json": FileTypeInfo(
        extension=".json",
        name="JSON Data",
        description="JSON configuration or data file.",
        typical_owner="Apps / Developer",
        safe_to_delete=False,
        risk=RiskLevel.MEDIUM,
        impact="May break app configuration or lose data.",
        recoverable=False,
        category="data",
    ),
    ".xml": FileTypeInfo(
        extension=".xml",
        name="XML Data",
        description="XML configuration or data file.",
        typical_owner="Apps / OS",
        safe_to_delete=False,
        risk=RiskLevel.MEDIUM,
        impact="May break app configuration.",
        recoverable=False,
        category="data",
    ),
    ".yaml": FileTypeInfo(
        extension=".yaml",
        name="YAML Config",
        description="YAML configuration file.",
        typical_owner="Developer / Apps",
        safe_to_delete=False,
        risk=RiskLevel.MEDIUM,
        impact="May break configuration.",
        recoverable=False,
        category="data",
    ),
    ".yml": FileTypeInfo(
        extension=".yml",
        name="YAML Config",
        description="YAML configuration file.",
        typical_owner="Developer / Apps",
        safe_to_delete=False,
        risk=RiskLevel.MEDIUM,
        impact="May break configuration.",
        recoverable=False,
        category="data",
    ),

    # --- Archives ---
    ".zip": FileTypeInfo(
        extension=".zip",
        name="ZIP Archive",
        description="Compressed archive file.",
        typical_owner="User / Apps",
        safe_to_delete=True,
        risk=RiskLevel.LOW,
        impact="Lose the archive. Contents may or may not exist elsewhere.",
        recoverable=True,
        category="archive",
    ),
    ".rar": FileTypeInfo(
        extension=".rar",
        name="RAR Archive",
        description="RAR compressed archive.",
        typical_owner="User",
        safe_to_delete=True,
        risk=RiskLevel.LOW,
        impact="Lose the archive.",
        recoverable=True,
        category="archive",
    ),
    ".7z": FileTypeInfo(
        extension=".7z",
        name="7-Zip Archive",
        description="7-Zip compressed archive.",
        typical_owner="User",
        safe_to_delete=True,
        risk=RiskLevel.LOW,
        impact="Lose the archive.",
        recoverable=True,
        category="archive",
    ),
    ".tar": FileTypeInfo(
        extension=".tar",
        name="TAR Archive",
        description="Tape archive file (often compressed with gzip).",
        typical_owner="Developer / Linux",
        safe_to_delete=True,
        risk=RiskLevel.LOW,
        impact="Lose the archive.",
        recoverable=True,
        category="archive",
    ),
    ".gz": FileTypeInfo(
        extension=".gz",
        name="Gzip Archive",
        description="Gzip compressed file.",
        typical_owner="Developer / Linux",
        safe_to_delete=True,
        risk=RiskLevel.LOW,
        impact="Lose the compressed file.",
        recoverable=True,
        category="archive",
    ),

    # --- Database ---
    ".db": FileTypeInfo(
        extension=".db",
        name="Database File",
        description="SQLite or other database file.",
        typical_owner="Apps",
        safe_to_delete=False,
        risk=RiskLevel.HIGH,
        impact="May lose application data permanently.",
        recoverable=False,
        category="database",
    ),
    ".sqlite": FileTypeInfo(
        extension=".sqlite",
        name="SQLite Database",
        description="SQLite database file.",
        typical_owner="Apps",
        safe_to_delete=False,
        risk=RiskLevel.HIGH,
        impact="May lose application data permanently.",
        recoverable=False,
        category="database",
    ),
    ".mdb": FileTypeInfo(
        extension=".mdb",
        name="Access Database (Legacy)",
        description="Microsoft Access database in legacy format.",
        typical_owner="User / Office",
        safe_to_delete=False,
        risk=RiskLevel.HIGH,
        impact="Permanent loss of database.",
        recoverable=False,
        category="database",
    ),

    # --- System ---
    ".sys": FileTypeInfo(
        extension=".sys",
        name="System Driver",
        description="Windows system driver file.",
        typical_owner="Windows",
        safe_to_delete=False,
        risk=RiskLevel.CRITICAL,
        impact="May crash the system or break hardware.",
        recoverable=True,
        category="system",
    ),
    ".inf": FileTypeInfo(
        extension=".inf",
        name="Setup Information",
        description="Windows driver installation information file.",
        typical_owner="Windows / Hardware vendors",
        safe_to_delete=False,
        risk=RiskLevel.MEDIUM,
        impact="May prevent driver reinstallation.",
        recoverable=True,
        category="system",
    ),
}


# ---------------------------------------------------------------------------
# File analysis result
# ---------------------------------------------------------------------------

@dataclass
class FileAnalysis:
    """Result of analyzing a single file."""
    path: str
    size: int
    extension: str
    file_type_info: Optional[FileTypeInfo]
    risk: RiskLevel
    risk_reason: str
    category: str
    can_delete: bool
    impact: str
    age_days: float          # Days since last access
    last_accessed: float     # Timestamp
    last_modified: float     # Timestamp
    score: int = 0           # 0-100, higher = more recommended to clean


# ---------------------------------------------------------------------------
# Smart Analyzer
# ---------------------------------------------------------------------------

class SmartAnalyzer:
    """Analyzes files with deep knowledge of file types and deletion risk."""

    def __init__(self):
        self.knowledge = FILE_TYPE_KNOWLEDGE

    def analyze_file(
        self,
        path: str,
        size: int,
        extension: str,
        accessed: float,
        modified: float,
        is_system: bool = False,
        is_hidden: bool = False,
    ) -> FileAnalysis:
        """Analyze a single file and return detailed analysis."""
        ext_lower = extension.lower()
        file_type_info = self.knowledge.get(ext_lower)
        now = time.time()
        age_days = (now - accessed) / 86400 if accessed > 0 else 0

        # Determine risk
        risk, risk_reason = self._assess_risk(
            file_type_info, ext_lower, size, age_days, is_system, is_hidden
        )

        # Determine category
        category = self._determine_category(file_type_info, ext_lower)

        # Determine if safe to delete
        can_delete = self._can_delete(file_type_info, is_system, age_days, size)

        # Determine impact
        impact = self._get_impact(file_type_info, ext_lower)

        # Calculate cleanup score (higher = more recommended to clean)
        score = self._calculate_score(risk, age_days, size, file_type_info)

        return FileAnalysis(
            path=path,
            size=size,
            extension=ext_lower,
            file_type_info=file_type_info,
            risk=risk,
            risk_reason=risk_reason,
            category=category,
            can_delete=can_delete,
            impact=impact,
            age_days=age_days,
            last_accessed=accessed,
            last_modified=modified,
            score=score,
        )

    def get_type_info(self, extension: str) -> Optional[FileTypeInfo]:
        """Look up knowledge about a file extension."""
        return self.knowledge.get(extension.lower())

    def get_risk_color(self, risk: RiskLevel) -> str:
        """Return a hex color for the given risk level (for UI)."""
        return {
            RiskLevel.SAFE: "#4CAF50",      # Green
            RiskLevel.LOW: "#8BC34A",       # Light green
            RiskLevel.MEDIUM: "#FFC107",    # Amber
            RiskLevel.HIGH: "#FF5722",      # Deep orange
            RiskLevel.CRITICAL: "#F44336",  # Red
        }.get(risk, "#9E9E9E")

    def get_risk_label(self, risk: RiskLevel) -> str:
        """Return a human-readable label for the risk level."""
        return {
            RiskLevel.SAFE: "Safe",
            RiskLevel.LOW: "Low Risk",
            RiskLevel.MEDIUM: "Medium Risk",
            RiskLevel.HIGH: "High Risk",
            RiskLevel.CRITICAL: "Critical",
        }.get(risk, "Unknown")

    def get_type_name(self, extension: str) -> str:
        """Return a human-readable name for the file type."""
        info = self.knowledge.get(extension.lower())
        if info:
            return info.name
        ext = extension.lstrip(".")
        return f"{ext.upper()} File" if ext else "Unknown File"

    def generate_report(self, analyses: List[FileAnalysis]) -> Dict:
        """Generate a summary report from a list of file analyses."""
        total = len(analyses)
        total_size = sum(a.size for a in analyses)

        by_risk: Dict[RiskLevel, List[FileAnalysis]] = {}
        by_category: Dict[str, List[FileAnalysis]] = {}
        safe_to_clean: List[FileAnalysis] = []
        high_risk: List[FileAnalysis] = []

        for a in analyses:
            by_risk.setdefault(a.risk, []).append(a)
            by_category.setdefault(a.category, []).append(a)
            if a.can_delete and a.risk in (RiskLevel.SAFE, RiskLevel.LOW):
                safe_to_clean.append(a)
            if a.risk in (RiskLevel.HIGH, RiskLevel.CRITICAL):
                high_risk.append(a)

        safe_to_clean.sort(key=lambda x: x.score, reverse=True)
        safe_size = sum(a.size for a in safe_to_clean)

        return {
            "total_files": total,
            "total_size": total_size,
            "by_risk": {r.value: len(files) for r, files in by_risk.items()},
            "by_category": {c: len(files) for c, files in by_category.items()},
            "safe_to_clean_count": len(safe_to_clean),
            "safe_to_clean_size": safe_size,
            "high_risk_count": len(high_risk),
            "top_cleanable": safe_to_clean[:20],
            "high_risk_files": high_risk[:10],
        }

    # ------------------------------------------------------------------
    # Internal methods
    # ------------------------------------------------------------------

    def _assess_risk(
        self,
        info: Optional[FileTypeInfo],
        ext: str,
        size: int,
        age_days: float,
        is_system: bool,
        is_hidden: bool,
    ) -> Tuple[RiskLevel, str]:
        """Assess the risk of deleting this file."""
        # System files are always critical
        if is_system:
            return RiskLevel.CRITICAL, "System file -- never delete"

        # DLL/SYS are critical
        if ext in (".dll", ".sys", ".drv"):
            return RiskLevel.CRITICAL, f"System library ({ext}) -- may break Windows"

        # Use knowledge base
        if info:
            base_risk = info.risk
        else:
            # Unknown extension -- assess by context
            base_risk = RiskLevel.MEDIUM

        # Adjust based on age
        if age_days > 365:
            if base_risk == RiskLevel.MEDIUM:
                return RiskLevel.LOW, f"Old file ({int(age_days)} days) -- likely unused"
            if base_risk == RiskLevel.HIGH:
                return RiskLevel.MEDIUM, f"Old file ({int(age_days)} days) -- but content may matter"

        # Adjust based on location (temp dirs = safer)
        return base_risk, self._risk_reason(info, ext)

    def _risk_reason(self, info: Optional[FileTypeInfo], ext: str) -> str:
        """Generate a risk explanation."""
        if info:
            return info.description
        ext_clean = ext.lstrip(".")
        return f"Unknown file type (.{ext_clean}) -- review before deleting"

    def _determine_category(self, info: Optional[FileTypeInfo], ext: str) -> str:
        """Determine the file category."""
        if info:
            return info.category

        # Fallback heuristics
        media_exts = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".mp4", ".mp3", ".wav", ".avi", ".mkv"}
        doc_exts = {".doc", ".docx", ".pdf", ".txt", ".rtf"}
        code_exts = {".py", ".js", ".ts", ".java", ".cpp", ".c", ".h", ".go", ".rs"}

        if ext in media_exts:
            return "media"
        if ext in doc_exts:
            return "document"
        if ext in code_exts:
            return "code"
        return "other"

    def _can_delete(
        self,
        info: Optional[FileTypeInfo],
        is_system: bool,
        age_days: float,
        size: int,
    ) -> bool:
        """Determine if the file is safe to delete."""
        if is_system:
            return False
        if info and info.safe_to_delete:
            return True
        # Large old files of unknown type -- ask user
        if age_days > 90 and size > 50 * 1024 * 1024:
            return True  # User should decide
        return False

    def _get_impact(self, info: Optional[FileTypeInfo], ext: str) -> str:
        """Describe the impact of deleting this file."""
        if info:
            return info.impact
        return "Unknown impact -- review before deleting"

    def _calculate_score(
        self,
        risk: RiskLevel,
        age_days: float,
        size: int,
        info: Optional[FileTypeInfo],
    ) -> int:
        """Calculate a cleanup recommendation score (0-100)."""
        score = 50  # Base

        # Risk adjustment
        risk_adj = {
            RiskLevel.SAFE: 40,
            RiskLevel.LOW: 20,
            RiskLevel.MEDIUM: 0,
            RiskLevel.HIGH: -30,
            RiskLevel.CRITICAL: -100,
        }
        score += risk_adj.get(risk, 0)

        # Age adjustment (older = more recommended to clean)
        if age_days > 365:
            score += 20
        elif age_days > 90:
            score += 10
        elif age_days < 7:
            score -= 10

        # Size adjustment (larger = more worth cleaning)
        if size > 100 * 1024 * 1024:   # > 100MB
            score += 15
        elif size > 10 * 1024 * 1024:  # > 10MB
            score += 5

        return max(0, min(100, score))
