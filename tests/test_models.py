import pytest

from quiz_game.models import Player, Question, Score


def test_question_answer_and_correct_choice():
    question = Question("Two plus two?", ("3", "4"), 1)
    assert question.answer == "4"
    assert question.is_correct(2)


def test_question_rejects_invalid_answer_index():
    with pytest.raises(ValueError):
        Question("Broken?", ("A", "B"), 2)


def test_player_strips_name_and_adds_points():
    player = Player("  Byte  ")
    player.add_points(3)
    assert player.name == "Byte"
    assert player.points == 3


def test_player_rejects_blank_name():
    with pytest.raises(ValueError):
        Player("   ")


def test_score_percentage_handles_zero_total():
    score = Score("Byte", 0, 0, "All", "all", "2026-01-01")
    assert score.percentage == 0
