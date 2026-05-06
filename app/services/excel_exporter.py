from __future__ import annotations

import json
from pathlib import Path

from app.models.session_state import SessionState


class ExcelExporter:
    def export_winners(self, session: SessionState, output_path: Path) -> None:
        workbook = self._new_workbook()
        sheet = workbook.active
        sheet.title = "winners"
        sheet.append(["email", "first_name", "last_name", "chosen_prize"])
        for winner in session.winners:
            sheet.append([winner.email, winner.first_name, winner.last_name, winner.chosen_prize])
        output_path.parent.mkdir(parents=True, exist_ok=True)
        workbook.save(output_path)

    def export_event_log(self, event_log_path: Path, output_path: Path) -> None:
        workbook = self._new_workbook()
        sheet = workbook.active
        sheet.title = "event_log"
        headers = [
            "timestamp",
            "action_type",
            "email",
            "first_name",
            "last_name",
            "prize_id",
            "prize_title",
            "details",
        ]
        sheet.append(headers)
        if event_log_path.exists():
            for line in event_log_path.read_text(encoding="utf-8").splitlines():
                event = json.loads(line)
                sheet.append([event.get(header, "") for header in headers])
        output_path.parent.mkdir(parents=True, exist_ok=True)
        workbook.save(output_path)

    def _new_workbook(self):
        try:
            from openpyxl import Workbook
        except ModuleNotFoundError as exc:
            raise RuntimeError("openpyxl is required to export Excel files.") from exc
        return Workbook()