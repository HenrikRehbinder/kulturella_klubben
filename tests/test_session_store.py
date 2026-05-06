from app.models.participant import Participant
from app.models.prize import Prize
from app.models.session_state import SessionState
from app.services.session_store import SessionStore


def test_save_and_load_round_trip(tmp_path) -> None:
    store = SessionStore(tmp_path / "2026-05-06")
    session = SessionState(
        session_date="2026-05-06",
        participants=[Participant(email="a@example.com", first_name="A", last_name="Alpha")],
        prizes=[Prize(prize_id="p1", title="Prize 1", description="One", image_path="one.png")],
        previous_winner_emails={"previous@example.com"},
    )

    store.save_state(session)
    loaded = store.load_state()

    assert loaded.session_date == session.session_date
    assert loaded.participants[0].email == "a@example.com"
    assert loaded.prizes[0].prize_id == "p1"
    assert loaded.previous_winner_emails == {"previous@example.com"}