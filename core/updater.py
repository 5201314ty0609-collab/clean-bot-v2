"""
CleanBot v2.0 — 更新检测器（国内网络优化）

更新源优先级：Gitee → 自定义 JSON → GitHub（兜底）
所有 URL 均可通过配置文件覆盖，无需修改代码。

国内用户无代理也能正常检测更新。
"""

import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional
from urllib.request import urlopen, Request
from urllib.error import URLError

# 当前版本 (与 core/__init__.py 保持同步)
CURRENT_VERSION = "2.0.0"

# ── 更新源（按优先级排列，国内网络可达） ──
# 发布新版本时，至少更新 Gitee 和 version.json 两个源即可覆盖全部用户。
#
# 如何部署更新源：
#   1. Gitee (推荐): 在 gitee.com 创建仓库 → 发布 Release → 上传 exe
#   2. 自定义 JSON: 把 version.json 上传到任意可公网访问的位置
#   3. GitHub (备用): 对开了代理的用户可用
#
# 链接中的 YOUR_GITEE_USER / YOUR_REPO 发布前需替换为实际值。

DEFAULT_UPDATE_URLS = [
    # Gitee Releases API（国内首选，无需代理）
    "https://gitee.com/api/v5/repos/YOUR_GITEE_USER/clean-bot-v2/releases/latest",
    # 自定义 version.json（托管在 Gitee Pages 或任意国内可访问的静态服务器）
    "https://gitee.com/YOUR_GITEE_USER/clean-bot-v2/raw/main/version.json",
    # GitHub Releases API（海外/代理用户备用）
    "https://api.github.com/repos/YOUR_USERNAME/clean-bot-v2/releases/latest",
    # GitHub raw（海外/代理用户备用）
    "https://raw.githubusercontent.com/YOUR_USERNAME/clean-bot-v2/main/version.json",
]

# 下载页回退（当自动下载失败时，引导用户到这些页面手动下载）
DEFAULT_DOWNLOAD_PAGES = [
    "https://gitee.com/YOUR_GITEE_USER/clean-bot-v2/releases",
    "https://github.com/YOUR_USERNAME/clean-bot-v2/releases",
]


@dataclass
class UpdateInfo:
    """更新信息"""
    version: str
    download_url: str
    release_notes: str
    release_date: str
    download_pages: List[str]    # 手动下载页面（当直接链接失效时使用）
    is_newer: bool = False
    download_failed: bool = False


def _load_config() -> dict:
    """加载用户自定义更新配置（可选）。"""
    config_paths = [
        Path(__file__).parent.parent / "config" / "update_config.json",
        Path(os.path.expanduser("~/.cleanbot/update_config.json")),
    ]
    for path in config_paths:
        if path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError):
                pass
    return {}


def _get_update_urls() -> List[str]:
    """获取更新检查 URL 列表（配置 > 默认）。"""
    config = _load_config()
    urls = config.get("update_urls", [])
    if urls:
        return urls
    return DEFAULT_UPDATE_URLS


def _get_download_pages() -> List[str]:
    """获取手动下载页面列表。"""
    config = _load_config()
    pages = config.get("download_pages", [])
    if pages:
        return pages
    return DEFAULT_DOWNLOAD_PAGES


def _parse_semver(version: str) -> tuple:
    """解析语义化版本号。"""
    try:
        parts = version.strip().lstrip("v").split(".")
        return tuple(int(p) for p in parts[:3])
    except (ValueError, IndexError):
        return (0, 0, 0)


def _fetch_url(url: str, timeout: int = 15) -> Optional[dict]:
    """获取 JSON 数据，国内网络适当延长超时。"""
    try:
        req = Request(url, headers={
            "User-Agent": f"CleanBot/{CURRENT_VERSION} (Windows)",
            "Accept": "application/json",
        })
        with urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except (URLError, json.JSONDecodeError, OSError, ValueError):
        return None


def _extract_update_info(data: dict) -> Optional[UpdateInfo]:
    """从 API 响应提取更新信息，兼容 Gitee / GitHub / 自定义 JSON。"""
    try:
        # Gitee Releases API 格式 (tag_name + assets)
        if "tag_name" in data:
            version = data["tag_name"].lstrip("v")
            assets = data.get("assets", [])
            download_url = assets[0]["browser_download_url"] if assets else ""
            # Gitee 用 body，GitHub 也用它
            release_notes = data.get("body", "")
            release_date = (data.get("published_at") or data.get("created_at", ""))[:10]
        else:
            # 自定义 version.json 格式
            version = data.get("version", "0.0.0")
            download_url = data.get("download_url", "")
            release_notes = data.get("release_notes", "")
            release_date = data.get("release_date", "")

        return UpdateInfo(
            version=version,
            download_url=download_url,
            release_notes=release_notes,
            release_date=release_date,
            download_pages=_get_download_pages(),
        )
    except (KeyError, IndexError, TypeError):
        return None


def check_for_update() -> Optional[UpdateInfo]:
    """检查是否有可用更新（遍历所有源，首个成功即返回）。

    Returns:
        UpdateInfo 如果有新版本。
        None 如果已是最新，或所有源都检查失败（网络不可达等）。
    """
    for url in _get_update_urls():
        data = _fetch_url(url)
        if data is None:
            continue

        info = _extract_update_info(data)
        if info is None:
            continue

        current = _parse_semver(CURRENT_VERSION)
        latest = _parse_semver(info.version)
        info.is_newer = latest > current
        return info

    return None  # 所有源都不可达 —— 静默失败，不影响正常使用


def get_current_version() -> str:
    """返回当前版本号。"""
    return CURRENT_VERSION
