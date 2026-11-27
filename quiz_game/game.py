"""Quiz selection and scoring rules."""

import random
from collections.abc import Iterator

from quiz_game.models import Player, Question, Score


LEVEL_POINTS = {"easy": 1, "medium": 2, "hard": 3}


class QuizGame:
    """Run quiz rules independently from terminal input and output."""

    def __init__(self, questions: list[Question], rng: random.Random | None = None) -> None:
        self.questions = questions
        self.rng = rng or random.Random()

    @property
    def categories(self) -> list[str]:
        """Return sorted unique categories."""
        return sorted({question.category for question in self.questions})

    def select_questions(
        self, category: str = "All", level: str = "all", limit: int = 5
    ) -> list[Question]:
        """Filter, shuffle and limit questions."""
        matches = [
            question
            for question in self.questions
            if (category.lower() == "all" or question.category.lower() == category.lower())
            and (level.lower() == "all" or question.level.lower() == level.lower())
        ]
        self.rng.shuffle(matches)
        return matches[: max(0, limit)]

    def question_rounds(self, questions: list[Question]) -> Iterator[tuple[int, Question]]:
        """Generate numbered quiz rounds."""
        for number, question in enumerate(questions, start=1):
            yield number, question

    @staticmethod
    def answer(player: Player, question: Question, choice_number: int) -> bool:
        """Score one answer and return whether it was correct."""
        correct = question.is_correct(choice_number)
        if correct:
            player.add_points(LEVEL_POINTS.get(question.level, 1))
        return correct

    @staticmethod
    def result(player: Player, questions: list[Question], category: str, level: str) -> Score:
        """Build a result whose total reflects level points."""
        total = sum(LEVEL_POINTS.get(question.level, 1) for question in questions)
        return Score.create(player, total, category, level)
