"""
CleanBot v2.0 — 形象选择界面

让用户选择不同的桌面机器人形象。
"""

import sys
import os
from pathlib import Path
from typing import Dict, List, Optional

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGridLayout, QScrollArea, QFrame, QMessageBox, QFileDialog
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QPixmap, QFont, QColor


class CharacterCard(QFrame):
    """角色卡片"""

    clicked = pyqtSignal(str)

    def __init__(self, character_id: str, name: str, description: str,
                 image_path: str, parent=None):
        super().__init__(parent)

        self.character_id = character_id
        self.name = name
        self.description = description
        self.image_path = image_path

        self._init_ui()

    def _init_ui(self):
        """初始化 UI"""
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        self.setFixedSize(180, 220)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        # 设置样式
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 2px solid #E0E0E0;
                border-radius: 10px;
                padding: 10px;
            }
            QFrame:hover {
                border: 2px solid #2196F3;
                background-color: #F5F5F5;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # 角色图片
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setFixedSize(150, 150)

        if os.path.exists(self.image_path):
            pixmap = QPixmap(self.image_path)
            pixmap = pixmap.scaled(
                150, 150,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.image_label.setPixmap(pixmap)
        else:
            self.image_label.setText("暂无图片")
            self.image_label.setStyleSheet("color: #999999;")

        layout.addWidget(self.image_label)

        # 角色名称
        name_label = QLabel(self.name)
        name_label.setFont(QFont("Microsoft YaHei", 12, QFont.Weight.Bold))
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(name_label)

        # 角色描述
        desc_label = QLabel(self.description)
        desc_label.setFont(QFont("Microsoft YaHei", 9))
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #666666;")
        layout.addWidget(desc_label)

    def mousePressEvent(self, event):
        """鼠标点击事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.character_id)


class CharacterSelector(QWidget):
    """形象选择界面"""

    character_selected = pyqtSignal(str)

    def __init__(self, character_manager, parent=None):
        super().__init__(parent)

        self.character_manager = character_manager
        self.selected_character_id = None

        self.setWindowTitle("选择形象")
        self.setFixedSize(600, 500)

        self._init_ui()
        self._load_characters()

    def _init_ui(self):
        """初始化 UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # 标题
        title_label = QLabel("选择你的桌面机器人形象")
        title_label.setFont(QFont("Microsoft YaHei", 18, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # 描述
        desc_label = QLabel("选择一个你喜欢的形象，它会出现在你的桌面上")
        desc_label.setFont(QFont("Microsoft YaHei", 11))
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setStyleSheet("color: #666666;")
        layout.addWidget(desc_label)

        # 角色列表滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # 角色网格
        self.character_grid = QWidget()
        self.grid_layout = QGridLayout(self.character_grid)
        self.grid_layout.setSpacing(20)

        scroll_area.setWidget(self.character_grid)
        layout.addWidget(scroll_area)

        # 按钮区域
        button_layout = QHBoxLayout()

        # 导入自定义形象按钮
        import_button = QPushButton("导入自定义形象")
        import_button.setFont(QFont("Microsoft YaHei", 11))
        import_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #388E3C;
            }
        """)
        import_button.clicked.connect(self._import_character)
        button_layout.addWidget(import_button)

        button_layout.addStretch()

        # 确认按钮
        confirm_button = QPushButton("确认选择")
        confirm_button.setFont(QFont("Microsoft YaHei", 11))
        confirm_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        confirm_button.clicked.connect(self._confirm_selection)
        button_layout.addWidget(confirm_button)

        # 取消按钮
        cancel_button = QPushButton("取消")
        cancel_button.setFont(QFont("Microsoft YaHei", 11))
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #F5F5F5;
                color: #333333;
                border: 1px solid #E0E0E0;
                border-radius: 5px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #E0E0E0;
            }
        """)
        cancel_button.clicked.connect(self.close)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

    def _load_characters(self):
        """加载角色列表"""
        # 清空现有内容
        while self.grid_layout.count():
            child = self.grid_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # 获取所有角色
        character_names = self.character_manager.get_character_names()
        character_list = self.character_manager.get_character_list()

        # 添加角色卡片
        row = 0
        col = 0

        for character_id in character_list:
            character = self.character_manager.get_character(character_id)
            if character:
                name = character.get_name()
                description = character.get_description()
                image_path = character.get_default_image() or ""

                card = CharacterCard(character_id, name, description, image_path)
                card.clicked.connect(self._on_character_clicked)

                self.grid_layout.addWidget(card, row, col)

                col += 1
                if col >= 3:
                    col = 0
                    row += 1

    def _on_character_clicked(self, character_id: str):
        """角色卡片点击事件"""
        self.selected_character_id = character_id

        # 更新选中状态
        for i in range(self.grid_layout.count()):
            widget = self.grid_layout.itemAt(i).widget()
            if isinstance(widget, CharacterCard):
                if widget.character_id == character_id:
                    widget.setStyleSheet("""
                        QFrame {
                            background-color: #E3F2FD;
                            border: 2px solid #2196F3;
                            border-radius: 10px;
                            padding: 10px;
                        }
                    """)
                else:
                    widget.setStyleSheet("""
                        QFrame {
                            background-color: white;
                            border: 2px solid #E0E0E0;
                            border-radius: 10px;
                            padding: 10px;
                        }
                        QFrame:hover {
                            border: 2px solid #2196F3;
                            background-color: #F5F5F5;
                        }
                    """)

    def _import_character(self):
        """导入自定义形象"""
        # 打开文件对话框
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择形象配置文件",
            "",
            "JSON 文件 (*.json);;所有文件 (*.*)"
        )

        if file_path:
            try:
                # 复制文件到角色目录
                import shutil
                character_dir = os.path.join(
                    os.path.dirname(__file__),
                    "characters",
                    "custom"
                )
                os.makedirs(character_dir, exist_ok=True)

                # 复制配置文件
                dest_path = os.path.join(character_dir, "config.json")
                shutil.copy2(file_path, dest_path)

                # 重新加载角色
                self.character_manager._load_characters()
                self._load_characters()

                QMessageBox.information(self, "成功", "形象导入成功！")

            except Exception as e:
                QMessageBox.critical(self, "错误", f"导入失败: {str(e)}")

    def _confirm_selection(self):
        """确认选择"""
        if self.selected_character_id:
            self.character_selected.emit(self.selected_character_id)
            self.close()
        else:
            QMessageBox.warning(self, "提示", "请先选择一个形象")


def main():
    """测试入口"""
    from PyQt6.QtWidgets import QApplication
    from ui.robot.character import CharacterManager

    app = QApplication(sys.argv)

    # 创建角色管理器
    character_manager = CharacterManager()

    # 创建形象选择界面
    selector = CharacterSelector(character_manager)
    selector.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
