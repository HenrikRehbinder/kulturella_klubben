from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class WinnerRecord:
    email: str
    first_name: str
    last_name: str
    chosen_prize: str
    confirmed_at: str

    def to_dict(self) -> dict[str, str]:
        return {
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "chosen_prize": self.chosen_prize,
            "confirmed_at": self.confirmed_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> "WinnerRecord":
        return cls(
            email=data["email"],
            first_name=data["first_name"],
            last_name=data["last_name"],
            chosen_prize=data["chosen_prize"],
            confirmed_at=data["confirmed_at"],
        )