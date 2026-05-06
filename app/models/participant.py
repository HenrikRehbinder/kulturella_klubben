from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Participant:
    email: str
    first_name: str
    last_name: str

    def to_dict(self) -> dict[str, str]:
        return {
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
        }

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> "Participant":
        return cls(
            email=data["email"],
            first_name=data["first_name"],
            last_name=data["last_name"],
        )