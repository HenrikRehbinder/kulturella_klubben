from __future__ import annotations

from datetime import date
from pathlib import Path

from PySide6.QtWidgets import (
    QDialog,
    QLabel,
    QPushButton,
    QVBoxLayout,
)


class ResumeDialog(QDialog):
    """Dialog to offer resuming an unfinished session."""

    RESUME = 1
    NEW_SESSION = 2

    def __init__(self, session_dir: Path, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Resume Session?")
        self.setGeometry(200, 200, 400, 200)
        self.result_action = self.NEW_SESSION

        layout = QVBoxLayout(self)

        # Message
        message = QLabel(
            f"An unfinished lottery session was found for {date.today().isoformat()}.\n\n"
            "Would you like to resume it or start a new session?"
        )
        layout.addWidget(message)

        # Buttons
        resume_button = QPushButton("Resume")
        resume_button.clicked.connect(self._on_resume)
        layout.addWidget(resume_button)

        new_button = QPushButton("Start New Session")
        new_button.clicked.connect(self._on_new_session)
        layout.addWidget(new_button)

    def _on_resume(self) -> None:
        self.result_action = self.RESUME
        self.accept()

    def _on_new_session(self) -> None:
        self.result_action = self.NEW_SESSION
        self.accept()

    def get_action(self) -> int:
        return self.result_action
