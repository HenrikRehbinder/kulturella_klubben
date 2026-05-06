from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.models.participant import Participant


class CurrentCandidateWidget(QWidget):
    """Display the current candidate and action buttons."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(15)

        # Title
        title = QLabel("Current Draw")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.layout.addWidget(title)

        # Candidate display
        self.candidate_label = QLabel("No candidate drawn yet")
        self.candidate_label.setStyleSheet("font-size: 16px; padding: 20px; background-color: #f0f0f0; border: 2px solid #ccc;")
        self.candidate_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.candidate_label)

        # Action buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        self.draw_button = QPushButton("DRAW!")
        self.draw_button.setMinimumHeight(60)
        self.draw_button.setMinimumWidth(150)
        self.draw_button.setStyleSheet("font-size: 16px; font-weight: bold; background-color: #4CAF50; color: white;")
        button_layout.addWidget(self.draw_button)

        self.confirm_button = QPushButton("Confirm")
        self.confirm_button.setMinimumHeight(60)
        self.confirm_button.setMinimumWidth(150)
        self.confirm_button.setEnabled(False)
        self.confirm_button.setStyleSheet("font-size: 16px; font-weight: bold; background-color: #2196F3; color: white;")
        button_layout.addWidget(self.confirm_button)

        self.not_present_button = QPushButton("Not Present")
        self.not_present_button.setMinimumHeight(60)
        self.not_present_button.setMinimumWidth(150)
        self.not_present_button.setEnabled(False)
        self.not_present_button.setStyleSheet("font-size: 16px; font-weight: bold; background-color: #FF9800; color: white;")
        button_layout.addWidget(self.not_present_button)

        self.layout.addLayout(button_layout)

    def set_candidate(self, candidate: Participant | None) -> None:
        """Update the candidate display."""
        if candidate is None:
            self.candidate_label.setText("No candidate drawn yet")
            self.confirm_button.setEnabled(False)
            self.not_present_button.setEnabled(False)
            self.draw_button.setEnabled(True)
        else:
            self.candidate_label.setText(f"{candidate.first_name} {candidate.last_name}\n({candidate.email})")
            self.confirm_button.setEnabled(True)
            self.not_present_button.setEnabled(True)
            self.draw_button.setEnabled(False)

    def await_prize_selection(self, candidate_name: str) -> None:
        """Show that we're waiting for prize selection."""
        self.candidate_label.setText(f"Waiting for prize selection:\n{candidate_name}")
        self.confirm_button.setEnabled(False)
        self.not_present_button.setEnabled(False)
        self.draw_button.setEnabled(False)

    def set_ready_to_draw(self) -> None:
        """Enable draw button."""
        self.candidate_label.setText("Ready to draw next winner")
        self.confirm_button.setEnabled(False)
        self.not_present_button.setEnabled(False)
        self.draw_button.setEnabled(True)
