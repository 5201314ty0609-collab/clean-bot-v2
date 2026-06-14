"""
CleanBot v2.0 — 磁盘监控器

实时监控磁盘使用情况，预测趋势，自动告警。
"""

import os
import sys
import time
import json
import psutil
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import deque
import threading


@dataclass
class DiskUsage:
    """磁盘使用情况"""
    drive: str
    total: int
    used: int
    free: int
    percent: float
    timestamp: float


@dataclass
class DiskTrend:
    """磁盘使用趋势"""
    drive: str
    slope: float  # 每天变化量 (bytes)
    prediction_days: int  # 预计几天后满
    will_full_soon: bool  # 是否即将满
    trend_direction: str  # increasing, decreasing, stable


@dataclass
class DiskAlert:
    """磁盘告警"""
    drive: str
    alert_type: str  # low_space, high_usage, rapid_growth
    message: str
    severity: str  # low, medium, high, critical
    timestamp: float
    is_active: bool = True


class DiskMonitor:
    """磁盘监控器"""

    def __init__(self, history_size: int = 1000):
        self.history_size = history_size
        self.history: Dict[str, deque] = {}  # drive -> deque of DiskUsage
        self.alerts: List[DiskAlert] = []
        self.is_monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.lock = threading.Lock()

        # 告警阈值
        self.alert_thresholds = {
            "low_space_percent": 90,
            "critical_space_percent": 95,
            "rapid_growth_mb_per_hour": 100,
        }

    def start_monitoring(self, interval: int = 60):
        """开始监控"""
        if self.is_monitoring:
            return

        self.is_monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            args=(interval,),
            daemon=True,
        )
        self.monitor_thread.start()

    def stop_monitoring(self):
        """停止监控"""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)

    def _monitor_loop(self, interval: int):
        """监控循环"""
        while self.is_monitoring:
            try:
                self._collect_disk_usage()
                self._check_alerts()
                time.sleep(interval)
            except Exception as e:
                print(f"监控错误: {e}")
                time.sleep(interval)

    def _collect_disk_usage(self):
        """收集磁盘使用情况"""
        with self.lock:
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    drive = partition.device

                    if drive not in self.history:
                        self.history[drive] = deque(maxlen=self.history_size)

                    disk_usage = DiskUsage(
                        drive=drive,
                        total=usage.total,
                        used=usage.used,
                        free=usage.free,
                        percent=usage.percent,
                        timestamp=time.time(),
                    )

                    self.history[drive].append(disk_usage)

                except (PermissionError, OSError):
                    pass

    def _check_alerts(self):
        """检查告警"""
        with self.lock:
            for drive, history in self.history.items():
                if not history:
                    continue

                latest = history[-1]

                # 检查低空间
                if latest.percent >= self.alert_thresholds["critical_space_percent"]:
                    self._add_alert(
                        drive,
                        "low_space",
                        f"磁盘 {drive} 空间严重不足 ({latest.percent:.1f}%)",
                        "critical",
                    )
                elif latest.percent >= self.alert_thresholds["low_space_percent"]:
                    self._add_alert(
                        drive,
                        "low_space",
                        f"磁盘 {drive} 空间不足 ({latest.percent:.1f}%)",
                        "high",
                    )

                # 检查快速增长
                if len(history) >= 2:
                    prev = history[-2]
                    time_diff = latest.timestamp - prev.timestamp
                    if time_diff > 0:
                        growth_per_hour = (latest.used - prev.used) / time_diff * 3600
                        if growth_per_hour > self.alert_thresholds["rapid_growth_mb_per_hour"] * 1024 * 1024:
                            self._add_alert(
                                drive,
                                "rapid_growth",
                                f"磁盘 {drive} 空间快速增长 ({growth_per_hour / 1024 / 1024:.1f} MB/小时)",
                                "medium",
                            )

    def _add_alert(self, drive: str, alert_type: str, message: str, severity: str):
        """添加告警"""
        # 检查是否已有相同类型的活跃告警
        for alert in self.alerts:
            if alert.drive == drive and alert.alert_type == alert_type and alert.is_active:
                return

        alert = DiskAlert(
            drive=drive,
            alert_type=alert_type,
            message=message,
            severity=severity,
            timestamp=time.time(),
        )
        self.alerts.append(alert)

    def get_current_usage(self) -> Dict[str, DiskUsage]:
        """获取当前使用情况"""
        with self.lock:
            result = {}
            for drive, history in self.history.items():
                if history:
                    result[drive] = history[-1]
            return result

    def get_history(self, drive: str, hours: int = 24) -> List[DiskUsage]:
        """获取历史数据"""
        with self.lock:
            if drive not in self.history:
                return []

            cutoff = time.time() - hours * 3600
            return [u for u in self.history[drive] if u.timestamp >= cutoff]

    def get_trend(self, drive: str, days: int = 7) -> Optional[DiskTrend]:
        """获取使用趋势"""
        with self.lock:
            if drive not in self.history or len(self.history[drive]) < 2:
                return None

            history = list(self.history[drive])

            # 计算线性回归
            n = len(history)
            x = [i for i in range(n)]
            y = [u.used for u in history]

            # 计算斜率
            x_mean = sum(x) / n
            y_mean = sum(y) / n

            numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
            denominator = sum((x[i] - x_mean) ** 2 for i in range(n))

            if denominator == 0:
                slope = 0
            else:
                slope = numerator / denominator

            # 转换为每天变化量
            if n >= 2:
                time_span_days = (history[-1].timestamp - history[0].timestamp) / 86400
                if time_span_days > 0:
                    daily_slope = slope * (n / time_span_days)
                else:
                    daily_slope = 0
            else:
                daily_slope = 0

            # 预测几天后满
            latest = history[-1]
            if daily_slope > 0:
                days_until_full = latest.free / daily_slope
            else:
                days_until_full = float('inf')

            # 判断趋势方向
            if daily_slope > 1024 * 1024:  # > 1MB/天
                trend_direction = "increasing"
            elif daily_slope < -1024 * 1024:  # < -1MB/天
                trend_direction = "decreasing"
            else:
                trend_direction = "stable"

            return DiskTrend(
                drive=drive,
                slope=daily_slope,
                prediction_days=int(days_until_full),
                will_full_soon=days_until_full < 7,
                trend_direction=trend_direction,
            )

    def get_active_alerts(self) -> List[DiskAlert]:
        """获取活跃告警"""
        with self.lock:
            return [a for a in self.alerts if a.is_active]

    def dismiss_alert(self, drive: str, alert_type: str):
        """关闭告警"""
        with self.lock:
            for alert in self.alerts:
                if alert.drive == drive and alert.alert_type == alert_type:
                    alert.is_active = False

    def get_summary(self) -> Dict:
        """获取摘要"""
        with self.lock:
            summary = {
                "drives": {},
                "total_alerts": len(self.get_active_alerts()),
                "monitoring": self.is_monitoring,
            }

            for drive, history in self.history.items():
                if history:
                    latest = history[-1]
                    trend = self.get_trend(drive)

                    summary["drives"][drive] = {
                        "total_gb": latest.total / (1024 ** 3),
                        "used_gb": latest.used / (1024 ** 3),
                        "free_gb": latest.free / (1024 ** 3),
                        "percent": latest.percent,
                        "trend": trend.trend_direction if trend else "unknown",
                        "days_until_full": trend.prediction_days if trend else None,
                    }

            return summary


