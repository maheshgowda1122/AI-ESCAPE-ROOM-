import unittest
from game_logic import initial_state, process_action

class Version2GameTests(unittest.TestCase):
    def setUp(self):
        self.state = initial_state("Test Player")

    def solve_first_puzzle(self):
        process_action(self.state, "examine the painting")
        process_action(self.state, "inspect the key table")
        return process_action(self.state, "I think the answer is blue")

    def solve_second_puzzle(self):
        process_action(self.state, "inspect the bookshelf")
        return process_action(self.state, "The numbers spell CAT")

    def test_wrong_key_does_not_award_inventory(self):
        process_action(self.state, "examine painting")
        process_action(self.state, "inspect key table")
        process_action(self.state, "I choose red")
        self.assertFalse(self.state["puzzles"]["coloured_key"])
        self.assertNotIn("blue_key", self.state["inventory"])

    def test_cannot_open_drawer_without_key_and_cipher(self):
        result = process_action(self.state, "open the drawer")
        self.assertFalse(self.state["drawer_open"])
        self.assertIn("locked", result.lower())

    def test_cannot_use_uncollected_key(self):
        result = process_action(self.state, "use the blue key")
        self.assertNotIn("blue_key", self.state["inventory"])
        self.assertIn("cannot use", result.lower())

    def test_correct_key_and_cipher_open_drawer(self):
        self.solve_first_puzzle()
        self.solve_second_puzzle()
        result = process_action(self.state, "open the drawer")
        self.assertTrue(self.state["drawer_open"])
        self.assertIn("Inside is a note", result)

    def test_cannot_escape_before_all_puzzles(self):
        result = process_action(self.state, "unlock the exit door")
        self.assertFalse(self.state["escaped"])
        self.assertIn("remains sealed", result.lower())

if __name__ == "__main__":
    unittest.main()
