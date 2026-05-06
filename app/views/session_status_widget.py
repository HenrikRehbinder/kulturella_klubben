from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QVBoxLayout,
    QWidget,
)

from app.models.session_state import SessionState


class SessionStatusWidget(QWidget):
    """Display session status and progress."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(10)

        # Status label
        self.status_label = QLabel("Status: Ready")
        self.status_label.setStyleSheet("font-size: 12px; font-weight: bold;")
        self.layout.addWidget(self.status_label)

        # Progress bar for prizes
        progress_layout = QHBoxLayout()
        self.prizes_label = QLabel("Prizes assigned: 0/0")
        self.prizes_label.setStyleSheet("font-size: 11px;")
        progress_layout.addWidget(self.prizes_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        progress_layout.addWidget(self.progress_bar)

        self.layout.addLayout(progress_layout)

        # Winners count
        self.winners_label = QLabel("Winners: 0")
        self.winners_label.setStyleSheet("font-size: 11px;")
        self.layout.addWidget(self.winners_label)

    def update_status(self, session: SessionState) -> None:
        """Update status display based on session state."""
        self.status_label.setText(f"Status: {session.status}")

        total_prizes = len(session.prizes)
        assigned_prizes = sum(1 for p in session.prizes if not p.is_available)
        self.prizes_label.setText(f"Prizes assigned: {assigned_prizes}/{total_prizes}")

        if total_prizes > 0:
            progress = int((assigned_prizes / total_prizes) * 100)
            self.progress_bar.setValue(progress)
        else:
            self.progress_bar.setValue(0)

        self.winners_label.setText(f"Winners: {len(session.winners)}")
