import unittest
from src.models import Puzzle, Cage
from src.validator import SudokuValidator


class TestValidator(unittest.TestCase):
    def test_row_col_box_validation(self):
        puzzle = Puzzle("Test", size=9, box_size=3)
        puzzle.get_cell(0, 0).player_value = 5
        puzzle.get_cell(0, 5).player_value = 5  # Row duplicate

        res = SudokuValidator.validate_puzzle(puzzle)
        self.assertIn((0, 0), res.invalid_cells)
        self.assertIn((0, 5), res.invalid_cells)

    def test_cage_validation(self):
        # Cage sum 10 with 2 cells
        cage = Cage(10, [(0, 0), (0, 1)])
        puzzle = Puzzle("Test", size=9, box_size=3, cages=[cage])

        # Partial valid
        puzzle.get_cell(0, 0).player_value = 4
        res = SudokuValidator.validate_puzzle(puzzle)
        self.assertEqual(res.cage_statuses[cage], "INCOMPLETE_VALID")

        # Partial invalid (4 + 8 = 12 > 10)
        puzzle.get_cell(0, 1).player_value = 8
        res = SudokuValidator.validate_puzzle(puzzle)
        self.assertEqual(res.cage_statuses[cage], "INVALID")

        # Complete valid (4 + 6 = 10)
        puzzle.get_cell(0, 1).player_value = 6
        res = SudokuValidator.validate_puzzle(puzzle)
        self.assertEqual(res.cage_statuses[cage], "CORRECT")

    def test_cage_impossible_remaining_sum(self):
        # Cage sum 5 with 3 cells: 1+2+3=6 > 5 (Impossible)
        cage = Cage(5, [(0, 0), (0, 1), (0, 2)])
        puzzle = Puzzle("Test", size=9, box_size=3, cages=[cage])
        puzzle.get_cell(0, 0).player_value = 4  # Remaining sum 1 with 2 cells needed -> impossible!

        res = SudokuValidator.validate_puzzle(puzzle)
        self.assertEqual(res.cage_statuses[cage], "INVALID")


if __name__ == "__main__":
    unittest.main()
