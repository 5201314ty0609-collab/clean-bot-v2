"""
CleanBot v2.0 -- UI Stylesheets

Centralized QSS styles for the main window.
Collected here so main_window.py stays focused on layout logic.
"""

MAIN_STYLESHEET = """
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
"""
