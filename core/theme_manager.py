"""
CleanBot v3.0 -- Theme Manager

Manages application themes:
- Light/Dark theme support
- Custom theme creation
- Theme persistence
- Dynamic theme switching
"""

import json
import os
from pathlib import Path
from typing import Dict, Optional, List
from dataclasses import dataclass, field


@dataclass
class ThemeColors:
    """Theme color palette."""
    # Primary colors
    primary: str = "#3b82f6"
    primary_hover: str = "#2563eb"
    primary_light: str = "#dbeafe"

    # Background colors
    background: str = "#ffffff"
    background_secondary: str = "#f8fafc"
    background_tertiary: str = "#f1f5f9"

    # Text colors
    text_primary: str = "#1e293b"
    text_secondary: str = "#64748b"
    text_tertiary: str = "#94a3b8"

    # Border colors
    border: str = "#e2e8f0"
    border_light: str: str = "#f1f5f9"

    # Status colors
    success: str = "#22c55e"
    success_light: str = "#dcfce7"
    warning: str = "#eab308"
    warning_light: str = "#fef3c7"
    error: str = "#ef4444"
    error_light: str = "#fee2e2"
    info: str = "#3b82f6"
    info_light: str = "#dbeafe"

    # Accent colors
    accent: str = "#8b5cf6"
    accent_light: str = "#ede9fe"

    # Shadow
    shadow: str = "rgba(0, 0, 0, 0.1)"
    shadow_light: str = "rgba(0, 0, 0, 0.05)"


@dataclass
class ThemeConfig:
    """Theme configuration."""
    name: str
    display_name: str
    colors: ThemeColors
    font_family: str = "Microsoft YaHei"
    font_size_small: int = 10
    font_size_normal: int = 12
    font_size_large: int = 14
    font_size_xlarge: int = 16
    border_radius: int = 8
    border_radius_large: int = 12
    spacing_small: int = 8
    spacing_normal: int = 12
    spacing_large: int = 16
    spacing_xlarge: int = 24


