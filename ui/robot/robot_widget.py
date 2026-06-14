"""
CleanBot v2.0 — 桌面机器人控件

可爱的桌面机器人，支持动画、表情、交互。
"""

import sys
import os
import json
import random
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QMenu,
    QGraphicsOpacityEffect, QSystemTrayIcon, QApplication
)
from PyQt6.QtCore import (
    Qt, QTimer, QPoint, QSize, pyqtSignal, QPropertyAnimation,
    QEasingCurve, QRect, QThread
)
from PyQt6.QtGui import (
    QPixmap, QPainter, QColor, QFont, QPen, QBrush,
    QCursor, QAction, QIcon, QContextMenuEvent, QMouseEvent,
    QPaintEvent, QMoveEvent
)

from ui.robot.character import Character, CharacterManager
from ui.robot.animation import AnimationSystem
from ui.robot.expression import ExpressionSystem


class RobotWidget(QWidget):
    """桌面机器人控件"""

    # 信号
    clicked = pyqtSignal()
    double_clicked = pyqtSignal()
    right_clicked = pyqtSignal(QPoint)
    character_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        # 设置窗口属性
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(200, 200)

        # 初始化系统
        self.character_manager = CharacterManager()
        self.animation_system = AnimationSystem()
        self.expression_system = ExpressionSystem()

        # 状态
        self.is_dragging = False
        self.drag_position = QPoint()
        self.current_state = "idle"
        self.is_speaking = False
        self.speech_text = ""

        # 初始化 UI
        self._init_ui()

        # 初始化定时器
        self._init_timers()

        # 加载默认角色
        self._load_default_character()

        # 初始位置
        self._set_initial_position()

    def _init_ui(self):
        """初始化 UI"""
        # 角色图片标签
        self.character_label = QLabel(self)
        self.character_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.character_label.setGeometry(0, 0, 200, 200)

        # 对话气泡
        self.speech_bubble = QLabel(self)
        self.speech_bubble.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.speech_bubble.setWordWrap(True)
        self.speech_bubble.setStyleSheet("""
            QLabel {
                background-color: white;
                border: 2px solid #2196F3;
                border-radius: 10px;
                padding: 10px;
                font-family: "Microsoft YaHei";
                font-size: 12px;
            }
        """)
        self.speech_bubble.hide()

        # 状态指示器
        self.status_label = QLabel(self)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("""
            QLabel {
                background-color: rgba(0, 0, 0, 0.7);
                color: white;
                border-radius: 8px;
                padding: 2px 6px;
                font-family: "Microsoft YaHei";
                font-size: 10px;
            }
        """)
        self.status_label.hide()

    def _init_timers(self):
        """初始化定时器"""
        # 眨眼定时器
        self.blink_timer = QTimer()
        self.blink_timer.timeout.connect(self._blink)
        self.blink_timer.start(3000)  # 每3秒眨眼一次

        # 动画更新定时器
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self._update_animation)
        self.animation_timer.start(100)  # 10fps

        # 随机行为定时器
        self.random_behavior_timer = QTimer()
        self.random_behavior_timer.timeout.connect(self._random_behavior)
        self.random_behavior_timer.start(10000)  # 每10秒随机行为

        # 对话隐藏定时器
        self.speech_timer = QTimer()
        self.speech_timer.timeout.connect(self._hide_speech)
        self.speech_timer.setSingleShot(True)

    def _load_default_character(self):
        """加载默认角色"""
        self.character_manager.switch_character("conan")
        self._update_character_display()

    def _set_initial_position(self):
        """设置初始位置"""
        # 获取屏幕尺寸
        screen = QApplication.primaryScreen()
        if screen:
            geometry = screen.availableGeometry()
            # 默认放在右下角
            x = geometry.width() - 250
            y = geometry.height() - 250
            self.move(x, y)

    def _update_character_display(self):
        """更新角色显示"""
        character = self.character_manager.get_current_character()
        if character:
            # 获取当前表情的图片
            expression = self.expression_system.get_current_expression()
            image_path = character.get_expression_image(expression)

            if image_path and os.path.exists(image_path):
                pixmap = QPixmap(image_path)
                pixmap = pixmap.scaled(
                    180, 180,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.character_label.setPixmap(pixmap)
            else:
                # 使用默认图片
                default_image = character.get_default_image()
                if default_image and os.path.exists(default_image):
                    pixmap = QPixmap(default_image)
                    pixmap = pixmap.scaled(
                        180, 180,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                    self.character_label.setPixmap(pixmap)

    def _blink(self):
        """眨眼动画"""
        character = self.character_manager.get_current_character()
        if character:
            # 临时切换到眨眼表情
            self.expression_system.set_expression("blink")
            self._update_character_display()

            # 200ms后恢复
            QTimer.singleShot(200, lambda: (
                self.expression_system.set_expression(self.current_state),
                self._update_character_display()
            ))

    def _update_animation(self):
        """更新动画"""
        frame = self.animation_system.update()
        if frame:
            # 更新角色图片
            character = self.character_manager.get_current_character()
            if character:
                image_path = character.get_animation_frame(frame)
                if image_path and os.path.exists(image_path):
                    pixmap = QPixmap(image_path)
                    pixmap = pixmap.scaled(
                        180, 180,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                    self.character_label.setPixmap(pixmap)

    def _random_behavior(self):
        """随机行为"""
        behaviors = [
            self._look_around,
            self._stretch,
            self._yawn,
            self._wave,
        ]

        # 随机选择一个行为
        behavior = random.choice(behaviors)
        behavior()

    def _look_around(self):
        """左右看"""
        self.animation_system.play("look_around", loop=False)

    def _stretch(self):
        """伸懒腰"""
        self.animation_system.play("stretch", loop=False)

    def _yawn(self):
        """打哈欠"""
        self.animation_system.play("yawn", loop=False)
        self.show_speech("好困啊...")

    def _wave(self):
        """挥手"""
        self.animation_system.play("wave", loop=False)

    def set_state(self, state: str):
        """
        设置状态

        Args:
            state: 状态名称 (idle, thinking, working, happy, sad)
        """
        self.current_state = state
        self.expression_system.set_expression(state)
        self._update_character_display()

        # 更新状态指示器
        state_texts = {
            "idle": "空闲",
            "thinking": "思考中...",
            "working": "工作中...",
            "happy": "开心！",
            "sad": "难过...",
        }

        if state in state_texts:
            self.status_label.setText(state_texts[state])
            self.status_label.show()

            # 3秒后隐藏
            QTimer.singleShot(3000, self.status_label.hide)

    def show_speech(self, text: str, duration: int = 3000):
        """
        显示对话气泡

        Args:
            text: 对话文本
            duration: 显示时长（毫秒）
        """
        self.speech_text = text
        self.is_speaking = True

        # 设置文本
        self.speech_bubble.setText(text)
        self.speech_bubble.adjustSize()

        # 调整位置（在角色上方）
        bubble_width = self.speech_bubble.width()
        bubble_height = self.speech_bubble.height()
        x = (200 - bubble_width) // 2
        y = -bubble_height - 10

        self.speech_bubble.move(x, y)
        self.speech_bubble.show()

        # 设置隐藏定时器
        self.speech_timer.start(duration)

    def _hide_speech(self):
        """隐藏对话气泡"""
        self.speech_bubble.hide()
        self.is_speaking = False

    def switch_character(self, character_id: str):
        """
        切换角色

        Args:
            character_id: 角色ID
        """
        self.character_manager.switch_character(character_id)
        self._update_character_display()
        self.character_changed.emit(character_id)

    def get_character_list(self) -> List[str]:
        """获取可用角色列表"""
        return self.character_manager.get_character_list()

    # 鼠标事件
    def mousePressEvent(self, event: QMouseEvent):
        """鼠标按下事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = True
            self.drag_position = event.globalPosition().toPoint() - self.pos()
            self.clicked.emit()

    def mouseMoveEvent(self, event: QMouseEvent):
        """鼠标移动事件"""
        if self.is_dragging and event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)

    def mouseReleaseEvent(self, event: QMouseEvent):
        """鼠标释放事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = False

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        """鼠标双击事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.double_clicked.emit()

    def contextMenuEvent(self, event: QContextMenuEvent):
        """右键菜单事件"""
        self.right_clicked.emit(event.globalPos())

        # 创建菜单
        menu = QMenu(self)

        # 角色子菜单
        character_menu = menu.addMenu("切换角色")
        for character_id in self.get_character_list():
            action = QAction(character_id, self)
            action.triggered.connect(lambda checked, cid=character_id: self.switch_character(cid))
            character_menu.addAction(action)

        menu.addSeparator()

        # 状态子菜单
        state_menu = menu.addMenu("设置状态")
        states = [
            ("空闲", "idle"),
            ("思考中", "thinking"),
            ("工作中", "working"),
            ("开心", "happy"),
            ("难过", "sad"),
        ]
        for text, state in states:
            action = QAction(text, self)
            action.triggered.connect(lambda checked, s=state: self.set_state(s))
            state_menu.addAction(action)

        menu.addSeparator()

        # 对话测试
        speech_action = QAction("测试对话", self)
        speech_action.triggered.connect(lambda: self.show_speech("你好！我是CleanBot！"))
        menu.addAction(speech_action)

        menu.addSeparator()

        # 退出
        quit_action = QAction("退出", self)
        quit_action.triggered.connect(QApplication.quit)
        menu.addAction(quit_action)

        # 显示菜单
        menu.exec(event.globalPos())


def main():
    """测试入口"""
    app = QApplication(sys.argv)

    # 创建机器人
    robot = RobotWidget()
    robot.show()

    # 测试对话
    robot.show_speech("你好！我是CleanBot！")

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
