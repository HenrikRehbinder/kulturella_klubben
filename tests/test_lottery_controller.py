import random

from app.controllers.lottery_controller import LotteryController
from app.models.participant import Participant
from app.models.prize import Prize
from app.models.session_state import SessionState
from app.services.draw_engine import DrawEngine
from app.services.session_store import SessionStore


class StubExcelExporter:
    def export_winners(self, session, output_path):
        return None

    def export_event_log(self, event_log_path, output_path):
        return None


def test_not_present_does_not_create_a_winner(tmp_path) -> None:
    session = SessionState(
        session_date="2026-05-06",
        participants=[
            Participant(email="a@example.com", first_name="A", last_name="Alpha"),
            Participant(email="b@example.com", first_name="B", last_name="Beta"),
        ],
        prizes=[Prize(prize_id="p1", title="Prize 1", description="One", image_path="one.png")],
    )
    controller = LotteryController(
        session=session,
        draw_engine=DrawEngine(random.Random(0)),
        session_store=SessionStore(tmp_path / "2026-05-06"),
        excel_exporter=StubExcelExporter(),
    )

    controller.draw()
    controller.mark_not_present()

    assert session.winners == []
    assert session.pending_winner is None
    assert session.status == "ready_to_draw"
    assert [attempt.result for attempt in session.draw_attempts] == ["drawn", "not_present"]


def test_confirm_and_assign_prize_finalizes_winner_and_consumes_prize(tmp_path) -> None:
    session = SessionState(
        session_date="2026-05-06",
        participants=[Participant(email="a@example.com", first_name="A", last_name="Alpha")],
        prizes=[Prize(prize_id="p1", title="Prize 1", description="One", image_path="one.png")],
    )
    controller = LotteryController(
        session=session,
        draw_engine=DrawEngine(random.Random(0)),
        session_store=SessionStore(tmp_path / "2026-05-06"),
        excel_exporter=StubExcelExporter(),
    )

    controller.draw()
    controller.confirm_candidate()
    controller.assign_prize("p1")

    assert len(session.winners) == 1
    assert session.winners[0].email == "a@example.com"
    assert session.winners[0].chosen_prize == "Prize 1"
    assert session.prizes[0].is_available is False
    assert session.status == "completed"