#!/usr/bin/env python3
"""
Killer Sudoku Desktop Application Main Entry Point.
Double-click or run with python/pythonw.
"""

import os
import sys
from src.config_manager import log_error
from src.gui import KillerSudokuApp


def main():
    # Ensure working directory is the application root
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    # Ensure required directories exist
    os.makedirs("puzzles", exist_ok=True)
    os.makedirs("saves", exist_ok=True)
    os.makedirs("assets", exist_ok=True)

    try:
        app = KillerSudokuApp("config.json")
        app.mainloop()
    except Exception as e:
        log_error("Uncaught application exception", e)
        # Display GUI error dialog if possible
        try:
            import tkinter.messagebox as mb
            mb.showerror("Application Error", f"An unexpected error occurred:\n{e}\n\nSee error.log for details.")
        except Exception:
            pass
        sys.exit(1)


if __name__ == "__main__":
    main()
