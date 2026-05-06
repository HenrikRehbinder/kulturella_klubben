from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from app.controllers.lottery_controller import LotteryController
from app.models.session_state import SessionState
from app.services.config_loader import AppConfig, load_config
from app.services.draw_engine import DrawEngine
from app.services.excel_exporter import ExcelExporter
from app.services.participant_repository import ParticipantRepository
from app.services.previous_winners_repository import PreviousWinnersRepository
from app.services.prize_repository import PrizeRepository
from app.services.session_store import SessionStore


class AppController:
    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self.participant_repo = ParticipantRepository()
        self.prize_repo = PrizeRepository()
        self.previous_winners_repo = PreviousWinnersRepository()
        self.today = date.today().isoformat()
        self.session_dir = config.sessions_root / self.today

    def has_unfinished_session(self) -> bool:
        """Check if there's an unfinished session for today."""
        session_store = SessionStore(self.session_dir)
        if not session_store.state_path.exists():
            return False
        try:
            session = session_store.load_state()
            return session.session_date == self.today and session.status != "completed"
        except Exception:
            return False

    def initialize_session(self, force_new: bool = False) -> tuple[SessionState, LotteryController]:
        """Load or create today's lottery session and return ready controllers.
        
        Args:
            force_new: If True, create a new session even if one exists.
        
        Raises:
            ValueError: If prizes.xlsx is not found in the session folder.
        """
        # Load prizes from session folder (must be prepared manually before lottery)
        prizes_path = self.session_dir / "prizes.xlsx"
        if not prizes_path.exists():
            raise ValueError(
                f"Prizes file not found at {prizes_path}\n"
                "Please prepare prizes.xlsx in the session folder before starting the lottery."
            )

        participants = self.participant_repo.load_from_excel(self.config.participants_excel)
        prizes = self.prize_repo.load_from_excel(prizes_path)
        previous_winners = self.previous_winners_repo.load_previous_winners(self.config.sessions_root)

        session_store = SessionStore(self.session_dir)

        # Try to resume existing session unless force_new is True
        if not force_new and session_store.state_path.exists() and self.config.resume_same_day:
            session = session_store.load_state()
            # Validate loaded state integrity
            if session.session_date == self.today and session.status != "completed":
                draw_engine = DrawEngine(
                    exclusion_threshold=self.config.previous_winners_excluded_until_confirmed_winners
                )
                excel_exporter = ExcelExporter()
                lottery_controller = LotteryController(
                    session=session,
                    draw_engine=draw_engine,
                    session_store=session_store,
                    excel_exporter=excel_exporter,
                )
                return session, lottery_controller

        # Create a new session
        session = SessionState(
            session_date=self.today,
            participants=participants,
            prizes=prizes,
            previous_winner_emails=previous_winners,
        )

        # Snapshot input files if configured
        if self.config.snapshot_inputs:
            self._snapshot_inputs(participants, prizes)

        # Initialize session store
        session_store.save_state(session)
        session_store.append_event(
            {"timestamp": self._now_iso(), "action_type": "session_created", "details": "New lottery session created."}
        )

        draw_engine = DrawEngine(
            exclusion_threshold=self.config.previous_winners_excluded_until_confirmed_winners
        )
        excel_exporter = ExcelExporter()
        lottery_controller = LotteryController(
            session=session,
            draw_engine=draw_engine,
            session_store=session_store,
            excel_exporter=excel_exporter,
        )

        return session, lottery_controller

    def _snapshot_inputs(self, participants, prizes) -> None:
        """Save snapshots of loaded input data."""
        try:
            from openpyxl import Workbook
        except ImportError:
            return

        # Participant snapshot
        participants_file = self.session_dir / "participants_snapshot.xlsx"
        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "participants"
        sheet.append(["email", "first_name", "last_name"])
        for p in participants:
            sheet.append([p.email, p.first_name, p.last_name])
        participants_file.parent.mkdir(parents=True, exist_ok=True)
        workbook.save(participants_file)

        # Prize snapshot
        prizes_file = self.session_dir / "prizes_snapshot.xlsx"
        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "prizes"
        sheet.append(["prize_id", "title", "description", "image_path"])
        for p in prizes:
            sheet.append([p.prize_id, p.title, p.description, p.image_path])
        workbook.save(prizes_file)

    def _now_iso(self) -> str:
        from datetime import UTC, datetime

        return datetime.now(UTC).replace(microsecond=0).isoformat()
