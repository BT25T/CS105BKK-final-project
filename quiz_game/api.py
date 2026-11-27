"""Open Trivia Database import with offline cache support."""

import html
import json
from pathlib import Path
from urllib.request import urlopen

from quiz_game.models import Question


API_URL = "https://opentdb.com/api.php?amount=10&type=multiple"


class TriviaApi:
    """Fetch public quiz questions and retain the last reply."""

    def __init__(self, cache_path: Path, url: str = API_URL) -> None:
        self.cache_path = cache_path
        self.url = url

    def fetch(self, timeout: float = 5.0) -> list[Question]:
        """Fetch online; fall back to a cached API reply."""
        payload = None
        try:
            with urlopen(self.url, timeout=timeout) as response:  # noqa: S310
                payload = json.load(response)
            questions = self._convert(payload)
            if not questions:
                raise ValueError("API reply contained no valid questions")
            self.cache_path.parent.mkdir(parents=True, exist_ok=True)
            self.cache_path.write_text(
                json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
            )
        except (OSError, ValueError):
            try:
                payload = json.loads(self.cache_path.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                return []
            return self._convert(payload)
        return questions

    @staticmethod
    def _convert(payload: object) -> list[Question]:
        if not isinstance(payload, dict) or not isinstance(payload.get("results"), list):
            return []
        questions = []
        for item in payload.get("results", []):
            try:
                answer = html.unescape(item["correct_answer"])
                choices = [html.unescape(value) for value in item["incorrect_answers"]]
                choices.append(answer)
                questions.append(
                    Question(
                        text=html.unescape(item["question"]),
                        choices=tuple(choices),
                        correct_index=len(choices) - 1,
                        category=html.unescape(item["category"]),
                        level=item["difficulty"],
                    )
                )
            except (KeyError, TypeError, ValueError, AttributeError):
                continue
        return questions
