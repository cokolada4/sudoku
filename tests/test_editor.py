import unittest
import os
import shutil
import tkinter as tk
from src.puzzle_manager import PuzzleManager
from src.editor import PuzzleEditorWindow


class TestEditor(unittest.TestCase):
    def setUp(self):
        self.test_dir = "tests_tmp_editor"
        os.makedirs(self.test_dir, exist_ok=True)
        self.pm = PuzzleManager(puzzle_dir=self.test_dir)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_editor_window_instantiation(self):
        try:
            root = tk.Tk()
            root.withdraw()
        except tk.TclError:
            self.skipTest("Tkinter display not available")

        editor = PuzzleEditorWindow(root, self.pm)
        editor.withdraw()
        self.assertEqual(editor.puzzle_name, "New Killer Sudoku")
        editor.destroy()
        root.destroy()


if __name__ == "__main__":
    unittest.main()
