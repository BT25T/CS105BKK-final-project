import json

from quiz_game.models import Player, Score
from quiz_game.storage import JsonStore


def test_broken_question_file_returns_empty_list(tmp_path):
    store = JsonStore(tmp_path)
    store.questions_path.write_text("not json", encoding="utf-8")
    assert store.load_questions() == []


def test_score_survives_save_and_load(tmp_path):
    store = JsonStore(tmp_path)
    score = Score.create(Player("Byte", 4), 5, "All", "all")
    assert store.save_score(score)
    assert store.load_scores() == [score]


def test_high_scores_skips_invalid_fields_and_unreadable_files(tmp_path):
    store = JsonStore(tmp_path)
    assert store.high_scores() == []
    store.scores_path.write_bytes(b"\xff")
    assert store.high_scores() == []
    store.scores_path.write_text(
        '[{"player":"A","points":"5","total":10,"category":"All",'
        '"level":"all","played_at":"x"}]',
        encoding="utf-8",
    )
    assert store.high_scores() == []


def test_high_scores_rank_by_percentage(tmp_path):
    store = JsonStore(tmp_path)
    store.scores_path.write_text(
        json.dumps([
            {
                "player": "A", "points": 5, "total": 10,
                "category": "All", "level": "all", "played_at": "x",
            },
            {
                "player": "B", "points": 4, "total": 5,
                "category": "All", "level": "all", "played_at": "x",
            },
        ]),
        encoding="utf-8",
    )
    assert store.high_scores()[0].player == "B"
