"""
CleanBot v2.0 — 系统诊断引擎

智能诊断系统问题，提供解决方案。
"""

import os
import sys
import time
import json
import subprocess
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from enum import Enum


def _run_hidden(cmd: list, timeout: int = 15) -> subprocess.CompletedProcess:
    """运行命令但不弹出控制台窗口（EXE 打包后必需）。"""
    if sys.platform == "win32":
        return subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


class ProblemSeverity(Enum):
    """问题严重程度"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ProblemCategory(Enum):
    """问题类别"""
    SYSTEM = "system"
    PERFORMANCE = "performance"
    SECURITY = "security"
    DISK = "disk"
    NETWORK = "network"
    REGISTRY = "registry"
    SERVICE = "service"
    STARTUP = "startup"


@dataclass
class Problem:
    """问题定义"""
    id: str
    title: str
    description: str
    severity: ProblemSeverity
    category: ProblemCategory
    solution: str
    details: Dict = field(default_factory=dict)
    detected_at: float = field(default_factory=time.time)
    is_fixed: bool = False
    fix_result: Optional[str] = None


@dataclass
class Solution:
    """解决方案"""
    problem_id: str
    title: str
    description: str
    steps: List[str]
    risk_level: str  # low, medium, high
    estimated_time: int  # 秒
    requires_restart: bool = False
    requires_admin: bool = False


@dataclass
class DiagnosisReport:
    """诊断报告"""
    timestamp: float
    system_info: Dict
    health_score: int  # 0-100
    problems: List[Problem]
    solutions: List[Solution]
    recommendations: List[str]
    summary: str


class SystemDiagnosis:
    """系统诊断引擎"""

    def __init__(self):
        self.problems: List[Problem] = []
        self.solutions: List[Solution] = []
        self.system_info: Dict = {}

    def run_full_diagnosis(self) -> DiagnosisReport:
        """运行完整诊断"""
        start_time = time.time()

        # 收集系统信息
        self.system_info = self._collect_system_info()

        # 检测问题
        self.problems = []

        # 系统问题检测
        self.problems.extend(self._detect_system_problems())

        # 性能问题检测
        self.problems.extend(self._detect_performance_problems())

        # 安全问题检测
        self.problems.extend(self._detect_security_problems())

        # 磁盘问题检测
        self.problems.extend(self._detect_disk_problems())

        # 注册表问题检测
        self.problems.extend(self._detect_registry_problems())

        # 服务问题检测
        self.problems.extend(self._detect_service_problems())

        # 启动项问题检测
        self.problems.extend(self._detect_startup_problems())

        # 生成解决方案
        self.solutions = self._generate_solutions()

        # 计算健康分数
        health_score = self._calculate_health_score()

        # 生成推荐
        recommendations = self._generate_recommendations()

        # 生成摘要
        summary = self._generate_summary()

        return DiagnosisReport(
            timestamp=time.time(),
            system_info=self.system_info,
            health_score=health_score,
            problems=self.problems,
            solutions=self.solutions,
            recommendations=recommendations,
            summary=summary,
        )

    def _collect_system_info(self) -> Dict:
        """收集系统信息"""
        import platform
        import psutil

        info = {
            "os": platform.system(),
            "os_version": platform.version(),
            "os_release": platform.release(),
            "architecture": platform.machine(),
            "processor": platform.processor(),
            "hostname": platform.node(),
            "python_version": platform.python_version(),
        }

        # CPU 信息
        info["cpu_count"] = psutil.cpu_count()
        info["cpu_freq"] = psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None

        # 内存信息
        memory = psutil.virtual_memory()
        info["memory_total"] = memory.total
        info["memory_available"] = memory.available
        info["memory_percent"] = memory.percent

        # 磁盘信息
        info["disks"] = []
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                info["disks"].append({
                    "device": partition.device,
                    "mountpoint": partition.mountpoint,
                    "fstype": partition.fstype,
                    "total": usage.total,
                    "used": usage.used,
                    "free": usage.free,
                    "percent": usage.percent,
                })
            except (PermissionError, OSError):
                pass

        return info

    def _detect_system_problems(self) -> List[Problem]:
        """检测系统问题"""
        problems = []

        # 检查系统文件完整性（None = 无法检查，不报错）
        integrity = self._check_system_files_integrity()
        if integrity is False:
            problems.append(Problem(
                id="sys_001",
                title="系统文件可能损坏",
                description="检测到系统文件完整性问题，可能导致系统不稳定",
                severity=ProblemSeverity.HIGH,
                category=ProblemCategory.SYSTEM,
                solution="运行系统文件检查器 (sfc /scannow) 修复系统文件",
            ))

        # 检查 Windows 更新（None = 无法检查，不报错）
        pending = self._has_pending_updates()
        if pending is True:
            problems.append(Problem(
                id="sys_002",
                title="有待安装的 Windows 更新",
                description="系统有未安装的重要更新，可能包含安全补丁",
                severity=ProblemSeverity.MEDIUM,
                category=ProblemCategory.SYSTEM,
                solution="安装 Windows 更新以保持系统安全",
            ))

        # 检查系统还原点（None = 无法检查，不报错）
        restore = self._has_restore_points()
        if restore is False:
            problems.append(Problem(
                id="sys_003",
                title="没有系统还原点",
                description="没有系统还原点，无法在出现问题时恢复系统",
                severity=ProblemSeverity.LOW,
                category=ProblemCategory.SYSTEM,
                solution="创建系统还原点以便在需要时恢复系统",
            ))

        return problems

    def _detect_performance_problems(self) -> List[Problem]:
        """检测性能问题"""
        import psutil

        problems = []

        # CPU 使用率过高
        cpu_percent = psutil.cpu_percent(interval=1)
        if cpu_percent > 80:
            problems.append(Problem(
                id="perf_001",
                title="CPU 使用率过高",
                description=f"当前 CPU 使用率 {cpu_percent}%，可能影响系统响应速度",
                severity=ProblemSeverity.HIGH,
                category=ProblemCategory.PERFORMANCE,
                solution="检查并关闭占用 CPU 较高的程序",
                details={"cpu_percent": cpu_percent},
            ))

        # 内存使用率过高
        memory = psutil.virtual_memory()
        if memory.percent > 85:
            problems.append(Problem(
                id="perf_002",
                title="内存使用率过高",
                description=f"当前内存使用率 {memory.percent}%，可能导致系统变慢",
                severity=ProblemSeverity.HIGH,
                category=ProblemCategory.PERFORMANCE,
                solution="关闭不必要的程序或增加内存",
                details={"memory_percent": memory.percent},
            ))

        # 磁盘空间不足
        for disk in self.system_info.get("disks", []):
            if disk["percent"] > 90:
                problems.append(Problem(
                    id=f"perf_003_{disk['device']}",
                    title=f"磁盘 {disk['device']} 空间不足",
                    description=f"磁盘 {disk['device']} 已使用 {disk['percent']}%，剩余空间不足",
                    severity=ProblemSeverity.HIGH,
                    category=ProblemCategory.DISK,
                    solution="清理磁盘空间或扩展磁盘容量",
                    details={"disk": disk["device"], "percent": disk["percent"]},
                ))

        return problems

    def _detect_security_problems(self) -> List[Problem]:
        """检测安全问题"""
        problems = []

        # 检查 Windows Defender 状态（None = 无法检查，不报错）
        defender = self._is_defender_enabled()
        if defender is False:
            problems.append(Problem(
                id="sec_001",
                title="Windows Defender 已禁用",
                description="Windows Defender 防病毒软件已禁用，系统可能面临安全风险",
                severity=ProblemSeverity.CRITICAL,
                category=ProblemCategory.SECURITY,
                solution="启用 Windows Defender 以保护系统安全",
            ))

        # 检查防火墙状态（None = 无法检查，不报错）
        fw = self._is_firewall_enabled()
        if fw is False:
            problems.append(Problem(
                id="sec_002",
                title="Windows 防火墙已禁用",
                description="Windows 防火墙已禁用，系统可能面临网络攻击风险",
                severity=ProblemSeverity.HIGH,
                category=ProblemCategory.SECURITY,
                solution="启用 Windows 防火墙以保护系统安全",
            ))

        # 检查 UAC 状态
        if not self._is_uac_enabled():
            problems.append(Problem(
                id="sec_003",
                title="用户账户控制 (UAC) 已禁用",
                description="UAC 已禁用，恶意软件可能更容易获取管理员权限",
                severity=ProblemSeverity.MEDIUM,
                category=ProblemCategory.SECURITY,
                solution="启用用户账户控制以提高系统安全性",
            ))

        return problems

    def _detect_disk_problems(self) -> List[Problem]:
        """检测磁盘问题"""
        problems = []

        # 检查磁盘错误
        for disk in self.system_info.get("disks", []):
            if not self._check_disk_health(disk["device"]):
                problems.append(Problem(
                    id=f"disk_001_{disk['device']}",
                    title=f"磁盘 {disk['device']} 可能有错误",
                    description=f"检测到磁盘 {disk['device']} 可能存在文件系统错误",
                    severity=ProblemSeverity.HIGH,
                    category=ProblemCategory.DISK,
                    solution=f"运行磁盘检查工具 (chkdsk {disk['device']}: /f) 修复错误",
                    details={"disk": disk["device"]},
                ))

        # 检查磁盘碎片
        for disk in self.system_info.get("disks", []):
            if self._is_fragmented(disk["device"]):
                problems.append(Problem(
                    id=f"disk_002_{disk['device']}",
                    title=f"磁盘 {disk['device']} 碎片率较高",
                    description=f"磁盘 {disk['device']} 碎片率较高，可能影响读写性能",
                    severity=ProblemSeverity.MEDIUM,
                    category=ProblemCategory.DISK,
                    solution=f"运行磁盘碎片整理工具优化磁盘性能",
                    details={"disk": disk["device"]},
                ))

        return problems

    def _detect_registry_problems(self) -> List[Problem]:
        """检测注册表问题"""
        problems = []

        # 检查无效的注册表项
        invalid_entries = self._scan_invalid_registry_entries()
        if invalid_entries:
            problems.append(Problem(
                id="reg_001",
                title="发现无效的注册表项",
                description=f"检测到 {len(invalid_entries)} 个无效的注册表项",
                severity=ProblemSeverity.MEDIUM,
                category=ProblemCategory.REGISTRY,
                solution="使用注册表清理器清理无效的注册表项",
                details={"count": len(invalid_entries)},
            ))

        return problems

    def _detect_service_problems(self) -> List[Problem]:
        """检测服务问题"""
        problems = []

        # 检查关键服务状态
        critical_services = [
            "wuauserv",  # Windows Update
            "WinDefend",  # Windows Defender
            "mpssvc",  # Windows Firewall
            "Dhcp",  # DHCP Client
            "Dnscache",  # DNS Client
        ]

        for service in critical_services:
            if not self._is_service_running(service):
                service_name = self._get_service_display_name(service)
                problems.append(Problem(
                    id=f"svc_001_{service}",
                    title=f"关键服务 {service_name} 未运行",
                    description=f"关键服务 {service_name} ({service}) 未运行，可能影响系统功能",
                    severity=ProblemSeverity.HIGH,
                    category=ProblemCategory.SERVICE,
                    solution=f"启动服务 {service_name}",
                    details={"service": service},
                ))

        return problems

    def _detect_startup_problems(self) -> List[Problem]:
        """检测启动项问题"""
        problems = []

        # 检查启动项数量
        startup_count = self._get_startup_count()
        if startup_count > 20:
            problems.append(Problem(
                id="start_001",
                title="启动项过多",
                description=f"系统有 {startup_count} 个启动项，可能影响启动速度",
                severity=ProblemSeverity.MEDIUM,
                category=ProblemCategory.STARTUP,
                solution="禁用不必要的启动项以加快系统启动速度",
                details={"count": startup_count},
            ))

        return problems

    def _generate_solutions(self) -> List[Solution]:
        """生成解决方案"""
        solutions = []

        for problem in self.problems:
            solution = self._get_solution_for_problem(problem)
            if solution:
                solutions.append(solution)

        return solutions

    def _get_solution_for_problem(self, problem: Problem) -> Optional[Solution]:
        """获取问题的解决方案"""
        solutions_map = {
            "sys_001": Solution(
                problem_id="sys_001",
                title="修复系统文件",
                description="运行系统文件检查器修复损坏的系统文件",
                steps=[
                    "以管理员身份打开命令提示符",
                    "运行命令: sfc /scannow",
                    "等待扫描完成",
                    "重启计算机",
                ],
                risk_level="low",
                estimated_time=600,
                requires_restart=True,
                requires_admin=True,
            ),
            "sys_002": Solution(
                problem_id="sys_002",
                title="安装 Windows 更新",
                description="安装待处理的 Windows 更新",
                steps=[
                    "打开 Windows 设置",
                    "进入 更新和安全",
                    "点击 检查更新",
                    "安装所有可用更新",
                    "重启计算机",
                ],
                risk_level="low",
                estimated_time=1800,
                requires_restart=True,
            ),
            "sec_001": Solution(
                problem_id="sec_001",
                title="启用 Windows Defender",
                description="启用 Windows Defender 防病毒软件",
                steps=[
                    "打开 Windows 安全中心",
                    "进入 病毒和威胁防护",
                    "启用 实时保护",
                    "运行快速扫描",
                ],
                risk_level="low",
                estimated_time=300,
                requires_admin=True,
            ),
            "perf_001": Solution(
                problem_id="perf_001",
                title="降低 CPU 使用率",
                description="关闭占用 CPU 较高的程序",
                steps=[
                    "打开任务管理器 (Ctrl+Shift+Esc)",
                    "查看 CPU 使用率最高的进程",
                    "结束不必要的进程",
                    "检查是否有程序异常占用 CPU",
                ],
                risk_level="low",
                estimated_time=120,
            ),
            "perf_002": Solution(
                problem_id="perf_002",
                title="释放内存",
                description="关闭不必要的程序释放内存",
                steps=[
                    "打开任务管理器",
                    "查看内存使用率最高的进程",
                    "结束不必要的程序",
                    "考虑增加物理内存",
                ],
                risk_level="low",
                estimated_time=120,
            ),
        }

        return solutions_map.get(problem.id)

    def _calculate_health_score(self) -> int:
        """计算健康分数"""
        if not self.problems:
            return 100

        # 根据问题严重程度扣分
        score = 100
        for problem in self.problems:
            if problem.severity == ProblemSeverity.CRITICAL:
                score -= 20
            elif problem.severity == ProblemSeverity.HIGH:
                score -= 10
            elif problem.severity == ProblemSeverity.MEDIUM:
                score -= 5
            elif problem.severity == ProblemSeverity.LOW:
                score -= 2

        return max(0, score)

    def _generate_recommendations(self) -> List[str]:
        """生成推荐"""
        recommendations = []

        # 根据问题生成推荐
        high_problems = [p for p in self.problems if p.severity in [ProblemSeverity.CRITICAL, ProblemSeverity.HIGH]]
        if high_problems:
            recommendations.append(f"发现 {len(high_problems)} 个高优先级问题，建议立即处理")

        # 根据系统状态生成推荐
        for disk in self.system_info.get("disks", []):
            if disk["percent"] > 80:
                recommendations.append(f"磁盘 {disk['device']} 使用率 {disk['percent']}%，建议清理空间")

        # 通用推荐
        if not recommendations:
            recommendations.append("系统状态良好，建议定期进行系统维护")

        return recommendations

    def _generate_summary(self) -> str:
        """生成摘要"""
        total = len(self.problems)
        critical = len([p for p in self.problems if p.severity == ProblemSeverity.CRITICAL])
        high = len([p for p in self.problems if p.severity == ProblemSeverity.HIGH])
        medium = len([p for p in self.problems if p.severity == ProblemSeverity.MEDIUM])
        low = len([p for p in self.problems if p.severity == ProblemSeverity.LOW])

        if total == 0:
            return "系统状态良好，未发现明显问题。"

        summary_parts = []
        if critical > 0:
            summary_parts.append(f"{critical} 个严重问题")
        if high > 0:
            summary_parts.append(f"{high} 个高优先级问题")
        if medium > 0:
            summary_parts.append(f"{medium} 个中等优先级问题")
        if low > 0:
            summary_parts.append(f"{low} 个低优先级问题")

        return f"检测到 {total} 个问题：{', '.join(summary_parts)}。"

    # 辅助方法
    def _check_system_files_integrity(self) -> Optional[bool]:
        """检查系统文件完整性。返回 None 表示无法检查。"""
        try:
            result = _run_hidden(
                ["sfc", "/verifyonly"],
                timeout=60)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            return None  # 无法检查 — 不要假设正常

    def _has_pending_updates(self) -> Optional[bool]:
        """检查是否有待安装的更新。返回 None 表示无法检查。"""
        try:
            result = _run_hidden(
                ["powershell", "-Command",
                 "(New-Object -ComObject Microsoft.Update.Session)"
                 ".CreateUpdateSearcher().Search('IsInstalled=0').Updates.Count"],
                timeout=60)
            if result.returncode == 0 and result.stdout.strip().isdigit():
                return int(result.stdout.strip()) > 0
            return None  # 无法解析输出
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            return None

    def _has_restore_points(self) -> Optional[bool]:
        """检查是否有系统还原点。返回 None 表示无法检查。"""
        try:
            result = _run_hidden(
                ["powershell", "-Command",
                 "(Get-ComputerRestorePoint | Measure-Object).Count"],
                timeout=60)
            if result.returncode == 0 and result.stdout.strip().isdigit():
                return int(result.stdout.strip()) > 0
            return None
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            return None

    def _is_defender_enabled(self) -> Optional[bool]:
        """检查 Windows Defender 是否启用。返回 None 表示无法检查。"""
        try:
            result = _run_hidden(
                ["powershell", "-Command",
                 "Get-MpComputerStatus | Select-Object -ExpandProperty "
                 "RealTimeProtectionEnabled"],
                timeout=60)
            if "True" in result.stdout:
                return True
            if "False" in result.stdout:
                return False
            return None
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            return None

    def _is_firewall_enabled(self) -> Optional[bool]:
        """检查防火墙是否启用。返回 None 表示无法检查。"""
        try:
            result = _run_hidden(
                ["netsh", "advfirewall", "show", "allprofiles", "state"],
                timeout=60)
            if "ON" in result.stdout:
                return True
            if "OFF" in result.stdout:
                return False
            return None
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            return None

    def _is_uac_enabled(self) -> bool:
        """检查 UAC 是否启用"""
        if sys.platform != "win32":
            return True  # 非 Windows 系统，假设启用

        try:
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System",
            )
            value, _ = winreg.QueryValueEx(key, "EnableLUA")
            winreg.CloseKey(key)
            return value == 1
        except (OSError, FileNotFoundError):
            return True  # 假设启用

    def _check_disk_health(self, drive: str) -> bool:
        """检查磁盘健康"""
        try:
            # 使用 wmic 检查磁盘状态
            result = _run_hidden(
                ["wmic", "diskdrive", "get", "status"],
                timeout=60)
            return "OK" in result.stdout
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return True  # 假设正常

    def _is_fragmented(self, drive: str) -> bool:
        """检查磁盘碎片"""
        # 白名单校验：只允许单个字母 A-Z
        if not drive or len(drive) < 1:
            return False

        letter = drive[0].upper()
        if not ('A' <= letter <= 'Z'):
            return False

        try:
            # 使用碎片分析工具
            result = _run_hidden(
                ["defrag", f"{letter}:", "/a", "/v"],
                timeout=60)
            return "碎片率" in result.stdout and "0%" not in result.stdout
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def _scan_invalid_registry_entries(self) -> List[str]:
        """扫描无效的注册表项"""
        # 简化实现：只检查常见的无效项
        invalid = []

        if sys.platform != "win32":
            return invalid  # 非 Windows 系统，跳过

        try:
            import winreg

            # 检查卸载程序注册表
            try:
                key = winreg.OpenKey(
                    winreg.HKEY_LOCAL_MACHINE,
                    r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
                )
                winreg.CloseKey(key)
            except OSError:
                invalid.append("Uninstall registry key missing")

        except ImportError:
            pass

        return invalid

    def _is_service_running(self, service_name: str) -> bool:
        """检查服务是否运行"""
        try:
            import psutil
            for service in psutil.win_service_iter():
                if service.name() == service_name:
                    return service.status() == psutil.STATUS_RUNNING
        except (AttributeError, psutil.NoSuchProcess):
            pass
        return False

    def _get_service_display_name(self, service_name: str) -> str:
        """获取服务显示名称"""
        try:
            import psutil
            for service in psutil.win_service_iter():
                if service.name() == service_name:
                    return service.display_name()
        except (AttributeError, psutil.NoSuchProcess):
            pass
        return service_name

    def _get_startup_count(self) -> int:
        """获取启动项数量"""
        if sys.platform != "win32":
            return 0

        try:
            import winreg

            count = 0

            # 检查当前用户的启动项
            try:
                key = winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER,
                    r"Software\Microsoft\Windows\CurrentVersion\Run"
                )
                i = 0
                while True:
                    try:
                        winreg.EnumValue(key, i)
                        count += 1
                        i += 1
                    except OSError:
                        break
                winreg.CloseKey(key)
            except OSError:
                pass

            # 检查所有用户的启动项
            try:
                key = winreg.OpenKey(
                    winreg.HKEY_LOCAL_MACHINE,
                    r"Software\Microsoft\Windows\CurrentVersion\Run"
                )
                i = 0
                while True:
                    try:
                        winreg.EnumValue(key, i)
                        count += 1
                        i += 1
                    except OSError:
                        break
                winreg.CloseKey(key)
            except OSError:
                pass

            return count

        except (ImportError, OSError):
            return 0


def main():
    """CLI 入口"""
    print("=" * 60)
    print("CleanBot v2.0 — 系统诊断")
    print("=" * 60)

    diagnosis = SystemDiagnosis()

    print("\n正在运行系统诊断...")
    report = diagnosis.run_full_diagnosis()

    print("\n诊断完成!")
    print("-" * 60)

    print(f"\n系统健康分数: {report.health_score}/100")
    print(f"\n摘要: {report.summary}")

    if report.problems:
        print(f"\n发现的问题 ({len(report.problems)}):")
        for i, problem in enumerate(report.problems, 1):
            print(f"  {i}. [{problem.severity.value.upper()}] {problem.title}")
            print(f"     {problem.description}")
            print(f"     解决方案: {problem.solution}")
            print()

    if report.recommendations:
        print("\n推荐:")
        for rec in report.recommendations:
            print(f"  - {rec}")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
