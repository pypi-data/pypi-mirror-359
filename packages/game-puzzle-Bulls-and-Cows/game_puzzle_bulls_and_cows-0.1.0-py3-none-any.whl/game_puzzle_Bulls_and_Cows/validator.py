import logging

logger = logging.getLogger(__name__)

# Function to validate input for Bulls and Cows
def validate_bulls_and_cows_input(input_str: str) -> bool:
    # Check if the string is empty
    if len(input_str) == 0:
        logger.error("The string is empty")
        return False

    # Check if all characters in the string are unique
    if len(input_str) != len(set(input_str)):
        logger.error("There are duplicate characters")
        return False

    # Check if all characters are digits
    if not input_str.isdigit():
        logger.error("Not all characters are digits")
        return False

    # Check if the first character is '0'
    if input_str[0] == '0':
        logger.error("The first character is 0")
        return False

    # If all checks pass, return True
    return True
