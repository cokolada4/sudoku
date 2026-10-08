"""
Sudoku Canvas Board UI Component for Killer Sudoku.
Renders cells, 3x3 box outlines, dashed/colored cage borders, upper-left cage sum labels, numbers, notes, and cell selection/highlights.
"""

import tkinter as tk
from typing import Optional, Tuple, Set, Dict
from src.game_manager import GameManager
from src.validator import ValidationResult


class SudokuBoard(tk.Canvas):
    """
    Tkinter Canvas widget rendering the interactive Killer Sudoku grid.
    """
    def __init__(self, parent, game_mgr: GameManager, **kwargs):
        super().__init__(parent, **kwargs)
        self.game_mgr: GameManager = game_mgr
        self.bind("<Configure>", self.on_resize)
        self.bind("<Button-1>", self.on_click)

    def on_resize(self, event):
        self.redraw()

    def on_click(self, event):
        if self.game_mgr.is_paused:
            return
        width = self.winfo_width()
        height = self.winfo_height()
        grid_size = self.game_mgr.puzzle.size
        cell_size = min(width, height) / grid_size

        # Offsets to center grid
        offset_x = (width - cell_size * grid_size) / 2
        offset_y = (height - cell_size * grid_size) / 2

        col = int((event.x - offset_x) // cell_size)
        row = int((event.y - offset_y) // cell_size)

        if 0 <= row < grid_size and 0 <= col < grid_size:
            self.game_mgr.select_cell(row, col)

    def redraw(self):
        self.delete("all")
        width = self.winfo_width()
        height = self.winfo_height()
        if width <= 1 or height <= 1:
            try:
                width = int(self.cget("width"))
                height = int(self.cget("height"))
            except Exception:
                width = 600
                height = 600

        puzzle = self.game_mgr.puzzle
        grid_size = puzzle.size
        box_size = puzzle.box_size
        cell_size = min(width, height) / grid_size

        offset_x = (width - cell_size * grid_size) / 2
        offset_y = (height - cell_size * grid_size) / 2

        # Color config
        cfg = self.game_mgr.config_mgr
        bg_color = cfg.get_appearance("background", "#FFFFFF")
        grid_color = cfg.get_appearance("grid_color", "#CCCCCC")
        box_line_color = cfg.get_appearance("box_line_color", "#000000")
        cage_line_color = cfg.get_appearance("cage_line_color", "#2A65A0")
        selected_color = cfg.get_appearance("selected_color", "#B3D8FF")
        highlight_color = cfg.get_appearance("highlight_color", "#EAF2FC")
        same_number_color = cfg.get_appearance("same_number_color", "#CCE5FF")
        error_color = cfg.get_appearance("error_color", "#FFCCCC")
        given_font_color = cfg.get_appearance("given_font_color", "#000000")
        player_font_color = cfg.get_appearance("player_font_color", "#002288")
        note_font_color = cfg.get_appearance("note_font_color", "#666666")

        self.configure(bg=bg_color)

        # Validate state for error highlighting
        val_result: ValidationResult = self.game_mgr.validate_current_state()

        sel_r, sel_c = self.game_mgr.selected_cell if self.game_mgr.selected_cell else (-1, -1)
        sel_value = puzzle.get_cell(sel_r, sel_c).value if (0 <= sel_r < grid_size and 0 <= sel_c < grid_size) else None

        # 1. Draw Cell Backgrounds & Highlights
        for r in range(grid_size):
            for c in range(grid_size):
                x1 = offset_x + c * cell_size
                y1 = offset_y + r * cell_size
                x2 = x1 + cell_size
                y2 = y1 + cell_size

                cell = puzzle.get_cell(r, c)
                is_selected = (r == sel_r and c == sel_c)
                is_invalid = (r, c) in val_result.invalid_cells

                # Determine background color
                cell_bg = bg_color
                if is_invalid:
                    cell_bg = error_color
                elif is_selected:
                    cell_bg = selected_color
                elif sel_value is not None and cell.value == sel_value and cfg.get_setting("highlight_same_numbers", True):
                    cell_bg = same_number_color
                elif 0 <= sel_r < grid_size and 0 <= sel_c < grid_size:
                    in_same_row = (r == sel_r) and cfg.get_setting("highlight_row", True)
                    in_same_col = (c == sel_c) and cfg.get_setting("highlight_column", True)
                    in_same_box = (r // box_size == sel_r // box_size) and (c // box_size == sel_c // box_size) and cfg.get_setting("highlight_box", True)
                    if in_same_row or in_same_col or in_same_box:
                        cell_bg = highlight_color

                self.create_rectangle(x1, y1, x2, y2, fill=cell_bg, outline=grid_color, width=1)

        # 2. Draw Cage Outlines and Cage Sum Labels
        cage_cell_map = {}
        for cage in puzzle.cages:
            for r, c in cage.cells:
                cage_cell_map[(r, c)] = cage

        # Draw cage borders (where adjacent cell is not in the same cage)
        cage_border_width = max(2, int(cell_size / 25))
        for r in range(grid_size):
            for c in range(grid_size):
                cage = cage_cell_map.get((r, c))
                if not cage:
                    continue

                x1 = offset_x + c * cell_size
                y1 = offset_y + r * cell_size
                x2 = x1 + cell_size
                y2 = y1 + cell_size

                inset = cage_border_width / 2

                # Top border
                if (r - 1, c) not in cage.cells:
                    self.create_line(x1 + inset, y1 + inset, x2 - inset, y1 + inset, fill=cage_line_color, width=cage_border_width, dash=(4, 2))
                # Bottom border
                if (r + 1, c) not in cage.cells:
                    self.create_line(x1 + inset, y2 - inset, x2 - inset, y2 - inset, fill=cage_line_color, width=cage_border_width, dash=(4, 2))
                # Left border
                if (r, c - 1) not in cage.cells:
                    self.create_line(x1 + inset, y1 + inset, x1 + inset, y2 - inset, fill=cage_line_color, width=cage_border_width, dash=(4, 2))
                # Right border
                if (r, c + 1) not in cage.cells:
                    self.create_line(x2 - inset, y1 + inset, x2 - inset, y2 - inset, fill=cage_line_color, width=cage_border_width, dash=(4, 2))

        # Cage Sum Labels
        sum_font_size = max(8, int(cell_size / 5.5))
        for cage in puzzle.cages:
            top_r, top_c = cage.top_left_cell
            lx = offset_x + top_c * cell_size + cell_size * 0.08
            ly = offset_y + top_r * cell_size + cell_size * 0.06
            self.create_text(
                lx, ly,
                text=str(cage.target_sum),
                anchor="nw",
                font=("Arial", sum_font_size, "bold"),
                fill=cage_line_color
            )

        # 3. Draw Standard 3x3 Sudoku Box Lines
        box_line_width = max(3, int(cell_size / 18))
        for i in range(grid_size + 1):
            lw = box_line_width if i % box_size == 0 else 1
            lc = box_line_color if i % box_size == 0 else grid_color

            # Vertical lines
            x = offset_x + i * cell_size
            self.create_line(x, offset_y, x, offset_y + grid_size * cell_size, fill=lc, width=lw)

            # Horizontal lines
            y = offset_y + i * cell_size
            self.create_line(offset_x, y, offset_x + grid_size * cell_size, y, fill=lc, width=lw)

        # 4. Draw Cell Values (Given / Player / Notes)
        val_font_size = max(16, int(cell_size / 2.2))
        note_font_size = max(8, int(cell_size / 5.5))

        for r in range(grid_size):
            for c in range(grid_size):
                cell = puzzle.get_cell(r, c)
                cx = offset_x + c * cell_size + cell_size / 2
                cy = offset_y + r * cell_size + cell_size / 2

                if cell.value is not None:
                    # Draw Main Digit
                    f_weight = "bold" if cell.is_given else "normal"
                    f_color = given_font_color if cell.is_given else player_font_color
                    self.create_text(
                        cx, cy + cell_size * 0.05,
                        text=str(cell.value),
                        font=("Arial", val_font_size, f_weight),
                        fill=f_color
                    )
                elif cell.notes:
                    # Draw 3x3 Notes Grid
                    note_step = cell_size / 3.5
                    for n in cell.notes:
                        nr = (n - 1) // 3
                        nc = (n - 1) % 3
                        nx = offset_x + c * cell_size + (nc + 0.8) * note_step
                        ny = offset_y + r * cell_size + (nr + 0.9) * note_step
                        self.create_text(
                            nx, ny,
                            text=str(n),
                            font=("Arial", note_font_size, "normal"),
                            fill=note_font_color
                        )
