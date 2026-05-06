from __future__ import annotations

from dataclasses import asdict
from typing import Any

from app.models.draw_attempt import DrawAttempt
from app.models.session_state import PendingWinner, SessionState
from app.services.draw_engine import DrawEngine
from app.services.excel_exporter import ExcelExporter
from app.services.session_store import SessionStore
from app.utils.time_utils import utc_now_iso


class LotteryController:
    def __init__(
        self,
        session: SessionState,
        draw_engine: DrawEngine,
        session_store: SessionStore,
        excel_exporter: ExcelExporter,
    ) -> None:
        self.session = session
        self.draw_engine = draw_engine
        self.session_store = session_store
        self.excel_exporter = excel_exporter

    def draw(self) -> None:
        if self.session.status != "ready_to_draw":
            raise ValueError("Cannot draw unless the session is ready to draw.")

        candidate = self.draw_engine.choose_candidate(self.session)
        self.session.current_candidate = candidate
        self.session.status = "candidate_drawn"
        self.session.draw_attempts.append(
            DrawAttempt(
                attempt_id=self.session.next_attempt_id(),
                timestamp=utc_now_iso(),
                email=candidate.email,
                first_name=candidate.first_name,
                last_name=candidate.last_name,
                result="drawn",
                details="Candidate drawn.",
            )
        )
        self._persist(
            action_type="draw_performed",
            email=candidate.email,
            first_name=candidate.first_name,
            last_name=candidate.last_name,
            details="Candidate drawn.",
        )

    def mark_not_present(self) -> None:
        candidate = self._require_current_candidate()
        self.session.draw_attempts.append(
            DrawAttempt(
                attempt_id=self.session.next_attempt_id(),
                timestamp=utc_now_iso(),
                email=candidate.email,
                first_name=candidate.first_name,
                last_name=candidate.last_name,
                result="not_present",
                details="Candidate marked not present.",
            )
        )
        self.session.current_candidate = None
        self.session.status = "ready_to_draw"
        self._persist(
            action_type="candidate_marked_not_present",
            email=candidate.email,
            first_name=candidate.first_name,
            last_name=candidate.last_name,
            details="Candidate marked not present.",
        )

    def confirm_candidate(self) -> None:
        candidate = self._require_current_candidate()
        self.session.pending_winner = PendingWinner(
            email=candidate.email,
            first_name=candidate.first_name,
            last_name=candidate.last_name,
            confirmed_at=utc_now_iso(),
        )
        self.session.current_candidate = None
        self.session.status = "awaiting_prize_selection"
        self.session.draw_attempts.append(
            DrawAttempt(
                attempt_id=self.session.next_attempt_id(),
                timestamp=utc_now_iso(),
                email=candidate.email,
                first_name=candidate.first_name,
                last_name=candidate.last_name,
                result="confirmed",
                details="Candidate confirmed present.",
            )
        )
        self._persist(
            action_type="candidate_confirmed",
            email=candidate.email,
            first_name=candidate.first_name,
            last_name=candidate.last_name,
            details="Candidate confirmed present.",
        )

    def assign_prize(self, prize_id: str) -> None:
        if self.session.status != "awaiting_prize_selection" or self.session.pending_winner is None:
            raise ValueError("Cannot assign a prize without a pending winner.")

        prize = self.session.find_available_prize(prize_id)
        prize.is_available = False
        pending = self.session.pending_winner
        self.session.add_winner_from_pending(prize.title)
        self.session.draw_attempts.append(
            DrawAttempt(
                attempt_id=self.session.next_attempt_id(),
                timestamp=utc_now_iso(),
                email=pending.email,
                first_name=pending.first_name,
                last_name=pending.last_name,
                result="finalized",
                details=f"Prize assigned: {prize.title}",
            )
        )
        self.session.status = "completed" if not self.session.available_prizes() else "ready_to_draw"
        self._persist(
            action_type="prize_assigned",
            email=pending.email,
            first_name=pending.first_name,
            last_name=pending.last_name,
            prize_id=prize.prize_id,
            prize_title=prize.title,
            details=f"Prize assigned: {prize.title}",
        )

    def _require_current_candidate(self):
        if self.session.status != "candidate_drawn" or self.session.current_candidate is None:
            raise ValueError("No current candidate is available.")
        return self.session.current_candidate

    def _persist(self, action_type: str, **payload: Any) -> None:
        event = {"timestamp": utc_now_iso(), "action_type": action_type, **payload}
        self.session_store.append_event(event)
        self.session_store.save_state(self.session)
        self.excel_exporter.export_winners(
            self.session,
            self.session_store.session_dir / "winners.xlsx",
        )
        self.excel_exporter.export_event_log(
            self.session_store.event_log_path,
            self.session_store.session_dir / "event_log.xlsx",
        )