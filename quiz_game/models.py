"""Data models used by the quiz game."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Question:
    """A multiple-choice question."""

    text: str
    choices: tuple[str, ...]
    correct_index: int
    category: str = "General"
    level: str = "easy"

    def __post_init__(self) -> None:
        if not self.text.strip():
            raise ValueError("Question text cannot be empty")
        if len(self.choices) < 2:
            raise ValueError("A question needs at least two choices")
        if not 0 <= self.correct_index < len(self.choices):
            raise ValueError("Correct answer index is outside the choices")

    @property
    def answer(self) -> str:
        """Return the correct answer text."""
        return self.choices[self.correct_index]

    def is_correct(self, choice_number: int) -> bool:
        """Check a one-based answer number."""
        return choice_number - 1 == self.correct_index

    def __str__(self) -> str:
        return self.text


@dataclass
class Player:
    """A player and their current score."""

    name: str
    points: int = 0

    def __post_init__(self) -> None:
        self.name = self.name.strip()
        if not self.name:
            raise ValueError("Player name cannot be empty")

    def add_points(self, amount: int) -> None:
        """Add non-negative points to the player."""
        if amount < 0:
            raise ValueError("Points cannot be negative")
        self.points += amount


@dataclass(frozen=True)
class Score:
    """A completed game result."""

    player: str
    points: int
    total: int
    category: str
    level: str
    played_at: str

    @classmethod
    def create(
        cls, player: Player, total: int, category: str, level: str
    ) -> "Score":
        """Create a timestamped result from a player."""
        return cls(
            player=player.name,
            points=player.points,
            total=total,
            category=category,
            level=level,
            played_at=datetime.now().isoformat(timespec="seconds"),
        )

    @property
    def percentage(self) -> int:
        """Return the rounded percentage score."""
        return round(self.points / self.total * 100) if self.total else 0
