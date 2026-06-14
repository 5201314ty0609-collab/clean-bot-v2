"""
CleanBot v2.0 — 仪表盘视图

美观的系统监控仪表盘。
"""

import sys
import os
from pathlib import Path
from typing import Optional

# PyQt6 imports
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QGridLayout, QProgressBar, QScrollArea, QGroupBox,
    QSizePolicy, QSpacerItem
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt6.QtGui import QFont, QColor, QPalette, QPainter, QBrush, QPen

# 导入核心模块
from core.monitor.disk_monitor import DiskMonitor, format_size
from core.diagnosis.system_diagnosis import SystemDiagnosis
from core.ai.recommendation import RecommendationEngine


class DashboardDataThread(QThread):
    """仪表盘数据采集线程 - 避免 psutil 阻塞 UI"""
    data_ready = pyqtSignal(dict)

    def __init__(self):
        super().__init__()

    def run(self):
        import psutil
        from core.utils import get_system_drive

        data = {}

        # 磁盘使用情况
        try:
            system_drive = get_system_drive()
            disk_usage = psutil.disk_usage(system_drive)
            data["disk"] = {
                "total": disk_usage.total,
                "used": disk_usage.used,
                "free": disk_usage.free,
                "percent": disk_usage.percent,
            }
        except (PermissionError, OSError):
            pass

        # 内存使用情况
        memory = psutil.virtual_memory()
        data["memory"] = {
            "total": memory.total,
            "used": memory.used,
            "available": memory.available,
            "percent": memory.percent,
        }

        # CPU 使用情况
        cpu_percent = psutil.cpu_percent(interval=0.1)
        data["cpu"] = {
            "percent": cpu_percent,
            "count": psutil.cpu_count(),
        }

        self.data_ready.emit(data)


