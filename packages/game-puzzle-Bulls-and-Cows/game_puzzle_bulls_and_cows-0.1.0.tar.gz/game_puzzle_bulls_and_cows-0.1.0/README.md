# game_puzzle_Bulls_and_Cows

A simple Python package for validating input strings in the "Bulls and Cows" puzzle game with GitHub Actions.

## Installation

```bash
pip install game_puzzle_Bulls_and_Cows
```

## Usage

```python
from game_puzzle_Bulls_and_Cows import validate_bulls_and_cows_input

print(validate_bulls_and_cows_input("1234"))  # True
```

## Validation Rules

- Input must not be empty
- All characters must be digits
- All digits must be unique
- The first digit must not be '0'

## License

MIT
