"""
CleanBot v2.0 -- Smart File Analyzer

Provides deep file analysis with:
- File type knowledge base (loaded from config/file_types.json)
- Deletion impact assessment
- Risk level classification
- Intelligent categorization
"""

import json
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
# File type knowledge
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


def _load_knowledge() -> Dict[str, FileTypeInfo]:
    """Load file type knowledge base from config JSON.

    Returns an empty dict on any load error (missing file, bad JSON, bad
    enum values) so the application can still start without the knowledge
    base — file analysis will fall back to heuristics.
    """
    config_paths = [
        Path(__file__).parent.parent.parent / "config" / "file_types.json",
        Path("config/file_types.json"),
    ]
    for config_path in config_paths:
        if not config_path.exists():
            continue
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                raw = json.load(f)
            return {
                ext: FileTypeInfo(
                    extension=info["extension"],
                    name=info["name"],
                    description=info["description"],
                    typical_owner=info["typical_owner"],
                    safe_to_delete=info["safe_to_delete"],
                    risk=RiskLevel(info["risk"]),
                    impact=info["impact"],
                    recoverable=info["recoverable"],
                    category=info["category"],
                )
                for ext, info in raw.items()
            }
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            print(
                f"Warning: failed to load {config_path}: {e}",
                file=sys.stderr,
            )
    # Fallback: empty knowledge base (heuristics still work)
    return {}


# Module-level knowledge base
FILE_TYPE_KNOWLEDGE: Dict[str, FileTypeInfo] = _load_knowledge()


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

    # Risk → UI color mapping
    RISK_COLORS = {
        RiskLevel.SAFE: "#4CAF50",
        RiskLevel.LOW: "#8BC34A",
        RiskLevel.MEDIUM: "#FFC107",
        RiskLevel.HIGH: "#FF5722",
        RiskLevel.CRITICAL: "#F44336",
    }
    RISK_LABELS = {
        RiskLevel.SAFE: "Safe",
        RiskLevel.LOW: "Low Risk",
        RiskLevel.MEDIUM: "Medium Risk",
        RiskLevel.HIGH: "High Risk",
        RiskLevel.CRITICAL: "Critical",
    }

    # Fallback heuristics for unknown extensions
    _MEDIA_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".mp4", ".mp3", ".wav", ".avi", ".mkv"}
    _DOC_EXTS = {".doc", ".docx", ".pdf", ".txt", ".rtf"}
    _CODE_EXTS = {".py", ".js", ".ts", ".java", ".cpp", ".c", ".h", ".go", ".rs"}
    _CRITICAL_EXTS = {".dll", ".sys", ".drv"}

    def __init__(self):
        self.knowledge = FILE_TYPE_KNOWLEDGE

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

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

        risk, risk_reason = self._assess_risk(file_type_info, ext_lower, size, age_days, is_system, is_hidden)
        category = self._determine_category(file_type_info, ext_lower)
        can_delete = self._can_delete(file_type_info, is_system, age_days, size)
        impact = self._get_impact(file_type_info, ext_lower)
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

    def get_type_name(self, extension: str) -> str:
        """Return a human-readable name for the file type."""
        info = self.knowledge.get(extension.lower())
        if info:
            return info.name
        ext = extension.lstrip(".")
        return f"{ext.upper()} File" if ext else "Unknown File"

    def get_risk_color(self, risk: RiskLevel) -> str:
        """Return a hex color for the given risk level (for UI)."""
        return self.RISK_COLORS.get(risk, "#9E9E9E")

    def get_risk_label(self, risk: RiskLevel) -> str:
        """Return a human-readable label for the risk level."""
        return self.RISK_LABELS.get(risk, "Unknown")

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
        self, info: Optional[FileTypeInfo], ext: str,
        size: int, age_days: float, is_system: bool, is_hidden: bool,
    ) -> Tuple[RiskLevel, str]:
        """Assess the risk of deleting this file."""
        if is_system:
            return RiskLevel.CRITICAL, "System file -- never delete"

        if ext in self._CRITICAL_EXTS:
            return RiskLevel.CRITICAL, f"System library ({ext}) -- may break Windows"

        base_risk = info.risk if info else RiskLevel.MEDIUM

        # Age adjustment
        if age_days > 365:
            if base_risk == RiskLevel.MEDIUM:
                return RiskLevel.LOW, f"Old file ({int(age_days)} days) -- likely unused"
            if base_risk == RiskLevel.HIGH:
                return RiskLevel.MEDIUM, f"Old file ({int(age_days)} days) -- but content may matter"

        reason = info.description if info else f"Unknown file type (.{ext.lstrip('.')}) -- review before deleting"
        return base_risk, reason

    def _determine_category(self, info: Optional[FileTypeInfo], ext: str) -> str:
        """Determine the file category."""
        if info:
            return info.category
        if ext in self._MEDIA_EXTS:
            return "media"
        if ext in self._DOC_EXTS:
            return "document"
        if ext in self._CODE_EXTS:
            return "code"
        return "other"

    def _can_delete(
        self, info: Optional[FileTypeInfo],
        is_system: bool, age_days: float, size: int,
    ) -> bool:
        """Determine if the file is safe to delete."""
        if is_system:
            return False
        if info and info.safe_to_delete:
            return True
        # Large old files — flag for user review
        if age_days > 90 and size > 50 * 1024 * 1024:
            return True
        return False

    def _get_impact(self, info: Optional[FileTypeInfo], ext: str) -> str:
        """Describe the impact of deleting this file."""
        return info.impact if info else "Unknown impact -- review before deleting"

    def _calculate_score(
        self, risk: RiskLevel, age_days: float,
        size: int, info: Optional[FileTypeInfo],
    ) -> int:
        """Calculate a cleanup recommendation score (0-100)."""
        score = 50
        score += {RiskLevel.SAFE: 40, RiskLevel.LOW: 20, RiskLevel.MEDIUM: 0,
                   RiskLevel.HIGH: -30, RiskLevel.CRITICAL: -100}.get(risk, 0)

        if age_days > 365:
            score += 20
        elif age_days > 90:
            score += 10
        elif age_days < 7:
            score -= 10

        if size > 100 * 1024 * 1024:
            score += 15
        elif size > 10 * 1024 * 1024:
            score += 5

        return max(0, min(100, score))
