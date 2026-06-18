"""
CleanBot v3.0 -- Progress Dialog

Provides detailed progress feedback:
- Step-by-step progress display
- Estimated time remaining
- Current operation description
- Cancel support
"""

import time
from typing import Optional, List, Callable
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QProgressBar, QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt6.QtGui import QFont


class ProgressDialog(QDialog):
    """Progress dialog with detailed feedback."""

    cancelled = pyqtSignal()

    def __init__(
        self,
        title: str = "Processing...",
        parent=None,
        cancellable: bool = True,
        show_details: bool = True,
    ):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumWidth(450)
        self.setWindowFlags(
            Qt.WindowType.Dialog |
            Qt.WindowType.WindowTitleHint |
            Qt.WindowType.CustomizeWindowHint
        )

        self._start_time = time.time()
        self._current_step = 0
        self._total_steps = 0
        self._is_cancelled = False
        self._cancellable = cancellable
        self._show_details = show_details

        self._init_ui()
        self._init_timers()

    def _init_ui(self):
        """Initialize UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        # Title
        self._title_label = QLabel("Processing...")
        self._title_label.setFont(QFont("Microsoft YaHei", 14, QFont.Weight.Bold))
        self._title_label.setStyleSheet("color: #1e293b;")
        layout.addWidget(self._title_label)

        # Progress bar
        self._progress_bar = QProgressBar()
        self._progress_bar.setFixedHeight(12)
        self._progress_bar.setTextVisible(False)
        self._progress_bar.setStyleSheet("""
            QProgressBar {
                background: #e2e8f0;
                border: none;
                border-radius: 6px;
            }
            QProgressBar::chunk {
                background: #3b82f6;
                border-radius: 6px;
            }
        """)
        layout.addWidget(self._progress_bar)

        # Step info
        step_layout = QHBoxLayout()
        step_layout.setSpacing(8)

        self._step_label = QLabel("Step 0/0")
        self._step_label.setFont(QFont("Microsoft YaHei", 10))
        self._step_label.setStyleSheet("color: #64748b;")
        step_layout.addWidget(self._step_label)

        step_layout.addStretch()

        self._time_label = QLabel("00:00")
        self._time_label.setFont(QFont("Microsoft YaHei", 10))
        self._time_label.setStyleSheet("color: #64748b;")
        step_layout.addWidget(self._time_label)

        layout.addLayout(step_layout)

        # Details (optional)
        if self._show_details:
            self._details_frame = QFrame()
            self._details_frame.setStyleSheet("""
                QFrame {
                    background: #f8fafc;
                    border: 1px solid #e2e8f0;
                    border-radius: 8px;
                    padding: 12px;
                }
            """)
            details_layout = QVBoxLayout(self._details_frame)
            details_layout.setSpacing(4)

            self._current_operation = QLabel("Current operation: None")
            self._current_operation.setFont(QFont("Microsoft YaHei", 10))
            self._current_operation.setStyleSheet("color: #475569;")
            self._current_operation.setWordWrap(True)
            details_layout.addWidget(self._current_operation)

            self._estimated_time = QLabel("Estimated time remaining: Calculating...")
            self._estimated_time.setFont(QFont("Microsoft YaHei", 10))
            self._estimated_time.setStyleSheet("color: #475569;")
            details_layout.addWidget(self._estimated_time)

            layout.addWidget(self._details_frame)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)

        button_layout.addStretch()

        if self._cancellable:
            self._cancel_btn = QPushButton("Cancel")
            self._cancel_btn.setFont(QFont("Microsoft YaHei", 10))
            self._cancel_btn.setStyleSheet("""
                QPushButton {
                    background: #f1f5f9;
                    color: #475569;
                    border: 1px solid #e2e8f0;
                    border-radius: 6px;
                    padding: 8px 16px;
                }
                QPushButton:hover {
                    background: #e2e8f0;
                }
            """)
            self._cancel_btn.clicked.connect(self._on_cancel)
            button_layout.addWidget(self._cancel_btn)

        layout.addLayout(button_layout)

    def _init_timers(self):
        """Initialize timers."""
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update_time)
        self._timer.start(100)  # Update every 100ms

    def _update_time(self):
        """Update elapsed time display."""
        elapsed = time.time() - self._start_time
        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)
        self._time_label.setText(f"{minutes:02d}:{seconds:02d}")

    def _on_cancel(self):
        """Handle cancel button click."""
        self._is_cancelled = True
        self._cancel_btn.setEnabled(False)
        self._cancel_btn.setText("Cancelling...")
        self.cancelled.emit()

    def set_total_steps(self, total: int):
        """Set total number of steps."""
        self._total_steps = total
        self._progress_bar.setMaximum(total)
        self._update_step_display()

    def set_current_step(self, step: int, operation: str = ""):
        """Set current step."""
        self._current_step = step
        self._progress_bar.setValue(step)

        if operation and self._show_details:
            self._current_operation.setText(f"Current operation: {operation}")

        self._update_step_display()
        self._update_estimated_time()

    def _update_step_display(self):
        """Update step display."""
        if self._total_steps > 0:
            self._step_label.setText(f"Step {self._current_step}/{self._total_steps}")
        else:
            self._step_label.setText(f"Step {self._current_step}")

    def _update_estimated_time(self):
        """Update estimated time remaining."""
        if self._current_step == 0 or self._total_steps == 0:
            return

        elapsed = time.time() - self._start_time
        avg_time_per_step = elapsed / self._current_step
        remaining_steps = self._total_steps - self._current_step
        estimated_remaining = avg_time_per_step * remaining_steps

        if estimated_remaining < 60:
            time_str = f"{int(estimated_remaining)} seconds"
        elif estimated_remaining < 3600:
            minutes = int(estimated_remaining // 60)
            seconds = int(estimated_remaining % 60)
            time_str = f"{minutes}m {seconds}s"
        else:
            hours = int(estimated_remaining // 3600)
            minutes = int((estimated_remaining % 3600) // 60)
            time_str = f"{hours}h {minutes}m"

        self._estimated_time.setText(f"Estimated time remaining: {time_str}")

    def set_title(self, title: str):
        """Set dialog title."""
        self._title_label.setText(title)

    def set_progress(self, value: int, maximum: int = 100):
        """Set progress bar value."""
        self._progress_bar.setMaximum(maximum)
        self._progress_bar.setValue(value)

    def is_cancelled(self) -> bool:
        """Check if cancelled."""
        return self._is_cancelled

    def closeEvent(self, event):
        """Handle close event."""
        if not self._is_cancelled and self._cancellable:
            self._is_cancelled = True
            self.cancelled.emit()
        super().closeEvent(event)


class StepProgressDialog(QDialog):
    """Step-by-step progress dialog."""

    cancelled = pyqtSignal()
    step_completed = pyqtSignal(int)

    def __init__(
        self,
        title: str = "Processing...",
        steps: List[str] = None,
        parent=None,
    ):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumWidth(500)
        self.setWindowFlags(
            Qt.WindowType.Dialog |
            Qt.WindowType.WindowTitleHint |
            Qt.WindowType.CustomizeWindowHint
        )

        self._steps = steps or []
        self._current_step = -1
        self._is_cancelled = False
        self._start_time = time.time()

        self._init_ui()

    def _init_ui(self):
        """Initialize UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        # Title
        self._title_label = QLabel(self.windowTitle())
        self._title_label.setFont(QFont("Microsoft YaHei", 14, QFont.Weight.Bold))
        self._title_label.setStyleSheet("color: #1e293b;")
        layout.addWidget(self._title_label)

        # Steps list
        self._step_labels: List[QLabel] = []
        for i, step in enumerate(self._steps):
            step_frame = QFrame()
            step_frame.setStyleSheet("""
                QFrame {
                    background: #f8fafc;
                    border: 1px solid #e2e8f0;
                    border-radius: 6px;
                    padding: 8px 12px;
                }
            """)
            step_layout = QHBoxLayout(step_frame)
            step_layout.setSpacing(8)

            # Status icon
            status_label = QLabel("⏳")
            status_label.setFixedWidth(20)
            step_layout.addWidget(status_label)

            # Step text
            step_label = QLabel(step)
            step_label.setFont(QFont("Microsoft YaHei", 10))
            step_label.setStyleSheet("color: #475569;")
            step_layout.addWidget(step_label)

            step_layout.addStretch()

            layout.addWidget(step_frame)

            self._step_labels.append({
                "frame": step_frame,
                "status": status_label,
                "text": step_label,
            })

        # Progress bar
        self._progress_bar = QProgressBar()
        self._progress_bar.setFixedHeight(8)
        self._progress_bar.setTextVisible(False)
        self._progress_bar.setMaximum(len(self._steps))
        self._progress_bar.setValue(0)
        self._progress_bar.setStyleSheet("""
            QProgressBar {
                background: #e2e8f0;
                border: none;
                border-radius: 4px;
            }
            QProgressBar::chunk {
                background: #3b82f6;
                border-radius: 4px;
            }
        """)
        layout.addWidget(self._progress_bar)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self._cancel_btn = QPushButton("Cancel")
        self._cancel_btn.setFont(QFont("Microsoft YaHei", 10))
        self._cancel_btn.setStyleSheet("""
            QPushButton {
                background: #f1f5f9;
                color: #475569;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background: #e2e8f0;
            }
        """)
        self._cancel_btn.clicked.connect(self._on_cancel)
        button_layout.addWidget(self._cancel_btn)

        layout.addLayout(button_layout)

    def _on_cancel(self):
        """Handle cancel button click."""
        self._is_cancelled = True
        self._cancel_btn.setEnabled(False)
        self._cancel_btn.setText("Cancelling...")
        self.cancelled.emit()

    def next_step(self, description: str = ""):
        """Move to next step."""
        if self._current_step >= 0 and self._current_step < len(self._step_labels):
            # Mark previous step as completed
            self._step_labels[self._current_step]["status"].setText("✅")

        self._current_step += 1

        if self._current_step < len(self._step_labels):
            # Mark current step as in progress
            self._step_labels[self._current_step]["status"].setText("🔄")
            if description:
                self._step_labels[self._current_step]["text"].setText(description)

        self._progress_bar.setValue(self._current_step + 1)
        self.step_completed.emit(self._current_step)

    def complete_step(self, success: bool = True):
        """Complete current step."""
        if self._current_step >= 0 and self._current_step < len(self._step_labels):
            if success:
                self._step_labels[self._current_step]["status"].setText("✅")
            else:
                self._step_labels[self._current_step]["status"].setText("❌")

    def is_cancelled(self) -> bool:
        """Check if cancelled."""
        return self._is_cancelled

    def closeEvent(self, event):
        """Handle close event."""
        if not self._is_cancelled:
            self._is_cancelled = True
            self.cancelled.emit()
        super().closeEvent(event)
