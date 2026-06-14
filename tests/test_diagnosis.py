"""
CleanBot v2.0 — 系统诊断测试
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.diagnosis.system_diagnosis import SystemDiagnosis, ProblemSeverity, ProblemCategory


def test_system_diagnosis():
    """测试系统诊断"""
    print("Testing SystemDiagnosis...")

    diagnosis = SystemDiagnosis()

    # 测试收集系统信息
    print("  Testing _collect_system_info...")
    system_info = diagnosis._collect_system_info()
    assert "os" in system_info, "Should have OS info"
    assert "cpu_count" in system_info, "Should have CPU count"
    assert "memory_total" in system_info, "Should have memory info"
    assert "disks" in system_info, "Should have disk info"
    print(f"    ✓ System info collected: {len(system_info)} items")

    # 测试运行诊断
    print("  Testing run_full_diagnosis...")
    report = diagnosis.run_full_diagnosis()

    assert report.timestamp > 0, "Should have timestamp"
    assert report.health_score >= 0 and report.health_score <= 100, "Health score should be 0-100"
    assert isinstance(report.problems, list), "Problems should be a list"
    assert isinstance(report.solutions, list), "Solutions should be a list"
    assert isinstance(report.recommendations, list), "Recommendations should be a list"
    assert len(report.summary) > 0, "Summary should not be empty"

    print(f"    ✓ Diagnosis completed:")
    print(f"      Health score: {report.health_score}")
    print(f"      Problems: {len(report.problems)}")
    print(f"      Solutions: {len(report.solutions)}")
    print(f"      Recommendations: {len(report.recommendations)}")

    # 测试问题检测
    if report.problems:
        print("\n  Detected problems:")
        for problem in report.problems[:5]:
            print(f"    - [{problem.severity.value}] {problem.title}")

    # 测试解决方案
    if report.solutions:
        print("\n  Generated solutions:")
        for solution in report.solutions[:3]:
            print(f"    - {solution.title} (risk: {solution.risk_level})")

    print("  ✓ SystemDiagnosis tests passed!")


def test_problem_severity():
    """测试问题严重程度"""
    print("Testing ProblemSeverity...")

    assert ProblemSeverity.LOW.value == "low"
    assert ProblemSeverity.MEDIUM.value == "medium"
    assert ProblemSeverity.HIGH.value == "high"
    assert ProblemSeverity.CRITICAL.value == "critical"

    print("  ✓ ProblemSeverity tests passed!")


def test_problem_category():
    """测试问题类别"""
    print("Testing ProblemCategory...")

    assert ProblemCategory.SYSTEM.value == "system"
    assert ProblemCategory.PERFORMANCE.value == "performance"
    assert ProblemCategory.SECURITY.value == "security"
    assert ProblemCategory.DISK.value == "disk"
    assert ProblemCategory.NETWORK.value == "network"
    assert ProblemCategory.REGISTRY.value == "registry"
    assert ProblemCategory.SERVICE.value == "service"
    assert ProblemCategory.STARTUP.value == "startup"

    print("  ✓ ProblemCategory tests passed!")


def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("CleanBot v2.0 — System Diagnosis Tests")
    print("=" * 60)
    print()

    tests = [
        test_problem_severity,
        test_problem_category,
        test_system_diagnosis,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
            print()
        except Exception as e:
            print(f"  ✗ {test.__name__} FAILED: {e}")
            failed += 1
            print()

    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
