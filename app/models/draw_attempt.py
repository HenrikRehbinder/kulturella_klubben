from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class DrawAttempt:
    attempt_id: str
    timestamp: str
    email: str
    first_name: str
    last_name: str
    result: str
    details: str

    def to_dict(self) -> dict[str, str]:
        return {
            "attempt_id": self.attempt_id,
            "timestamp": self.timestamp,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "result": self.result,
            "details": self.details,
        }

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> "DrawAttempt":
        return cls(
            attempt_id=data["attempt_id"],
            timestamp=data["timestamp"],
            email=data["email"],
            first_name=data["first_name"],
            last_name=data["last_name"],
            result=data["result"],
            details=data["details"],
        )