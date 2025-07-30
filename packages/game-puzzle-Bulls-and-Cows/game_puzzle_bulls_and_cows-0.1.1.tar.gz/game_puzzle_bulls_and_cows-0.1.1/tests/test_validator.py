import unittest
from game_puzzle_Bulls_and_Cows import validate_bulls_and_cows_input

class TestBullsAndCowsValidator(unittest.TestCase):
    def test_valid_input(self):
        self.assertTrue(validate_bulls_and_cows_input("1234"))

    def test_empty_string(self):
        self.assertFalse(validate_bulls_and_cows_input(""))

    def test_duplicate_digits(self):
        self.assertFalse(validate_bulls_and_cows_input("1123"))

    def test_non_digit_characters(self):
        self.assertFalse(validate_bulls_and_cows_input("12a4"))

    def test_starts_with_zero(self):
        self.assertFalse(validate_bulls_and_cows_input("0123"))

    def test_long_valid_input(self):
        self.assertTrue(validate_bulls_and_cows_input("9876543210"))

    def test_too_short(self):
        self.assertTrue(validate_bulls_and_cows_input("1"))  # One digit is valid

    def test_all_same_digits(self):
        self.assertFalse(validate_bulls_and_cows_input("9999"))

if __name__ == '__main__':
    unittest.main()
