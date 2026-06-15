"""
CleanBot v2.0 — 更新检测器

检查在线版本，与当前版本比较，提示用户更新。
支持 GitHub Releases API 和自定义 JSON 端点。
"""

import json
import sys
from dataclasses import dataclass
from typing import Optional
from urllib.request import urlopen, Request
from urllib.error import URLError

# 当前版本 (与 core/__init__.py 保持同步)
CURRENT_VERSION = "2.0.0"

# 更新检查 URL（按优先级尝试）
UPDATE_URLS = [
    # GitHub Releases API（需替换为实际仓库地址）
    "https://api.github.com/repos/YOUR_USERNAME/clean-bot-v2/releases/latest",
    # 备用：直接托管 version.json
    "https://raw.githubusercontent.com/YOUR_USERNAME/clean-bot-v2/main/version.json",
]


@dataclass
class UpdateInfo:
    """更新信息"""
    version: str
    download_url: str
    release_notes: str
    release_date: str
    is_newer: bool = False


def _parse_semver(version: str) -> tuple:
    """解析语义化版本号，返回可比较的元组。"""
    try:
        parts = version.strip().lstrip("v").split(".")
        return tuple(int(p) for p in parts[:3])
    except (ValueError, IndexError):
        return (0, 0, 0)


def _fetch_url(url: str, timeout: int = 10) -> Optional[dict]:
    """安全地获取 JSON 数据。"""
    try:
        req = Request(url, headers={
            "User-Agent": f"CleanBot/{CURRENT_VERSION}",
            "Accept": "application/json",
        })
        with urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except (URLError, json.JSONDecodeError, OSError):
        return None


def _extract_update_info(data: dict) -> Optional[UpdateInfo]:
    """从 API 响应中提取更新信息，兼容 GitHub Releases 和自定义 JSON。"""
    try:
        if "tag_name" in data:
            # GitHub Releases API 格式
            version = data["tag_name"].lstrip("v")
            download_url = (
                data["assets"][0]["browser_download_url"]
                if data.get("assets")
                else data.get("html_url", "")
            )
            release_notes = data.get("body", "")
            release_date = data.get("published_at", "")[:10]
        else:
            # 自定义 version.json 格式
            version = data["version"]
            download_url = data.get("download_url", "")
            release_notes = data.get("release_notes", "")
            release_date = data.get("release_date", "")

        return UpdateInfo(
            version=version,
            download_url=download_url,
            release_notes=release_notes,
            release_date=release_date,
        )
    except (KeyError, IndexError, TypeError):
        return None


def check_for_update() -> Optional[UpdateInfo]:
    """检查是否有可用更新。

    Returns:
        UpdateInfo 如果有新版本，None 如果已是最新或检查失败。
    """
    for url in UPDATE_URLS:
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

    return None  # 所有 URL 都失败


def get_current_version() -> str:
    """返回当前应用版本。"""
    return CURRENT_VERSION