class CircularProgress(QWidget):
    """环形进度条"""

    def __init__(self, value: float = 0, max_value: float = 100,
                 title: str = "", subtitle: str = "", color: str = "#2196F3"):
        super().__init__()
        self.value = value
        self.max_value = max_value
        self.title = title
        self.subtitle = subtitle
        self.color = QColor(color)

        self.setMinimumSize(150, 150)
        self.setMaximumSize(200, 200)

    def set_value(self, value: float):
        """设置值"""
        self.value = value
        self.update()

    def paintEvent(self, event):
        """绘制事件"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 计算尺寸
        width = self.width()
        height = self.height()
        size = min(width, height)
        center_x = width / 2
        center_y = height / 2
        radius = size / 2 - 20

        # 绘制背景圆环
        painter.setPen(QPen(QColor("#E0E0E0"), 12, Qt.PenStyle.SolidLine))
        painter.drawEllipse(int(center_x - radius), int(center_y - radius),
                           int(radius * 2), int(radius * 2))

        # 绘制进度圆环
        if self.max_value > 0:
            angle = int(360 * self.value / self.max_value)
            painter.setPen(QPen(self.color, 12, Qt.PenStyle.SolidLine))
            painter.drawArc(int(center_x - radius), int(center_y - radius),
                           int(radius * 2), int(radius * 2),
                           90 * 16, -angle * 16)

        # 绘制中心文字
        painter.setPen(QColor("#333333"))
        painter.setFont(QFont("Microsoft YaHei", 24, QFont.Weight.Bold))
        painter.drawText(int(center_x - 50), int(center_y - 20), 100, 40,
                        Qt.AlignmentFlag.AlignCenter, f"{self.value:.0f}%")

        # 绘制标题
        painter.setFont(QFont("Microsoft YaHei", 10))
        painter.setPen(QColor("#666666"))
        painter.drawText(int(center_x - 70), int(center_y + 20), 140, 30,
                        Qt.AlignmentFlag.AlignCenter, self.title)

        # 绘制副标题
        painter.setFont(QFont("Microsoft YaHei", 8))
        painter.setPen(QColor("#999999"))
        painter.drawText(int(center_x - 70), int(center_y + 40), 140, 20,
                        Qt.AlignmentFlag.AlignCenter, self.subtitle)

        painter.end()


class StatCard(QFrame):
    """统计卡片"""

    def __init__(self, title: str, value: str, icon: str = "", color: str = "#2196F3"):
        super().__init__()
        self.title = title
        self.value = value
        self.icon = icon
        self.color = color

        self._init_ui()

    def _init_ui(self):
        """初始化 UI"""
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 1px solid #E0E0E0;
                border-radius: 10px;
                padding: 15px;
            }}
            QFrame:hover {{
                border: 1px solid {self.color};
                background-color: #F5F5F5;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # 标题
        title_label = QLabel(self.title)
        title_label.setFont(QFont("Microsoft YaHei", 10))
        title_label.setStyleSheet("color: #666666;")
        layout.addWidget(title_label)

        # 值
        value_label = QLabel(self.value)
        value_label.setFont(QFont("Microsoft YaHei", 24, QFont.Weight.Bold))
        value_label.setStyleSheet(f"color: {self.color};")
        layout.addWidget(value_label)

        # 图标（简化）
        if self.icon:
            icon_label = QLabel(self.icon)
            icon_label.setFont(QFont("Microsoft YaHei", 12))
            icon_label.setStyleSheet("color: #999999;")
            layout.addWidget(icon_label)

    def set_value(self, value: str):
        """设置值"""
        self.value = value
        # 更新 UI
        value_label = self.findChild(QLabel)
        if value_label:
            value_label.setText(value)


class RecommendationsWidget(QWidget):
    """推荐列表控件"""

    def __init__(self):
        super().__init__()
        self.recommendations = []
        self._init_ui()

    def _init_ui(self):
        """初始化 UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # 标题
        title_layout = QHBoxLayout()
        title_label = QLabel("智能推荐")
        title_label.setFont(QFont("Microsoft YaHei", 14, QFont.Weight.Bold))
        title_layout.addWidget(title_label)

        title_layout.addStretch()

        refresh_button = QPushButton("刷新")
        refresh_button.clicked.connect(self._refresh)
        title_layout.addWidget(refresh_button)

        layout.addLayout(title_layout)

        # 推荐列表
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_area.setWidget(self.scroll_content)
        layout.addWidget(self.scroll_area)

    def _refresh(self):
        """刷新推荐"""
        engine = RecommendationEngine()
        recommendations = engine.generate_recommendations()
        self.update_recommendations(recommendations)

    def update_recommendations(self, recommendations):
        """更新推荐列表"""
        self.recommendations = recommendations

        # 清空现有内容
        while self.scroll_layout.count():
            child = self.scroll_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # 添加新推荐
        for rec in recommendations:
            card = self._create_recommendation_card(rec)
            self.scroll_layout.addWidget(card)

        # 添加弹性空间
        self.scroll_layout.addStretch()

    def _create_recommendation_card(self, recommendation) -> QFrame:
        """创建推荐卡片"""
        card = QFrame()
        card.setFrameStyle(QFrame.Shape.StyledPanel)
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                padding: 12px;
            }
            QFrame:hover {
                border: 1px solid #2196F3;
            }
        """)

        layout = QHBoxLayout(card)
        layout.setSpacing(15)

        # 优先级指示器
        priority_color = {
            "high": "#FF6B6B",
            "medium": "#FFD93D",
            "low": "#6BCB77",
        }.get(recommendation.risk_level, "#2196F3")

        priority_indicator = QLabel()
        priority_indicator.setFixedSize(8, 8)
        priority_indicator.setStyleSheet(f"""
            background-color: {priority_color};
            border-radius: 4px;
        """)
        layout.addWidget(priority_indicator)

        # 内容
        content_layout = QVBoxLayout()

        title_label = QLabel(recommendation.title)
        title_label.setFont(QFont("Microsoft YaHei", 11, QFont.Weight.Bold))
        content_layout.addWidget(title_label)

        desc_label = QLabel(recommendation.description)
        desc_label.setFont(QFont("Microsoft YaHei", 9))
        desc_label.setStyleSheet("color: #666666;")
        desc_label.setWordWrap(True)
        content_layout.addWidget(desc_label)

        # 标签
        tags_layout = QHBoxLayout()

        category_tag = QLabel(recommendation.category)
        category_tag.setStyleSheet("""
            background-color: #E3F2FD;
            color: #1976D2;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 10px;
        """)
        tags_layout.addWidget(category_tag)

        if recommendation.estimated_savings > 0:
            savings_tag = QLabel(f"节省 {format_size(recommendation.estimated_savings)}")
            savings_tag.setStyleSheet("""
                background-color: #E8F5E9;
                color: #388E3C;
                padding: 2px 8px;
                border-radius: 4px;
                font-size: 10px;
            """)
            tags_layout.addWidget(savings_tag)

        tags_layout.addStretch()
        content_layout.addLayout(tags_layout)

        layout.addLayout(content_layout)

        # 操作按钮
        button_layout = QVBoxLayout()

        accept_button = QPushButton("执行")
        accept_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        accept_button.clicked.connect(lambda: self._accept_recommendation(recommendation))
        button_layout.addWidget(accept_button)

        reject_button = QPushButton("忽略")
        reject_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #666666;
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #F5F5F5;
            }
        """)
        reject_button.clicked.connect(lambda: self._reject_recommendation(recommendation))
        button_layout.addWidget(reject_button)

        layout.addLayout(button_layout)

        return card

    def _accept_recommendation(self, recommendation):
        """接受推荐"""
        recommendation.is_accepted = True
        # 根据推荐类型执行相应操作
        if recommendation.action == "clean_disk":
            # 触发磁盘清理
            pass
        elif recommendation.action == "free_memory":
            # 提示用户关闭程序
            pass
        self._refresh()

    def _reject_recommendation(self, recommendation):
        """拒绝推荐"""
        recommendation.is_rejected = True
        self._refresh()


