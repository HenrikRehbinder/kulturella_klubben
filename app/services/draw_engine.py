from __future__ import annotations

import random

from app.models.participant import Participant
from app.models.session_state import SessionState


class DrawEngine:
    def __init__(self, random_source: random.Random | None = None, exclusion_threshold: int = 3) -> None:
        self.random_source = random_source or random.Random()
        self.exclusion_threshold = exclusion_threshold

    def eligible_participants(self, session: SessionState) -> list[Participant]:
        winner_emails = session.winner_emails()
        eligible = [participant for participant in session.participants if participant.email not in winner_emails]

        if session.confirmed_winner_count() < self.exclusion_threshold:
            eligible = [
                participant
                for participant in eligible
                if participant.email not in session.previous_winner_emails
            ]

        if session.current_candidate is not None:
            eligible = [
                participant for participant in eligible if participant.email != session.current_candidate.email
            ]

        if session.pending_winner is not None:
            eligible = [participant for participant in eligible if participant.email != session.pending_winner.email]

        return eligible

    def choose_candidate(self, session: SessionState) -> Participant:
        eligible = self.eligible_participants(session)
        if not eligible:
            raise ValueError("No eligible participants remain for the current draw.")
        return self.random_source.choice(eligible)