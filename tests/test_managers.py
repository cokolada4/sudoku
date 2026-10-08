import unittest
import os
import shutil
from src.config_manager import ConfigManager
from src.puzzle_manager import PuzzleManager, PuzzleValidationError
from src.save_manager import SaveManager
from src.models import Puzzle, Cage


class TestManagers(unittest.TestCase):
    def setUp(self):
        self.test_dir = "tests_tmp"
        os.makedirs(self.test_dir, exist_ok=True)
        self.puzzle_dir = os.path.join(self.test_dir, "puzzles")
        self.saves_dir = os.path.join(self.test_dir, "saves")
        os.makedirs(self.puzzle_dir, exist_ok=True)
        os.makedirs(self.saves_dir, exist_ok=True)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_config_manager(self):
        cfg_mgr = ConfigManager("non_existent.json")
        self.assertEqual(cfg_mgr.get_setting("autosave_interval"), 30)
        self.assertEqual(cfg_mgr.get_appearance("window_width"), 900)

    def test_puzzle_manager_validation(self):
        pm = PuzzleManager(puzzle_dir=self.puzzle_dir)
        invalid_json = {"name": "Bad", "cages": [{"sum": 5, "cells": ["R10C1"]}]}
        with self.assertRaises(PuzzleValidationError):
            pm.validate_puzzle_data(invalid_json)

        duplicate_cage = {
            "name": "Dup",
            "size": 9,
            "cages": [
                {"sum": 5, "cells": ["R1C1"]},
                {"sum": 5, "cells": ["R1C1"]}
            ]
        }
        with self.assertRaises(PuzzleValidationError):
            pm.validate_puzzle_data(duplicate_cage)

    def test_save_and_load_manager(self):
        cage = Cage(target_sum=10, cells=[(0, 0), (0, 1)])
        puzzle = Puzzle("TestSavePuzzle", size=9, box_size=3, cages=[cage], givens={"R1C1": 4})
        puzzle.get_cell(0, 1).player_value = 6
        puzzle.get_cell(1, 1).toggle_note(2)
        puzzle.get_cell(1, 1).toggle_note(5)

        sm = SaveManager(saves_dir=self.saves_dir)
        success = sm.save_game(puzzle, elapsed_seconds=123)
        self.assertTrue(success)

        # Clear cell values
        puzzle.get_cell(0, 1).player_value = None
        puzzle.get_cell(1, 1).notes.clear()

        # Reload
        elapsed = sm.load_game(puzzle)
        self.assertEqual(elapsed, 123)
        self.assertEqual(puzzle.get_cell(0, 1).player_value, 6)
        self.assertEqual(puzzle.get_cell(1, 1).notes, {2, 5})


if __name__ == "__main__":
    unittest.main()
