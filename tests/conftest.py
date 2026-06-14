"""
CleanBot v2.0 — pytest 配置
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def pytest_configure(config):
    """pytest 配置"""
    # 添加自定义标记
    config.addinivalue_line("markers", "slow: 标记为慢速测试")
    config.addinivalue_line("markers", "windows: 只在 Windows 上运行的测试")
    config.addinivalue_line("markers", "admin: 需要管理员权限的测试")


def pytest_collection_modifyitems(items):
    """修改测试项"""
    import sys

    for item in items:
        # 自动跳过 Windows 特定测试
        if "windows" in item.keywords and sys.platform != "win32":
            item.add_marker(pytest.mark.skip(reason="只在 Windows 上运行"))

        # 自动跳过需要管理员权限的测试
        if "admin" in item.keywords:
            from core.utils import is_admin
            if not is_admin():
                item.add_marker(pytest.mark.skip(reason="需要管理员权限"))
