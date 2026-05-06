from __future__ import annotations

from typing import Callable

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QGridLayout,
    QPushButton,
    QScrollArea,
    QWidget,
)

from app.models.prize import Prize


class PrizeGridWidget(QWidget):
    """Grid display of available prizes."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.layout = QGridLayout(self)
        self.layout.setSpacing(10)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.prize_buttons: dict[str, QPushButton] = {}
        self.on_prize_selected: Callable[[Prize], None] | None = None

    def set_prizes(self, prizes: list[Prize], image_width: int = 180, image_height: int = 180) -> None:
        """Populate the grid with prize buttons."""
        # Clear existing buttons
        while self.layout.count():
            item = self.layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.prize_buttons.clear()

        columns = 4
        row = 0
        col = 0

        for prize in prizes:
            button = QPushButton()
            button.setFixedSize(200, 250)
            button.setStyleSheet("text-align: top;")

            # Try to load and display image
            if prize.image_path and prize.is_available:
                try:
                    pixmap = QPixmap(prize.image_path)
                    if not pixmap.isNull():
                        scaled = pixmap.scaledToWidth(image_width, Qt.SmoothTransformation)
                        button.setIcon(scaled)
                        button.setIconSize(scaled.size())
                except Exception:
                    pass

            # Set button text
            text = f"{prize.title}\n{prize.description}"
            button.setText(text)

            # Disable if not available
            if not prize.is_available:
                button.setEnabled(False)
                button.setStyleSheet("color: gray; background-color: #f0f0f0;")

            # Wire click event
            prize_id = prize.prize_id
            button.clicked.connect(lambda checked=False, pid=prize_id: self._on_prize_clicked(pid))

            self.layout.addWidget(button, row, col)
            self.prize_buttons[prize.prize_id] = button

            col += 1
            if col >= columns:
                col = 0
                row += 1

    def _on_prize_clicked(self, prize_id: str) -> None:
        """Handle prize button click."""
        if self.on_prize_selected:
            # Find the prize in the current set
            for button_id, button in self.prize_buttons.items():
                if button_id == prize_id and button.isEnabled():
                    # Create a Prize object from the button
                    prize = Prize(
                        prize_id=prize_id,
                        title=button.text().split("\n")[0],
                        description=button.text().split("\n")[1] if "\n" in button.text() else "",
                        image_path="",
                        is_available=True,
                    )
                    self.on_prize_selected(prize)
                    break

    def disable_all_prizes(self) -> None:
        """Disable all prize buttons."""
        for button in self.prize_buttons.values():
            button.setEnabled(False)

    def enable_available_prizes(self, prizes: list[Prize]) -> None:
        """Enable/disable buttons based on prize availability."""
        available_ids = {p.prize_id for p in prizes if p.is_available}
        for prize_id, button in self.prize_buttons.items():
            button.setEnabled(prize_id in available_ids)
            if prize_id not in available_ids:
                button.setStyleSheet("color: gray; background-color: #f0f0f0;")
