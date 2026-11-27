"""Terminal interface for the quiz game."""

from collections.abc import Callable
from functools import wraps

from quiz_game.api import TriviaApi
from quiz_game.game import QuizGame
from quiz_game.models import Player
from quiz_game.storage import JsonStore


def safe_action(function: Callable) -> Callable:
    """Keep unexpected user-facing errors out of the terminal."""
    @wraps(function)
    def wrapper(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except (EOFError, KeyboardInterrupt):
            print("\nReturning to menu.")
            return None

    return wrapper


def read_choice(prompt: str, minimum: int, maximum: int) -> int:
    """Read an integer within an inclusive range."""
    while True:
        try:
            value = int(input(prompt).strip())
            if minimum <= value <= maximum:
                return value
        except ValueError:
            pass
        print(f"Enter a number from {minimum} to {maximum}.")


class QuizCli:
    """Display menus and connect terminal input to game rules."""

    def __init__(self, store: JsonStore | None = None) -> None:
        self.store = store or JsonStore()

    @safe_action
    def play(self) -> None:
        """Play one complete quiz."""
        game = QuizGame(self.store.load_questions())
        if not game.questions:
            print("No questions found. Choose refresh first.")
            return

        name = input("Player name: ").strip()
        try:
            player = Player(name)
        except ValueError as error:
            print(error)
            return

        categories = ["All", *game.categories]
        print("\nCategories:")
        for number, category in enumerate(categories, start=1):
            print(f"{number}. {category}")
        category = categories[read_choice("Choose: ", 1, len(categories)) - 1]

        levels = ["all", "easy", "medium", "hard"]
        print("\nLevels: 1. All  2. Easy  3. Medium  4. Hard")
        level = levels[read_choice("Choose: ", 1, 4) - 1]
        questions = game.select_questions(category, level, 5)
        if not questions:
            print("No questions match that selection.")
            return

        for number, question in game.question_rounds(questions):
            print(f"\n{number}/{len(questions)} [{question.level}] {question}")
            for choice_number, choice in enumerate(question.choices, start=1):
                print(f"  {choice_number}. {choice}")
            choice = read_choice("Answer: ", 1, len(question.choices))
            if game.answer(player, question, choice):
                print("Correct!")
            else:
                print(f"Wrong. Answer: {question.answer}")

        result = game.result(player, questions, category, level)
        self.store.save_score(result)
        print(f"\n{player.name}: {result.points}/{result.total} ({result.percentage}%)")

    def show_scores(self) -> None:
        """Print the high-score table."""
        scores = self.store.high_scores()
        if not scores:
            print("No scores yet.")
            return
        print("\nHIGH SCORES")
        for rank, score in enumerate(scores, start=1):
            print(
                f"{rank:>2}. {score.player:<16} "
                f"{score.points}/{score.total} ({score.percentage}%)"
            )

    def refresh_questions(self) -> None:
        """Add questions from a public API or its offline cache."""
        api_questions = TriviaApi(self.store.cache_path).fetch()
        if not api_questions:
            print("No online or cached questions available.")
            return
        questions = self.store.load_questions()
        known = {question.text for question in questions}
        new_questions = [q for q in api_questions if q.text not in known]
        self.store.save_questions([*questions, *new_questions])
        print(f"Added {len(new_questions)} new questions.")

    def run(self) -> None:
        """Run until the player exits."""
        while True:
            print("\nQUIZ GAME\n1. Play\n2. High scores\n3. Refresh questions\n4. Exit")
            choice = read_choice("Choose: ", 1, 4)
            if choice == 1:
                self.play()
            elif choice == 2:
                self.show_scores()
            elif choice == 3:
                self.refresh_questions()
            else:
                print("Goodbye!")
                return


def main() -> None:
    """Start the terminal application."""
    try:
        QuizCli().run()
    except (EOFError, KeyboardInterrupt):
        print("\nGoodbye!")