from core.utils import format_size


def main():
    """CLI 入口"""
    print("=" * 60)
    print("CleanBot v2.0 — 磁盘监控器")
    print("=" * 60)

    monitor = DiskMonitor()

    print("\n开始监控磁盘使用情况...")
    print("按 Ctrl+C 停止监控\n")

    try:
        monitor.start_monitoring(interval=10)

        while True:
            # 清屏
            os.system('cls' if os.name == 'nt' else 'clear')

            print("=" * 60)
            print("CleanBot v2.0 — 磁盘监控器")
            print("=" * 60)
            print(f"\n监控时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

            # 显示当前使用情况
            usage = monitor.get_current_usage()
            if usage:
                print("\n磁盘使用情况:")
                for drive, disk_usage in usage.items():
                    print(f"  {drive}: {format_size(disk_usage.used)} / {format_size(disk_usage.total)} "
                          f"({disk_usage.percent:.1f}%)")

            # 显示趋势
            print("\n使用趋势:")
            for drive in usage.keys():
                trend = monitor.get_trend(drive)
                if trend:
                    direction = {"increasing": "↑", "decreasing": "↓", "stable": "→"}.get(trend.trend_direction, "?")
                    print(f"  {drive}: {direction} {format_size(abs(int(trend.slope)))}/天")
                    if trend.will_full_soon:
                        print(f"    ⚠️ 预计 {trend.prediction_days} 天后磁盘满")

            # 显示告警
            alerts = monitor.get_active_alerts()
            if alerts:
                print("\n⚠️ 告警:")
                for alert in alerts:
                    severity_icon = {
                        "critical": "🔴",
                        "high": "🟠",
                        "medium": "🟡",
                        "low": "🟢",
                    }.get(alert.severity, "⚪")
                    print(f"  {severity_icon} {alert.message}")

            print("\n按 Ctrl+C 停止监控")
            time.sleep(5)

    except KeyboardInterrupt:
        print("\n\n停止监控...")
        monitor.stop_monitoring()
        print("监控已停止。")


if __name__ == "__main__":
    main()
