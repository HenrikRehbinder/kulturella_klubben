from __future__ import annotations

import json
from pathlib import Path

from app.models.session_state import SessionState


class SessionStore:
    def __init__(self, session_dir: Path) -> None:
        self.session_dir = session_dir
        self.state_path = session_dir / "session_state.json"
        self.event_log_path = session_dir / "event_log.jsonl"
        self.session_dir.mkdir(parents=True, exist_ok=True)

    def save_state(self, session: SessionState) -> None:
        self.state_path.write_text(
            json.dumps(session.to_dict(), indent=2, ensure_ascii=True),
            encoding="utf-8",
        )

    def load_state(self) -> SessionState:
        return SessionState.from_dict(json.loads(self.state_path.read_text(encoding="utf-8")))

    def append_event(self, event: dict[str, object]) -> None:
        with self.event_log_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, ensure_ascii=True) + "\n")