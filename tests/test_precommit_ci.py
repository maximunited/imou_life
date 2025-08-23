# Test file for pre-commit.ci demonstration
# This file contains intentional style issues that should be caught by pre-commit hooks


def test_function_with_very_long_line_that_exceeds_flake8_max_line_length():
    """This function has a very long line that should trigger flake8."""
    return (
        "this line is intentionally too long to test pre-commit hooks "
        "and should be caught by the linter"
    )


def test_function_with_trailing_whitespace():
    """This function has trailing whitespace that should be caught."""
    return "test"


def test_function_with_missing_spaces():
    """This function is missing spaces around operators."""
    x = 1 + 2
    return x


# This line has no newline at the end
