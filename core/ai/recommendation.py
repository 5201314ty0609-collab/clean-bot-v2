"""
CleanBot v2.0 — 智能推荐引擎

根据用户使用习惯和系统状态，智能推荐清理和优化方案。
"""

import os
import sys
import time
import json
import psutil
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict


@dataclass
class UserProfile:
    """用户画像"""
    user_id: str
    frequent_apps: List[str] = field(default_factory=list)
    infrequent_apps: List[str] = field(default_factory=list)
    disk_usage_pattern: Dict = field(default_factory=dict)
    cleanup_frequency: str = "monthly"  # daily, weekly, monthly, rarely
    risk_tolerance: str = "medium"  # low, medium, high
    last_cleanup: Optional[float] = None


@dataclass
class Recommendation:
    """推荐"""
    id: str
    title: str
    description: str
    category: str  # cleanup, optimization, maintenance
    priority: int  # 1-10, 10 is highest
    risk_level: str  # low, medium, high
    estimated_savings: int  # bytes
    action: str  # 具体操作
    details: Dict = field(default_factory=dict)
    is_accepted: bool = False
    is_rejected: bool = False


@dataclass
class Prediction:
    """预测"""
    metric: str  # disk_space, memory_usage, etc.
    current_value: float
    predicted_value: float
    prediction_date: float
    confidence: float  # 0-1
    trend: str  # increasing, decreasing, stable


