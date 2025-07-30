import pytest

from cotyper.utils.dictionary import flatten_dict_by_keys


@pytest.mark.parametrize(
    "input_dict,expected",
    [
        ({}, {}),
        ({"a": 1}, {"a": 1}),
        ({"a": 1, "b": 2}, {"a": 1, "b": 2}),
        ({"a": {"b": 1}}, {"a/b": 1}),
        ({"a": {"b": 1}, "c": 2}, {"a/b": 1, "c": 2}),
        ({"x": {"y": {"z": 1}}}, {"x/y": {"z": 1}}),  # Only flattens 1 level by default
    ],
)
def test_flatten_dict_basic(input_dict, expected):
    result = flatten_dict_by_keys(input_dict)
    assert result == expected


# Test with different separators
@pytest.mark.parametrize(
    "input_dict,separator,expected",
    [
        ({"a": {"b": 1}}, ".", {"a.b": 1}),
        ({"a": {"b": 1}}, "_", {"a_b": 1}),
        ({"a": {"b": 1}}, "-", {"a-b": 1}),
        ({"a": {"b": 1}}, "", {"ab": 1}),
        ({"a": {"b": 1}}, "->", {"a->b": 1}),
        (
            {"user": {"profile": {"name": "John"}}},
            "::",
            {"user::profile": {"name": "John"}},
        ),
    ],
)
def test_flatten_dict_custom_separator(input_dict, separator, expected):
    result = flatten_dict_by_keys(input_dict, cat_key=separator)
    assert result == expected


# Test with different levels
@pytest.mark.parametrize(
    "input_dict,level,expected",
    [
        ({"a": {"b": {"c": 1}}}, 0, {"a": {"b": {"c": 1}}}),  # No flattening
        ({"a": {"b": {"c": 1}}}, 1, {"a/b": {"c": 1}}),  # 1 level
        ({"a": {"b": {"c": 1}}}, 2, {"a/b/c": 1}),  # 2 levels
        ({"a": {"b": {"c": 1}}}, 3, {"a/b/c": 1}),  # More levels than needed
        ({"a": {"b": {"c": {"d": 1}}}}, 2, {"a/b/c": {"d": 1}}),  # Stop at level 2
    ],
)
def test_flatten_dict_different_levels(input_dict, level, expected):
    result = flatten_dict_by_keys(input_dict, level=level)
    assert result == expected


# Test complex nested structures
def test_flatten_dict_complex_structure():
    input_dict = {
        "user": {
            "profile": {"name": "John", "age": 30},
            "settings": {"theme": "dark", "notifications": True},
        },
        "app": {"version": "1.0.0"},
        "simple_key": "simple_value",
    }

    expected = {
        "user/profile": {"name": "John", "age": 30},
        "user/settings": {"theme": "dark", "notifications": True},
        "app/version": "1.0.0",
        "simple_key": "simple_value",
    }

    result = flatten_dict_by_keys(input_dict)
    assert result == expected


def test_flatten_dict_deep_nesting_with_level_2():
    input_dict = {"a": {"b": {"c": {"d": 1, "e": 2}, "f": 3}, "g": 4}, "h": 5}

    expected = {"a/b/c": {"d": 1, "e": 2}, "a/b/f": 3, "a/g": 4, "h": 5}

    result = flatten_dict_by_keys(input_dict, level=2)
    assert result == expected


# Test mixed data types
@pytest.mark.parametrize(
    "input_dict,expected",
    [
        ({"a": {"b": None}}, {"a/b": None}),
        ({"a": {"b": [1, 2, 3]}}, {"a/b": [1, 2, 3]}),
        ({"a": {"b": True}}, {"a/b": True}),
        ({"a": {"b": 3.14}}, {"a/b": 3.14}),
        (
            {"a": {"b": {"nested": "dict"}, "c": [1, 2]}},
            {"a/b": {"nested": "dict"}, "a/c": [1, 2]},
        ),
    ],
)
def test_flatten_dict_mixed_types(input_dict, expected):
    result = flatten_dict_by_keys(input_dict)
    assert result == expected


# Test edge cases with keys
def test_flatten_dict_special_key_names():
    input_dict = {
        "": {"value": 1},  # Empty key
        "key with spaces": {"nested": 2},
        "key/with/slashes": {"data": 3},
        "123": {"numeric_key": 4},
    }

    expected = {
        "/value": 1,
        "key with spaces/nested": 2,
        "key/with/slashes/data": 3,
        "123/numeric_key": 4,
    }

    result = flatten_dict_by_keys(input_dict)
    assert result == expected


# Test with custom separator and special keys
def test_flatten_dict_separator_conflicts():
    input_dict = {
        "a.b": {"c": 1},  # Key contains the separator
        "x": {"y.z": 2},  # Nested key contains separator
    }

    expected_dot = {"a.b.c": 1, "x.y.z": 2}

    expected_slash = {"a.b/c": 1, "x/y.z": 2}

    result_dot = flatten_dict_by_keys(input_dict, cat_key=".")
    result_slash = flatten_dict_by_keys(input_dict, cat_key="/")

    assert result_dot == expected_dot
    assert result_slash == expected_slash


# Test level 0 (no flattening)
def test_flatten_dict_level_zero():
    input_dict = {"a": {"b": {"c": 1}}, "x": {"y": 2}, "simple": 3}

    result = flatten_dict_by_keys(input_dict, level=0)
    assert result == input_dict


# Test very deep nesting with high level
def test_flatten_dict_very_deep():
    input_dict = {
        "level1": {"level2": {"level3": {"level4": {"level5": "deep_value"}}}}
    }

    result_level_4 = flatten_dict_by_keys(input_dict, level=4)
    expected_level_4 = {"level1/level2/level3/level4/level5": "deep_value"}

    assert result_level_4 == expected_level_4


# Test with non-dict values that might look like dicts
def test_flatten_dict_non_dict_objects():
    class FakeDict:
        def __init__(self):
            self.items = lambda: [("key", "value")]

    input_dict = {
        "a": {"b": 1},
        "fake": FakeDict(),  # Not actually a dict
        "list": [{"not": "flattened"}],  # List containing dict
        "string": "not_a_dict",
    }

    expected = {
        "a/b": 1,
        "fake": input_dict["fake"],  # Should remain as-is
        "list": [{"not": "flattened"}],  # Should remain as-is
        "string": "not_a_dict",
    }

    result = flatten_dict_by_keys(input_dict)
    assert result == expected


# Test combination of parameters
@pytest.mark.parametrize(
    "separator,level",
    [
        (".", 1),
        ("_", 2),
        ("::", 3),
        ("->", 1),
    ],
)
def test_flatten_dict_parameter_combinations(separator, level):
    input_dict = {"a": {"b": {"c": {"d": 1}}}}

    result = flatten_dict_by_keys(input_dict, cat_key=separator, level=level)

    # Verify the result uses the correct separator and respects the level
    assert isinstance(result, dict)
    if level >= 1:
        assert any(separator in key for key in result.keys())

    # For level 1, should have exactly one separator per key (for keys that were flattened)
    if level == 1:
        for key in result.keys():
            if separator in key:
                assert key.count(separator) == 1


# Test immutability (original dict shouldn't be modified)
def test_flatten_dict_immutability():
    original = {"a": {"b": 1}, "c": {"d": {"e": 2}}}
    original_copy = {"a": {"b": 1}, "c": {"d": {"e": 2}}}

    flatten_dict_by_keys(original, level=2)

    # Original should be unchanged
    assert original == original_copy
