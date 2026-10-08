"""
Main Application GUI window and control panel for Killer Sudoku.
"""

import tkinter as tk
from tkinter import messagebox, filedialog
import os
from typing import Optional

from src.models import Puzzle
from src.config_manager import ConfigManager, log_error
from src.puzzle_manager import PuzzleManager, PuzzleValidationError
from src.save_manager import SaveManager
from src.game_manager import GameManager
from src.board import SudokuBoard


class KillerSudokuApp(tk.Tk):
    """
    Main application window containing menu, board canvas, keypad, control panel, timer, and pause overlay.
    """
    def __init__(self, config_path: str = "config.json"):
        super().__init__()

        self.config_mgr = ConfigManager(config_path)
        self.save_mgr = SaveManager("saves")
        self.puzzle_mgr = PuzzleManager("puzzles")

        title = self.config_mgr.config.get("app_title", "Killer Sudoku")
        self.title(title)

        w = self.config_mgr.get_appearance("window_width", 900)
        h = self.config_mgr.get_appearance("window_height", 900)
        self.geometry(f"{w}x{h}")
        self.minsize(600, 650)

        self.game_mgr: Optional[GameManager] = None
        self.board: Optional[SudokuBoard] = None

        # UI Components
        self.top_frame: Optional[tk.Frame] = None
        self.timer_label: Optional[tk.Label] = None
        self.puzzle_label: Optional[tk.Label] = None
        self.keypad_frame: Optional[tk.Frame] = None
        self.control_frame: Optional[tk.Frame] = None
        self.pause_overlay: Optional[tk.Frame] = None
        self.notes_btn: Optional[tk.Button] = None
        self.pause_btn: Optional[tk.Button] = None

        self.setup_menu()
        self.setup_ui()
        self.bind_shortcuts()

        # Load initial puzzle
        available = self.puzzle_mgr.get_available_puzzles()
        if available:
            self.load_puzzle_by_path(available[0][1])
        else:
            messagebox.showerror("Error", "No valid puzzle files found in 'puzzles/' directory.")

        # Timer tick loop
        self.update_timer_loop()

    def setup_menu(self):
        menubar = tk.Menu(self)

        # File Menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Select Puzzle...", command=self.on_select_puzzle_dialog)
        file_menu.add_command(label="Open Puzzle File... (Ctrl+O)", command=self.on_open_puzzle_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_exit)
        menubar.add_cascade(label="File", menu=file_menu)

        # Game Menu
        game_menu = tk.Menu(menubar, tearoff=0)
        game_menu.add_command(label="Save Game (Ctrl+S)", command=self.on_save_game)
        game_menu.add_command(label="Load Game (L)", command=self.on_load_game)
        game_menu.add_command(label="Reset Puzzle (R)", command=self.on_reset_game)
        game_menu.add_separator()
        game_menu.add_command(label="Pause / Resume (P)", command=self.on_toggle_pause)
        menubar.add_cascade(label="Game", menu=game_menu)

        # Editor Menu
        editor_menu = tk.Menu(menubar, tearoff=0)
        editor_menu.add_command(label="Open Puzzle Editor...", command=self.on_open_editor)
        menubar.add_cascade(label="Editor", menu=editor_menu)

        # Help Menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self.on_about)
        menubar.add_cascade(label="Help", menu=help_menu)

        self.config(menu=menubar)

    def setup_ui(self):
        # 1. Top Header Frame (Puzzle Name & Timer)
        self.top_frame = tk.Frame(self, bg="#2A65A0", height=40)
        self.top_frame.pack(side=tk.TOP, fill=tk.X)

        self.puzzle_label = tk.Label(
            self.top_frame,
            text="Killer Sudoku",
            font=("Arial", 14, "bold"),
            fg="#FFFFFF",
            bg="#2A65A0"
        )
        self.puzzle_label.pack(side=tk.LEFT, padx=15, pady=5)

        self.timer_label = tk.Label(
            self.top_frame,
            text="Time: 00:00",
            font=("Arial", 14, "bold"),
            fg="#FFFFFF",
            bg="#2A65A0"
        )
        self.timer_label.pack(side=tk.RIGHT, padx=15, pady=5)

        # 2. Main Board Area & Pause Overlay Container
        self.board_container = tk.Frame(self, bg="#FFFFFF")
        self.board_container.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # 3. Bottom Controls Area (Keypad & Action Buttons)
        bottom_area = tk.Frame(self, bg="#F0F0F0")
        bottom_area.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

        # Keypad (1-9 and Clear)
        self.keypad_frame = tk.Frame(bottom_area, bg="#F0F0F0")
        self.keypad_frame.pack(side=tk.TOP, pady=5)

        for i in range(1, 10):
            btn = tk.Button(
                self.keypad_frame,
                text=str(i),
                font=("Arial", 12, "bold"),
                width=4,
                height=1,
                command=lambda num=i: self.game_mgr.set_number(num) if self.game_mgr else None
            )
            btn.grid(row=0, column=i-1, padx=2, pady=2)

        clear_btn = tk.Button(
            self.keypad_frame,
            text="Clear",
            font=("Arial", 11, "bold"),
            width=6,
            height=1,
            bg="#FFDDDD",
            command=lambda: self.game_mgr.clear_cell() if self.game_mgr else None
        )
        clear_btn.grid(row=0, column=9, padx=5, pady=2)

        # Action Buttons (Notes, Check, Save, Load, Reset, Pause)
        self.control_frame = tk.Frame(bottom_area, bg="#F0F0F0")
        self.control_frame.pack(side=tk.TOP, pady=5)

        self.notes_btn = tk.Button(
            self.control_frame,
            text="Notes: OFF (N)",
            font=("Arial", 10, "bold"),
            width=14,
            command=self.on_toggle_notes
        )
        self.notes_btn.pack(side=tk.LEFT, padx=5)

        check_btn = tk.Button(
            self.control_frame,
            text="Check",
            font=("Arial", 10, "bold"),
            width=8,
            command=self.on_check_puzzle
        )
        check_btn.pack(side=tk.LEFT, padx=5)

        save_btn = tk.Button(
            self.control_frame,
            text="Save (S)",
            font=("Arial", 10, "bold"),
            width=8,
            command=self.on_save_game
        )
        save_btn.pack(side=tk.LEFT, padx=5)

        load_btn = tk.Button(
            self.control_frame,
            text="Load (L)",
            font=("Arial", 10, "bold"),
            width=8,
            command=self.on_load_game
        )
        load_btn.pack(side=tk.LEFT, padx=5)

        reset_btn = tk.Button(
            self.control_frame,
            text="Reset (R)",
            font=("Arial", 10, "bold"),
            width=8,
            command=self.on_reset_game
        )
        reset_btn.pack(side=tk.LEFT, padx=5)

        self.pause_btn = tk.Button(
            self.control_frame,
            text="Pause (P)",
            font=("Arial", 10, "bold"),
            width=10,
            command=self.on_toggle_pause
        )
        self.pause_btn.pack(side=tk.LEFT, padx=5)

    def load_puzzle_by_path(self, filepath: str):
        try:
            puzzle = self.puzzle_mgr.load_puzzle(filepath)
            self.game_mgr = GameManager(puzzle, self.config_mgr, self.save_mgr)
            self.game_mgr.on_state_changed = self.update_ui_state
            self.game_mgr.on_game_won = self.on_victory

            # Replace board
            if self.board:
                self.board.destroy()
            self.board = SudokuBoard(self.board_container, self.game_mgr, bg="#FFFFFF")
            self.board.pack(fill=tk.BOTH, expand=True)

            self.puzzle_label.config(text=puzzle.name)
            self.update_ui_state()

        except Exception as e:
            log_error(f"Error loading puzzle {filepath}", e)
            messagebox.showerror("Configuration Error", f"Could not load puzzle:\n{e}")

    def update_ui_state(self):
        if not self.game_mgr:
            return

        # Update board
        if self.board:
            self.board.redraw()

        # Update notes button text
        if self.notes_btn:
            state_str = "ON" if self.game_mgr.note_mode else "OFF"
            self.notes_btn.config(text=f"Notes: {state_str} (N)", bg="#DDF0FF" if self.game_mgr.note_mode else "#F0F0F0")

        # Update pause button & overlay
        if self.pause_btn:
            self.pause_btn.config(text="Resume (P)" if self.game_mgr.is_paused else "Pause (P)")

        if self.game_mgr.is_paused:
            self.show_pause_overlay()
        else:
            self.hide_pause_overlay()

    def show_pause_overlay(self):
        if not self.pause_overlay:
            self.pause_overlay = tk.Frame(self.board_container, bg="#333333")
            lbl = tk.Label(
                self.pause_overlay,
                text="GAME PAUSED",
                font=("Arial", 28, "bold"),
                fg="#FFFFFF",
                bg="#333333"
            )
            lbl.pack(expand=True, pady=(150, 20))
            res_btn = tk.Button(
                self.pause_overlay,
                text="Resume",
                font=("Arial", 14, "bold"),
                width=12,
                command=self.on_toggle_pause
            )
            res_btn.pack(pady=20)
        self.pause_overlay.place(relx=0, rely=0, relwidth=1, relheight=1)

    def hide_pause_overlay(self):
        if self.pause_overlay:
            self.pause_overlay.place_forget()

    def update_timer_loop(self):
        if self.game_mgr and self.timer_label:
            formatted = self.game_mgr.timer.get_formatted_time()
            self.timer_label.config(text=f"Time: {formatted}")
            self.game_mgr.check_autosave()
        self.after(500, self.update_timer_loop)

    def bind_shortcuts(self):
        # Digits 1-9
        for i in range(1, 10):
            self.bind(str(i), lambda e, num=i: self.game_mgr.set_number(num) if self.game_mgr else None)
        # Clear digits (0, Backspace, Delete)
        for key in ["0", "<BackSpace>", "<Delete>"]:
            self.bind(key, lambda e: self.game_mgr.clear_cell() if self.game_mgr else None)

        # Letter shortcuts
        self.bind("n", lambda e: self.on_toggle_notes())
        self.bind("N", lambda e: self.on_toggle_notes())
        self.bind("p", lambda e: self.on_toggle_pause())
        self.bind("P", lambda e: self.on_toggle_pause())
        self.bind("r", lambda e: self.on_reset_game())
        self.bind("R", lambda e: self.on_reset_game())
        self.bind("s", lambda e: self.on_save_game())
        self.bind("S", lambda e: self.on_save_game())
        self.bind("l", lambda e: self.on_load_game())
        self.bind("L", lambda e: self.on_load_game())

        # Control key combos
        self.bind("<Control-s>", lambda e: self.on_save_game())
        self.bind("<Control-S>", lambda e: self.on_save_game())
        self.bind("<Control-o>", lambda e: self.on_open_puzzle_file())
        self.bind("<Control-O>", lambda e: self.on_open_puzzle_file())

    def on_toggle_notes(self):
        if self.game_mgr:
            self.game_mgr.toggle_notes_mode()

    def on_toggle_pause(self):
        if self.game_mgr:
            self.game_mgr.toggle_pause()

    def on_save_game(self):
        if self.game_mgr:
            self.game_mgr.save_game()
            messagebox.showinfo("Game Saved", f"Progress for '{self.game_mgr.puzzle.name}' has been saved.")

    def on_load_game(self):
        if self.game_mgr:
            saved_time = self.save_mgr.load_game(self.game_mgr.puzzle)
            if saved_time is not None:
                self.game_mgr.timer.accumulated_seconds = float(saved_time)
                self.update_ui_state()
                messagebox.showinfo("Game Loaded", f"Progress for '{self.game_mgr.puzzle.name}' loaded.")
            else:
                messagebox.showinfo("Load Game", "No saved game found for this puzzle.")

    def on_reset_game(self):
        if not self.game_mgr:
            return
        ans = messagebox.askyesno(
            "Reset Game",
            "Are you sure you want to reset this puzzle?\nAll current progress will be lost."
        )
        if ans:
            self.game_mgr.reset_game()

    def on_check_puzzle(self):
        if not self.game_mgr:
            return
        res = self.game_mgr.validate_current_state()
        if res.is_valid:
            messagebox.showinfo("Validation Check", "All entered numbers and cages are currently valid!")
        else:
            messagebox.showwarning(
                "Validation Check",
                f"Found {len(res.invalid_cells)} invalid cell(s) or cage(s) in violation of Sudoku / Killer rules."
            )

    def on_select_puzzle_dialog(self):
        available = self.puzzle_mgr.get_available_puzzles()
        if not available:
            messagebox.showinfo("Select Puzzle", "No available puzzles.")
            return

        dlg = tk.Toplevel(self)
        dlg.title("Select Puzzle")
        dlg.geometry("350x250")
        dlg.transient(self)
        dlg.grab_set()

        lbl = tk.Label(dlg, text="Select a Killer Sudoku Puzzle:", font=("Arial", 11, "bold"))
        lbl.pack(pady=10)

        listbox = tk.Listbox(dlg, font=("Arial", 10), height=6)
        listbox.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)

        for name, path in available:
            listbox.insert(tk.END, name)

        listbox.selection_set(0)

        def confirm():
            idx = listbox.curselection()
            if idx:
                path = available[idx[0]][1]
                if self.game_mgr:
                    self.game_mgr.save_game()
                self.load_puzzle_by_path(path)
                dlg.destroy()

        btn = tk.Button(dlg, text="Load Selected", font=("Arial", 10, "bold"), command=confirm)
        btn.pack(pady=10)

    def on_open_puzzle_file(self):
        path = filedialog.askopenfilename(
            title="Open Puzzle JSON",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
        )
        if path:
            if self.game_mgr:
                self.game_mgr.save_game()
            self.load_puzzle_by_path(path)

    def on_open_editor(self):
        from src.editor import PuzzleEditorWindow
        if self.game_mgr:
            self.game_mgr.pause_game()
        editor = PuzzleEditorWindow(self, self.puzzle_mgr)
        self.wait_window(editor)
        if self.game_mgr:
            self.game_mgr.resume_game()

    def on_victory(self, formatted_time: str):
        messagebox.showinfo(
            "Congratulations!",
            f"You solved the Killer Sudoku!\n\nTime: {formatted_time}"
        )

    def on_about(self):
        messagebox.showinfo(
            "About Killer Sudoku",
            "Killer Sudoku Desktop Application\n\n"
            "Features:\n"
            "• Configurable JSON puzzles & cage rules\n"
            "• Notes, validation, timer, & autosave\n"
            "• Built-in Puzzle/Cage Editor\n"
            "• Console-free Windows desktop compatibility\n"
        )

    def on_exit(self):
        if self.game_mgr:
            self.game_mgr.save_game()
        self.destroy()
