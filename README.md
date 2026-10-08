# Killer Sudoku Desktop Application

A full-featured, highly configurable 9×9 **Killer Sudoku** desktop application written in Python using Tkinter.

## Features

- **GUI-First Desktop Experience**:
  - Double-click `main.py` or `main.pyw` on Windows to launch directly into the game window.
  - Complete gameplay using mouse clicks and/or keyboard shortcuts. No terminal or console commands required.
- **Killer Sudoku Rules & Cage Rendering**:
  - Renders 9×9 grid, standard 3×3 Sudoku box outlines, dashed colored cage borders, and top-left cage sum labels.
  - Built-in validation checking row, column, 3×3 box duplicates, exact cage sum completion, and partial cage sum feasibility.
- **Candidate Notes & Controls**:
  - Toggle candidate Note mode (`N` key) to enter small 3×3 candidate numbers.
  - On-screen keypad (digits 1–9 and Clear button).
  - Cell selection and row, column, 3×3 box, and matching digit highlighting.
- **Timer, Pause, & Safe Autosave**:
  - Stopwatch timer with pause/resume support (`P` key).
  - Pause overlay shielding the grid.
  - Atomic background autosave every 30 seconds (temporary file -> validation -> backup -> atomic replace).
- **Interactive Puzzle & Cage Editor**:
  - Integrated editor mode (`Editor -> Open Puzzle Editor...`) allows selecting cells interactively, setting custom cage sums, defining given starting numbers, validating 81-cell grid coverage, and saving puzzle JSON files.
- **JSON Configuration & Customization**:
  - Appearance themes, colors, and game settings configured via `config.json`.
  - Puzzles loaded from `puzzles/` JSON files without modifying source code.

---

## Directory Structure

```text
KillerSudoku/
│
├── main.py              # Standard Python entry point
├── main.pyw             # Console-free Windows entry point
├── config.json          # Main application & theme configuration
├── error.log            # Application error log file
├── README.md            # Documentation
│
├── src/
│   ├── models.py        # Data models (Cell, Cage, Puzzle, coordinates)
│   ├── validator.py     # Sudoku & Killer cage validation engine
│   ├── timer.py         # Precision stopwatch timer
│   ├── config_manager.py# Configuration loader and error logging
│   ├── puzzle_manager.py# Puzzle JSON parser and schema validator
│   ├── save_manager.py  # Atomic save file manager
│   ├── game_manager.py  # Central game state controller
│   ├── board.py         # Tkinter Canvas rendering component
│   ├── gui.py           # Main window UI and menu system
│   └── editor.py        # Interactive Puzzle/Cage Editor GUI
│
├── puzzles/
│   ├── puzzle_001.json  # Initial Killer Sudoku puzzle
│   └── puzzle_002.json  # Secondary test puzzle
│
├── saves/               # Saved game states directory (created automatically)
└── assets/              # Optional assets directory
```

---

## How to Run

### Windows (Console-Free Launch)
Double-click `main.py` or `main.pyw`.

Alternatively, launch using `pythonw.exe`:
```cmd
pythonw main.pyw
```

### Command Line / Linux / macOS
Run with Python 3:
```bash
python3 main.py
```

---

## Keybindings & Shortcuts

| Key / Shortcut | Action |
| --- | --- |
| `1` – `9` | Enter number in selected cell |
| `0`, `Backspace`, `Delete` | Clear selected cell |
| `N` | Toggle Notes mode |
| `P` | Pause / Resume game |
| `S` / `Ctrl+S` | Save current game progress |
| `L` | Load saved game progress |
| `R` | Reset puzzle |
| `Ctrl+O` | Open puzzle JSON file |

---

## Editing & Creating Puzzles

1. Open the application.
2. Go to **Editor** menu → **Open Puzzle Editor...**.
3. Click cells on the grid to select them.
4. Click **Create Cage from Selected**, enter the target sum, and click OK.
5. Enter a **Puzzle Name** and click **Save Puzzle**.
