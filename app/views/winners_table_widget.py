from __future__ import annotations

from PySide6.QtWidgets import (
    QAbstractItemView,
    QHeaderView,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.models.winner_record import WinnerRecord


class WinnersTableWidget(QWidget):
    """Display the list of finalized winners."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)

        # Title
        title = QLabel("Winners")
        title.setStyleSheet("font-size: 14px; font-weight: bold;")
        self.layout.addWidget(title)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Email", "First Name", "Last Name", "Chosen Prize"])
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.layout.addWidget(self.table)

    def update_winners(self, winners: list[WinnerRecord]) -> None:
        """Update the winners table."""
        self.table.setRowCount(len(winners))
        for row, winner in enumerate(winners):
            self.table.setItem(row, 0, QTableWidgetItem(winner.email))
            self.table.setItem(row, 1, QTableWidgetItem(winner.first_name))
            self.table.setItem(row, 2, QTableWidgetItem(winner.last_name))
            self.table.setItem(row, 3, QTableWidgetItem(winner.chosen_prize))
