"""
CleanBot v3.0 — 浏览器缓存扫描与清理

支持: Chrome / Edge / Firefox
"""
import os, sys, glob, time
from dataclasses import dataclass, field
from typing import List, Optional
from core.utils import format_size


@dataclass
class BrowserCache:
    name: str           # "Chrome" / "Edge" / "Firefox"
    path: str           # 缓存路径
    size: int = 0       # 字节
    file_count: int = 0
    exists: bool = False
    cleaned: bool = False


def _get_browser_paths() -> List[BrowserCache]:
    """获取所有浏览器缓存路径"""
    local = os.environ.get("LOCALAPPDATA", "")
    roaming = os.environ.get("APPDATA", "")
    results = []

    # Chrome
    chrome_base = os.path.join(local, "Google", "Chrome", "User Data")
    if os.path.exists(chrome_base):
        for profile in ["Default", "Profile 1", "Profile 2", "Profile 3"]:
            for cache_dir in ["Cache", "Code Cache", "Service Worker"]:
                p = os.path.join(chrome_base, profile, cache_dir)
                results.append(BrowserCache(name="Chrome", path=p))

    # Edge
    edge_base = os.path.join(local, "Microsoft", "Edge", "User Data")
    if os.path.exists(edge_base):
        for profile in ["Default", "Profile 1", "Profile 2"]:
            for cache_dir in ["Cache", "Code Cache", "Service Worker"]:
                p = os.path.join(edge_base, profile, cache_dir)
                results.append(BrowserCache(name="Edge", path=p))

    # Firefox
    ff_base = os.path.join(roaming, "Mozilla", "Firefox", "Profiles")
    if os.path.exists(ff_base):
        for prof in glob.glob(os.path.join(ff_base, "*.default*")):
            for cache_dir in ["cache2", "OfflineCache"]:
                p = os.path.join(prof, cache_dir)
                results.append(BrowserCache(name="Firefox", path=p))

    return results


def scan_browser_caches() -> List[BrowserCache]:
    """扫描所有浏览器缓存，返回大小统计"""
    caches = _get_browser_paths()
    for cache in caches:
        if not os.path.exists(cache.path):
            continue
        cache.exists = True
        total_size = 0
        total_count = 0
        try:
            for root, dirs, files in os.walk(cache.path):
                for f in files:
                    try:
                        total_size += os.path.getsize(os.path.join(root, f))
                        total_count += 1
                    except OSError:
                        pass
        except PermissionError:
            pass
        cache.size = total_size
        cache.file_count = total_count
    return [c for c in caches if c.exists and c.size > 0]


def clean_browser_cache(cache: BrowserCache) -> bool:
    """清理指定浏览器缓存"""
    if not os.path.exists(cache.path):
        return False
    import shutil
    try:
        # 删除缓存目录内容（保留目录结构）
        for item in os.listdir(cache.path):
            item_path = os.path.join(cache.path, item)
            try:
                if os.path.isfile(item_path) or os.path.islink(item_path):
                    os.remove(item_path)
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path, ignore_errors=True)
            except OSError:
                pass
        cache.cleaned = True
        cache.size = 0
        return True
    except PermissionError:
        return False


def get_browser_summary() -> dict:
    """获取浏览器缓存汇总"""
    caches = scan_browser_caches()
    by_browser = {}
    total = 0
    for c in caches:
        by_browser.setdefault(c.name, []).append(c)
        total += c.size
    return {
        "caches": caches,
        "by_browser": by_browser,
        "total_size": total,
        "browser_count": len(by_browser),
    }