class ThemeManager:
    """Manages application themes."""

    # Predefined themes
    THEMES = {
        "light": ThemeConfig(
            name="light",
            display_name="Light",
            colors=ThemeColors(),
        ),
        "dark": ThemeConfig(
            name="dark",
            display_name="Dark",
            colors=ThemeColors(
                primary="#60a5fa",
                primary_hover="#3b82f6",
                primary_light="#1e3a5f",
                background="#0f172a",
                background_secondary="#1e293b",
                background_tertiary="#334155",
                text_primary="#f1f5f9",
                text_secondary="#94a3b8",
                text_tertiary="#64748b",
                border="#334155",
                border_light="#1e293b",
                success="#4ade80",
                success_light="#14532d",
                warning="#fbbf24",
                warning_light="#78350f",
                error="#f87171",
                error_light="#7f1d1d",
                info="#60a5fa",
                info_light="#1e3a5f",
                accent="#a78bfa",
                accent_light="#2e1065",
                shadow="rgba(0, 0, 0, 0.3)",
                shadow_light="rgba(0, 0, 0, 0.2)",
            ),
        ),
        "blue": ThemeConfig(
            name="blue",
            display_name="Blue",
            colors=ThemeColors(
                primary="#2563eb",
                primary_hover="#1d4ed8",
                primary_light="#dbeafe",
                background="#eff6ff",
                background_secondary="#dbeafe",
                background_tertiary="#bfdbfe",
                text_primary="#1e3a8a",
                text_secondary="#1e40af",
                text_tertiary="#3b82f6",
                border="#93c5fd",
                border_light="#bfdbfe",
            ),
        ),
        "green": ThemeConfig(
            name="green",
            display_name="Green",
            colors=ThemeColors(
                primary="#16a34a",
                primary_hover="#15803d",
                primary_light="#dcfce7",
                background="#f0fdf4",
                background_secondary="#dcfce7",
                background_tertiary="#bbf7d0",
                text_primary="#14532d",
                text_secondary="#166534",
                text_tertiary="#22c55e",
                border="#86efac",
                border_light="#bbf7d0",
            ),
        ),
    }

    def __init__(self, config_dir: str = None):
        self.config_dir = Path(config_dir or os.path.expanduser("~/CleanBot/config"))
        self.config_dir.mkdir(parents=True, exist_ok=True)

        self._current_theme: str = "light"
        self._custom_themes: Dict[str, ThemeConfig] = {}
        self._listeners: List[callable] = []

        # Load saved theme preference
        self._load_theme_preference()

        # Load custom themes
        self._load_custom_themes()

    def _load_theme_preference(self):
        """Load saved theme preference."""
        pref_file = self.config_dir / "theme_preference.json"
        if pref_file.exists():
            try:
                with open(pref_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._current_theme = data.get("theme", "light")
            except (json.JSONDecodeError, OSError):
                pass

    def _save_theme_preference(self):
        """Save theme preference."""
        pref_file = self.config_dir / "theme_preference.json"
        try:
            with open(pref_file, "w", encoding="utf-8") as f:
                json.dump({"theme": self._current_theme}, f, indent=2)
        except OSError:
            pass

    def _load_custom_themes(self):
        """Load custom themes from config directory."""
        themes_dir = self.config_dir / "themes"
        if not themes_dir.exists():
            return

        for theme_file in themes_dir.glob("*.json"):
            try:
                with open(theme_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    theme = self._parse_theme_config(data)
                    if theme:
                        self._custom_themes[theme.name] = theme
            except (json.JSONDecodeError, OSError):
                continue

    def _parse_theme_config(self, data: dict) -> Optional[ThemeConfig]:
        """Parse theme config from JSON data."""
        try:
            colors_data = data.get("colors", {})
            colors = ThemeColors(**colors_data)

            return ThemeConfig(
                name=data.get("name", "custom"),
                display_name=data.get("display_name", "Custom"),
                colors=colors,
                font_family=data.get("font_family", "Microsoft YaHei"),
                font_size_small=data.get("font_size_small", 10),
                font_size_normal=data.get("font_size_normal", 12),
                font_size_large=data.get("font_size_large", 14),
                font_size_xlarge=data.get("font_size_xlarge", 16),
                border_radius=data.get("border_radius", 8),
                border_radius_large=data.get("border_radius_large", 12),
                spacing_small=data.get("spacing_small", 8),
                spacing_normal=data.get("spacing_normal", 12),
                spacing_large=data.get("spacing_large", 16),
                spacing_xlarge=data.get("spacing_xlarge", 24),
            )
        except (KeyError, TypeError):
            return None

    def get_current_theme(self) -> ThemeConfig:
        """Get current theme configuration."""
        if self._current_theme in self.THEMES:
            return self.THEMES[self._current_theme]
        elif self._current_theme in self._custom_themes:
            return self._custom_themes[self._current_theme]
        else:
            return self.THEMES["light"]

    def get_current_theme_name(self) -> str:
        """Get current theme name."""
        return self._current_theme

    def set_theme(self, theme_name: str) -> bool:
        """Set current theme."""
        if theme_name in self.THEMES or theme_name in self._custom_themes:
            self._current_theme = theme_name
            self._save_theme_preference()
            self._notify_listeners()
            return True
        return False

    def get_available_themes(self) -> List[Dict[str, str]]:
        """Get list of available themes."""
        themes = []

        for name, config in self.THEMES.items():
            themes.append({
                "name": name,
                "display_name": config.display_name,
                "type": "built-in",
            })

        for name, config in self._custom_themes.items():
            themes.append({
                "name": name,
                "display_name": config.display_name,
                "type": "custom",
            })

        return themes

    def register_listener(self, listener: callable):
        """Register theme change listener."""
        self._listeners.append(listener)

    def unregister_listener(self, listener: callable):
        """Unregister theme change listener."""
        if listener in self._listeners:
            self._listeners.remove(listener)

    def _notify_listeners(self):
        """Notify all listeners of theme change."""
        theme = self.get_current_theme()
        for listener in self._listeners:
            try:
                listener(theme)
            except Exception:
                pass

    def get_stylesheet(self, component: str = "global") -> str:
        """Get stylesheet for a component."""
        theme = self.get_current_theme()
        colors = theme.colors

        if component == "global":
            return self._get_global_stylesheet(theme)
        elif component == "button":
            return self._get_button_stylesheet(theme)
        elif component == "input":
            return self._get_input_stylesheet(theme)
        elif component == "card":
            return self._get_card_stylesheet(theme)
        elif component == "navigation":
            return self._get_navigation_stylesheet(theme)
        else:
            return ""

    def _get_global_stylesheet(self, theme: ThemeConfig) -> str:
        """Get global stylesheet."""
        c = theme.colors
        return f"""
            QMainWindow {{
                background-color: {c.background};
            }}
            QWidget {{
                font-family: {theme.font_family};
                font-size: {theme.font_size_normal}px;
                color: {c.text_primary};
            }}
            QLabel {{
                color: {c.text_primary};
                border: none;
            }}
            QFrame {{
                border: none;
            }}
        """

    def _get_button_stylesheet(self, theme: ThemeConfig) -> str:
        """Get button stylesheet."""
        c = theme.colors
        r = theme.border_radius
        return f"""
            QPushButton {{
                background-color: {c.primary};
                color: white;
                border: none;
                border-radius: {r}px;
                padding: 8px 16px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {c.primary_hover};
            }}
            QPushButton:disabled {{
                background-color: {c.text_tertiary};
                color: {c.background};
            }}
            QPushButton:pressed {{
                background-color: {c.primary_hover};
            }}
        """

    def _get_input_stylesheet(self, theme: ThemeConfig) -> str:
        """Get input stylesheet."""
        c = theme.colors
        r = theme.border_radius
        return f"""
            QLineEdit, QTextEdit, QSpinBox, QComboBox {{
                background-color: {c.background};
                color: {c.text_primary};
                border: 1px solid {c.border};
                border-radius: {r}px;
                padding: 8px 12px;
            }}
            QLineEdit:focus, QTextEdit:focus, QSpinBox:focus, QComboBox:focus {{
                border-color: {c.primary};
            }}
        """

    def _get_card_stylesheet(self, theme: ThemeConfig) -> str:
        """Get card stylesheet."""
        c = theme.colors
        r = theme.border_radius_large
        return f"""
            QFrame[class="card"] {{
                background-color: {c.background};
                border: 1px solid {c.border};
                border-radius: {r}px;
                padding: {theme.spacing_large}px;
            }}
        """

    def _get_navigation_stylesheet(self, theme: ThemeConfig) -> str:
        """Get navigation stylesheet."""
        c = theme.colors
        r = theme.border_radius
        return f"""
            QPushButton[class="nav-item"] {{
                background-color: transparent;
                color: {c.text_secondary};
                border: none;
                border-radius: {r}px;
                padding: 10px 16px;
                text-align: left;
                font-size: {theme.font_size_normal}px;
            }}
            QPushButton[class="nav-item"]:hover {{
                background-color: {c.background_tertiary};
                color: {c.text_primary};
            }}
            QPushButton[class="nav-item"]:checked {{
                background-color: {c.primary_light};
                color: {c.primary};
                font-weight: 600;
            }}
        """

    def save_custom_theme(self, name: str, config: ThemeConfig) -> bool:
        """Save a custom theme."""
        try:
            themes_dir = self.config_dir / "themes"
            themes_dir.mkdir(parents=True, exist_ok=True)

            theme_file = themes_dir / f"{name}.json"
            data = {
                "name": config.name,
                "display_name": config.display_name,
                "colors": config.colors.__dict__,
                "font_family": config.font_family,
                "font_size_small": config.font_size_small,
                "font_size_normal": config.font_size_normal,
                "font_size_large": config.font_size_large,
                "font_size_xlarge": config.font_size_xlarge,
                "border_radius": config.border_radius,
                "border_radius_large": config.border_radius_large,
                "spacing_small": config.spacing_small,
                "spacing_normal": config.spacing_normal,
                "spacing_large": config.spacing_large,
                "spacing_xlarge": config.spacing_xlarge,
            }

            with open(theme_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            self._custom_themes[name] = config
            return True
        except OSError:
            return False

    def delete_custom_theme(self, name: str) -> bool:
        """Delete a custom theme."""
        if name not in self._custom_themes:
            return False

        try:
            theme_file = self.config_dir / "themes" / f"{name}.json"
            if theme_file.exists():
                theme_file.unlink()

            del self._custom_themes[name]

            # Switch to light theme if current theme was deleted
            if self._current_theme == name:
                self.set_theme("light")

            return True
        except OSError:
            return False


# Global theme manager instance
_theme_manager: Optional[ThemeManager] = None


def get_theme_manager() -> ThemeManager:
    """Get global theme manager instance."""
    global _theme_manager
    if _theme_manager is None:
        _theme_manager = ThemeManager()
    return _theme_manager


def get_current_theme() -> ThemeConfig:
    """Get current theme configuration."""
    return get_theme_manager().get_current_theme()


def get_stylesheet(component: str = "global") -> str:
    """Get stylesheet for a component."""
    return get_theme_manager().get_stylesheet(component)