class RecommendationEngine:
    """推荐引擎"""

    def __init__(self, data_dir: str = None):
        self.data_dir = data_dir or os.path.expanduser("~\\CleanBot\\data")
        self.user_profile: Optional[UserProfile] = None
        self.recommendations: List[Recommendation] = []
        self.predictions: List[Prediction] = []

        # 加载用户画像
        self._load_user_profile()

    def _load_user_profile(self):
        """加载用户画像"""
        profile_path = os.path.join(self.data_dir, "user_profile.json")

        if os.path.exists(profile_path):
            try:
                with open(profile_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.user_profile = UserProfile(**data)
            except Exception:
                self.user_profile = UserProfile(user_id="default")
        else:
            self.user_profile = UserProfile(user_id="default")

    def _save_user_profile(self):
        """保存用户画像"""
        os.makedirs(self.data_dir, exist_ok=True)
        profile_path = os.path.join(self.data_dir, "user_profile.json")

        with open(profile_path, "w", encoding="utf-8") as f:
            json.dump(self.user_profile.__dict__, f, indent=2, ensure_ascii=False)

    def generate_recommendations(self) -> List[Recommendation]:
        """生成推荐"""
        self.recommendations = []

        # 基于系统状态推荐
        self.recommendations.extend(self._recommend_by_system_state())

        # 基于使用习惯推荐
        self.recommendations.extend(self._recommend_by_usage_pattern())

        # 基于历史数据推荐
        self.recommendations.extend(self._recommend_by_history())

        # 基于时间推荐
        self.recommendations.extend(self._recommend_by_time())

        # 去重
        self.recommendations = self._deduplicate_recommendations(self.recommendations)

        # 按优先级排序
        self.recommendations.sort(key=lambda r: r.priority, reverse=True)

        return self.recommendations

    def _recommend_by_system_state(self) -> List[Recommendation]:
        """基于系统状态推荐"""
        recommendations = []

        # 磁盘空间推荐
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                drive = partition.device

                if usage.percent > 90:
                    recommendations.append(Recommendation(
                        id=f"disk_space_{drive}",
                        title=f"清理磁盘 {drive}",
                        description=f"磁盘 {drive} 使用率 {usage.percent:.1f}%，建议清理空间",
                        category="cleanup",
                        priority=9,
                        risk_level="low",
                        estimated_savings=usage.used * 0.1,  # 假设可以清理 10%
                        action="clean_disk",
                        details={"drive": drive, "percent": usage.percent},
                    ))
                elif usage.percent > 80:
                    recommendations.append(Recommendation(
                        id=f"disk_space_{drive}",
                        title=f"清理磁盘 {drive}",
                        description=f"磁盘 {drive} 使用率 {usage.percent:.1f}%，建议清理空间",
                        category="cleanup",
                        priority=7,
                        risk_level="low",
                        estimated_savings=usage.used * 0.05,  # 假设可以清理 5%
                        action="clean_disk",
                        details={"drive": drive, "percent": usage.percent},
                    ))

            except (PermissionError, OSError):
                pass

        # 内存推荐
        memory = psutil.virtual_memory()
        if memory.percent > 85:
            recommendations.append(Recommendation(
                id="memory_usage",
                title="释放内存",
                description=f"内存使用率 {memory.percent:.1f}%，建议关闭不必要的程序",
                category="optimization",
                priority=8,
                risk_level="low",
                estimated_savings=memory.available,
                action="free_memory",
                details={"percent": memory.percent},
            ))

        # CPU 推荐
        cpu_percent = psutil.cpu_percent(interval=1)
        if cpu_percent > 80:
            recommendations.append(Recommendation(
                id="cpu_usage",
                title="降低 CPU 使用率",
                description=f"CPU 使用率 {cpu_percent:.1f}%，建议检查占用 CPU 的程序",
                category="optimization",
                priority=7,
                risk_level="low",
                estimated_savings=0,
                action="reduce_cpu",
                details={"percent": cpu_percent},
            ))

        return recommendations

    def _recommend_by_usage_pattern(self) -> List[Recommendation]:
        """基于使用习惯推荐"""
        recommendations = []

        # 分析常用应用
        frequent_apps = self._analyze_frequent_apps()

        # 推荐清理不常用应用的缓存
        for app_name, cache_size in self._get_app_cache_sizes().items():
            if app_name not in frequent_apps and cache_size > 100 * 1024 * 1024:  # > 100MB
                recommendations.append(Recommendation(
                    id=f"app_cache_{app_name}",
                    title=f"清理 {app_name} 缓存",
                    description=f"{app_name} 缓存占用 {self._format_size(cache_size)}",
                    category="cleanup",
                    priority=6,
                    risk_level="low",
                    estimated_savings=cache_size,
                    action="clean_app_cache",
                    details={"app": app_name, "size": cache_size},
                ))

        return recommendations

    def _recommend_by_history(self) -> List[Recommendation]:
        """基于历史数据推荐"""
        recommendations = []

        # 检查上次清理时间
        if self.user_profile.last_cleanup:
            days_since_cleanup = (time.time() - self.user_profile.last_cleanup) / 86400

            if days_since_cleanup > 30:
                recommendations.append(Recommendation(
                    id="regular_cleanup",
                    title="定期清理提醒",
                    description=f"距离上次清理已过 {int(days_since_cleanup)} 天，建议进行定期清理",
                    category="maintenance",
                    priority=5,
                    risk_level="low",
                    estimated_savings=0,
                    action="regular_cleanup",
                    details={"days_since": days_since_cleanup},
                ))

        return recommendations

    def _recommend_by_time(self) -> List[Recommendation]:
        """基于时间推荐"""
        recommendations = []

        # 检查是否是月初
        if datetime.now().day <= 7:
            recommendations.append(Recommendation(
                id="monthly_cleanup",
                title="月度清理",
                description="月初是进行系统清理的好时机",
                category="maintenance",
                priority=4,
                risk_level="low",
                estimated_savings=0,
                action="monthly_cleanup",
            ))

        # 检查是否是周一
        if datetime.now().weekday() == 0:
            recommendations.append(Recommendation(
                id="weekly_cleanup",
                title="周度清理",
                description="周一进行系统清理，保持系统流畅",
                category="maintenance",
                priority=3,
                risk_level="low",
                estimated_savings=0,
                action="weekly_cleanup",
            ))

        return recommendations

    def _deduplicate_recommendations(self, recommendations: List[Recommendation]) -> List[Recommendation]:
        """去重推荐"""
        seen_ids = set()
        unique = []

        for rec in recommendations:
            if rec.id not in seen_ids:
                seen_ids.add(rec.id)
                unique.append(rec)

        return unique

    def _analyze_frequent_apps(self) -> List[str]:
        """分析常用应用"""
        # 简化实现：返回用户画像中的常用应用
        return self.user_profile.frequent_apps

    def _get_app_cache_sizes(self) -> Dict[str, int]:
        """获取应用缓存大小"""
        cache_sizes = {}

        # 常见应用缓存路径
        cache_paths = {
            "Chrome": os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data\Default\Cache"),
            "Firefox": os.path.expandvars(r"%LOCALAPPDATA%\Mozilla\Firefox\Profiles"),
            "Edge": os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\Cache"),
            "VSCode": os.path.expandvars(r"%APPDATA%\Code\Cache"),
            "Slack": os.path.expandvars(r"%APPDATA%\Slack\Cache"),
            "Discord": os.path.expandvars(r"%APPDATA%\discord\Cache"),
        }

        for app_name, cache_path in cache_paths.items():
            if os.path.exists(cache_path):
                try:
                    total_size = 0
                    for dirpath, dirnames, filenames in os.walk(cache_path):
                        for filename in filenames:
                            filepath = os.path.join(dirpath, filename)
                            try:
                                total_size += os.path.getsize(filepath)
                            except (OSError, PermissionError):
                                pass
                    cache_sizes[app_name] = total_size
                except (OSError, PermissionError):
                    pass

        return cache_sizes

    def _format_size(self, size_bytes: int) -> str:
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} PB"

    def accept_recommendation(self, recommendation_id: str):
        """接受推荐"""
        for rec in self.recommendations:
            if rec.id == recommendation_id:
                rec.is_accepted = True
                break

    def reject_recommendation(self, recommendation_id: str):
        """拒绝推荐"""
        for rec in self.recommendations:
            if rec.id == recommendation_id:
                rec.is_rejected = True
                break

    def update_user_profile(self, updates: Dict):
        """更新用户画像"""
        for key, value in updates.items():
            if hasattr(self.user_profile, key):
                setattr(self.user_profile, key, value)

        self._save_user_profile()

    def get_predictions(self) -> List[Prediction]:
        """获取预测"""
        predictions = []

        # 磁盘空间预测
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                drive = partition.device

                # 简单的线性预测（实际应该用更复杂的算法）
                # 假设每天增长 0.1%
                daily_growth = usage.used * 0.001
                days_until_full = usage.free / daily_growth if daily_growth > 0 else float('inf')

                predictions.append(Prediction(
                    metric=f"disk_space_{drive}",
                    current_value=usage.percent,
                    predicted_value=min(100, usage.percent + (daily_growth / usage.total * 100 * 30)),
                    prediction_date=time.time() + 30 * 86400,
                    confidence=0.7,
                    trend="increasing" if daily_growth > 0 else "stable",
                ))

            except (PermissionError, OSError):
                pass

        # 内存预测
        memory = psutil.virtual_memory()
        predictions.append(Prediction(
            metric="memory_usage",
            current_value=memory.percent,
            predicted_value=memory.percent,  # 内存使用通常波动较大
            prediction_date=time.time() + 86400,
            confidence=0.5,
            trend="stable",
        ))

        self.predictions = predictions
        return predictions

    def get_summary(self) -> Dict:
        """获取摘要"""
        return {
            "total_recommendations": len(self.recommendations),
            "accepted": len([r for r in self.recommendations if r.is_accepted]),
            "rejected": len([r for r in self.recommendations if r.is_rejected]),
            "pending": len([r for r in self.recommendations if not r.is_accepted and not r.is_rejected]),
            "total_savings": sum(r.estimated_savings for r in self.recommendations if r.is_accepted),
            "predictions": len(self.predictions),
        }


def main():
    """CLI 入口"""
    print("=" * 60)
    print("CleanBot v2.0 — 智能推荐引擎")
    print("=" * 60)

    engine = RecommendationEngine()

    print("\n正在生成推荐...")
    recommendations = engine.generate_recommendations()

    print(f"\n生成了 {len(recommendations)} 个推荐:")
    print("-" * 60)

    for i, rec in enumerate(recommendations, 1):
        priority_icon = "🔴" if rec.priority >= 8 else "🟡" if rec.priority >= 5 else "🟢"
        print(f"\n{i}. {priority_icon} {rec.title}")
        print(f"   {rec.description}")
        print(f"   类别: {rec.category}")
        print(f"   优先级: {rec.priority}/10")
        print(f"   风险: {rec.risk_level}")
        if rec.estimated_savings > 0:
            print(f"   预计节省: {engine._format_size(rec.estimated_savings)}")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
