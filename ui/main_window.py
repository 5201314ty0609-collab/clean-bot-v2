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
    QSizePolicy, QSpacerItem, QComboBox, QLineEdit, QTextEdit, QSpinBox
)
from PyQt6.QtCore import Qt, QTimer, QSize
from PyQt6.QtGui import QFont, QColor, QPalette, QIcon, QAction

# 导入核心模块
from core.monitor.disk_monitor import DiskMonitor, format_size

# 导入自定义控件
from ui.dashboard import DashboardView, StatCard, RecommendationsWidget, CircularProgress

# 导入后台线程
from ui.threads import (
    ScanThread, CleanThread, MonitorThread, RecommendationThread,
)

# 导入对话系统
from core.ai.dialog_system import DialogSystem, DialogContext, Mood

# 导入更新检测
from core.updater import check_for_update, CURRENT_VERSION
from ui.update_dialog import show_update_dialog


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

        # 启动时静默检查更新（延迟3秒，避免阻塞窗口显示）
        QTimer.singleShot(3000, self.check_update_on_startup)

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
        """创建顶部工具栏"""
        toolbar = QFrame()
        toolbar.setFixedHeight(56)
        toolbar.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: none;
                border-bottom: 1px solid #e2e8f0;
            }
        """)

        layout = QHBoxLayout(toolbar)
        layout.setContentsMargins(24, 0, 24, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        # Logo / 标题
        title = QLabel("🧹 CleanBot")
        title.setFont(QFont("Microsoft YaHei", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: #1e293b; border: none;")
        layout.addWidget(title)

        layout.addSpacing(8)

        # 管理员状态
        from core.utils import is_admin
        if is_admin():
            badge = QLabel("管理员")
            badge.setStyleSheet(
                "background: #dcfce7; color: #166534; border-radius: 10px;"
                "padding: 3px 12px; font-size: 11px; font-weight: 600; border: none;"
            )
        else:
            badge = QLabel("普通模式")
            badge.setStyleSheet(
                "background: #fef3c7; color: #92400e; border-radius: 10px;"
                "padding: 3px 12px; font-size: 11px; font-weight: 600; border: none;"
            )
        layout.addWidget(badge)

        layout.addStretch()

        # 扫描按钮
        self.scan_btn = QPushButton("🔍 开始扫描")
        self.scan_btn.setFont(QFont("Microsoft YaHei", 12, QFont.Weight.Bold))
        self.scan_btn.setStyleSheet("""
            QPushButton {
                background: #2563eb; color: white; border: none;
                border-radius: 10px; padding: 10px 24px;
            }
            QPushButton:hover { background: #1d4ed8; }
            QPushButton:disabled { background: #94a3b8; }
        """)
        self.scan_btn.clicked.connect(self._start_scan)
        layout.addWidget(self.scan_btn)

        # 清理按钮
        self.clean_btn = QPushButton("🧹 清理选中")
        self.clean_btn.setFont(QFont("Microsoft YaHei", 12, QFont.Weight.Bold))
        self.clean_btn.setStyleSheet("""
            QPushButton {
                background: #ef4444; color: white; border: none;
                border-radius: 10px; padding: 10px 24px;
            }
            QPushButton:hover { background: #dc2626; }
            QPushButton:disabled { background: #fca5a5; }
        """)
        self.clean_btn.setEnabled(False)
        self.clean_btn.clicked.connect(self._start_clean)
        layout.addWidget(self.clean_btn)

        return toolbar

    def _create_navigation(self) -> QWidget:
        """创建侧边导航栏（深色主题）"""
        nav = QFrame()
        nav.setFixedWidth(220)
        nav.setStyleSheet("""
            QFrame {
                background-color: #0f172a;
                border: none;
                border-right: 1px solid #1e293b;
            }
        """)

        layout = QVBoxLayout(nav)
        layout.setSpacing(2)
        layout.setContentsMargins(10, 16, 10, 16)

        # 应用 Logo
        logo = QLabel("  🧹  CleanBot")
        logo.setFont(QFont("Microsoft YaHei", 14, QFont.Weight.Bold))
        logo.setStyleSheet("color: #f1f5f9; padding: 12px 8px; border: none; margin-bottom: 12px;")
        layout.addWidget(logo)

        # 分隔线
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background: #334155; border: none; margin: 4px 8px;")
        layout.addWidget(sep)

        # 导航项 (图标, 文字, 页面索引)
        nav_items = [
            ("📊", "仪表盘", 0),
            ("🔍", "文件扫描", 1),
            ("📁", "文件迁移", 2),
            ("📦", "应用迁移", 3),
            ("🗑️", "智能删除", 4),
            ("💡", "智能推荐", 5),
            ("📈", "磁盘监控", 6),
            ("⚙️", "设置", 7),
        ]

        self.nav_buttons = []
        for icon, text, index in nav_items:
            btn = QPushButton(f"  {icon}  {text}")
            btn.setFont(QFont("Microsoft YaHei", 11))
            btn.setFixedHeight(42)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setCheckable(True)
            btn.setChecked(index == 0)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #94a3b8;
                    border: none;
                    border-radius: 8px;
                    text-align: left;
                    padding-left: 12px;
                }
                QPushButton:hover {
                    background-color: #1e293b;
                    color: #e2e8f0;
                }
                QPushButton:checked {
                    background-color: #2563eb;
                    color: white;
                    font-weight: 600;
                }
            """)
            btn.clicked.connect(lambda checked, i=index: self._switch_page(i))
            layout.addWidget(btn)
            self.nav_buttons.append(btn)

        layout.addStretch()

        # 版本号
        ver = QLabel(f"  v{CURRENT_VERSION}")
        ver.setStyleSheet("color: #475569; font-size: 11px; padding: 8px; border: none;")
        layout.addWidget(ver)

        return nav

    def _create_pages(self):
        """创建各个页面"""
        # 仪表盘页面
        dash_scroll = QScrollArea()
        dash_scroll.setWidgetResizable(True)
        dash_scroll.setStyleSheet("QScrollArea { border: none; background: #f0f2f5; }")
        self.dashboard_page = DashboardView()
        dash_scroll.setWidget(self.dashboard_page)
        self.content_stack.addWidget(dash_scroll)

        # 文件扫描页面
        self.scan_page = self._create_scan_page()
        self.content_stack.addWidget(self.scan_page)

        # 文件迁移页面
        self.migrate_page = self._create_migrate_page()
        self.content_stack.addWidget(self.migrate_page)

        # 应用迁移页面
        self.app_migrate_page = self._create_app_migrate_page()
        self.content_stack.addWidget(self.app_migrate_page)

        # 智能删除页面
        self.interactive_page = self._create_interactive_page()
        self.content_stack.addWidget(self.interactive_page)

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
        self.recommendations_widget.cleanup_requested.connect(self._on_rec_cleanup)
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

        self.monitor_disk_gauge = CircularProgress(color="red")
        self.monitor_disk_gauge.set(0, "C 盘", "--")
        disk_layout.addWidget(self.monitor_disk_gauge)

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

    def _create_migrate_page(self) -> QWidget:
        """创建文件迁移页面"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # 标题
        title_layout = QHBoxLayout()
        title_label = QLabel("文件迁移")
        title_label.setFont(QFont("Microsoft YaHei", 20, QFont.Weight.Bold))
        title_layout.addWidget(title_label)

        title_layout.addStretch()

        layout.addLayout(title_layout)

        # 说明
        info_label = QLabel("将 C 盘的大文件迁移到其他盘，释放空间。文件内容不会改变，原位置仍可正常访问。")
        info_label.setFont(QFont("Microsoft YaHei", 11))
        info_label.setStyleSheet("color: #666;")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        # 目标盘选择
        target_layout = QHBoxLayout()
        target_label = QLabel("迁移到:")
        target_label.setFont(QFont("Microsoft YaHei", 11))
        target_layout.addWidget(target_label)

        self.migrate_target_combo = QComboBox()
        self.migrate_target_combo.setFont(QFont("Microsoft YaHei", 11))
        self.migrate_target_combo.addItems(["D:\\", "E:\\", "F:\\"])
        target_layout.addWidget(self.migrate_target_combo)

        target_layout.addStretch()
        layout.addLayout(target_layout)

        # 扫描按钮
        scan_migrate_button = QPushButton("扫描可迁移文件")
        scan_migrate_button.setFont(QFont("Microsoft YaHei", 11))
        scan_migrate_button.setStyleSheet("""
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
        scan_migrate_button.clicked.connect(self._scan_migrate_files)
        layout.addWidget(scan_migrate_button)

        # 迁移文件表格
        self.migrate_table = QTableWidget()
        self.migrate_table.setColumnCount(4)
        self.migrate_table.setHorizontalHeaderLabels(["选择", "文件路径", "大小", "类型"])
        self.migrate_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.migrate_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.migrate_table.setAlternatingRowColors(True)
        layout.addWidget(self.migrate_table)

        # 迁移按钮
        migrate_button = QPushButton("迁移选中文件")
        migrate_button.setFont(QFont("Microsoft YaHei", 11))
        migrate_button.setStyleSheet("""
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
        migrate_button.clicked.connect(self._start_migrate)
        layout.addWidget(migrate_button)

        return page

    def _create_app_migrate_page(self) -> QWidget:
        """创建应用迁移页面"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # 标题
        title_layout = QHBoxLayout()
        title_label = QLabel("应用迁移")
        title_label.setFont(QFont("Microsoft YaHei", 20, QFont.Weight.Bold))
        title_layout.addWidget(title_label)

        title_layout.addStretch()

        layout.addLayout(title_layout)

        # 说明
        info_label = QLabel("将已安装的应用从 C 盘迁移到其他盘。应用的所有数据和设置都会保留，迁移后可正常打开和使用。")
        info_label.setFont(QFont("Microsoft YaHei", 11))
        info_label.setStyleSheet("color: #666;")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        # 目标盘选择
        target_layout = QHBoxLayout()
        target_label = QLabel("迁移到:")
        target_label.setFont(QFont("Microsoft YaHei", 11))
        target_layout.addWidget(target_label)

        self.app_target_combo = QComboBox()
        self.app_target_combo.setFont(QFont("Microsoft YaHei", 11))
        self.app_target_combo.addItems(["D:\\", "E:\\", "F:\\"])
        target_layout.addWidget(self.app_target_combo)

        target_layout.addStretch()
        layout.addLayout(target_layout)

        # 扫描按钮
        scan_app_button = QPushButton("扫描已安装应用")
        scan_app_button.setFont(QFont("Microsoft YaHei", 11))
        scan_app_button.setStyleSheet("""
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
        scan_app_button.clicked.connect(self._scan_installed_apps)
        layout.addWidget(scan_app_button)

        # 应用表格
        self.app_table = QTableWidget()
        self.app_table.setColumnCount(5)
        self.app_table.setHorizontalHeaderLabels(["选择", "应用名称", "安装路径", "大小", "版本"])
        self.app_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.app_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.app_table.setAlternatingRowColors(True)
        layout.addWidget(self.app_table)

        # 迁移按钮
        migrate_app_button = QPushButton("迁移选中应用")
        migrate_app_button.setFont(QFont("Microsoft YaHei", 11))
        migrate_app_button.setStyleSheet("""
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
        migrate_app_button.clicked.connect(self._start_app_migrate)
        layout.addWidget(migrate_app_button)

        return page

    def _create_interactive_page(self) -> QWidget:
        """创建智能删除页面"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # 标题
        title_layout = QHBoxLayout()
        title_label = QLabel("智能删除")
        title_label.setFont(QFont("Microsoft YaHei", 20, QFont.Weight.Bold))
        title_layout.addWidget(title_label)

        title_layout.addStretch()

        layout.addLayout(title_layout)

        # 说明
        info_label = QLabel("输入文件或应用路径，系统会分析并提供详细信息。确认后会深度清理，包括注册表、快捷方式、启动项等，确保不留残渣。")
        info_label.setFont(QFont("Microsoft YaHei", 11))
        info_label.setStyleSheet("color: #666;")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        # 输入框
        input_layout = QHBoxLayout()
        self.delete_path_input = QLineEdit()
        self.delete_path_input.setFont(QFont("Microsoft YaHei", 11))
        self.delete_path_input.setPlaceholderText("输入文件或应用路径，例如: C:\\Program Files\\SomeApp")
        input_layout.addWidget(self.delete_path_input)

        browse_button = QPushButton("浏览")
        browse_button.setFont(QFont("Microsoft YaHei", 11))
        browse_button.clicked.connect(self._browse_delete_path)
        input_layout.addWidget(browse_button)

        analyze_button = QPushButton("分析")
        analyze_button.setFont(QFont("Microsoft YaHei", 11))
        analyze_button.setStyleSheet("""
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
        analyze_button.clicked.connect(self._analyze_delete_target)
        input_layout.addWidget(analyze_button)

        layout.addLayout(input_layout)

        # 分析结果
        self.analysis_frame = QFrame()
        self.analysis_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        self.analysis_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #E0E0E0;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        self.analysis_frame.setVisible(False)

        analysis_layout = QVBoxLayout(self.analysis_frame)

        self.analysis_title = QLabel("分析结果")
        self.analysis_title.setFont(QFont("Microsoft YaHei", 14, QFont.Weight.Bold))
        analysis_layout.addWidget(self.analysis_title)

        self.analysis_info = QLabel("")
        self.analysis_info.setFont(QFont("Microsoft YaHei", 11))
        self.analysis_info.setWordWrap(True)
        analysis_layout.addWidget(self.analysis_info)

        self.analysis_risk = QLabel("")
        self.analysis_risk.setFont(QFont("Microsoft YaHei", 11))
        analysis_layout.addWidget(self.analysis_risk)

        self.analysis_impact = QLabel("")
        self.analysis_impact.setFont(QFont("Microsoft YaHei", 11))
        analysis_layout.addWidget(self.analysis_impact)

        self.analysis_related = QLabel("")
        self.analysis_related.setFont(QFont("Microsoft YaHei", 11))
        self.analysis_related.setWordWrap(True)
        analysis_layout.addWidget(self.analysis_related)

        # 删除按钮
        delete_button = QPushButton("深度删除")
        delete_button.setFont(QFont("Microsoft YaHei", 11))
        delete_button.setStyleSheet("""
            QPushButton {
                background-color: #FF5722;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 20px;
            }
            QPushButton:hover {
                background-color: #E64A19;
            }
        """)
        delete_button.clicked.connect(self._execute_deep_delete)
        analysis_layout.addWidget(delete_button)

        layout.addWidget(self.analysis_frame)

        layout.addStretch()

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

        # 更新设置
        update_group = QGroupBox("软件更新")
        update_layout = QVBoxLayout(update_group)

        version_layout = QHBoxLayout()
        version_label = QLabel(f"当前版本: v{CURRENT_VERSION}")
        version_label.setFont(QFont("Microsoft YaHei", 11))
        version_layout.addWidget(version_label)
        version_layout.addStretch()
        update_layout.addLayout(version_layout)

        # 启动时检查更新
        self.auto_update_checkbox = QCheckBox("启动时自动检查更新")
        self.auto_update_checkbox.setChecked(True)
        self.auto_update_checkbox.setFont(QFont("Microsoft YaHei", 11))
        update_layout.addWidget(self.auto_update_checkbox)

        # 检查更新按钮
        self.update_btn = QPushButton("检查更新")
        self.update_btn.setFont(QFont("Microsoft YaHei", 11))
        self.update_btn.setStyleSheet("""
            QPushButton {
                background: #2563eb; color: white; border: none;
                border-radius: 6px; padding: 10px 20px;
            }
            QPushButton:hover { background: #1d4ed8; }
        """)
        self.update_btn.clicked.connect(self._check_for_update)
        update_layout.addWidget(self.update_btn)

        # 状态标签
        self.update_status_label = QLabel("")
        self.update_status_label.setFont(QFont("Microsoft YaHei", 10))
        self.update_status_label.setStyleSheet("color: #6b7280;")
        update_layout.addWidget(self.update_status_label)

        layout.addWidget(update_group)

        layout.addStretch()

        return page

    def _init_style(self):
        """初始化样式"""
        from ui.styles import MAIN_STYLESHEET
        self.setStyleSheet(MAIN_STYLESHEET)

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
        self.scan_btn.setEnabled(False)
        self.clean_btn.setEnabled(False)

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
        self.scan_btn.setEnabled(True)
        self.clean_btn.setEnabled(True)

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
        self.scan_btn.setEnabled(False)
        self.clean_btn.setEnabled(False)

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

        self.scan_btn.setEnabled(True)
        self.clean_btn.setEnabled(True)

        msg = (
            f"清理完成！\n\n"
            f"已删除: {result.deleted_files} 个文件\n"
            f"释放空间: {format_size(result.freed_size)}\n"
            f"跳过: {result.skipped_files} 个文件\n"
            f"失败: {result.failed_files} 个文件\n"
        )
        if result.errors:
            msg += f"\n失败原因（前5条）:\n"
            for err in result.errors[:5]:
                msg += f"  • {err}\n"
        msg += "\n文件已移到回收站，可以随时恢复。"

        icon = QMessageBox.Icon.Warning if result.failed_files > 0 else QMessageBox.Icon.Information
        QMessageBox.information(self, "清理完成", msg)

        self.statusBar().showMessage("清理完成")

        # Robot: show cleanup result
        if self.robot:
            ctx = DialogContext(space_freed=result.freed_size)
            msg, mood = self.dialog.on_clean_complete(ctx)
            self.robot.set_state(mood.value)
            self.robot.show_speech(msg, duration=5000)

        self._start_scan()

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

    def _on_rec_cleanup(self, rec):
        """点击推荐卡片的一键清理"""
        self.statusBar().showMessage(f"正在执行: {rec.title}...")

        # 切换到扫描页面开始扫描
        self._switch_page(1)  # 文件扫描页
        self._start_scan()

        # 标记该推荐已完成
        self.recommendations_widget.mark_completed(rec.id)
        self.statusBar().showMessage(f"已完成: {rec.title}，正在扫描可清理文件...")

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
            self.monitor_disk_gauge.set(
                disk["percent"], "C 盘",
                f"{format_size(disk['used'])} / {format_size(disk['total'])}"
            )

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

    def _scan_migrate_files(self):
        """扫描可迁移文件"""
        from core.scanner.file_scanner import FileScanner
        from core.utils import get_system_drive

        self.statusBar().showMessage("正在扫描可迁移文件...")

        # 扫描大文件（>100MB）
        scanner = FileScanner(get_system_drive())
        result = scanner.scan()

        # 过滤大文件
        large_files = [f for f in result.largest_files if f.size > 100 * 1024 * 1024]

        # 更新表格
        self.migrate_table.setRowCount(len(large_files))

        for i, file_info in enumerate(large_files[:50]):  # 最多显示50个
            # 选择框
            checkbox = QCheckBox()
            checkbox.setChecked(False)
            self.migrate_table.setCellWidget(i, 0, checkbox)

            # 文件路径
            path_item = QTableWidgetItem(file_info.path)
            path_item.setFlags(path_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.migrate_table.setItem(i, 1, path_item)

            # 大小
            size_item = QTableWidgetItem(format_size(file_info.size))
            size_item.setFlags(size_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.migrate_table.setItem(i, 2, size_item)

            # 类型
            type_name = getattr(file_info, "type_name", "") or file_info.file_type
            type_item = QTableWidgetItem(type_name)
            type_item.setFlags(type_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.migrate_table.setItem(i, 3, type_item)

        self.statusBar().showMessage(f"扫描完成，发现 {len(large_files)} 个可迁移文件")

    def _start_migrate(self):
        """开始文件迁移"""
        from core.utils import is_admin, run_as_admin

        if not is_admin():
            reply = QMessageBox.question(
                self, "需要管理员权限",
                "文件迁移需要管理员权限才能创建符号链接。\n\n是否以管理员身份重新启动 CleanBot？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.Yes:
                run_as_admin()
            return

        from core.migrator.file_migrator import FileMigrator

        # 获取选中的文件
        files = []
        for i in range(self.migrate_table.rowCount()):
            checkbox = self.migrate_table.cellWidget(i, 0)
            if checkbox and checkbox.isChecked():
                path = self.migrate_table.item(i, 1).text()
                files.append(path)

        if not files:
            QMessageBox.information(self, "提示", "没有选中要迁移的文件")
            return

        # 获取目标盘
        target_drive = self.migrate_target_combo.currentText()

        # 确认对话框
        total_size = 0
        for i in range(self.migrate_table.rowCount()):
            checkbox = self.migrate_table.cellWidget(i, 0)
            if checkbox and checkbox.isChecked():
                size_text = self.migrate_table.item(i, 2).text()
                total_size += self._parse_size(size_text)

        reply = QMessageBox.question(
            self,
            "确认迁移",
            f"确定要迁移 {len(files)} 个文件到 {target_drive} 吗？\n\n"
            f"总大小: {format_size(total_size)}\n\n"
            f"迁移后原位置仍可正常访问文件。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        # 执行迁移
        self.statusBar().showMessage("正在迁移文件...")

        migrator = FileMigrator(target_drive)

        def progress_callback(prog):
            self.statusBar().showMessage(f"正在迁移... {prog.current}/{prog.total}")

        result = migrator.migrate_files(files, progress_callback=progress_callback)

        if result.success:
            QMessageBox.information(
                self,
                "迁移完成",
                f"文件迁移完成！\n\n"
                f"已迁移: {result.migrated_files} 个文件\n"
                f"释放空间: {format_size(result.migrated_size)}\n\n"
                f"原位置仍可正常访问文件。"
            )
        else:
            QMessageBox.warning(
                self,
                "迁移完成（有错误）",
                f"文件迁移完成，但有错误：\n\n"
                f"已迁移: {result.migrated_files} 个文件\n"
                f"失败: {result.failed_files} 个文件\n\n"
                f"错误信息:\n" + "\n".join(result.errors[:5])
            )

        self.statusBar().showMessage("迁移完成")

    def _scan_installed_apps(self):
        """扫描已安装应用"""
        from core.migrator.app_migrator import AppMigrator

        self.statusBar().showMessage("正在扫描已安装应用...")

        migrator = AppMigrator()
        apps = migrator.scan_installed_apps()

        # 过滤 C 盘应用
        c_apps = [app for app in apps if app.install_path.lower().startswith("c:\\")]

        # 更新表格
        self.app_table.setRowCount(len(c_apps))

        for i, app in enumerate(c_apps[:100]):  # 最多显示100个
            # 选择框
            checkbox = QCheckBox()
            checkbox.setChecked(False)
            self.app_table.setCellWidget(i, 0, checkbox)

            # 应用名称
            name_item = QTableWidgetItem(app.name)
            name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.app_table.setItem(i, 1, name_item)

            # 安装路径
            path_item = QTableWidgetItem(app.install_path)
            path_item.setFlags(path_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.app_table.setItem(i, 2, path_item)

            # 大小
            size_item = QTableWidgetItem(format_size(app.size))
            size_item.setFlags(size_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.app_table.setItem(i, 3, size_item)

            # 版本
            version_item = QTableWidgetItem(app.version)
            version_item.setFlags(version_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.app_table.setItem(i, 4, version_item)

        self.statusBar().showMessage(f"扫描完成，发现 {len(c_apps)} 个 C 盘应用")

    def _start_app_migrate(self):
        """开始应用迁移"""
        from core.utils import is_admin, run_as_admin

        if not is_admin():
            reply = QMessageBox.question(
                self, "需要管理员权限",
                "应用迁移需要管理员权限。\n\n是否以管理员身份重新启动 CleanBot？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.Yes:
                run_as_admin()
            return

        from core.migrator.app_migrator import AppMigrator, AppInfo

        # 获取选中的应用
        selected_apps = []
        for i in range(self.app_table.rowCount()):
            checkbox = self.app_table.cellWidget(i, 0)
            if checkbox and checkbox.isChecked():
                name = self.app_table.item(i, 1).text()
                path = self.app_table.item(i, 2).text()
                selected_apps.append((name, path))

        if not selected_apps:
            QMessageBox.information(self, "提示", "没有选中要迁移的应用")
            return

        # 获取目标盘
        target_drive = self.app_target_combo.currentText()

        # 确认对话框
        reply = QMessageBox.question(
            self,
            "确认迁移",
            f"确定要迁移 {len(selected_apps)} 个应用到 {target_drive} 吗？\n\n"
            f"⚠️ 请确保要迁移的应用已关闭！\n\n"
            f"迁移后应用的所有数据和设置都会保留，可正常打开和使用。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        # 执行迁移
        self.statusBar().showMessage("正在迁移应用...")

        migrator = AppMigrator(target_drive)
        migrator.scan_installed_apps()

        success_count = 0
        fail_count = 0
        errors = []

        for app_name, app_path in selected_apps:
            app = migrator.get_app_info(app_name)
            if not app:
                errors.append(f"未找到应用: {app_name}")
                fail_count += 1
                continue

            def progress_callback(msg, percent):
                self.statusBar().showMessage(f"正在迁移 {app_name}: {msg}")

            result = migrator.migrate_app(app, progress_callback=progress_callback)

            if result.success:
                success_count += 1
            else:
                fail_count += 1
                errors.extend(result.errors)

        if fail_count == 0:
            QMessageBox.information(
                self,
                "迁移完成",
                f"应用迁移完成！\n\n"
                f"已迁移: {success_count} 个应用\n\n"
                f"应用的所有数据和设置都已保留，可正常打开和使用。"
            )
        else:
            QMessageBox.warning(
                self,
                "迁移完成（有错误）",
                f"应用迁移完成，但有错误：\n\n"
                f"成功: {success_count} 个应用\n"
                f"失败: {fail_count} 个应用\n\n"
                f"错误信息:\n" + "\n".join(errors[:5])
            )

        self.statusBar().showMessage("迁移完成")

    def _browse_delete_path(self):
        """浏览删除路径"""
        path = QFileDialog.getExistingDirectory(self, "选择要删除的文件夹")
        if path:
            self.delete_path_input.setText(path)

    def _analyze_delete_target(self):
        """分析删除目标"""
        from core.interactive.interactive_cleaner import InteractiveCleaner

        path = self.delete_path_input.text().strip()
        if not path:
            QMessageBox.information(self, "提示", "请输入文件或应用路径")
            return

        if not os.path.exists(path):
            QMessageBox.warning(self, "错误", "路径不存在")
            return

        # 分析目标
        cleaner = InteractiveCleaner()
        info = cleaner.get_file_info_summary(path)

        # 显示分析结果
        self.analysis_frame.setVisible(True)

        self.analysis_title.setText(f"分析结果: {info['name']}")

        self.analysis_info.setText(
            f"类型: {info['type_name']}\n"
            f"大小: {info['size_formatted']}\n"
            f"路径: {info['path']}"
        )

        # 风险等级
        risk_icon = {
            "low": "🟢 低风险",
            "medium": "🟡 中风险",
            "high": "🔴 高风险",
        }.get(info['risk_level'], "⚪ 未知风险")

        self.analysis_risk.setText(f"风险等级: {risk_icon}")
        if info['risk_reason']:
            self.analysis_risk.setText(f"风险等级: {risk_icon}\n原因: {info['risk_reason']}")

        # 删除影响
        if info['delete_impact']:
            self.analysis_impact.setText(f"删除影响: {info['delete_impact']}")

        # 关联项
        if info['related_items']:
            related_text = "⚠️ 发现关联项（也会被删除）:\n"
            for item in info['related_items'][:5]:
                related_text += f"  - {item}\n"
            if info['related_count'] > 5:
                related_text += f"  ... 还有 {info['related_count'] - 5} 项"
            self.analysis_related.setText(related_text)
        else:
            self.analysis_related.setText("未发现关联项")

    def _execute_deep_delete(self):
        """执行深度删除"""
        from core.interactive.interactive_cleaner import InteractiveCleaner
        from core.deep_cleaner.deep_cleaner import DeepCleaner

        path = self.delete_path_input.text().strip()
        if not path:
            return

        # 获取分析信息
        cleaner = InteractiveCleaner()
        info = cleaner.get_file_info_summary(path)

        # 二次确认
        confirm_msg = cleaner.get_confirmation_message(cleaner.analyze_file(path))

        reply = QMessageBox.question(
            self,
            "二次确认 - 深度删除",
            confirm_msg + "\n\n确定要删除吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        # 执行深度删除
        self.statusBar().showMessage("正在深度删除...")

        result = cleaner.delete_file(path)

        if result.success:
            QMessageBox.information(
                self,
                "删除完成",
                f"深度删除完成！\n\n"
                f"已删除: {result.deleted_files} 个文件\n"
                f"清理注册表: {result.deleted_registry} 项\n"
                f"清理快捷方式: {result.deleted_shortcuts} 个\n"
                f"释放空间: {format_size(result.freed_size)}\n\n"
                f"所有相关项目已清理干净。"
            )

            # 清空输入框和分析结果
            self.delete_path_input.clear()
            self.analysis_frame.setVisible(False)
        else:
            QMessageBox.warning(
                self,
                "删除失败",
                f"深度删除失败：\n\n" + "\n".join(result.errors)
            )

        self.statusBar().showMessage("删除完成")

    def set_robot(self, robot):
        """Set the robot reference for task integration."""
        self.robot = robot
        if robot:
            context = DialogContext()
            greeting = self.dialog.greet(context)
            robot.show_speech(greeting)

    def _check_for_update(self):
        """检查更新（在后台线程中执行网络请求）。"""
        self.update_btn.setEnabled(False)
        self.update_btn.setText("检查中...")
        self.update_status_label.setText("正在检查更新...")
        self.update_status_label.setStyleSheet("color: #6b7280;")

        from ui.threads import UpdateCheckThread
        self._update_thread = UpdateCheckThread()
        self._update_thread.finished.connect(self._on_update_check_done)
        self._update_thread.start()

    def _on_update_check_done(self, update_info):
        """更新检查完成回调。"""
        self.update_btn.setEnabled(True)
        self.update_btn.setText("检查更新")

        if update_info is None:
            self.update_status_label.setText("检查失败，请检查网络连接")
            self.update_status_label.setStyleSheet("color: #dc2626;")
        elif not update_info.is_newer:
            self.update_status_label.setText(
                f"已是最新版本 (v{CURRENT_VERSION})"
            )
            self.update_status_label.setStyleSheet("color: #16a34a;")
        else:
            self.update_status_label.setText(
                f"发现新版本 v{update_info.version}！"
            )
            self.update_status_label.setStyleSheet("color: #2563eb; font-weight: bold;")
            show_update_dialog(update_info, self)

    def check_update_on_startup(self):
        """启动时静默检查更新（不显示"已是最新"的提示）。"""
        from ui.threads import UpdateCheckThread
        self._update_thread = UpdateCheckThread()
        self._update_thread.finished.connect(self._on_startup_update_done)
        self._update_thread.start()

    def _on_startup_update_done(self, update_info):
        """启动更新检查完成 — 只在有新版本时弹窗。"""
        if update_info and update_info.is_newer:
            show_update_dialog(update_info, self)


def main():
    """GUI 入口"""
    app = QApplication(sys.argv)
    app.setApplicationName("CleanBot")
    app.setApplicationVersion("2.0.0")
    app.setOrganizationName("PHOENIX")

    # 启动时检查管理员权限
    from core.utils import is_admin, run_as_admin
    if not is_admin():
        answer = QMessageBox.question(
            None,
            "CleanBot — 管理员权限",
            "建议以管理员身份运行 CleanBot，以便使用全部功能：\n\n"
            "  • 文件迁移和应用迁移\n"
            "  • 系统诊断和修复\n"
            "  • 深度清理\n\n"
            "是否以管理员身份重新启动？\n"
            "（选择「否」将以普通模式继续，部分功能受限）",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes,
        )
        if answer == QMessageBox.StandardButton.Yes:
            run_as_admin()
            sys.exit(0)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
