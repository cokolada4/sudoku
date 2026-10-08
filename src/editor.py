"""
Interactive Puzzle / Cage Editor GUI for Killer Sudoku.
Allows selecting grid cells, creating/assigning cage sums, adding givens, validating full grid coverage, and saving puzzles.
"""

import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
from typing import Set, Tuple, List, Dict, Optional
import os

from src.models import parse_coord, to_coord_str
from src.puzzle_manager import PuzzleManager, PuzzleValidationError


class PuzzleEditorWindow(tk.Toplevel):
    """
    Dedicated Puzzle and Cage Editor dialog window.
    """
    def __init__(self, parent, puzzle_mgr: PuzzleManager):
        super().__init__(parent)
        self.title("Killer Sudoku - Puzzle & Cage Editor")
        self.geometry("850x700")
        self.minsize(700, 600)
        self.transient(parent)
        self.grab_set()

        self.puzzle_mgr: PuzzleManager = puzzle_mgr

        self.puzzle_name: str = "New Killer Sudoku"
        self.cages: List[Dict] = []  # List of {"sum": int, "cells": ["R1C1", ...]}
        self.givens: Dict[str, int] = {}  # Map "R1C1": int
        self.selected_cells: Set[Tuple[int, int]] = set()

        self.cell_size: float = 50.0

        self.setup_ui()
        self.redraw_grid()

    def setup_ui(self):
        # Top Controls: Name, Load Existing, Save
        top_frame = tk.Frame(self, bg="#E8E8E8", pady=5, padx=10)
        top_frame.pack(side=tk.TOP, fill=tk.X)

        tk.Label(top_frame, text="Puzzle Name:", font=("Arial", 10, "bold"), bg="#E8E8E8").pack(side=tk.LEFT, padx=5)
        self.name_entry = tk.Entry(top_frame, font=("Arial", 10), width=20)
        self.name_entry.insert(0, self.puzzle_name)
        self.name_entry.pack(side=tk.LEFT, padx=5)

        tk.Button(top_frame, text="Load Puzzle...", font=("Arial", 10), command=self.on_load_puzzle).pack(side=tk.LEFT, padx=10)
        tk.Button(top_frame, text="Save Puzzle", font=("Arial", 10, "bold"), bg="#DDF0FF", command=self.on_save_puzzle).pack(side=tk.RIGHT, padx=5)

        # Main Layout: Left Canvas Grid, Right Panel (Cage List & Actions)
        main_frame = tk.Frame(self)
        main_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Canvas Frame
        self.canvas = tk.Canvas(main_frame, bg="#FFFFFF")
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.canvas.bind("<Configure>", lambda e: self.redraw_grid())
        self.canvas.bind("<Button-1>", self.on_canvas_click)

        # Right Panel
        right_panel = tk.Frame(main_frame, width=300, bg="#F5F5F5", padx=10, pady=10)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y)

        tk.Label(right_panel, text="Selected Cells:", font=("Arial", 10, "bold"), bg="#F5F5F5").pack(anchor="w", pady=(0, 2))
        self.selected_lbl = tk.Label(right_panel, text="None", font=("Arial", 9), bg="#FFFFFF", relief="sunken", anchor="w", wraplength=260)
        self.selected_lbl.pack(fill=tk.X, pady=(0, 10))

        # Cage Action Buttons
        tk.Button(right_panel, text="Create Cage from Selected", font=("Arial", 10, "bold"), bg="#CCE5FF", command=self.on_create_cage).pack(fill=tk.X, pady=3)
        tk.Button(right_panel, text="Clear Selected Cells", font=("Arial", 9), command=self.on_clear_selection).pack(fill=tk.X, pady=3)
        tk.Button(right_panel, text="Set/Clear Given Value", font=("Arial", 9), command=self.on_set_given).pack(fill=tk.X, pady=3)

        tk.Label(right_panel, text="Existing Cages:", font=("Arial", 10, "bold"), bg="#F5F5F5").pack(anchor="w", pady=(15, 2))

        # Cage Listbox
        list_frame = tk.Frame(right_panel)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.cage_listbox = tk.Listbox(list_frame, font=("Arial", 9), height=10)
        scrollbar = tk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.cage_listbox.yview)
        self.cage_listbox.config(yscrollcommand=scrollbar.set)
        self.cage_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        tk.Button(right_panel, text="Delete Selected Cage", font=("Arial", 9), bg="#FFCCCC", command=self.on_delete_cage).pack(fill=tk.X, pady=5)
        tk.Button(right_panel, text="Clear All Cages", font=("Arial", 9), command=self.on_clear_all_cages).pack(fill=tk.X, pady=2)

    def on_canvas_click(self, event):
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        grid_size = 9
        cell_size = min(w, h) / grid_size

        off_x = (w - cell_size * grid_size) / 2
        off_y = (h - cell_size * grid_size) / 2

        col = int((event.x - off_x) // cell_size)
        row = int((event.y - off_y) // cell_size)

        if 0 <= row < grid_size and 0 <= col < grid_size:
            coord = (row, col)
            if coord in self.selected_cells:
                self.selected_cells.remove(coord)
            else:
                self.selected_cells.add(coord)
            self.update_selected_label()
            self.redraw_grid()

    def update_selected_label(self):
        if not self.selected_cells:
            self.selected_lbl.config(text="None")
        else:
            sorted_coords = sorted(list(self.selected_cells))
            str_list = [to_coord_str(r, c) for r, c in sorted_coords]
            self.selected_lbl.config(text=", ".join(str_list))

    def redraw_grid(self):
        self.canvas.delete("all")
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w <= 1 or h <= 1:
            w, h = 500, 500

        grid_size = 9
        cell_size = min(w, h) / grid_size

        off_x = (w - cell_size * grid_size) / 2
        off_y = (h - cell_size * grid_size) / 2

        # Cell to cage lookup
        cell_cage_map = {}
        for c_idx, cage in enumerate(self.cages):
            for c_str in cage["cells"]:
                r, c = parse_coord(c_str)
                cell_cage_map[(r, c)] = (c_idx, cage)

        # 1. Backgrounds
        for r in range(grid_size):
            for c in range(grid_size):
                x1 = off_x + c * cell_size
                y1 = off_y + r * cell_size
                x2 = x1 + cell_size
                y2 = y1 + cell_size

                fill_col = "#FFFFFF"
                if (r, c) in self.selected_cells:
                    fill_col = "#B3D8FF"  # Highlighted selected
                elif (r, c) in cell_cage_map:
                    fill_col = "#F0F8FF"  # Belongs to cage

                self.canvas.create_rectangle(x1, y1, x2, y2, fill=fill_col, outline="#CCCCCC")

        # 2. Cage Borders & Sums
        cage_bw = max(2, int(cell_size / 25))
        for r in range(grid_size):
            for c in range(grid_size):
                if (r, c) in cell_cage_map:
                    c_idx, cage = cell_cage_map[(r, c)]
                    x1 = off_x + c * cell_size
                    y1 = off_y + r * cell_size
                    x2 = x1 + cell_size
                    y2 = y1 + cell_size
                    inset = cage_bw / 2

                    cage_coords = {parse_coord(cs) for cs in cage["cells"]}

                    if (r - 1, c) not in cage_coords:
                        self.canvas.create_line(x1 + inset, y1 + inset, x2 - inset, y1 + inset, fill="#2A65A0", width=cage_bw, dash=(4, 2))
                    if (r + 1, c) not in cage_coords:
                        self.canvas.create_line(x1 + inset, y2 - inset, x2 - inset, y2 - inset, fill="#2A65A0", width=cage_bw, dash=(4, 2))
                    if (r, c - 1) not in cage_coords:
                        self.canvas.create_line(x1 + inset, y1 + inset, x1 + inset, y2 - inset, fill="#2A65A0", width=cage_bw, dash=(4, 2))
                    if (r, c + 1) not in cage_coords:
                        self.canvas.create_line(x2 - inset, y1 + inset, x2 - inset, y2 - inset, fill="#2A65A0", width=cage_bw, dash=(4, 2))

        # Cage sum text
        sum_fsize = max(8, int(cell_size / 5.5))
        for cage in self.cages:
            coords = [parse_coord(cs) for cs in cage["cells"]]
            top_r, top_c = min(coords, key=lambda p: (p[0], p[1]))
            lx = off_x + top_c * cell_size + cell_size * 0.08
            ly = off_y + top_r * cell_size + cell_size * 0.06
            self.canvas.create_text(
                lx, ly,
                text=str(cage["sum"]),
                anchor="nw",
                font=("Arial", sum_fsize, "bold"),
                fill="#2A65A0"
            )

        # 3. 3x3 Box Lines
        box_bw = max(3, int(cell_size / 18))
        for i in range(grid_size + 1):
            lw = box_bw if i % 3 == 0 else 1
            lc = "#000000" if i % 3 == 0 else "#CCCCCC"

            x = off_x + i * cell_size
            self.canvas.create_line(x, off_y, x, off_y + grid_size * cell_size, fill=lc, width=lw)
            y = off_y + i * cell_size
            self.canvas.create_line(off_x, y, off_x + grid_size * cell_size, y, fill=lc, width=lw)

        # 4. Givens Display
        given_fsize = max(14, int(cell_size / 2.2))
        for c_str, val in self.givens.items():
            r, c = parse_coord(c_str)
            cx = off_x + c * cell_size + cell_size / 2
            cy = off_y + r * cell_size + cell_size / 2
            self.canvas.create_text(cx, cy, text=str(val), font=("Arial", given_fsize, "bold"), fill="#000000")

        self.update_listbox()

    def update_listbox(self):
        self.cage_listbox.delete(0, tk.END)
        for idx, cage in enumerate(self.cages):
            c_strs = ", ".join(cage["cells"])
            self.cage_listbox.insert(tk.END, f"Sum {cage['sum']}: [{c_strs}]")

    def on_create_cage(self):
        if not self.selected_cells:
            messagebox.showwarning("Create Cage", "No cells selected. Click cells on the grid first.")
            return

        # Check overlap
        new_coords = {to_coord_str(r, c) for r, c in self.selected_cells}
        for cage in self.cages:
            existing_coords = set(cage["cells"])
            overlap = new_coords.intersection(existing_coords)
            if overlap:
                messagebox.showerror(
                    "Overlap Error",
                    f"Selected cell(s) {', '.join(sorted(list(overlap)))} already belong to another cage."
                )
                return

        # Prompt for sum
        sum_val = simpledialog.askinteger("Cage Sum", "Enter target sum for cage:", minvalue=1, maxvalue=45, parent=self)
        if sum_val is not None:
            sorted_cell_strs = [to_coord_str(r, c) for r, c in sorted(list(self.selected_cells))]
            self.cages.append({
                "sum": sum_val,
                "cells": sorted_cell_strs
            })
            self.selected_cells.clear()
            self.update_selected_label()
            self.redraw_grid()

    def on_clear_selection(self):
        self.selected_cells.clear()
        self.update_selected_label()
        self.redraw_grid()

    def on_set_given(self):
        if len(self.selected_cells) != 1:
            messagebox.showwarning("Set Given", "Please select exactly one cell to set/clear its given starting value.")
            return

        r, c = list(self.selected_cells)[0]
        c_str = to_coord_str(r, c)
        curr_val = self.givens.get(c_str, "")

        val = simpledialog.askinteger(
            "Given Value",
            f"Enter given starting value for {c_str} (1-9), or 0/Cancel to clear:",
            minvalue=0, maxvalue=9, parent=self
        )
        if val is not None:
            if val == 0:
                self.givens.pop(c_str, None)
            else:
                self.givens[c_str] = val
            self.redraw_grid()

    def on_delete_cage(self):
        sel_idx = self.cage_listbox.curselection()
        if not sel_idx:
            messagebox.showwarning("Delete Cage", "Select a cage from the list to delete.")
            return
        idx = sel_idx[0]
        del self.cages[idx]
        self.redraw_grid()

    def on_clear_all_cages(self):
        if messagebox.askyesno("Clear Cages", "Are you sure you want to clear all cages?"):
            self.cages.clear()
            self.redraw_grid()

    def on_load_puzzle(self):
        path = filedialog.askopenfilename(
            title="Open Puzzle JSON for Editing",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
        )
        if path:
            try:
                data = self.puzzle_mgr.load_raw_json(path)
                self.puzzle_name = data.get("name", "Loaded Puzzle")
                self.name_entry.delete(0, tk.END)
                self.name_entry.insert(0, self.puzzle_name)
                self.cages = data.get("cages", [])
                self.givens = data.get("givens", {})
                self.selected_cells.clear()
                self.update_selected_label()
                self.redraw_grid()
            except Exception as e:
                messagebox.showerror("Error Loading Puzzle", f"Could not load puzzle for editing:\n{e}")

    def on_save_puzzle(self):
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Save Error", "Please enter a valid puzzle name.")
            return

        # Check cell coverage
        all_claimed = set()
        for cage in self.cages:
            all_claimed.update(cage["cells"])

        if len(all_claimed) < 81:
            ans = messagebox.askyesno(
                "Incomplete Grid",
                f"Only {len(all_claimed)} / 81 cells belong to cages.\nDo you still want to save?"
            )
            if not ans:
                return

        puzzle_data = {
            "name": name,
            "size": 9,
            "box_size": 3,
            "givens": self.givens,
            "cages": self.cages
        }

        # Validate structure
        try:
            self.puzzle_mgr.validate_puzzle_data(puzzle_data)
        except PuzzleValidationError as ve:
            messagebox.showerror("Validation Error", f"Puzzle structure is invalid:\n{ve}")
            return

        # Choose save file path
        safe_name = "".join(c if c.isalnum() else "_" for c in name.lower())
        default_filename = f"{safe_name}.json"
        save_path = filedialog.asksaveasfilename(
            title="Save Puzzle JSON",
            initialdir=self.puzzle_mgr.puzzle_dir,
            initialfile=default_filename,
            filetypes=[("JSON Files", "*.json")]
        )

        if save_path:
            try:
                self.puzzle_mgr.save_puzzle_file(save_path, puzzle_data)
                messagebox.showinfo("Puzzle Saved", f"Puzzle successfully saved to:\n{save_path}")
            except Exception as e:
                messagebox.showerror("Save Failed", f"Failed to save puzzle:\n{e}")
