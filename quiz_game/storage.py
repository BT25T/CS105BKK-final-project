"""JSON persistence for questions and high scores."""

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from quiz_game.models import Question, Score


class JsonStore:
    """Load and save quiz data without exposing file errors."""

    def __init__(self, data_dir: Path | str = "data") -> None:
        self.data_dir = Path(data_dir)
        self.questions_path = self.data_dir / "questions.json"
        self.scores_path = self.data_dir / "scores.json"
        self.cache_path = self.data_dir / "api_cache.json"

    @staticmethod
    def _read_json(path: Path, default: Any) -> Any:
        try:
            with path.open(encoding="utf-8") as file:
                return json.load(file)
        except (OSError, ValueError):
            return default

    @staticmethod
    def _write_json(path: Path, data: Any) -> bool:
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("w", encoding="utf-8") as file:
                json.dump(data, file, indent=2, ensure_ascii=False)
            return True
        except OSError:
            return False

    def load_questions(self, path: Path | None = None) -> list[Question]:
        """Load valid questions and skip broken entries."""
        raw_items = self._read_json(path or self.questions_path, [])
        questions = []
        if not isinstance(raw_items, list):
            return questions
        for item in raw_items:
            try:
                category = item.get("category", "General")
                if not isinstance(category, str):
                    continue
                questions.append(
                    Question(
                        text=item["text"],
                        choices=tuple(item["choices"]),
                        correct_index=int(item["correct_index"]),
                        category=category,
                        level=item.get("level", "easy").lower(),
                    )
                )
            except (KeyError, TypeError, ValueError, AttributeError):
                continue
        return questions

    def save_questions(self, questions: list[Question], path: Path | None = None) -> bool:
        """Save questions as JSON."""
        return self._write_json(path or self.questions_path, [asdict(q) for q in questions])

    def load_scores(self) -> list[Score]:
        """Load valid saved scores."""
        items = self._read_json(self.scores_path, [])
        scores = []
        if not isinstance(items, list):
            return scores
        for item in items:
            try:
                score = Score(**item)
            except TypeError:
                continue
            labels = (score.player, score.category, score.level, score.played_at)
            if (
                all(isinstance(value, str) for value in labels)
                and type(score.points) is int
                and type(score.total) is int
                and 0 <= score.points <= score.total
            ):
                scores.append(score)
        return scores

    def save_score(self, score: Score) -> bool:
        """Append one score to the score file."""
        scores = self.load_scores()
        scores.append(score)
        return self._write_json(self.scores_path, [asdict(item) for item in scores])

    def high_scores(self, limit: int = 10) -> list[Score]:
        """Return best scores, using percentage then points."""
        scores = self.load_scores()
        return sorted(
            scores,
            key=lambda score: (score.percentage, score.points),
            reverse=True,
        )[: max(0, limit)]
