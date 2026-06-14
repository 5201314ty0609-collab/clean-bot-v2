"""
CleanBot v2.0 — 主窗口

完整的 GUI 界面，整合所有功能。
"""

import sys
import os
from pathlib import Path
from typing import Optional

# PyQt6 imports
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QProgressBar, QTableWidget, QTableWidgetItem,
    QCheckBox, QGroupBox, QScrollArea, QFrame, QSplitter, QMessageBox,
    QFileDialog, QHeaderView, QAbstractItemView, QTabWidget, QStackedWidget,
    QSizePolicy, QSpacerItem
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QSize
from PyQt6.QtGui import QFont, QColor, QPalette, QIcon, QAction

# 导入核心模块
from core.diagnosis.system_diagnosis import SystemDiagnosis
from core.monitor.disk_monitor import DiskMonitor, format_size
from core.ai.recommendation import RecommendationEngine
from core.scanner.file_scanner import FileScanner
from core.cleaner.file_cleaner import FileCleaner

# 导入自定义控件
from ui.dashboard import DashboardView, CircularProgress, StatCard, RecommendationsWidget

# 导入对话系统
from core.ai.dialog_system import DialogSystem, DialogContext, Mood


class ScanThread(QThread):
    """扫描线程"""
    progress = pyqtSignal(int, int)
    finished = pyqtSignal(object)

    def __init__(self, root_path: str = None):
        super().__init__()
        from core.utils import get_system_drive
        self.root_path = root_path or get_system_drive()

    def run(self):
        scanner = FileScanner(self.root_path)
        result = scanner.scan(progress_callback=lambda c, s: self.progress.emit(c, s))
        self.finished.emit(result)


class CleanThread(QThread):
    """清理线程"""
    progress = pyqtSignal(int, int, str)
    finished = pyqtSignal(object)

    def __init__(self, files: list, use_trash: bool = True):
        super().__init__()
        self.files = files
        self.use_trash = use_trash

    def run(self):
        cleaner = FileCleaner(use_trash=self.use_trash)
        result = cleaner.clean(
            self.files,
            progress_callback=lambda prog: self.progress.emit(prog.current, prog.total, prog.current_file)
        )
        self.finished.emit(result)


class DiagnosisThread(QThread):
    """诊断线程"""
    finished = pyqtSignal(object)

    def __init__(self):
        super().__init__()

    def run(self):
        diagnosis = SystemDiagnosis()
        report = diagnosis.run_full_diagnosis()
        self.finished.emit(report)


class MonitorThread(QThread):
    """磁盘监控线程 - 避免 psutil 阻塞 UI"""
    data_ready = pyqtSignal(dict)

    def __init__(self):
        super().__init__()

    def run(self):
        import psutil
        from core.utils import get_system_drive

        data = {}
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

        self.data_ready.emit(data)


class RecommendationThread(QThread):
    """推荐生成线程 - 避免阻塞 UI"""
    finished = pyqtSignal(list)

    def __init__(self):
        super().__init__()

    def run(self):
        engine = RecommendationEngine()
        recommendations = engine.generate_recommendations()
        self.finished.emit(recommendations)


