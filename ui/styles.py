"""
CleanBot v2.0 — 现代化 UI 样式表
"""

MAIN_STYLESHEET = """
    /* ── 全局 ── */
    QMainWindow {
        background-color: #f0f2f5;
    }

    /* ── 分组框 ── */
    QGroupBox {
        font-weight: bold;
        font-size: 13px;
        color: #1e293b;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        margin-top: 16px;
        padding: 20px 16px 16px 16px;
        background-color: #ffffff;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 16px;
        padding: 0 8px;
        color: #2563eb;
    }

    /* ── 表格 ── */
    QTableWidget {
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        background-color: #ffffff;
        gridline-color: #f1f5f9;
        font-size: 12px;
    }
    QTableWidget::item {
        padding: 8px 10px;
    }
    QTableWidget::item:selected {
        background-color: #eff6ff;
        color: #1e40af;
    }
    QHeaderView::section {
        background-color: #f8fafc;
        border: none;
        border-bottom: 2px solid #e2e8f0;
        border-right: 1px solid #f1f5f9;
        padding: 10px 12px;
        font-weight: 600;
        font-size: 12px;
        color: #475569;
    }

    /* ── 进度条 ── */
    QProgressBar {
        border: none;
        border-radius: 8px;
        text-align: center;
        background-color: #e2e8f0;
        height: 10px;
        font-size: 10px;
    }
    QProgressBar::chunk {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #2563eb, stop:1 #3b82f6);
        border-radius: 8px;
    }

    /* ── 按钮 ── */
    QPushButton {
        border-radius: 8px;
        padding: 9px 18px;
        font-size: 13px;
        font-weight: 500;
    }

    /* ── 滚动条 ── */
    QScrollBar:vertical {
        border: none;
        background: transparent;
        width: 6px;
        margin: 0;
    }
    QScrollBar::handle:vertical {
        background: #cbd5e1;
        border-radius: 3px;
        min-height: 30px;
    }
    QScrollBar::handle:vertical:hover {
        background: #94a3b8;
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0;
    }
    QScrollBar:horizontal {
        height: 6px;
        background: transparent;
    }
    QScrollBar::handle:horizontal {
        background: #cbd5e1;
        border-radius: 3px;
    }

    /* ── 输入框 ── */
    QLineEdit, QSpinBox, QComboBox {
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 8px 12px;
        font-size: 13px;
        background: #ffffff;
    }
    QLineEdit:focus, QSpinBox:focus, QComboBox:focus {
        border-color: #2563eb;
    }
    QComboBox::drop-down {
        border: none;
        padding-right: 8px;
    }

    /* ── 复选框 ── */
    QCheckBox {
        font-size: 13px;
        spacing: 8px;
    }
    QCheckBox::indicator {
        width: 18px;
        height: 18px;
        border-radius: 4px;
        border: 2px solid #cbd5e1;
    }
    QCheckBox::indicator:checked {
        background-color: #2563eb;
        border-color: #2563eb;
    }

    /* ── 标签页 ── */
    QTabWidget::pane {
        border: none;
        background: transparent;
    }
    QTabBar::tab {
        padding: 10px 20px;
        font-size: 13px;
        border: none;
        border-bottom: 2px solid transparent;
        color: #64748b;
    }
    QTabBar::tab:selected {
        color: #2563eb;
        border-bottom: 2px solid #2563eb;
    }
"""
