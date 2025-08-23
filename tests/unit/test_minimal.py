"""Minimal test to diagnose CI issues."""


def test_basic_functionality():
    """Basic test that should always pass."""
    assert True


def test_simple_math():
    """Simple math test."""
    assert 2 + 2 == 4


def test_string_operations():
    """String operations test."""
    assert "hello" + " " + "world" == "hello world"


def test_list_operations():
    """List operations test."""
    test_list = [1, 2, 3]
    test_list.append(4)
    assert len(test_list) == 4
    assert test_list == [1, 2, 3, 4]


def test_dict_operations():
    """Dictionary operations test."""
    test_dict = {"key1": "value1"}
    test_dict["key2"] = "value2"
    assert len(test_dict) == 2
    assert test_dict["key1"] == "value1"
    assert test_dict["key2"] == "value2"


if __name__ == "__main__":
    # Allow running directly
    test_basic_functionality()
    test_simple_math()
    test_string_operations()
    test_list_operations()
    test_dict_operations()
    print("All minimal tests passed!")
