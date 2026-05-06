from __future__ import annotations

from pathlib import Path

from app.models.winner_record import WinnerRecord


class PreviousWinnersRepository:
    def load_previous_winners(self, sessions_root: Path) -> set[str]:
        """Load emails of winners from the most recent previous session."""
        if not sessions_root.exists():
            return set()

        # Find all session folders sorted by name (dates in YYYY-MM-DD format)
        session_folders = sorted(
            [d for d in sessions_root.iterdir() if d.is_dir()],
            key=lambda d: d.name,
            reverse=True,
        )

        if not session_folders:
            return set()

        # Skip today if it exists and look at the next folder
        today_candidates = [d for d in session_folders if d.name == self._today()]
        remaining = session_folders
        if today_candidates:
            # Remove today
            remaining = [d for d in session_folders if d.name != self._today()]

        if not remaining:
            return set()

        latest_previous = remaining[0]
        state_file = latest_previous / "session_state.json"
        if not state_file.exists():
            return set()

        import json

        try:
            state_data = json.loads(state_file.read_text(encoding="utf-8"))
            winners = state_data.get("winners", [])
            return {winner["email"] for winner in winners}
        except Exception:
            return set()

    def _today(self) -> str:
        from datetime import date

        return date.today().isoformat()
