#!/usr/bin/env python3
"""
CleanBot v2.0 — 桌面机器人入口

启动桌面机器人，显示在桌面上。

Usage:
  main_robot.py             启动桌面机器人
  main_robot.py --character conan  指定角色
  main_robot.py --selector  打开形象选择器
"""

import sys
import os
import argparse
from pathlib import Path

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt

from ui.robot import RobotWidget
from ui.robot.character import CharacterManager
from ui.robot.character_selector import CharacterSelector


class CleanBotApp:
    """CleanBot 应用程序"""

    def __init__(self, character_id: str = "conan"):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)

        # 创建角色管理器
        self.character_manager = CharacterManager()

        # 创建机器人
        self.robot = RobotWidget()
        self.robot.switch_character(character_id)

        # 连接信号
        self.robot.double_clicked.connect(self._on_robot_double_clicked)
        self.robot.character_changed.connect(self._on_character_changed)

        # 创建系统托盘
        self._create_system_tray()

        # 显示机器人
        self.robot.show()

        # 显示欢迎消息
        self.robot.show_speech("你好！我是CleanBot！")

    def _create_system_tray(self):
        """创建系统托盘"""
        # 检查系统托盘是否可用
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return

        # 创建系统托盘图标
        self.tray_icon = QSystemTrayIcon(self.app)

        # 设置图标
        icon_path = os.path.join(PROJECT_ROOT, "resources", "icons", "cleanbot.ico")
        if os.path.exists(icon_path):
            self.tray_icon.setIcon(QIcon(icon_path))
        else:
            # 使用默认图标
            self.tray_icon.setIcon(QIcon.fromTheme("edit-clear"))

        # 创建托盘菜单
        tray_menu = QMenu()

        # 显示/隐藏机器人
        show_action = QAction("显示机器人", self.app)
        show_action.triggered.connect(self.robot.show)
        tray_menu.addAction(show_action)

        hide_action = QAction("隐藏机器人", self.app)
        hide_action.triggered.connect(self.robot.hide)
        tray_menu.addAction(hide_action)

        tray_menu.addSeparator()

        # 切换角色
        character_menu = tray_menu.addMenu("切换角色")
        for character_id in self.character_manager.get_character_list():
            action = QAction(character_id, self.app)
            action.triggered.connect(
                lambda checked, cid=character_id: self.robot.switch_character(cid)
            )
            character_menu.addAction(action)

        tray_menu.addSeparator()

        # 打开形象选择器
        selector_action = QAction("选择形象", self.app)
        selector_action.triggered.connect(self._open_character_selector)
        tray_menu.addAction(selector_action)

        tray_menu.addSeparator()

        # 退出
        quit_action = QAction("退出", self.app)
        quit_action.triggered.connect(self._quit)
        tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(tray_menu)

        # 双击托盘图标显示机器人
        self.tray_icon.activated.connect(self._on_tray_icon_activated)

        # 显示托盘图标
        self.tray_icon.show()

    def _on_robot_double_clicked(self):
        """机器人双击事件"""
        # 打开主界面
        from ui.main_window import MainWindow
        self.main_window = MainWindow()
        self.main_window.show()

    def _on_character_changed(self, character_id: str):
        """角色改变事件"""
        self.robot.show_speech(f"我变成了{character_id}！")

    def _on_tray_icon_activated(self, reason):
        """托盘图标激活事件"""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.robot.show()
            self.robot.activateWindow()

    def _open_character_selector(self):
        """打开形象选择器"""
        self.selector = CharacterSelector(self.character_manager)
        self.selector.character_selected.connect(self.robot.switch_character)
        self.selector.show()

    def _quit(self):
        """退出程序"""
        self.robot.hide()
        self.tray_icon.hide()
        self.app.quit()

    def run(self):
        """运行应用程序"""
        return self.app.exec()


def main():
    """主入口"""
    parser = argparse.ArgumentParser(
        description="CleanBot v2.0 — 桌面机器人"
    )

    parser.add_argument(
        "--character",
        type=str,
        default="conan",
        help="指定角色ID（默认：conan）"
    )

    parser.add_argument(
        "--selector",
        action="store_true",
        help="打开形象选择器"
    )

    args = parser.parse_args()

    # 如果指定打开选择器
    if args.selector:
        app = QApplication(sys.argv)
        character_manager = CharacterManager()
        selector = CharacterSelector(character_manager)
        selector.show()
        sys.exit(app.exec())

    # 启动桌面机器人
    bot = CleanBotApp(args.character)
    sys.exit(bot.run())


if __name__ == "__main__":
    main()
