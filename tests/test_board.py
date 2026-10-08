import unittest
import os
import shutil
import tkinter as tk
from src.models import Puzzle, Cage
from src.config_manager import ConfigManager
from src.save_manager import SaveManager
from src.game_manager import GameManager
from src.board import SudokuBoard


class TestSudokuBoard(unittest.TestCase):
    def setUp(self):
        self.test_dir = "tests_tmp_board"
        os.makedirs(self.test_dir, exist_ok=True)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_board_instantiation_and_redraw(self):
        try:
            root = tk.Tk()
            root.withdraw()
        except tk.TclError:
            self.skipTest("Tkinter display not available")

        cage = Cage(10, [(0, 0), (0, 1)])
        puzzle = Puzzle("TestBoardPuzzle", size=9, box_size=3, cages=[cage])
        cfg = ConfigManager("non_existent.json")
        sm = SaveManager(saves_dir=self.test_dir)
        gm = GameManager(puzzle, cfg, sm)

        board = SudokuBoard(root, gm, width=600, height=600)
        board.pack()
        board.update_idletasks()
        board.redraw()

        items = board.find_all()
        self.assertGreater(len(items), 0)
        root.destroy()


if __name__ == "__main__":
    unittest.main()
