"""
CleanBot v2.0 — 更新对话框

美观的更新提示对话框，显示版本信息、更新内容和操作按钮。
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QFrame, QSizePolicy,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from core.updater import UpdateInfo, CURRENT_VERSION


class UpdateDialog(QDialog):
    """更新提示对话框"""

    def __init__(self, update_info: UpdateInfo, parent=None):
        super().__init__(parent)
        self.update_info = update_info
        self._init_ui()

    def _init_ui(self):
        self.setWindowTitle("发现新版本")
        self.setFixedSize(480, 380)
        self.setWindowFlags(
            Qt.WindowType.Dialog |
            Qt.WindowType.WindowCloseButtonHint |
            Qt.WindowType.WindowStaysOnTopHint
        )

        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(28, 24, 28, 24)

        # ── 标题 ──
        header = QHBoxLayout()
        icon_label = QLabel("🎉")
        icon_label.setFont(QFont("Segoe UI Emoji", 32))
        header.addWidget(icon_label)

        title_text = QVBoxLayout()
        title = QLabel("发现新版本！")
        title.setFont(QFont("Microsoft YaHei", 16, QFont.Weight.Bold))
        title_text.addWidget(title)

        subtitle = QLabel(
            f"当前版本: v{CURRENT_VERSION}  →  最新版本: v{self.update_info.version}"
        )
        subtitle.setStyleSheet("color: #6b7280; font-size: 13px;")
        title_text.addWidget(subtitle)
        header.addLayout(title_text)
        header.addStretch()
        layout.addLayout(header)

        # ── 分隔线 ──
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("background: #e5e7eb;")
        layout.addWidget(line)

        # ── 更新内容 ──
        notes_label = QLabel("更新内容:")
        notes_label.setFont(QFont("Microsoft YaHei", 12, QFont.Weight.Bold))
        layout.addWidget(notes_label)

        notes_edit = QTextEdit()
        notes_edit.setReadOnly(True)
        notes_edit.setPlainText(
            self.update_info.release_notes or "暂无更新说明"
        )
        notes_edit.setMaximumHeight(120)
        notes_edit.setStyleSheet("""
            QTextEdit {
                background: #f9fafb;
                border: 1px solid #e5e7eb;
                border-radius: 8px;
                padding: 10px;
                font-size: 13px;
            }
        """)
        layout.addWidget(notes_edit)

        if self.update_info.release_date:
            date_label = QLabel(f"发布日期: {self.update_info.release_date}")
            date_label.setStyleSheet("color: #9ca3af; font-size: 12px;")
            layout.addWidget(date_label)

        layout.addStretch()

        # ── 按钮 ──
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        skip_btn = QPushButton("稍后提醒")
        skip_btn.setStyleSheet("""
            QPushButton {
                background: #f3f4f6; color: #374151; border: 1px solid #d1d5db;
                border-radius: 6px; padding: 10px 20px; font-size: 13px;
            }
            QPushButton:hover { background: #e5e7eb; }
        """)
        skip_btn.clicked.connect(self.reject)
        button_layout.addWidget(skip_btn)

        # 直接下载按钮（如果有下载链接）
        if self.update_info.download_url:
            download_btn = QPushButton("下载更新")
            download_btn.setStyleSheet("""
                QPushButton {
                    background: #2563eb; color: white; border: none;
                    border-radius: 6px; padding: 10px 24px; font-size: 13px;
                    font-weight: 600;
                }
                QPushButton:hover { background: #1d4ed8; }
            """)
            download_btn.clicked.connect(self._open_download)
            button_layout.addWidget(download_btn)

        # 手动下载页按钮（始终显示，作为备用）
        page_btn = QPushButton("打开下载页")
        page_btn.setStyleSheet("""
            QPushButton {
                background: #ffffff; color: #2563eb; border: 1px solid #2563eb;
                border-radius: 6px; padding: 10px 20px; font-size: 13px;
            }
            QPushButton:hover { background: #eff6ff; }
        """)
        page_btn.clicked.connect(self._open_download_page)
        button_layout.addWidget(page_btn)

        layout.addLayout(button_layout)

    def _open_download(self):
        """在浏览器中打开直接下载链接。"""
        import webbrowser
        if self.update_info.download_url:
            webbrowser.open(self.update_info.download_url)
        self.accept()

    def _open_download_page(self):
        """打开手动下载页面（备用方案）。"""
        import webbrowser
        for page_url in self.update_info.download_pages:
            webbrowser.open(page_url)
            break  # 只打开第一个可用页面
        self.accept()


def show_update_dialog(update_info: UpdateInfo, parent=None) -> bool:
    """显示更新对话框，返回 True 表示用户选择了下载。

    如果 update_info.is_newer 为 False，不显示对话框。
    """
    if not update_info.is_newer:
        return False

    dialog = UpdateDialog(update_info, parent)
    result = dialog.exec()
    return result == QDialog.DialogCode.Accepted
