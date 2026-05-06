from __future__ import annotations

from dataclasses import dataclass, field

from app.models.draw_attempt import DrawAttempt
from app.models.participant import Participant
from app.models.prize import Prize
from app.models.winner_record import WinnerRecord


@dataclass(frozen=True, slots=True)
class PendingWinner:
    email: str
    first_name: str
    last_name: str
    confirmed_at: str

    def to_dict(self) -> dict[str, str]:
        return {
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "confirmed_at": self.confirmed_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> "PendingWinner":
        return cls(
            email=data["email"],
            first_name=data["first_name"],
            last_name=data["last_name"],
            confirmed_at=data["confirmed_at"],
        )


@dataclass(slots=True)
class SessionState:
    session_date: str
    participants: list[Participant]
    prizes: list[Prize]
    previous_winner_emails: set[str] = field(default_factory=set)
    winners: list[WinnerRecord] = field(default_factory=list)
    draw_attempts: list[DrawAttempt] = field(default_factory=list)
    current_candidate: Participant | None = None
    pending_winner: PendingWinner | None = None
    status: str = "ready_to_draw"

    def confirmed_winner_count(self) -> int:
        return len(self.winners) + (1 if self.pending_winner is not None else 0)

    def winner_emails(self) -> set[str]:
        return {winner.email for winner in self.winners}

    def available_prizes(self) -> list[Prize]:
        return [prize for prize in self.prizes if prize.is_available]

    def find_available_prize(self, prize_id: str) -> Prize:
        for prize in self.prizes:
            if prize.prize_id == prize_id and prize.is_available:
                return prize
        raise ValueError(f"Prize '{prize_id}' is not available.")

    def next_attempt_id(self) -> str:
        return f"attempt-{len(self.draw_attempts) + 1}"

    def add_winner_from_pending(self, chosen_prize: str) -> None:
        if self.pending_winner is None:
            raise ValueError("No pending winner to finalize.")
        pending = self.pending_winner
        self.winners.append(
            WinnerRecord(
                email=pending.email,
                first_name=pending.first_name,
                last_name=pending.last_name,
                chosen_prize=chosen_prize,
                confirmed_at=pending.confirmed_at,
            )
        )
        self.pending_winner = None

    def to_dict(self) -> dict[str, object]:
        return {
            "session_date": self.session_date,
            "participants": [participant.to_dict() for participant in self.participants],
            "prizes": [prize.to_dict() for prize in self.prizes],
            "previous_winner_emails": sorted(self.previous_winner_emails),
            "winners": [winner.to_dict() for winner in self.winners],
            "draw_attempts": [attempt.to_dict() for attempt in self.draw_attempts],
            "current_candidate": None if self.current_candidate is None else self.current_candidate.to_dict(),
            "pending_winner": None if self.pending_winner is None else self.pending_winner.to_dict(),
            "status": self.status,
        }

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "SessionState":
        current_candidate_data = data.get("current_candidate")
        pending_winner_data = data.get("pending_winner")
        return cls(
            session_date=str(data["session_date"]),
            participants=[Participant.from_dict(item) for item in data.get("participants", [])],
            prizes=[Prize.from_dict(item) for item in data.get("prizes", [])],
            previous_winner_emails=set(data.get("previous_winner_emails", [])),
            winners=[WinnerRecord.from_dict(item) for item in data.get("winners", [])],
            draw_attempts=[DrawAttempt.from_dict(item) for item in data.get("draw_attempts", [])],
            current_candidate=None if current_candidate_data is None else Participant.from_dict(current_candidate_data),
            pending_winner=None if pending_winner_data is None else PendingWinner.from_dict(pending_winner_data),
            status=str(data.get("status", "ready_to_draw")),
        )