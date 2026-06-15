"""
CleanBot v2.0 — 仪表盘视图（现代重设计）
"""

import sys
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QProgressBar, QSizePolicy,
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt6.QtGui import QFont

from core.monitor.disk_monitor import DiskMonitor, format_size
from core.utils import format_size as fmt


# ═══════════════════════════════════════════════════════════════════════════
# 后台线程
# ═══════════════════════════════════════════════════════════════════════════

class DashboardDataThread(QThread):
    data_ready = pyqtSignal(dict)

    def run(self):
        import psutil
        from core.utils import get_system_drive
        data = {}
        try:
            disk = psutil.disk_usage(get_system_drive())
            data["disk"] = {"total": disk.total, "used": disk.used, "free": disk.free, "percent": disk.percent}
        except Exception:
            pass
        mem = psutil.virtual_memory()
        data["memory"] = {"total": mem.total, "used": mem.used, "available": mem.available, "percent": mem.percent}
        data["cpu"] = {"percent": psutil.cpu_percent(interval=0.1), "count": psutil.cpu_count()}
        self.data_ready.emit(data)


class DiagnosisSummaryThread(QThread):
    """后台运行诊断，不阻塞 UI"""
    finished = pyqtSignal(object)

    def run(self):
        from core.diagnosis.system_diagnosis import SystemDiagnosis
        d = SystemDiagnosis()
        report = d.run_full_diagnosis()
        self.finished.emit(report)


# ═══════════════════════════════════════════════════════════════════════════
# 简单可靠的状态条
# ═══════════════════════════════════════════════════════════════════════════

class RingGauge(QWidget):
    """用标准 ProgressBar 替代自定义绘制，100% 可靠渲染。"""

    _bar_colors = {
        "green":  "QProgressBar::chunk { background: #22c55e; border-radius: 4px; }",
        "blue":   "QProgressBar::chunk { background: #3b82f6; border-radius: 4px; }",
        "yellow": "QProgressBar::chunk { background: #eab308; border-radius: 4px; }",
        "red":    "QProgressBar::chunk { background: #ef4444; border-radius: 4px; }",
        "purple": "QProgressBar::chunk { background: #8b5cf6; border-radius: 4px; }",
    }

    def __init__(self, color="blue"):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)
        self.setMinimumWidth(120)

        self._label = QLabel("--")
        self._label.setFont(QFont("Microsoft YaHei", 10, QFont.Weight.Bold))
        self._label.setStyleSheet("color: #0f172a; border: none;")
        self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._label)

        self._bar = QProgressBar()
        self._bar.setFixedHeight(14)
        self._bar.setTextVisible(False)
        self._bar.setStyleSheet(f"""
            QProgressBar {{
                background: #e2e8f0; border: none; border-radius: 7px;
            }}
            {self._bar_colors.get(color, self._bar_colors['blue'])}
        """)
        layout.addWidget(self._bar)

        self._detail = QLabel("--")
        self._detail.setFont(QFont("Microsoft YaHei", 8))
        self._detail.setStyleSheet("color: #94a3b8; border: none;")
        self._detail.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._detail)

    def set(self, value: float, label: str, detail: str):
        self._label.setText(f"{label}  {value:.0f}%")
        self._bar.setValue(int(value))
        self._detail.setText(detail)


# ═══════════════════════════════════════════════════════════════════════════
# 统计卡片
# ═══════════════════════════════════════════════════════════════════════════

class StatCard(QFrame):
    """纯色卡片 — 颜色即信息，无需图标"""

    _palette = {
        "#ef4444": ("#fef2f2", "#991b1b", "#dc2626"),  # 红
        "#3b82f6": ("#eff6ff", "#1e40af", "#2563eb"),  # 蓝
        "#22c55e": ("#f0fdf4", "#166534", "#16a34a"),  # 绿
        "#8b5cf6": ("#f5f3ff", "#5b21b6", "#7c3aed"),  # 紫
        "#eab308": ("#fefce8", "#854d0e", "#ca8a04"),  # 黄
    }

    def __init__(self, icon: str, label: str, value: str, accent: str = "#3b82f6"):
        super().__init__()
        bg, fg, border = self._palette.get(accent, self._palette["#3b82f6"])
        self.setStyleSheet(f"""
            QFrame {{
                background: {bg};
                border: 2px solid {border}30;
                border-radius: 16px;
                padding: 24px 16px;
            }}
        """)
        self.setMinimumHeight(100)

        layout = QVBoxLayout(self)
        layout.setSpacing(6)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.value_label = QLabel(value)
        self.value_label.setFont(QFont("Microsoft YaHei", 28, QFont.Weight.Bold))
        self.value_label.setStyleSheet("color: #0f172a; border: none;")
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.value_label)

        label_w = QLabel(label)
        label_w.setFont(QFont("Microsoft YaHei", 11))
        label_w.setStyleSheet("color: #475569; border: none;")
        label_w.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label_w)

    def set_value(self, v: str):
        self.value_label.setText(v)


