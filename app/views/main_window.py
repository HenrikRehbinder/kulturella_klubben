from __future__ import annotations

from typing import Callable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from app.controllers.lottery_controller import LotteryController
from app.models.session_state import SessionState
from app.views.current_candidate_widget import CurrentCandidateWidget
from app.views.prize_grid_widget import PrizeGridWidget
from app.views.session_status_widget import SessionStatusWidget
from app.views.winners_table_widget import WinnersTableWidget


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self, session: SessionState, controller: LotteryController, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.session = session
        self.controller = controller
        self.setWindowTitle("Kulturella Klubben - Lottery")
        self.setGeometry(100, 100, 1400, 900)

        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)

        # Header
        header = QLabel(f"Lottery Session - {session.session_date}")
        header.setStyleSheet("font-size: 20px; font-weight: bold; padding: 10px;")
        main_layout.addWidget(header)

        # Main content: Left side (prizes + candidate) and right side (winners + status)
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left panel: prizes
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.addWidget(QLabel("Available Prizes"))
        self.prize_grid = PrizeGridWidget()
        self.prize_grid.set_prizes(session.prizes)
        self.prize_grid.on_prize_selected = self._on_prize_selected
        left_layout.addWidget(self.prize_grid)

        # Center panel: candidate and actions
        center_panel = QWidget()
        center_layout = QVBoxLayout(center_panel)
        center_layout.setContentsMargins(0, 0, 0, 0)
        self.candidate_widget = CurrentCandidateWidget()
        self.candidate_widget.draw_button.clicked.connect(self._on_draw_clicked)
        self.candidate_widget.confirm_button.clicked.connect(self._on_confirm_clicked)
        self.candidate_widget.not_present_button.clicked.connect(self._on_not_present_clicked)
        center_layout.addWidget(self.candidate_widget)

        # Right panel: winners table and status
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        self.status_widget = SessionStatusWidget()
        right_layout.addWidget(self.status_widget)
        self.winners_table = WinnersTableWidget()
        right_layout.addWidget(self.winners_table)

        # Add panels to splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(center_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([400, 300, 400])

        main_layout.addWidget(splitter)

        # Update initial display
        self._update_display()

    def _on_draw_clicked(self) -> None:
        """Handle DRAW button click."""
        try:
            self.controller.draw()
            self._update_display()
        except Exception as exc:
            self._show_error(f"Draw failed: {exc}")

    def _on_confirm_clicked(self) -> None:
        """Handle Confirm button click."""
        try:
            self.controller.confirm_candidate()
            self.prize_grid.enable_available_prizes(self.session.prizes)
            self._update_display()
        except Exception as exc:
            self._show_error(f"Confirm failed: {exc}")

    def _on_not_present_clicked(self) -> None:
        """Handle Not Present button click."""
        try:
            self.controller.mark_not_present()
            self._update_display()
        except Exception as exc:
            self._show_error(f"Not present failed: {exc}")

    def _on_prize_selected(self, prize) -> None:
        """Handle prize selection."""
        try:
            self.controller.assign_prize(prize.prize_id)
            self.prize_grid.enable_available_prizes(self.session.prizes)
            self._update_display()
        except Exception as exc:
            self._show_error(f"Prize assignment failed: {exc}")

    def _update_display(self) -> None:
        """Update all UI elements based on session state."""
        if self.session.status == "ready_to_draw":
            self.candidate_widget.set_ready_to_draw()
        elif self.session.status == "candidate_drawn":
            self.candidate_widget.set_candidate(self.session.current_candidate)
        elif self.session.status == "awaiting_prize_selection":
            if self.session.pending_winner:
                name = f"{self.session.pending_winner.first_name} {self.session.pending_winner.last_name}"
                self.candidate_widget.await_prize_selection(name)
        elif self.session.status == "completed":
            self.candidate_widget.candidate_label.setText("Lottery Complete! All prizes assigned.")
            self.candidate_widget.draw_button.setEnabled(False)

        self.winners_table.update_winners(self.session.winners)
        self.status_widget.update_status(self.session)
        self.prize_grid.enable_available_prizes(self.session.prizes)

    def _show_error(self, message: str) -> None:
        """Show error message."""
        print(f"ERROR: {message}")
        from PySide6.QtWidgets import QMessageBox

        QMessageBox.critical(self, "Error", message)
