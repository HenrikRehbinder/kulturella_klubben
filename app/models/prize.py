from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Prize:
    prize_id: str
    title: str
    description: str
    image_path: str
    is_available: bool = True

    def to_dict(self) -> dict[str, str | bool]:
        return {
            "prize_id": self.prize_id,
            "title": self.title,
            "description": self.description,
            "image_path": self.image_path,
            "is_available": self.is_available,
        }

    @classmethod
    def from_dict(cls, data: dict[str, str | bool]) -> "Prize":
        return cls(
            prize_id=str(data["prize_id"]),
            title=str(data["title"]),
            description=str(data["description"]),
            image_path=str(data["image_path"]),
            is_available=bool(data.get("is_available", True)),
        )