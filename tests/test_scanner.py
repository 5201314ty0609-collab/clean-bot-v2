"""
CleanBot v2.0 — 文件扫描器测试
"""

import sys
import os
import tempfile
import shutil
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.scanner.file_scanner import FileScanner
from core.utils import format_size


def create_test_files(base_dir: str):
    """创建测试文件"""
    # 创建目录结构
    os.makedirs(os.path.join(base_dir, "temp"), exist_ok=True)
    os.makedirs(os.path.join(base_dir, "cache"), exist_ok=True)
    os.makedirs(os.path.join(base_dir, "logs"), exist_ok=True)
    os.makedirs(os.path.join(base_dir, "documents"), exist_ok=True)
    os.makedirs(os.path.join(base_dir, "duplicates"), exist_ok=True)

    # 创建临时文件
    with open(os.path.join(base_dir, "temp", "test.tmp"), "w") as f:
        f.write("temporary file")

    with open(os.path.join(base_dir, "temp", "test.temp"), "w") as f:
        f.write("temporary file")

    # 创建缓存文件
    with open(os.path.join(base_dir, "cache", "test.cache"), "w") as f:
        f.write("cache file")

    # 创建日志文件
    with open(os.path.join(base_dir, "logs", "test.log"), "w") as f:
        f.write("log file")

    # 创建普通文件
    with open(os.path.join(base_dir, "documents", "test.txt"), "w") as f:
        f.write("normal file")

    # 创建大文件（模拟）
    with open(os.path.join(base_dir, "documents", "large.zip"), "wb") as f:
        f.write(b"0" * 1024 * 1024)  # 1MB

    # 创建重复文件
    with open(os.path.join(base_dir, "duplicates", "file1.txt"), "w") as f:
        f.write("duplicate content")

    with open(os.path.join(base_dir, "duplicates", "file2.txt"), "w") as f:
        f.write("duplicate content")

    return base_dir


def test_scanner():
    """测试扫描器"""
    print("Testing FileScanner...")

    # 创建临时目录
    temp_dir = tempfile.mkdtemp()

    try:
        # 创建测试文件
        create_test_files(temp_dir)

        # 创建扫描器
        scanner = FileScanner(temp_dir, max_depth=3)

        # 扫描
        result = scanner.scan()

        # 验证结果
        assert result.total_files > 0, "Should find files"
        print(f"  ✓ Found {result.total_files} files")

        # 验证分类
        assert len(result.temp_files) > 0, "Should find temp files"
        print(f"  ✓ Found {len(result.temp_files)} temp files")

        assert len(result.cache_files) > 0, "Should find cache files"
        print(f"  ✓ Found {len(result.cache_files)} cache files")

        assert len(result.log_files) > 0, "Should find log files"
        print(f"  ✓ Found {len(result.log_files)} log files")

        # 验证安全删除列表
        safe_files = scanner.get_safe_to_delete()
        assert len(safe_files) > 0, "Should have safe-to-delete files"
        print(f"  ✓ Found {len(safe_files)} safe-to-delete files")

        # 验证重复文件检测
        duplicates = scanner.get_duplicates()
        print(f"  ✓ Found {len(duplicates)} duplicate groups")

        # 验证摘要
        summary = scanner.get_summary()
        assert summary["total_files"] > 0, "Summary should have total files"
        assert summary["safe_files"] > 0, "Summary should have safe files"
        print(f"  ✓ Summary: {summary['total_files']} files, {summary['safe_size_mb']:.2f} MB safe")

        print("  ✓ Scanner tests passed!")

    finally:
        # 清理临时目录
        shutil.rmtree(temp_dir)


def test_format_size():
    """测试大小格式化"""
    print("Testing format_size...")

    assert format_size(1024) == "1.00 KB"
    assert format_size(1024 * 1024) == "1.00 MB"
    assert format_size(1024 * 1024 * 1024) == "1.00 GB"

    print("  ✓ format_size tests passed!")


def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("CleanBot v2.0 — File Scanner Tests")
    print("=" * 60)
    print()

    tests = [
        test_scanner,
        test_format_size,
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
