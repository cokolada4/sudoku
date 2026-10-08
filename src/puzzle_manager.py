"""
Puzzle manager and JSON schema validator for Killer Sudoku.
"""

import json
import os
from typing import Dict, Any, List, Tuple
from src.models import Puzzle, Cage, parse_coord, to_coord_str
from src.config_manager import log_error


class PuzzleValidationError(Exception):
    """Exception raised when a puzzle JSON file fails validation."""
    pass


class PuzzleManager:
    """
    Handles loading, parsing, and validating Killer Sudoku puzzle files.
    """
    def __init__(self, puzzle_dir: str = "puzzles"):
        self.puzzle_dir: str = puzzle_dir
        if not os.path.exists(self.puzzle_dir):
            os.makedirs(self.puzzle_dir, exist_ok=True)

    def get_available_puzzles(self) -> List[Tuple[str, str]]:
        """
        Returns a list of (puzzle_name, filepath) tuples for valid puzzle files in puzzle_dir.
        """
        puzzles = []
        if not os.path.exists(self.puzzle_dir):
            return puzzles

        for fname in sorted(os.listdir(self.puzzle_dir)):
            if fname.endswith(".json"):
                fpath = os.path.join(self.puzzle_dir, fname)
                try:
                    p = self.load_puzzle(fpath)
                    puzzles.append((p.name, fpath))
                except Exception as e:
                    log_error(f"Skipping invalid puzzle file {fpath}", e)
        return puzzles

    def load_raw_json(self, filepath: str) -> Dict[str, Any]:
        if not os.path.exists(filepath):
            raise PuzzleValidationError(f"Puzzle file does not exist: {filepath}")
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data
        except json.JSONDecodeError as e:
            raise PuzzleValidationError(f"Invalid JSON syntax in {filepath}: {e}")
        except Exception as e:
            raise PuzzleValidationError(f"Could not read file {filepath}: {e}")

    def validate_puzzle_data(self, data: Dict[str, Any]):
        if not isinstance(data, dict):
            raise PuzzleValidationError("Root JSON must be an object.")

        if "name" not in data or not isinstance(data["name"], str):
            raise PuzzleValidationError("Puzzle missing valid 'name' string.")

        size = data.get("size", 9)
        box_size = data.get("box_size", 3)
        if size != 9 or box_size != 3:
            raise PuzzleValidationError(f"Only 9x9 puzzles (box_size 3) are supported. Got size={size}, box_size={box_size}.")

        cages_data = data.get("cages")
        if not isinstance(cages_data, list) or len(cages_data) == 0:
            raise PuzzleValidationError("Puzzle must contain a non-empty 'cages' list.")

        claimed_cells = set()
        for idx, cage in enumerate(cages_data):
            if not isinstance(cage, dict):
                raise PuzzleValidationError(f"Cage {idx + 1} must be a JSON object.")
            if "sum" not in cage or not isinstance(cage["sum"], int) or cage["sum"] <= 0:
                raise PuzzleValidationError(f"Cage {idx + 1} has invalid 'sum': {cage.get('sum')}.")

            cells = cage.get("cells")
            if not isinstance(cells, list) or len(cells) == 0:
                raise PuzzleValidationError(f"Cage {idx + 1} has no cells specified.")

            for coord_str in cells:
                if not isinstance(coord_str, str):
                    raise PuzzleValidationError(f"Cage {idx + 1} contains non-string coordinate.")
                try:
                    r, c = parse_coord(coord_str)
                except ValueError as ve:
                    raise PuzzleValidationError(f"Cage {idx + 1} has invalid cell coordinate '{coord_str}': {ve}")

                if not (0 <= r < size and 0 <= c < size):
                    raise PuzzleValidationError(f"Cell '{coord_str}' is out of bounds (1-9).")

                if (r, c) in claimed_cells:
                    raise PuzzleValidationError(f"Cell '{coord_str}' belongs to multiple cages.")
                claimed_cells.add((r, c))

        # Check starting givens
        givens = data.get("givens", {})
        if not isinstance(givens, dict):
            raise PuzzleValidationError("'givens' must be a JSON object mapping cell coordinate to number.")

        for coord_str, val in givens.items():
            try:
                r, c = parse_coord(coord_str)
            except ValueError as ve:
                raise PuzzleValidationError(f"Given value has invalid coordinate '{coord_str}': {ve}")
            if not (0 <= r < size and 0 <= c < size):
                raise PuzzleValidationError(f"Given cell '{coord_str}' is out of bounds.")
            if not isinstance(val, int) or not (1 <= val <= 9):
                raise PuzzleValidationError(f"Given value for '{coord_str}' must be integer between 1 and 9.")

    def load_puzzle(self, filepath: str) -> Puzzle:
        data = self.load_raw_json(filepath)
        self.validate_puzzle_data(data)

        cages = []
        for cdict in data["cages"]:
            cell_coords = [parse_coord(cs) for cs in cdict["cells"]]
            cages.append(Cage(cdict["sum"], cell_coords))

        return Puzzle(
            name=data["name"],
            size=data.get("size", 9),
            box_size=data.get("box_size", 3),
            cages=cages,
            givens=data.get("givens", {})
        )

    def save_puzzle_file(self, filepath: str, data: Dict[str, Any]):
        self.validate_puzzle_data(data)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
