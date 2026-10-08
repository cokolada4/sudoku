"""
Game manager coordinating puzzle state, timer, selection, inputs, autosave, and game events.
"""

from typing import Optional, Tuple, Callable
from src.models import Puzzle, Cell
from src.timer import Timer
from src.validator import SudokuValidator, ValidationResult
from src.save_manager import SaveManager
from src.config_manager import ConfigManager, log_error


class GameManager:
    """
    Central controller managing gameplay state and user actions.
    """
    def __init__(self, puzzle: Puzzle, config_mgr: ConfigManager, save_mgr: SaveManager):
        self.puzzle: Puzzle = puzzle
        self.config_mgr: ConfigManager = config_mgr
        self.save_mgr: SaveManager = save_mgr

        self.selected_cell: Optional[Tuple[int, int]] = (0, 0)  # Default select R1C1
        self.note_mode: bool = False
        self.is_paused: bool = False
        self.is_won: bool = False

        self.last_autosave_time: float = 0.0

        # Load saved time or 0
        saved_time = self.save_mgr.load_game(self.puzzle)
        initial_seconds = saved_time if saved_time is not None else 0

        self.timer: Timer = Timer(initial_elapsed=initial_seconds)
        if self.config_mgr.get_setting("enable_timer", True):
            self.timer.start()

        # Callbacks
        self.on_state_changed: Optional[Callable[[], None]] = None
        self.on_game_won: Optional[Callable[[str], None]] = None

    def select_cell(self, row: int, col: int):
        if self.is_paused:
            return
        if 0 <= row < self.puzzle.size and 0 <= col < self.puzzle.size:
            self.selected_cell = (row, col)
            self._notify_change()

    def set_number(self, num: int):
        if self.is_paused or self.is_won or not self.selected_cell:
            return

        r, c = self.selected_cell
        cell = self.puzzle.get_cell(r, c)

        if cell.is_given:
            return

        if self.note_mode:
            cell.toggle_note(num)
        else:
            if cell.player_value == num:
                cell.player_value = None  # Toggle off if same number
            else:
                cell.player_value = num

        self.check_game_completion()
        self._notify_change()

    def clear_cell(self):
        if self.is_paused or self.is_won or not self.selected_cell:
            return

        r, c = self.selected_cell
        cell = self.puzzle.get_cell(r, c)
        if not cell.is_given:
            cell.clear()
            self._notify_change()

    def toggle_notes_mode(self):
        if self.is_paused:
            return
        self.note_mode = not self.note_mode
        self._notify_change()

    def pause_game(self):
        if not self.is_paused:
            self.is_paused = True
            self.timer.pause()
            self._notify_change()

    def resume_game(self):
        if self.is_paused:
            self.is_paused = False
            if self.config_mgr.get_setting("enable_timer", True) and not self.is_won:
                self.timer.start()
            self._notify_change()

    def toggle_pause(self):
        if self.is_paused:
            self.resume_game()
        else:
            self.pause_game()

    def reset_game(self):
        for r in range(self.puzzle.size):
            for c in range(self.puzzle.size):
                self.puzzle.get_cell(r, c).clear()
        self.is_won = False
        self.timer.reset()
        if not self.is_paused and self.config_mgr.get_setting("enable_timer", True):
            self.timer.start()
        self.save_game()
        self._notify_change()

    def save_game(self):
        elapsed = self.timer.get_elapsed_seconds()
        self.save_mgr.save_game(self.puzzle, elapsed)

    def check_autosave(self):
        if self.config_mgr.get_setting("enable_autosave", True):
            interval = self.config_mgr.get_setting("autosave_interval", 30)
            elapsed = self.timer.get_elapsed_seconds()
            if elapsed - self.last_autosave_time >= interval:
                self.save_game()
                self.last_autosave_time = elapsed

    def validate_current_state(self) -> ValidationResult:
        return SudokuValidator.validate_puzzle(self.puzzle)

    def check_game_completion(self):
        if self.is_won:
            return

        if SudokuValidator.is_puzzle_complete_and_valid(self.puzzle):
            self.is_won = True
            self.timer.pause()
            self.save_game()
            formatted_time = self.timer.get_formatted_time()
            if self.on_game_won:
                self.on_game_won(formatted_time)

    def _notify_change(self):
        if self.on_state_changed:
            self.on_state_changed()