class DashboardView(QWidget):
    """仪表盘视图"""

    def __init__(self):
        super().__init__()

        # 初始化监控器
        self.disk_monitor = DiskMonitor()
        self.diagnosis = SystemDiagnosis()
        self.recommendation_engine = RecommendationEngine()

        # 初始化 UI
        self._init_ui()

        # 启动定时器
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_data)
        self.timer.start(5000)  # 每 5 秒更新

        # 初始更新
        self._update_data()

    def _init_ui(self):
        """初始化 UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # 标题
        title_layout = QHBoxLayout()
        title_label = QLabel("系统监控仪表盘")
        title_label.setFont(QFont("Microsoft YaHei", 20, QFont.Weight.Bold))
        title_layout.addWidget(title_label)

        title_layout.addStretch()

        # 刷新按钮
        refresh_button = QPushButton("刷新")
        refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        refresh_button.clicked.connect(self._update_data)
        title_layout.addWidget(refresh_button)

        layout.addLayout(title_layout)

        # 统计卡片区域
        stats_layout = QHBoxLayout()

        # C 盘空间卡片
        self.disk_card = StatCard(
            title="C 盘空间",
            value="0%",
            icon="💾",
            color="#FF6B6B",
        )
        stats_layout.addWidget(self.disk_card)

        # 内存使用卡片
        self.memory_card = StatCard(
            title="内存使用",
            value="0%",
            icon="🧠",
            color="#4ECDC4",
        )
        stats_layout.addWidget(self.memory_card)

        # CPU 使用卡片
        self.cpu_card = StatCard(
            title="CPU 使用",
            value="0%",
            icon="⚡",
            color="#45B7D1",
        )
        stats_layout.addWidget(self.cpu_card)

        # 系统健康卡片
        self.health_card = StatCard(
            title="系统健康",
            value="100 分",
            icon="❤️",
            color="#96CEB4",
        )
        stats_layout.addWidget(self.health_card)

        layout.addLayout(stats_layout)

        # 环形进度条区域
        progress_layout = QHBoxLayout()

        # C 盘使用率
        self.disk_progress = CircularProgress(
            value=0,
            title="C 盘使用率",
            subtitle="0 GB / 0 GB",
            color="#FF6B6B",
        )
        progress_layout.addWidget(self.disk_progress)

        # 内存使用率
        self.memory_progress = CircularProgress(
            value=0,
            title="内存使用率",
            subtitle="0 GB / 0 GB",
            color="#4ECDC4",
        )
        progress_layout.addWidget(self.memory_progress)

        # CPU 使用率
        self.cpu_progress = CircularProgress(
            value=0,
            title="CPU 使用率",
            subtitle="0 核心",
            color="#45B7D1",
        )
        progress_layout.addWidget(self.cpu_progress)

        layout.addLayout(progress_layout)

        # 推荐区域
        self.recommendations_widget = RecommendationsWidget()
        layout.addWidget(self.recommendations_widget)

    def _update_data(self):
        """更新数据 - 使用后台线程避免阻塞 UI"""
        self._data_thread = DashboardDataThread()
        self._data_thread.data_ready.connect(self._on_data_ready)
        self._data_thread.start()

    def _on_data_ready(self, data: dict):
        """数据就绪，更新 UI"""
        # 更新磁盘使用情况
        if "disk" in data:
            disk = data["disk"]
            self.disk_card.set_value(f"{disk['percent']:.1f}%")
            self.disk_progress.set_value(disk['percent'])
            self.disk_progress.subtitle = f"{format_size(disk['used'])} / {format_size(disk['total'])}"

        # 更新内存使用情况
        if "memory" in data:
            memory = data["memory"]
            self.memory_card.set_value(f"{memory['percent']:.1f}%")
            self.memory_progress.set_value(memory['percent'])
            self.memory_progress.subtitle = f"{format_size(memory['used'])} / {format_size(memory['total'])}"

        # 更新 CPU 使用情况
        if "cpu" in data:
            cpu = data["cpu"]
            self.cpu_card.set_value(f"{cpu['percent']:.1f}%")
            self.cpu_progress.set_value(cpu['percent'])
            self.cpu_progress.subtitle = f"{cpu['count']} 核心"

        # 更新系统健康分数
        if "health_score" in data:
            self.health_card.set_value(f"{data['health_score']} 分")


def main():
    """测试入口"""
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)

    # 创建仪表盘
    dashboard = DashboardView()
    dashboard.setWindowTitle("CleanBot v2.0 — 仪表盘")
    dashboard.resize(1000, 800)
    dashboard.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
