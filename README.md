# Quiz Game

A one-player command-line quiz with categories, difficulty levels, weighted points,
saved high scores, and optional questions from the Open Trivia Database.

## Run

Python 3.12 or newer is required. No third-party package is needed to play.

### Windows

```powershell
py -3.12 main.py
```

### macOS / Linux

```bash
python3 main.py
```

You can also run `python -m quiz_game` (use `python3` on systems where required).

The game creates `data/scores.json` after the first completed round. **Refresh
questions** uses a no-key public API and saves its last reply in
`data/api_cache.json`, so cached questions remain available offline.

## Test and check

```bash
python -m pip install pytest ruff
python -m pytest
python -m ruff check .
```

## Design

- `Question`, `Player`, and `Score` model the game data.
- `QuizGame` owns selection and scoring rules.
- `JsonStore` owns JSON loading and saving.
- `QuizCli` handles terminal input and output.
- `TriviaApi` imports and caches public questions.

Easy, medium, and hard answers are worth 1, 2, and 3 points. Invalid input and
missing or broken files are handled without a traceback.
