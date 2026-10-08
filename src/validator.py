"""
Sudoku and Killer Sudoku validation engine.
"""

from typing import List, Set, Dict, Tuple, Optional
from itertools import combinations
from src.models import Puzzle, Cage, Cell


class ValidationResult:
    """
    Holds invalid cell coordinates and cage status mappings.
    """
    def __init__(self):
        self.invalid_cells: Set[Tuple[int, int]] = set()
        self.invalid_cages: Set[Cage] = set()
        self.cage_statuses: Dict[Cage, str] = {}  # "CORRECT", "INCOMPLETE_VALID", "INVALID"

    @property
    def is_valid(self) -> bool:
        return len(self.invalid_cells) == 0 and len(self.invalid_cages) == 0


class SudokuValidator:
    """
    Validator for row, column, box, and Killer Sudoku cage constraints.
    """
    @staticmethod
    def validate_puzzle(puzzle: Puzzle) -> ValidationResult:
        res = ValidationResult()

        # 1. Row Validation
        for r in range(puzzle.size):
            seen: Dict[int, List[int]] = {}
            for c in range(puzzle.size):
                val = puzzle.get_cell(r, c).value
                if val is not None:
                    seen.setdefault(val, []).append(c)
            for val, cols in seen.items():
                if len(cols) > 1:
                    for c in cols:
                        res.invalid_cells.add((r, c))

        # 2. Column Validation
        for c in range(puzzle.size):
            seen: Dict[int, List[int]] = {}
            for r in range(puzzle.size):
                val = puzzle.get_cell(r, c).value
                if val is not None:
                    seen.setdefault(val, []).append(r)
            for val, rows in seen.items():
                if len(rows) > 1:
                    for r in rows:
                        res.invalid_cells.add((r, c))

        # 3. 3x3 Box Validation
        box_size = puzzle.box_size
        for br in range(0, puzzle.size, box_size):
            for bc in range(0, puzzle.size, box_size):
                seen: Dict[int, List[Tuple[int, int]]] = {}
                for r in range(br, br + box_size):
                    for c in range(bc, bc + box_size):
                        val = puzzle.get_cell(r, c).value
                        if val is not None:
                            seen.setdefault(val, []).append((r, c))
                for val, coords in seen.items():
                    if len(coords) > 1:
                        for r, c in coords:
                            res.invalid_cells.add((r, c))

        # 4. Cage Validation
        for cage in puzzle.cages:
            status = SudokuValidator._validate_cage(puzzle, cage)
            res.cage_statuses[cage] = status
            if status == "INVALID":
                res.invalid_cages.add(cage)
                for r, c in cage.cells:
                    res.invalid_cells.add((r, c))

        return res

    @staticmethod
    def _validate_cage(puzzle: Puzzle, cage: Cage) -> str:
        """
        Validates a single cage.
        Returns:
            "CORRECT": Cage is full, has no duplicate values, and sum == target_sum.
            "INCOMPLETE_VALID": Cage is partially full, no duplicates, remaining sum is mathematically possible with unique unused digits 1-9.
            "INVALID": Duplicate digit in cage, OR sum exceeds target, OR impossible remaining sum.
        """
        values = []
        filled_count = 0

        for r, c in cage.cells:
            val = puzzle.get_cell(r, c).value
            if val is not None:
                values.append(val)
                filled_count += 1

        # Check for duplicates in cage
        if len(values) != len(set(values)):
            return "INVALID"

        current_sum = sum(values)
        cage_size = len(cage.cells)
        remaining_count = cage_size - filled_count

        # Exceeded target sum
        if current_sum > cage.target_sum:
            return "INVALID"

        # Complete cage check
        if remaining_count == 0:
            if current_sum == cage.target_sum:
                return "CORRECT"
            else:
                return "INVALID"

        # Incomplete cage feasibility check:
        # Check if there exists a combination of `remaining_count` distinct digits from {1..9} \ set(values) that sums to (target_sum - current_sum).
        remaining_target = cage.target_sum - current_sum
        available_digits = [d for d in range(1, 10) if d not in values]

        possible = False
        for combo in combinations(available_digits, remaining_count):
            if sum(combo) == remaining_target:
                possible = True
                break

        if possible:
            return "INCOMPLETE_VALID"
        else:
            return "INVALID"

    @staticmethod
    def is_puzzle_complete_and_valid(puzzle: Puzzle) -> bool:
        """
        Returns True if all cells are filled and there are no validation errors.
        """
        # Check all cells filled
        for r in range(puzzle.size):
            for c in range(puzzle.size):
                if puzzle.get_cell(r, c).value is None:
                    return False

        res = SudokuValidator.validate_puzzle(puzzle)
        return res.is_valid
