import unittest
import os
import shutil
import tkinter as tk
from src.gui import KillerSudokuApp


class TestGUI(unittest.TestCase):
    def setUp(self):
        self.test_dir = "tests_tmp_gui"
        os.makedirs(self.test_dir, exist_ok=True)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_gui_instantiation(self):
        try:
            root = tk.Tk()
            root.withdraw()
            root.destroy()
        except tk.TclError:
            self.skipTest("Tkinter display not available")

        app = KillerSudokuApp(config_path="config.json")
        app.withdraw()
        self.assertIsNotNone(app.game_mgr)
        self.assertIsNotNone(app.board)
        app.destroy()


if __name__ == "__main__":
    unittest.main()
