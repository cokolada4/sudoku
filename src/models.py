"""
Data models and coordinate helpers for Killer Sudoku.
"""

from typing import List, Dict, Optional, Tuple, Set


def parse_coord(coord_str: str) -> Tuple[int, int]:
    """
    Converts human-readable coordinate string like 'R1C1' to 0-indexed (row, col) tuple.
    R1C1 -> (0, 0)
    R9C9 -> (8, 8)
    """
    coord_str = coord_str.strip().upper()
    if not (coord_str.startswith('R') and 'C' in coord_str):
        raise ValueError(f"Invalid coordinate format: '{coord_str}'. Expected 'R#C#'.")
    try:
        r_part, c_part = coord_str[1:].split('C')
        row = int(r_part) - 1
        col = int(c_part) - 1
        return row, col
    except Exception as e:
        raise ValueError(f"Invalid coordinate string '{coord_str}': {e}")


def to_coord_str(row: int, col: int) -> str:
    """
    Converts 0-indexed (row, col) tuple to coordinate string like 'R1C1'.
    (0, 0) -> 'R1C1'
    (8, 8) -> 'R9C9'
    """
    return f"R{row + 1}C{col + 1}"


class Cell:
    """
    Represents a single Sudoku grid cell.
    """
    def __init__(self, row: int, col: int, given_value: Optional[int] = None):
        self.row: int = row
        self.col: int = col
        self.given_value: Optional[int] = given_value
        self._player_value: Optional[int] = None
        self.notes: Set[int] = set()

    @property
    def coord_str(self) -> str:
        return to_coord_str(self.row, self.col)

    @property
    def is_given(self) -> bool:
        return self.given_value is not None

    @property
    def player_value(self) -> Optional[int]:
        return self._player_value

    @player_value.setter
    def player_value(self, val: Optional[int]):
        if not self.is_given:
            self._player_value = val
            if val is not None:
                self.notes.clear()

    @property
    def value(self) -> Optional[int]:
        if self.given_value is not None:
            return self.given_value
        return self._player_value

    def clear(self):
        if not self.is_given:
            self._player_value = None
            self.notes.clear()

    def toggle_note(self, num: int):
        if not self.is_given:
            self._player_value = None
            if num in self.notes:
                self.notes.remove(num)
            else:
                self.notes.add(num)


class Cage:
    """
    Represents a Killer Sudoku cage containing a set of cell coordinates and a target sum.
    """
    def __init__(self, target_sum: int, cells: List[Tuple[int, int]]):
        self.target_sum: int = target_sum
        self.cells: List[Tuple[int, int]] = cells  # List of (row, col) tuples

    @property
    def top_left_cell(self) -> Tuple[int, int]:
        """
        Returns the top-leftmost cell coordinate in the cage (smallest row, then smallest col).
        Used for displaying the cage sum label.
        """
        return min(self.cells, key=lambda c: (c[0], c[1]))


class Puzzle:
    """
    Represents a complete Killer Sudoku puzzle layout and grid state.
    """
    def __init__(self, name: str, size: int = 9, box_size: int = 3, cages: Optional[List[Cage]] = None, givens: Optional[Dict[str, int]] = None):
        self.name: str = name
        self.size: int = size
        self.box_size: int = box_size
        self.cages: List[Cage] = cages if cages is not None else []
        self.grid: List[List[Cell]] = [[Cell(r, c) for c in range(size)] for r in range(size)]

        if givens:
            for coord_str, val in givens.items():
                r, c = parse_coord(coord_str)
                if 0 <= r < size and 0 <= c < size:
                    self.grid[r][c].given_value = val

    def get_cell(self, row: int, col: int) -> Cell:
        return self.grid[row][col]

    def get_cage_for_cell(self, row: int, col: int) -> Optional[Cage]:
        for cage in self.cages:
            if (row, col) in cage.cells:
                return cage
        return None
