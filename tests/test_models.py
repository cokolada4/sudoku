import unittest
from src.models import parse_coord, to_coord_str, Cell, Cage, Puzzle


class TestModels(unittest.TestCase):
    def test_coordinate_helpers(self):
        self.assertEqual(parse_coord("R1C1"), (0, 0))
        self.assertEqual(parse_coord("r9c9"), (8, 8))
        self.assertEqual(parse_coord("R5C3"), (4, 2))
        self.assertEqual(to_coord_str(0, 0), "R1C1")
        self.assertEqual(to_coord_str(8, 8), "R9C9")
        self.assertEqual(to_coord_str(4, 2), "R5C3")

        with self.assertRaises(ValueError):
            parse_coord("X1C1")
        with self.assertRaises(ValueError):
            parse_coord("R10")

    def test_cell_model(self):
        cell = Cell(0, 0)
        self.assertFalse(cell.is_given)
        self.assertIsNone(cell.value)

        cell.player_value = 5
        self.assertEqual(cell.value, 5)

        cell.toggle_note(3)
        self.assertIn(3, cell.notes)
        cell.toggle_note(3)
        self.assertNotIn(3, cell.notes)

        cell.clear()
        self.assertIsNone(cell.player_value)

        given_cell = Cell(1, 1, given_value=9)
        self.assertTrue(given_cell.is_given)
        self.assertEqual(given_cell.value, 9)
        given_cell.clear()
        self.assertEqual(given_cell.value, 9)

    def test_cage_and_puzzle_model(self):
        cage = Cage(target_sum=10, cells=[(1, 1), (0, 1)])
        self.assertEqual(cage.top_left_cell, (0, 1))

        givens = {"R1C1": 7}
        puzzle = Puzzle("Test Puzzle", size=9, box_size=3, cages=[cage], givens=givens)
        self.assertEqual(puzzle.get_cell(0, 0).value, 7)
        self.assertTrue(puzzle.get_cell(0, 0).is_given)
        self.assertEqual(puzzle.get_cage_for_cell(0, 1), cage)
        self.assertIsNone(puzzle.get_cage_for_cell(0, 0))


if __name__ == "__main__":
    unittest.main()