class MainWindow(QMainWindow):
    """主窗口"""

    def __init__(self, robot=None):
        super().__init__()

        self.setWindowTitle("CleanBot v2.0 — 智能桌面清理机器人")
        self.setMinimumSize(1200, 800)

        # 扫描结果
        self.scan_result = None
        self.files_to_clean = []

        # Robot reference (optional, for task integration)
        self.robot = robot

        # Dialog system
        self.dialog = DialogSystem()

        # 初始化 UI
        self._init_ui()

        # 初始化样式
        self._init_style()

        # 初始化定时器
        self._init_timers()

        # Show greeting if robot is available
        if self.robot:
            context = DialogContext()
            greeting = self.dialog.greet(context)
            self.robot.show_speech(greeting)

    def _init_ui(self):
        """初始化 UI"""
        # 中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # 顶部工具栏
        toolbar = self._create_toolbar()
        main_layout.addWidget(toolbar)

        # 内容区域
        content_layout = QHBoxLayout()
        content_layout.setSpacing(0)
        content_layout.setContentsMargins(0, 0, 0, 0)

        # 左侧导航栏
        nav_widget = self._create_navigation()
        content_layout.addWidget(nav_widget)

        # 右侧内容区域
        self.content_stack = QStackedWidget()
        content_layout.addWidget(self.content_stack)

        # 创建各个页面
        self._create_pages()

        main_layout.addLayout(content_layout)

        # 底部状态栏
        self.statusBar().showMessage("准备就绪")

    def _create_toolbar(self) -> QWidget:
        """创建工具栏"""
        toolbar = QFrame()
        toolbar.setFrameStyle(QFrame.Shape.StyledPanel)
        toolbar.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1565C0, stop:1 #1976D2);
                border: none;
                border-bottom: 1px solid #0D47A1;
            }
        """)

        layout = QHBoxLayout(toolbar)
        layout.setContentsMargins(20, 10, 20, 10)

        # 标题
        title_label = QLabel("CleanBot v2.0")
        title_label.setFont(QFont("Microsoft YaHei", 18, QFont.Weight.Bold))
        title_label.setStyleSheet("color: white;")
        layout.addWidget(title_label)

        # 副标题
        subtitle_label = QLabel("智能桌面清理机器人")
        subtitle_label.setFont(QFont("Microsoft YaHei", 10))
        subtitle_label.setStyleSheet("color: rgba(255, 255, 255, 0.8);")
        layout.addWidget(subtitle_label)

        layout.addStretch()

        # 扫描按钮
        self.scan_button = QPushButton("开始扫描")
        self.scan_button.setFont(QFont("Microsoft YaHei", 11))
        self.scan_button.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #2196F3;
                border: none;
                border-radius: 5px;
                padding: 8px 20px;
            }
            QPushButton:hover {
                background-color: #E3F2FD;
            }
        """)
        self.scan_button.clicked.connect(self._start_scan)
        layout.addWidget(self.scan_button)

        # 清理按钮
        self.clean_button = QPushButton("清理选中")
        self.clean_button.setFont(QFont("Microsoft YaHei", 11))
        self.clean_button.setStyleSheet("""
            QPushButton {
                background-color: #FF6B6B;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 20px;
            }
            QPushButton:hover {
                background-color: #FF5252;
            }
        """)
        self.clean_button.setEnabled(False)
        self.clean_button.clicked.connect(self._start_clean)
        layout.addWidget(self.clean_button)

        return toolbar

    def _create_navigation(self) -> QWidget:
        """创建导航栏"""
        nav = QFrame()
        nav.setFrameStyle(QFrame.Shape.StyledPanel)
        nav.setFixedWidth(200)
        nav.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border: none;
                border-right: 1px solid #DEE2E6;
            }
        """)

        layout = QVBoxLayout(nav)
        layout.setSpacing(5)
        layout.setContentsMargins(10, 20, 10, 20)

        # 导航按钮
        nav_buttons = [
            ("仪表盘", 0),
            ("系统诊断", 1),
            ("文件扫描", 2),
            ("智能推荐", 3),
            ("磁盘监控", 4),
            ("设置", 5),
        ]

        for text, index in nav_buttons:
            button = QPushButton(text)
            button.setFont(QFont("Microsoft YaHei", 11))
            button.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #495057;
                    border: none;
                    border-radius: 8px;
                    padding: 12px 16px;
                    text-align: left;
                    font-size: 13px;
                }
                QPushButton:hover {
                    background-color: #F1F3F5;
                }
                QPushButton:checked {
                    background-color: #E3F2FD;
                    color: #1565C0;
                    font-weight: bold;
                }
            """)
            button.setCheckable(True)
            button.clicked.connect(lambda checked, idx=index: self._switch_page(idx))
            layout.addWidget(button)

            # 保存第一个按钮的引用
            if index == 0:
                self.nav_buttons = [button]
            else:
                self.nav_buttons.append(button)

        layout.addStretch()

        return nav

    def _create_pages(self):
        """创建各个页面"""
        # 仪表盘页面
        self.dashboard_page = DashboardView()
        self.content_stack.addWidget(self.dashboard_page)

        # 系统诊断页面
        self.diagnosis_page = self._create_diagnosis_page()
        self.content_stack.addWidget(self.diagnosis_page)

        # 文件扫描页面
        self.scan_page = self._create_scan_page()
        self.content_stack.addWidget(self.scan_page)

        # 智能推荐页面
        self.recommend_page = self._create_recommend_page()
        self.content_stack.addWidget(self.recommend_page)

        # 磁盘监控页面
        self.monitor_page = self._create_monitor_page()
        self.content_stack.addWidget(self.monitor_page)

        # 设置页面
        self.settings_page = self._create_settings_page()
        self.content_stack.addWidget(self.settings_page)

        # 默认选中仪表盘
        self.nav_buttons[0].setChecked(True)

    def _create_diagnosis_page(self) -> QWidget:
        """创建系统诊断页面"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # 标题
        title_layout = QHBoxLayout()
        title_label = QLabel("系统诊断")
        title_label.setFont(QFont("Microsoft YaHei", 20, QFont.Weight.Bold))
        title_layout.addWidget(title_label)

        title_layout.addStretch()

        # 诊断按钮
        diagnosis_button = QPushButton("开始诊断")
        diagnosis_button.setFont(QFont("Microsoft YaHei", 11))
        diagnosis_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 20px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        diagnosis_button.clicked.connect(self._start_diagnosis)
        title_layout.addWidget(diagnosis_button)

        layout.addLayout(title_layout)

        # 健康分数
        self.health_frame = QFrame()
        self.health_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        self.health_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #E0E0E0;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        health_layout = QHBoxLayout(self.health_frame)

        self.health_progress = CircularProgress(
            value=100,
            title="系统健康",
            subtitle="100 分",
            color="#4CAF50",
        )
        health_layout.addWidget(self.health_progress)

        # 问题列表
        problems_layout = QVBoxLayout()
        problems_title = QLabel("检测到的问题")
        problems_title.setFont(QFont("Microsoft YaHei", 14, QFont.Weight.Bold))
        problems_layout.addWidget(problems_title)

        self.problems_table = QTableWidget()
        self.problems_table.setColumnCount(4)
        self.problems_table.setHorizontalHeaderLabels(["严重程度", "问题", "描述", "解决方案"])
        self.problems_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.problems_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.problems_table.setAlternatingRowColors(True)
        problems_layout.addWidget(self.problems_table)

        health_layout.addLayout(problems_layout)
        layout.addWidget(self.health_frame)

        return page

    def _create_scan_page(self) -> QWidget:
        """创建文件扫描页面"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # 标题
        title_layout = QHBoxLayout()
        title_label = QLabel("文件扫描")
        title_label.setFont(QFont("Microsoft YaHei", 20, QFont.Weight.Bold))
        title_layout.addWidget(title_label)

        title_layout.addStretch()

        # 扫描按钮
        scan_button = QPushButton("开始扫描")
        scan_button.setFont(QFont("Microsoft YaHei", 11))
        scan_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 20px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        scan_button.clicked.connect(self._start_scan)
        title_layout.addWidget(scan_button)

        layout.addLayout(title_layout)

        # 进度条
        self.scan_progress = QProgressBar()
        self.scan_progress.setVisible(False)
        layout.addWidget(self.scan_progress)

        # 统计信息
        stats_layout = QHBoxLayout()

        self.total_files_label = QLabel("总文件数: 0")
        self.total_files_label.setFont(QFont("Microsoft YaHei", 12))
        stats_layout.addWidget(self.total_files_label)

        self.total_size_label = QLabel("总大小: 0 MB")
        self.total_size_label.setFont(QFont("Microsoft YaHei", 12))
        stats_layout.addWidget(self.total_size_label)

        self.safe_files_label = QLabel("可清理: 0 个")
        self.safe_files_label.setFont(QFont("Microsoft YaHei", 12))
        stats_layout.addWidget(self.safe_files_label)

        self.safe_size_label = QLabel("可释放: 0 MB")
        self.safe_size_label.setFont(QFont("Microsoft YaHei", 12))
        stats_layout.addWidget(self.safe_size_label)

        stats_layout.addStretch()
        layout.addLayout(stats_layout)

        # 风险分布标签
        risk_layout = QHBoxLayout()
        self.risk_safe_label = QLabel("Safe: 0")
        self.risk_safe_label.setFont(QFont("Microsoft YaHei", 10))
        self.risk_safe_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
        risk_layout.addWidget(self.risk_safe_label)

        self.risk_low_label = QLabel("Low: 0")
        self.risk_low_label.setFont(QFont("Microsoft YaHei", 10))
        self.risk_low_label.setStyleSheet("color: #8BC34A; font-weight: bold;")
        risk_layout.addWidget(self.risk_low_label)

        self.risk_medium_label = QLabel("Medium: 0")
        self.risk_medium_label.setFont(QFont("Microsoft YaHei", 10))
        self.risk_medium_label.setStyleSheet("color: #FFC107; font-weight: bold;")
        risk_layout.addWidget(self.risk_medium_label)

        self.risk_high_label = QLabel("High: 0")
        self.risk_high_label.setFont(QFont("Microsoft YaHei", 10))
        self.risk_high_label.setStyleSheet("color: #FF5722; font-weight: bold;")
        risk_layout.addWidget(self.risk_high_label)

        risk_layout.addStretch()
        layout.addLayout(risk_layout)

        # 文件表格
        self.files_table = QTableWidget()
        self.files_table.setColumnCount(7)
        self.files_table.setHorizontalHeaderLabels(["选择", "文件路径", "大小", "类型名称", "风险等级", "删除影响", "修改时间"])
        self.files_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.files_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.files_table.setAlternatingRowColors(True)
        layout.addWidget(self.files_table)

        # 全选/取消全选
        select_layout = QHBoxLayout()

        self.select_all_checkbox = QCheckBox("全选")
        self.select_all_checkbox.stateChanged.connect(self._toggle_select_all)
        select_layout.addWidget(self.select_all_checkbox)

        self.selected_label = QLabel("已选择: 0 个文件, 0 MB")
        self.selected_label.setFont(QFont("Microsoft YaHei", 10))
        select_layout.addWidget(self.selected_label)

        select_layout.addStretch()

        # 清理按钮
        clean_button = QPushButton("清理选中文件")
        clean_button.setFont(QFont("Microsoft YaHei", 11))
        clean_button.setStyleSheet("""
            QPushButton {
                background-color: #FF6B6B;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 20px;
            }
            QPushButton:hover {
                background-color: #FF5252;
            }
        """)
        clean_button.clicked.connect(self._start_clean)
        select_layout.addWidget(clean_button)

        layout.addLayout(select_layout)

        return page

    def _create_recommend_page(self) -> QWidget:
        """创建智能推荐页面"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # 标题
        title_layout = QHBoxLayout()
        title_label = QLabel("智能推荐")
        title_label.setFont(QFont("Microsoft YaHei", 20, QFont.Weight.Bold))
        title_layout.addWidget(title_label)

        title_layout.addStretch()

        # 刷新按钮
        refresh_button = QPushButton("刷新推荐")
        refresh_button.setFont(QFont("Microsoft YaHei", 11))
        refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 20px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        refresh_button.clicked.connect(self._refresh_recommendations)
        title_layout.addWidget(refresh_button)

        layout.addLayout(title_layout)

        # 推荐列表
        self.recommendations_widget = RecommendationsWidget()
        layout.addWidget(self.recommendations_widget)

        return page

    def _create_monitor_page(self) -> QWidget:
        """创建磁盘监控页面"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # 标题
        title_layout = QHBoxLayout()
        title_label = QLabel("磁盘监控")
        title_label.setFont(QFont("Microsoft YaHei", 20, QFont.Weight.Bold))
        title_layout.addWidget(title_label)

        title_layout.addStretch()

        # 监控按钮
        self.monitor_button = QPushButton("开始监控")
        self.monitor_button.setFont(QFont("Microsoft YaHei", 11))
        self.monitor_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 20px;
            }
            QPushButton:hover {
                background-color: #388E3C;
            }
        """)
        self.monitor_button.clicked.connect(self._toggle_monitor)
        title_layout.addWidget(self.monitor_button)

        layout.addLayout(title_layout)

        # 监控信息
        self.monitor_frame = QFrame()
        self.monitor_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        self.monitor_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #E0E0E0;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        monitor_layout = QVBoxLayout(self.monitor_frame)

        # 磁盘使用情况
        disk_layout = QHBoxLayout()

        self.disk_progress = CircularProgress(
            value=0,
            title="C 盘使用率",
            subtitle="0 GB / 0 GB",
            color="#FF6B6B",
        )
        disk_layout.addWidget(self.disk_progress)

        # 磁盘信息
        disk_info_layout = QVBoxLayout()

        self.disk_total_label = QLabel("总容量: 0 GB")
        self.disk_total_label.setFont(QFont("Microsoft YaHei", 12))
        disk_info_layout.addWidget(self.disk_total_label)

        self.disk_used_label = QLabel("已使用: 0 GB")
        self.disk_used_label.setFont(QFont("Microsoft YaHei", 12))
        disk_info_layout.addWidget(self.disk_used_label)

        self.disk_free_label = QLabel("剩余: 0 GB")
        self.disk_free_label.setFont(QFont("Microsoft YaHei", 12))
        disk_info_layout.addWidget(self.disk_free_label)

        self.disk_trend_label = QLabel("趋势: 稳定")
        self.disk_trend_label.setFont(QFont("Microsoft YaHei", 12))
        disk_info_layout.addWidget(self.disk_trend_label)

        disk_layout.addLayout(disk_info_layout)
        monitor_layout.addLayout(disk_layout)

        # 告警列表
        alerts_title = QLabel("告警信息")
        alerts_title.setFont(QFont("Microsoft YaHei", 14, QFont.Weight.Bold))
        monitor_layout.addWidget(alerts_title)

        self.alerts_table = QTableWidget()
        self.alerts_table.setColumnCount(3)
        self.alerts_table.setHorizontalHeaderLabels(["级别", "消息", "时间"])
        self.alerts_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.alerts_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.alerts_table.setAlternatingRowColors(True)
        monitor_layout.addWidget(self.alerts_table)

        layout.addWidget(self.monitor_frame)

        return page

    def _create_settings_page(self) -> QWidget:
        """创建设置页面"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # 标题
        title_label = QLabel("设置")
        title_label.setFont(QFont("Microsoft YaHei", 20, QFont.Weight.Bold))
        layout.addWidget(title_label)

        # 设置选项
        settings_group = QGroupBox("清理设置")
        settings_layout = QVBoxLayout(settings_group)

        # 使用回收站
        self.use_trash_checkbox = QCheckBox("删除文件时移到回收站（推荐）")
        self.use_trash_checkbox.setChecked(True)
        self.use_trash_checkbox.setFont(QFont("Microsoft YaHei", 11))
        settings_layout.addWidget(self.use_trash_checkbox)

        # 备份后删除
        self.backup_checkbox = QCheckBox("删除前备份文件")
        self.backup_checkbox.setFont(QFont("Microsoft YaHei", 11))
        settings_layout.addWidget(self.backup_checkbox)

        # 自动清理
        self.auto_clean_checkbox = QCheckBox("启用自动清理")
        self.auto_clean_checkbox.setFont(QFont("Microsoft YaHei", 11))
        settings_layout.addWidget(self.auto_clean_checkbox)

        layout.addWidget(settings_group)

        # 监控设置
        monitor_group = QGroupBox("监控设置")
        monitor_layout = QVBoxLayout(monitor_group)

        # 监控间隔
        interval_layout = QHBoxLayout()
        interval_label = QLabel("监控间隔（秒）:")
        interval_label.setFont(QFont("Microsoft YaHei", 11))
        interval_layout.addWidget(interval_label)

        self.interval_spinbox = QSpinBox()
        self.interval_spinbox.setRange(10, 3600)
        self.interval_spinbox.setValue(60)
        self.interval_spinbox.setFont(QFont("Microsoft YaHei", 11))
        interval_layout.addWidget(self.interval_spinbox)

        interval_layout.addStretch()
        monitor_layout.addLayout(interval_layout)

        # 告警阈值
        threshold_layout = QHBoxLayout()
        threshold_label = QLabel("告警阈值（%）:")
        threshold_label.setFont(QFont("Microsoft YaHei", 11))
        threshold_layout.addWidget(threshold_label)

        self.threshold_spinbox = QSpinBox()
        self.threshold_spinbox.setRange(50, 99)
        self.threshold_spinbox.setValue(90)
        self.threshold_spinbox.setFont(QFont("Microsoft YaHei", 11))
        threshold_layout.addWidget(self.threshold_spinbox)

        threshold_layout.addStretch()
        monitor_layout.addLayout(threshold_layout)

        layout.addWidget(monitor_group)

        layout.addStretch()

        return page

    def _init_style(self):
        """初始化样式"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #F8F9FA;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #DEE2E6;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 16px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 6px;
            }
            QTableWidget {
                border: 1px solid #DEE2E6;
                border-radius: 8px;
                background-color: white;
                gridline-color: #F1F3F5;
            }
            QTableWidget::item {
                padding: 6px;
            }
            QTableWidget::item:selected {
                background-color: #E3F2FD;
                color: #1565C0;
            }
            QHeaderView::section {
                background-color: #F1F3F5;
                border: none;
                border-bottom: 2px solid #DEE2E6;
                border-right: 1px solid #DEE2E6;
                padding: 8px 10px;
                font-weight: bold;
                color: #495057;
            }
            QProgressBar {
                border: 1px solid #DEE2E6;
                border-radius: 6px;
                text-align: center;
                background-color: #E9ECEF;
            }
            QProgressBar::chunk {
                background-color: #2196F3;
                border-radius: 5px;
            }
            QPushButton {
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 500;
            }
            QScrollBar:vertical {
                border: none;
                background: #F1F3F5;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #CED4DA;
                border-radius: 4px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background: #ADB5BD;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0;
            }
        """)

    def _init_timers(self):
        """初始化定时器"""
        # 监控定时器
        self.monitor_timer = QTimer()
        self.monitor_timer.timeout.connect(self._update_monitor)
        self.is_monitoring = False

    def _switch_page(self, index: int):
        """切换页面"""
        self.content_stack.setCurrentIndex(index)

        # 更新导航按钮状态
        for i, button in enumerate(self.nav_buttons):
            button.setChecked(i == index)

    def _start_scan(self):
        """开始扫描"""
        # 禁用按钮
        self.scan_button.setEnabled(False)
        self.clean_button.setEnabled(False)

        # 显示进度条
        self.scan_progress.setVisible(True)
        self.scan_progress.setRange(0, 0)

        # 更新状态
        self.statusBar().showMessage("正在扫描...")

        # Robot: show working state
        if self.robot:
            msg, mood = self.dialog.on_scan_start(DialogContext())
            self.robot.set_state(mood.value)
            self.robot.show_speech(msg)

        # 创建扫描线程
        from core.utils import get_system_drive
        self.scan_thread = ScanThread(get_system_drive())
        self.scan_thread.progress.connect(self._on_scan_progress)
        self.scan_thread.finished.connect(self._on_scan_finished)
        self.scan_thread.start()

    def _on_scan_progress(self, count: int, size: int):
        """扫描进度更新"""
        self.statusBar().showMessage(f"正在扫描... 已扫描 {count} 个文件, {format_size(size)}")

    def _on_scan_finished(self, result):
        """扫描完成"""
        self.scan_result = result

        # 更新统计信息
        self._update_scan_stats()

        # 更新文件表格
        self._update_files_table()

        # 启用按钮
        self.scan_button.setEnabled(True)
        self.clean_button.setEnabled(True)

        # 隐藏进度条
        self.scan_progress.setVisible(False)

        # 更新状态
        self.statusBar().showMessage("扫描完成")

        # Robot: show scan result
        if self.robot:
            safe_files = (
                self.scan_result.temp_files
                + self.scan_result.cache_files
                + self.scan_result.log_files
            )
            safe_size = sum(f.size for f in safe_files)
            ctx = DialogContext(
                files_scanned=len(safe_files),
                space_freed=safe_size,
            )
            msg, mood = self.dialog.on_scan_complete(ctx)
            self.robot.set_state(mood.value)
            self.robot.show_speech(msg, duration=5000)

    def _update_scan_stats(self):
        """更新扫描统计信息"""
        if not self.scan_result:
            return

        safe_files = [f for f in self.scan_result.temp_files +
                     self.scan_result.cache_files +
                     self.scan_result.log_files]
        safe_size = sum(f.size for f in safe_files)

        self.total_files_label.setText(f"总文件数: {self.scan_result.total_files:,}")
        self.total_size_label.setText(f"总大小: {format_size(self.scan_result.total_size)}")
        self.safe_files_label.setText(f"可清理: {len(safe_files):,} 个")
        self.safe_size_label.setText(f"可释放: {format_size(safe_size)}")

        # Update risk distribution
        risk_counts = {"safe": 0, "low": 0, "medium": 0, "high": 0}
        for f in safe_files:
            risk = getattr(f, "risk_level", "safe")
            if risk in risk_counts:
                risk_counts[risk] += 1
        self.risk_safe_label.setText(f"Safe: {risk_counts['safe']}")
        self.risk_low_label.setText(f"Low: {risk_counts['low']}")
        self.risk_medium_label.setText(f"Medium: {risk_counts['medium']}")
        self.risk_high_label.setText(f"High: {risk_counts['high']}")

    def _update_files_table(self):
        """更新文件表格"""
        if not self.scan_result:
            return

        files = self.scan_result.temp_files + self.scan_result.cache_files + self.scan_result.log_files

        self.files_table.setRowCount(len(files))

        # Risk level colors
        risk_colors = {
            "safe": QColor("#4CAF50"),
            "low": QColor("#8BC34A"),
            "medium": QColor("#FFC107"),
            "high": QColor("#FF5722"),
            "critical": QColor("#F44336"),
        }

        for i, file_info in enumerate(files):
            # 选择框
            checkbox = QCheckBox()
            checkbox.setChecked(True)
            checkbox.stateChanged.connect(self._update_selected_count)
            self.files_table.setCellWidget(i, 0, checkbox)

            # 文件路径
            path_item = QTableWidgetItem(file_info.path)
            path_item.setFlags(path_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.files_table.setItem(i, 1, path_item)

            # 大小
            size_item = QTableWidgetItem(format_size(file_info.size))
            size_item.setFlags(size_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            size_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.files_table.setItem(i, 2, size_item)

            # 类型名称
            type_name = getattr(file_info, "type_name", "") or file_info.file_type
            type_item = QTableWidgetItem(type_name)
            type_item.setFlags(type_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.files_table.setItem(i, 3, type_item)

            # 风险等级 (color-coded)
            risk = getattr(file_info, "risk_level", "safe")
            risk_label = {
                "safe": "Safe",
                "low": "Low",
                "medium": "Medium",
                "high": "High",
                "critical": "Critical",
            }.get(risk, risk)
            risk_item = QTableWidgetItem(risk_label)
            risk_item.setFlags(risk_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            color = risk_colors.get(risk)
            if color:
                risk_item.setForeground(color)
                risk_item.setFont(QFont("Microsoft YaHei", 10, QFont.Weight.Bold))
            self.files_table.setItem(i, 4, risk_item)

            # 删除影响
            impact = getattr(file_info, "impact", "")
            impact_item = QTableWidgetItem(impact)
            impact_item.setFlags(impact_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.files_table.setItem(i, 5, impact_item)

            # 修改时间
            from datetime import datetime
            mtime = datetime.fromtimestamp(file_info.modified)
            time_item = QTableWidgetItem(mtime.strftime("%Y-%m-%d %H:%M"))
            time_item.setFlags(time_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.files_table.setItem(i, 6, time_item)

        self._update_selected_count()

    def _toggle_select_all(self, state):
        """全选/取消全选"""
        for i in range(self.files_table.rowCount()):
            checkbox = self.files_table.cellWidget(i, 0)
            if checkbox:
                checkbox.setChecked(state == Qt.CheckState.Checked.value)

    def _update_selected_count(self):
        """更新选中计数"""
        selected_count = 0
        selected_size = 0

        for i in range(self.files_table.rowCount()):
            checkbox = self.files_table.cellWidget(i, 0)
            if checkbox and checkbox.isChecked():
                selected_count += 1
                size_text = self.files_table.item(i, 2).text()
                selected_size += self._parse_size(size_text)

        self.selected_label.setText(f"已选择: {selected_count} 个文件, {format_size(selected_size)}")

    def _parse_size(self, size_text: str) -> int:
        """解析大小文本"""
        parts = size_text.split()
        if len(parts) != 2:
            return 0

        try:
            value = float(parts[0])
            unit = parts[1]

            multipliers = {
                "B": 1,
                "KB": 1024,
                "MB": 1024 * 1024,
                "GB": 1024 * 1024 * 1024,
                "TB": 1024 * 1024 * 1024 * 1024,
            }

            return int(value * multipliers.get(unit, 1))
        except ValueError:
            return 0

    def _start_clean(self):
        """开始清理"""
        files = self._get_selected_files()

        if not files:
            QMessageBox.information(self, "提示", "没有选中要清理的文件")
            return

        reply = QMessageBox.question(
            self,
            "确认清理",
            f"确定要清理 {len(files)} 个文件吗？\n\n"
            f"文件将移到回收站，可以随时恢复。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        # 禁用按钮
        self.scan_button.setEnabled(False)
        self.clean_button.setEnabled(False)

        # 显示进度条
        self.scan_progress.setVisible(True)
        self.scan_progress.setRange(0, len(files))
        self.scan_progress.setValue(0)

        # 更新状态
        self.statusBar().showMessage("正在清理...")

        # Robot: show cleaning state
        if self.robot:
            msg, mood = self.dialog.on_clean_start(DialogContext())
            self.robot.set_state(mood.value)
            self.robot.show_speech(msg)

        # 创建清理线程
        self.clean_thread = CleanThread(files, use_trash=True)
        self.clean_thread.progress.connect(self._on_clean_progress)
        self.clean_thread.finished.connect(self._on_clean_finished)
        self.clean_thread.start()

    def _on_clean_progress(self, current: int, total: int, file_path: str):
        """清理进度更新"""
        self.scan_progress.setValue(current)
        self.statusBar().showMessage(f"正在清理... {current}/{total}")

    def _on_clean_finished(self, result):
        """清理完成"""
        self.scan_progress.setVisible(False)

        self.scan_button.setEnabled(True)
        self.clean_button.setEnabled(True)

        QMessageBox.information(
            self,
            "清理完成",
            f"清理完成！\n\n"
            f"已删除: {result.deleted_files} 个文件\n"
            f"释放空间: {format_size(result.freed_size)}\n"
            f"失败: {result.failed_files} 个文件\n\n"
            f"文件已移到回收站，可以随时恢复。"
        )

        self.statusBar().showMessage("清理完成")

        # Robot: show cleanup result
        if self.robot:
            ctx = DialogContext(space_freed=result.freed_size)
            msg, mood = self.dialog.on_clean_complete(ctx)
            self.robot.set_state(mood.value)
            self.robot.show_speech(msg, duration=5000)

        self._start_scan()

    def _start_diagnosis(self):
        """开始诊断"""
        self.statusBar().showMessage("正在诊断...")

        self.diagnosis_thread = DiagnosisThread()
        self.diagnosis_thread.finished.connect(self._on_diagnosis_finished)
        self.diagnosis_thread.start()

    def _on_diagnosis_finished(self, report):
        """诊断完成"""
        # 更新健康分数
        self.health_progress.set_value(report.health_score)
        self.health_progress.subtitle = f"{report.health_score} 分"

        # 更新问题表格
        self.problems_table.setRowCount(len(report.problems))

        for i, problem in enumerate(report.problems):
            # 严重程度
            severity_item = QTableWidgetItem(problem.severity.value.upper())
            severity_item.setFlags(severity_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            # Color-code severity
            severity_colors = {
                "CRITICAL": QColor("#F44336"),
                "HIGH": QColor("#FF5722"),
                "MEDIUM": QColor("#FFC107"),
                "LOW": QColor("#4CAF50"),
            }
            color = severity_colors.get(problem.severity.value.upper())
            if color:
                severity_item.setForeground(color)
            self.problems_table.setItem(i, 0, severity_item)

            # 问题标题
            title_item = QTableWidgetItem(problem.title)
            title_item.setFlags(title_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.problems_table.setItem(i, 1, title_item)

            # 描述
            desc_item = QTableWidgetItem(problem.description)
            desc_item.setFlags(desc_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.problems_table.setItem(i, 2, desc_item)

            # 解决方案
            solution_item = QTableWidgetItem(problem.solution)
            solution_item.setFlags(solution_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.problems_table.setItem(i, 3, solution_item)

        self.statusBar().showMessage(f"诊断完成 - 健康分数: {report.health_score}")

        # Robot: show diagnosis result
        if self.robot:
            ctx = DialogContext(
                health_score=report.health_score,
                problem_count=len(report.problems),
            )
            msg, mood = self.dialog.on_diagnosis(ctx)
            self.robot.set_state(mood.value)
            self.robot.show_speech(msg, duration=6000)

    def _refresh_recommendations(self):
        """刷新推荐 - 使用后台线程"""
        self.statusBar().showMessage("正在生成推荐...")
        self._recommendation_thread = RecommendationThread()
        self._recommendation_thread.finished.connect(self._on_recommendations_ready)
        self._recommendation_thread.start()

    def _on_recommendations_ready(self, recommendations: list):
        """推荐生成完成"""
        self.recommendations_widget.update_recommendations(recommendations)
        self.statusBar().showMessage(f"已生成 {len(recommendations)} 个推荐")

    def _toggle_monitor(self):
        """切换监控状态"""
        if self.is_monitoring:
            self.monitor_timer.stop()
            self.monitor_button.setText("开始监控")
            self.is_monitoring = False
        else:
            self.monitor_timer.start(5000)
            self.monitor_button.setText("停止监控")
            self.is_monitoring = True

    def _update_monitor(self):
        """更新监控数据 - 使用后台线程避免阻塞 UI"""
        self._monitor_thread = MonitorThread()
        self._monitor_thread.data_ready.connect(self._on_monitor_data_ready)
        self._monitor_thread.start()

    def _on_monitor_data_ready(self, data: dict):
        """监控数据就绪"""
        if "disk" in data:
            disk = data["disk"]
            self.disk_progress.set_value(disk["percent"])
            self.disk_progress.subtitle = f"{format_size(disk['used'])} / {format_size(disk['total'])}"

            self.disk_total_label.setText(f"总容量: {format_size(disk['total'])}")
            self.disk_used_label.setText(f"已使用: {format_size(disk['used'])}")
            self.disk_free_label.setText(f"剩余: {format_size(disk['free'])}")

    def _get_selected_files(self) -> list:
        """获取选中的文件"""
        files = []

        for i in range(self.files_table.rowCount()):
            checkbox = self.files_table.cellWidget(i, 0)
            if checkbox and checkbox.isChecked():
                path = self.files_table.item(i, 1).text()
                files.append(path)

        return files

    def set_robot(self, robot):
        """Set the robot reference for task integration."""
        self.robot = robot
        if robot:
            context = DialogContext()
            greeting = self.dialog.greet(context)
            robot.show_speech(greeting)


def main():
    """GUI 入口"""
    app = QApplication(sys.argv)

    app.setApplicationName("CleanBot")
    app.setApplicationVersion("2.0.0")
    app.setOrganizationName("PHOENIX")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
