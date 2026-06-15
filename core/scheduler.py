"""
CleanBot v3.0 — 定时清理调度器

支持：每天/每周/每月自动扫描和清理。
所有安全文件自动清理，需确认文件跳过。
"""
import json, os, time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


CONFIG_PATH = Path(os.path.expanduser("~")) / "CleanBot" / "schedule.json"


@dataclass
class ScheduleConfig:
    enabled: bool = False
    interval: str = "weekly"     # daily / weekly / monthly
    auto_clean: bool = True      # 自动清理安全文件
    last_run: float = 0.0
    next_run: float = 0.0


def _calc_next(interval: str) -> float:
    now = time.time()
    if interval == "daily":
        return now + 86400
    elif interval == "monthly":
        return now + 86400 * 30
    else:  # weekly
        return now + 86400 * 7


def load_config() -> ScheduleConfig:
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH) as f:
                d = json.load(f)
            return ScheduleConfig(**d)
        except Exception:
            pass
    return ScheduleConfig()


def save_config(cfg: ScheduleConfig):
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        json.dump({"enabled": cfg.enabled, "interval": cfg.interval,
                    "auto_clean": cfg.auto_clean, "last_run": cfg.last_run,
                    "next_run": cfg.next_run}, f, indent=2)


def should_run() -> bool:
    """检查是否到了定时清理时间"""
    cfg = load_config()
    if not cfg.enabled:
        return False
    now = time.time()
    if cfg.next_run == 0:
        cfg.next_run = _calc_next(cfg.interval)
        save_config(cfg)
        return False
    if now >= cfg.next_run:
        return True
    return False


def mark_completed():
    """标记定时清理已完成"""
    cfg = load_config()
    cfg.last_run = time.time()
    cfg.next_run = _calc_next(cfg.interval)
    save_config(cfg)


def get_status() -> dict:
    cfg = load_config()
    return {
        "enabled": cfg.enabled,
        "interval": cfg.interval,
        "auto_clean": cfg.auto_clean,
        "last_run": cfg.last_run,
        "next_run": cfg.next_run,
    }
