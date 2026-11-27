import random

from quiz_game.game import QuizGame
from quiz_game.models import Player, Question


def sample_questions():
    return [
        Question("Easy?", ("Yes", "No"), 0, "Test", "easy"),
        Question("Hard?", ("Yes", "No"), 0, "Test", "hard"),
        Question("Other?", ("Yes", "No"), 1, "Other", "easy"),
    ]


def test_categories_are_unique_and_sorted():
    assert QuizGame(sample_questions()).categories == ["Other", "Test"]


def test_select_questions_filters_category_and_level():
    game = QuizGame(sample_questions(), random.Random(1))
    selected = game.select_questions("Test", "hard", 5)
    assert [question.text for question in selected] == ["Hard?"]


def test_select_questions_respects_limit():
    selected = QuizGame(sample_questions()).select_questions(limit=2)
    assert len(selected) == 2


def test_correct_answer_scores_by_level():
    player = Player("Byte")
    assert QuizGame.answer(player, sample_questions()[1], 1)
    assert player.points == 3


def test_wrong_answer_does_not_score():
    player = Player("Byte")
    assert not QuizGame.answer(player, sample_questions()[0], 2)
    assert player.points == 0


def test_question_rounds_is_numbered_generator():
    rounds = QuizGame(sample_questions()).question_rounds(sample_questions()[:2])
    assert iter(rounds) is rounds
    assert [number for number, _ in rounds] == [1, 2]
