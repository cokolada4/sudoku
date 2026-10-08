"""
Atomic save and load manager for Killer Sudoku game progress.
"""

import os
import json
import time
import shutil
from typing import Dict, Any, Optional, Tuple
from src.models import Puzzle, parse_coord, to_coord_str
from src.config_manager import log_error


class SaveManager:
    """
    Handles atomic loading and saving of game state with backups.
    """
    def __init__(self, saves_dir: str = "saves"):
        self.saves_dir: str = saves_dir
        if not os.path.exists(self.saves_dir):
            os.makedirs(self.saves_dir, exist_ok=True)

    def _get_save_filepath(self, puzzle_name: str) -> str:
        safe_name = "".join(c if c.isalnum() else "_" for c in puzzle_name)
        return os.path.join(self.saves_dir, f"save_{safe_name}.json")

    def save_game(self, puzzle: Puzzle, elapsed_seconds: int) -> bool:
        """
        Atomically saves game progress using temporary file + atomic rename.
        """
        save_path = self._get_save_filepath(puzzle.name)
        temp_path = save_path + ".tmp"
        backup_path = save_path + ".bak"

        # Serialize values and notes
        values = []
        notes = {}
        for r in range(puzzle.size):
            for c in range(puzzle.size):
                cell = puzzle.get_cell(r, c)
                if not cell.is_given and cell.player_value is not None:
                    values.append({
                        "coord": cell.coord_str,
                        "value": cell.player_value
                    })
                if not cell.is_given and cell.notes:
                    notes[cell.coord_str] = sorted(list(cell.notes))

        save_data = {
            "version": 1,
            "puzzle": puzzle.name,
            "elapsed_seconds": elapsed_seconds,
            "timestamp": time.time(),
            "values": values,
            "notes": notes
        }

        try:
            # 1. Write temporary save file
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(save_data, f, indent=4)

            # 2. Validate temporary save file
            with open(temp_path, "r", encoding="utf-8") as f:
                loaded = json.load(f)
                if loaded.get("version") != 1:
                    raise ValueError("Temp save verification failed.")

            # 3. Create backup of current save file if exists
            if os.path.exists(save_path):
                shutil.copy2(save_path, backup_path)

            # 4. Atomically replace save file with temp file
            os.replace(temp_path, save_path)
            return True

        except Exception as e:
            log_error(f"Failed to save game for puzzle {puzzle.name}", e)
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except Exception:
                    pass
            return False

    def load_game(self, puzzle: Puzzle) -> Optional[int]:
        """
        Loads saved game progress into the puzzle object.
        Returns elapsed_seconds if successful, or None if no save file exists / failed.
        """
        save_path = self._get_save_filepath(puzzle.name)
        backup_path = save_path + ".bak"

        target_path = None
        if os.path.exists(save_path):
            target_path = save_path
        elif os.path.exists(backup_path):
            target_path = backup_path

        if not target_path:
            return None

        try:
            with open(target_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            if data.get("puzzle") != puzzle.name:
                log_error(f"Save file {target_path} puzzle mismatch: expected {puzzle.name}, got {data.get('puzzle')}")
                return None

            # Apply player values
            for entry in data.get("values", []):
                coord = entry.get("coord")
                val = entry.get("value")
                if coord and val:
                    r, c = parse_coord(coord)
                    cell = puzzle.get_cell(r, c)
                    cell.player_value = val

            # Apply notes
            for coord, note_list in data.get("notes", {}).items():
                r, c = parse_coord(coord)
                cell = puzzle.get_cell(r, c)
                cell.notes = set(note_list)

            return data.get("elapsed_seconds", 0)

        except Exception as e:
            log_error(f"Failed to load game from {target_path}", e)
            return None

    def has_save(self, puzzle_name: str) -> bool:
        save_path = self._get_save_filepath(puzzle_name)
        return os.path.exists(save_path) or os.path.exists(save_path + ".bak")