# ═══════════════════════════════════════════════════════════════════════════
# 仪表盘主页
# ═══════════════════════════════════════════════════════════════════════════

class DashboardView(QWidget):

    def __init__(self):
        super().__init__()
        self._init_ui()
        self._start_monitoring()

    def _init_ui(self):
        main = QVBoxLayout(self)
        main.setContentsMargins(28, 24, 28, 24)
        main.setSpacing(20)

        # ── 标题行 ──
        title_row = QHBoxLayout()
        title = QLabel("📊 系统概览")
        title.setFont(QFont("Microsoft YaHei", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: #0f172a; border: none;")
        title_row.addWidget(title)
        title_row.addStretch()

        refresh = QPushButton("🔄 刷新")
        refresh.setStyleSheet("""
            QPushButton { background: #f1f5f9; border: 1px solid #e2e8f0; border-radius: 8px;
                          padding: 8px 16px; font-size: 12px; color: #475569; }
            QPushButton:hover { background: #e2e8f0; }
        """)
        refresh.clicked.connect(self._start_monitoring)
        title_row.addWidget(refresh)
        main.addLayout(title_row)

        # ── 四张核心卡片 ──
        cards_row = QHBoxLayout()
        cards_row.setSpacing(16)

        self.disk_card = StatCard("💾", "C 盘使用率", "--%", "#ef4444")
        cards_row.addWidget(self.disk_card)

        self.mem_card = StatCard("🧠", "内存使用率", "--%", "#3b82f6")
        cards_row.addWidget(self.mem_card)

        self.cpu_card = StatCard("⚡", "CPU 使用率", "--%", "#22c55e")
        cards_row.addWidget(self.cpu_card)

        self.health_card = StatCard("❤️", "系统健康", "检查中...", "#8b5cf6")
        cards_row.addWidget(self.health_card)

        main.addLayout(cards_row)

        # ── 环形仪表 + 诊断摘要 ──
        mid_row = QHBoxLayout()
        mid_row.setSpacing(16)

        # 环形仪表区
        gauges_frame = QFrame()
        gauges_frame.setStyleSheet("QFrame { background: #ffffff; border: 1px solid #e2e8f0; border-radius: 14px; }")
        gauges_layout = QHBoxLayout(gauges_frame)
        gauges_layout.setContentsMargins(20, 16, 20, 16)
        gauges_layout.setSpacing(20)

        self.disk_gauge = RingGauge("red")
        gauges_layout.addWidget(self.disk_gauge)
        self.mem_gauge = RingGauge("blue")
        gauges_layout.addWidget(self.mem_gauge)
        self.cpu_gauge = RingGauge("green")
        gauges_layout.addWidget(self.cpu_gauge)
        gauges_layout.addStretch()
        mid_row.addWidget(gauges_frame, 3)

        # 诊断摘要
        self.diag_card = QFrame()
        self.diag_card.setStyleSheet("QFrame { background: #ffffff; border: 1px solid #e2e8f0; border-radius: 14px; }")
        diag_layout = QVBoxLayout(self.diag_card)
        diag_layout.setContentsMargins(20, 16, 20, 16)
        diag_title = QLabel("🏥 系统诊断")
        diag_title.setFont(QFont("Microsoft YaHei", 14, QFont.Weight.Bold))
        diag_title.setStyleSheet("color: #0f172a; border: none;")
        diag_layout.addWidget(diag_title)

        self.diag_status = QLabel("正在检查...")
        self.diag_status.setFont(QFont("Microsoft YaHei", 11))
        self.diag_status.setStyleSheet("color: #64748b; border: none; padding: 8px 0;")
        self.diag_status.setWordWrap(True)
        diag_layout.addWidget(self.diag_status)

        self.diag_detail = QLabel("")
        self.diag_detail.setFont(QFont("Microsoft YaHei", 10))
        self.diag_detail.setStyleSheet("color: #94a3b8; border: none;")
        self.diag_detail.setWordWrap(True)
        diag_layout.addWidget(self.diag_detail)

        diag_layout.addStretch()

        run_diag = QPushButton("🔍 运行完整诊断")
        run_diag.setStyleSheet("""
            QPushButton { background: #2563eb; color: white; border: none; border-radius: 8px;
                          padding: 10px; font-size: 12px; font-weight: 600; }
            QPushButton:hover { background: #1d4ed8; }
        """)
        run_diag.clicked.connect(self._run_diagnosis)
        diag_layout.addWidget(run_diag)

        mid_row.addWidget(self.diag_card, 2)
        main.addLayout(mid_row)


    # ── 数据更新 ──

    def _start_monitoring(self):
        self._update_disk_mem_cpu()
        self._run_diagnosis()

    def _update_disk_mem_cpu(self):
        self._data_thread = DashboardDataThread()
        self._data_thread.data_ready.connect(self._on_hw_data)
        self._data_thread.start()

    def _on_hw_data(self, data: dict):
        if "disk" in data:
            d = data["disk"]
            pct = d["percent"]
            color = "#ef4444" if pct > 85 else ("#eab308" if pct > 70 else "#22c55e")
            self.disk_card.set_value(f"{pct:.1f}%")
            self.disk_gauge.set(pct, "C 盘", f"{fmt(d['used'])} / {fmt(d['total'])}")
        if "memory" in data:
            m = data["memory"]
            self.mem_card.set_value(f"{m['percent']:.1f}%")
            self.mem_gauge.set(m["percent"], "内存", f"{fmt(m['used'])} / {fmt(m['total'])}")
        if "cpu" in data:
            c = data["cpu"]
            self.cpu_card.set_value(f"{c['percent']:.1f}%")
            self.cpu_gauge.set(c["percent"], "CPU", f"{c['count']} 核心")

    # ── 诊断 ──

    def _run_diagnosis(self):
        self.diag_status.setText("正在检查系统健康状态...")
        self.diag_detail.setText("")
        self._diag_thread = DiagnosisSummaryThread()
        self._diag_thread.finished.connect(self._on_diag_done)
        self._diag_thread.start()

    def _on_diag_done(self, report):
        score = report.health_score
        self.health_card.set_value(f"{score} 分")

        if score >= 95:
            self.diag_status.setText("✅ 你的电脑很健康，没有发现问题")
            self.diag_detail.setText("各项指标正常，请继续保持良好的使用习惯")
        elif score >= 80:
            self.diag_status.setText(f"⚠️ 系统健康分数 {score} 分，有少量可优化项")
            self.diag_detail.setText(f"发现 {len(report.problems)} 个问题，建议切换到「系统诊断」页面查看详情")
        elif score >= 60:
            self.diag_status.setText(f"🔶 系统健康分数 {score} 分，建议尽快处理")
            self.diag_detail.setText(f"发现 {len(report.problems)} 个问题，请切换到「系统诊断」页面处理")
        else:
            self.diag_status.setText(f"🔴 系统健康分数 {score} 分，需要立即处理")
            self.diag_detail.setText(f"发现 {len(report.problems)} 个问题，建议立刻处理")

        # 列出前 3 个问题
        if report.problems:
            self.diag_detail.setText(
                self.diag_detail.text() + "\n\n主要问题:\n" +
                "\n".join(f"  • {p.title}" for p in report.problems[:3])
            )

# ═══════════════════════════════════════════════════════════════════════════
# 导出（兼容旧引用）
# ═══════════════════════════════════════════════════════════════════════════

CircularProgress = RingGauge


class RecommendationsWidget(QWidget):
    """推荐列表（供推荐页面使用）"""
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        self.content = QWidget()
        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setSpacing(8)
        self.scroll.setWidget(self.content)
        layout.addWidget(self.scroll)
        self._recs = []

    def update_recommendations(self, recs):
        self._recs = recs
        while self.content_layout.count():
            w = self.content_layout.takeAt(0)
            if w.widget(): w.widget().deleteLater()
        if not recs:
            empty = QLabel("暂无优化建议 ✨")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty.setStyleSheet("color: #94a3b8; padding: 24px; font-size: 13px; border: none;")
            self.content_layout.addWidget(empty)
        for r in recs[:8]:
            self.content_layout.addWidget(self._make_card(r))
        self.content_layout.addStretch()

    def _make_card(self, rec) -> QFrame:
        card = QFrame()
        card.setStyleSheet("QFrame { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; }")
        layout = QHBoxLayout(card)
        layout.setContentsMargins(14, 10, 14, 10)
        prio = {"high": "#ef4444", "medium": "#eab308", "low": "#22c55e"}.get(rec.risk_level, "#94a3b8")
        dot = QLabel("●")
        dot.setStyleSheet(f"color: {prio}; font-size: 13px; border: none;")
        layout.addWidget(dot)
        col = QVBoxLayout()
        t = QLabel(rec.title)
        t.setFont(QFont("Microsoft YaHei", 11, QFont.Weight.Bold))
        t.setStyleSheet("color: #0f172a; border: none;")
        col.addWidget(t)
        d = QLabel(rec.description)
        d.setFont(QFont("Microsoft YaHei", 9))
        d.setStyleSheet("color: #64748b; border: none;")
        d.setWordWrap(True)
        col.addWidget(d)
        layout.addLayout(col)
        if rec.estimated_savings > 0:
            sv = QLabel(fmt(rec.estimated_savings))
            sv.setStyleSheet("color: #16a34a; font-size: 11px; font-weight: 600; border: none;")
            layout.addWidget(sv)
        return card
