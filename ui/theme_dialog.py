"""
CleanBot v3.0 -- Theme Dialog

Provides theme selection and customization:
- Theme preview
- Theme switching
- Custom theme creation
- Theme persistence
"""

from typing import Optional, List
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QWidget, QGroupBox, QGridLayout,
    QComboBox, QColorDialog, QSpinBox, QLineEdit, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor

from core.theme_manager import (
    ThemeManager, ThemeConfig, ThemeColors,
    get_theme_manager
)


class ThemeCard(QFrame):
    """Theme preview card."""

    clicked = pyqtSignal(str)

    def __init__(self, theme_name: str, display_name: str, colors: ThemeColors, parent=None):
        super().__init__(parent)
        self.theme_name = theme_name
        self._display_name = display_name
        self._colors = colors

        self.setFixedSize(180, 120)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._update_style(selected=False)

        self._init_ui()

    def _init_ui(self):
        """Initialize UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(12, 12, 12, 12)

        # Theme name
        name_label = QLabel(self._display_name)
        name_label.setFont(QFont("Microsoft YaHei", 11, QFont.Weight.Bold))
        name_label.setStyleSheet(f"color: {self._colors.text_primary};")
        layout.addWidget(name_label)

        # Color preview
        colors_layout = QHBoxLayout()
        colors_layout.setSpacing(4)

        color_items = [
            ("Primary", self._colors.primary),
            ("Background", self._colors.background),
            ("Text", self._colors.text_primary),
            ("Border", self._colors.border),
        ]

        for name, color in color_items:
            color_frame = QFrame()
            color_frame.setFixedSize(24, 24)
            color_frame.setStyleSheet(f"""
                QFrame {{
                    background-color: {color};
                    border: 1px solid {self._colors.border};
                    border-radius: 4px;
                }}
            """)
            color_frame.setToolTip(f"{name}: {color}")
            colors_layout.addWidget(color_frame)

        colors_layout.addStretch()
        layout.addLayout(colors_layout)

        # Preview text
        preview = QLabel("Preview Text")
        preview.setFont(QFont("Microsoft YaHei", 9))
        preview.setStyleSheet(f"color: {self._colors.text_secondary};")
        layout.addWidget(preview)

        layout.addStretch()

    def _update_style(self, selected: bool):
        """Update card style."""
        if selected:
            self.setStyleSheet(f"""
                QFrame {{
                    background-color: {self._colors.background};
                    border: 2px solid {self._colors.primary};
                    border-radius: 12px;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QFrame {{
                    background-color: {self._colors.background};
                    border: 2px solid {self._colors.border};
                    border-radius: 12px;
                }}
                QFrame:hover {{
                    border-color: {self._colors.primary};
                }}
            """)

    def set_selected(self, selected: bool):
        """Set selected state."""
        self._update_style(selected)

    def mousePressEvent(self, event):
        """Handle mouse press."""
        self.clicked.emit(self.theme_name)
        super().mousePressEvent(event)


class ThemeDialog(QDialog):
    """Theme selection dialog."""

    theme_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Theme Settings")
        self.setMinimumSize(600, 500)
        self.setWindowFlags(
            Qt.WindowType.Dialog |
            Qt.WindowType.WindowTitleHint |
            Qt.WindowType.CustomizeWindowHint
        )

        self._theme_manager = get_theme_manager()
        self._current_theme = self._theme_manager.get_current_theme_name()
        self._theme_cards: List[ThemeCard] = []

        self._init_ui()
        self._load_themes()

    def _init_ui(self):
        """Initialize UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        # Title
        title = QLabel("Choose Theme")
        title.setFont(QFont("Microsoft YaHei", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: #1e293b;")
        layout.addWidget(title)

        # Description
        desc = QLabel("Select a theme for CleanBot. You can switch between light and dark modes.")
        desc.setFont(QFont("Microsoft YaHei", 11))
        desc.setStyleSheet("color: #64748b;")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        # Theme grid
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
        """)

        self._theme_container = QWidget()
        self._theme_grid = QGridLayout(self._theme_container)
        self._theme_grid.setSpacing(16)
        self._theme_grid.setContentsMargins(0, 0, 0, 0)

        scroll_area.setWidget(self._theme_container)
        layout.addWidget(scroll_area)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)

        button_layout.addStretch()

        self._apply_btn = QPushButton("Apply")
        self._apply_btn.setFont(QFont("Microsoft YaHei", 11))
        self._apply_btn.setStyleSheet("""
            QPushButton {
                background: #3b82f6;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 24px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: #2563eb;
            }
        """)
        self._apply_btn.clicked.connect(self._apply_theme)
        button_layout.addWidget(self._apply_btn)

        self._cancel_btn = QPushButton("Cancel")
        self._cancel_btn.setFont(QFont("Microsoft YaHei", 11))
        self._cancel_btn.setStyleSheet("""
            QPushButton {
                background: #f1f5f9;
                color: #475569;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 10px 24px;
            }
            QPushButton:hover {
                background: #e2e8f0;
            }
        """)
        self._cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self._cancel_btn)

        layout.addLayout(button_layout)

    def _load_themes(self):
        """Load available themes."""
        # Clear existing cards
        for card in self._theme_cards:
            card.deleteLater()
        self._theme_cards.clear()

        # Get available themes
        themes = self._theme_manager.get_available_themes()

        # Create theme cards
        row = 0
        col = 0
        for theme_info in themes:
            theme_name = theme_info["name"]
            display_name = theme_info["display_name"]

            # Get theme config
            if theme_name in ThemeManager.THEMES:
                config = ThemeManager.THEMES[theme_name]
            elif theme_name in self._theme_manager._custom_themes:
                config = self._theme_manager._custom_themes[theme_name]
            else:
                continue

            # Create card
            card = ThemeCard(theme_name, display_name, config.colors)
            card.clicked.connect(self._on_theme_selected)
            self._theme_grid.addWidget(card, row, col)

            # Set selected state
            is_selected = theme_name == self._current_theme
            card.set_selected(is_selected)

            self._theme_cards.append(card)

            # Update grid position
            col += 1
            if col >= 3:
                col = 0
                row += 1

    def _on_theme_selected(self, theme_name: str):
        """Handle theme selection."""
        self._current_theme = theme_name

        # Update card selection states
        for card in self._theme_cards:
            card.set_selected(card.theme_name == theme_name)

    def _apply_theme(self):
        """Apply selected theme."""
        if self._theme_manager.set_theme(self._current_theme):
            self.theme_changed.emit(self._current_theme)
            self.accept()
        else:
            QMessageBox.warning(
                self,
                "Theme Error",
                f"Failed to apply theme: {self._current_theme}"
            )

    def get_selected_theme(self) -> str:
        """Get selected theme name."""
        return self._current_theme
