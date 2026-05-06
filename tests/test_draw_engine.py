import random

from app.models.participant import Participant
from app.models.prize import Prize
from app.models.session_state import PendingWinner, SessionState
from app.models.winner_record import WinnerRecord
from app.services.draw_engine import DrawEngine


def build_session() -> SessionState:
    participants = [
        Participant(email="a@example.com", first_name="A", last_name="Alpha"),
        Participant(email="b@example.com", first_name="B", last_name="Beta"),
        Participant(email="c@example.com", first_name="C", last_name="Gamma"),
        Participant(email="d@example.com", first_name="D", last_name="Delta"),
    ]
    prizes = [Prize(prize_id="p1", title="Prize 1", description="One", image_path="one.png")]
    return SessionState(
        session_date="2026-05-06",
        participants=participants,
        prizes=prizes,
        previous_winner_emails={"a@example.com", "b@example.com"},
    )


def test_previous_winners_excluded_before_three_confirmed_winners() -> None:
    session = build_session()
    session.winners = [
        WinnerRecord("c@example.com", "C", "Gamma", "Prize X", "2026-05-06T10:00:00+00:00"),
        WinnerRecord("d@example.com", "D", "Delta", "Prize Y", "2026-05-06T10:05:00+00:00"),
    ]
    engine = DrawEngine(random.Random(1))

    eligible = {participant.email for participant in engine.eligible_participants(session)}

    assert eligible == set()


def test_previous_winners_return_after_three_confirmed_winners() -> None:
    session = build_session()
    session.winners = [
        WinnerRecord("c@example.com", "C", "Gamma", "Prize X", "2026-05-06T10:00:00+00:00"),
        WinnerRecord("d@example.com", "D", "Delta", "Prize Y", "2026-05-06T10:05:00+00:00"),
    ]
    session.pending_winner = PendingWinner("x@example.com", "X", "Xi", "2026-05-06T10:06:00+00:00")
    engine = DrawEngine(random.Random(1))

    eligible = {participant.email for participant in engine.eligible_participants(session)}

    assert eligible == {"a@example.com", "b@example.com"}


def test_choose_candidate_fails_when_pool_is_empty() -> None:
    session = build_session()
    session.winners = [
        WinnerRecord("c@example.com", "C", "Gamma", "Prize X", "2026-05-06T10:00:00+00:00"),
        WinnerRecord("d@example.com", "D", "Delta", "Prize Y", "2026-05-06T10:05:00+00:00"),
    ]
    engine = DrawEngine(random.Random(1))

    try:
        engine.choose_candidate(session)
    except ValueError as exc:
        assert "No eligible participants" in str(exc)
    else:
        raise AssertionError("Expected choose_candidate to fail for an empty pool.")