import unittest
import time
import os
import shutil
from src.timer import Timer
from src.models import Puzzle, Cage
from src.config_manager import ConfigManager
from src.save_manager import SaveManager
from src.game_manager import GameManager


class TestGameManagerAndTimer(unittest.TestCase):
    def setUp(self):
        self.test_dir = "tests_tmp_game"
        os.makedirs(self.test_dir, exist_ok=True)
        self.cfg_mgr = ConfigManager("non_existent.json")
        self.save_mgr = SaveManager(saves_dir=self.test_dir)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_timer(self):
        timer = Timer(initial_elapsed=10)
        self.assertEqual(timer.get_elapsed_seconds(), 10)
        self.assertEqual(timer.get_formatted_time(), "00:10")

        timer.start()
        time.sleep(0.1)
        timer.pause()
        self.assertGreaterEqual(timer.get_elapsed_seconds(), 10)

    def test_game_manager_actions(self):
        cage = Cage(target_sum=10, cells=[(0, 0), (0, 1)])
        puzzle = Puzzle("TestGamePuzzle", size=9, box_size=3, cages=[cage])
        gm = GameManager(puzzle, self.cfg_mgr, self.save_mgr)

        gm.select_cell(0, 0)
        self.assertEqual(gm.selected_cell, (0, 0))

        # Enter number
        gm.set_number(4)
        self.assertEqual(puzzle.get_cell(0, 0).player_value, 4)

        # Toggle note mode and add note to cell (0, 1)
        gm.select_cell(0, 1)
        gm.toggle_notes_mode()
        self.assertTrue(gm.note_mode)
        gm.set_number(6)
        self.assertIn(6, puzzle.get_cell(0, 1).notes)
        self.assertIsNone(puzzle.get_cell(0, 1).player_value)

        # Pause game
        gm.pause_game()
        self.assertTrue(gm.is_paused)
        gm.set_number(2)  # Should be ignored while paused
        self.assertNotIn(2, puzzle.get_cell(0, 1).notes)


if __name__ == "__main__":
    unittest.main()
