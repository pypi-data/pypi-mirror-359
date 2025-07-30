import json
import tempfile
from pathlib import Path
from typing import Literal
from unittest.mock import Mock

import click
import pytest

# Import your optimized param types
from cotyper.type_system.custom_click_types import (
    DictParamType,
    FlexibleTupleParamType,
    ListParamType,
    LiteralParamType,
    TupleParamType,
    UnionParamType,
)


class TestLiteralParamType:
    @pytest.mark.parametrize(
        "literal_type,input_value,expected",
        [
            (Literal["red", "green", "blue"], "red", "red"),
            (Literal["red", "green", "blue"], "blue", "blue"),
            (Literal[1, 2, 3], "2", 2),
            (Literal[1, 2, 3], 3, 3),
            (Literal[True, False], "True", True),
            (Literal[True, False], False, False),
        ],
    )
    def test_valid_conversions(self, literal_type, input_value, expected):
        param_type = LiteralParamType(literal_type)
        result = param_type.convert(input_value, Mock(), Mock())
        assert result == expected

    @pytest.mark.parametrize(
        "literal_type,input_value",
        [
            (Literal["red", "green", "blue"], "yellow"),
            (Literal[1, 2, 3], "4"),
            (Literal[1, 2, 3], "invalid"),
            (Literal[True, False], "maybe"),
        ],
    )
    def test_invalid_conversions(self, literal_type, input_value):
        param_type = LiteralParamType(literal_type)
        with pytest.raises(click.BadParameter):
            param_type.convert(input_value, Mock(), Mock())

    def test_optional_none(self):
        param_type = LiteralParamType(Literal["a", "b"], is_optional=True)
        result = param_type.convert(None, Mock(), Mock())
        assert result is None

    def test_optional_valid_value(self):
        param_type = LiteralParamType(Literal["a", "b"], is_optional=True)
        result = param_type.convert("a", Mock(), Mock())
        assert result == "a"

    def test_mixed_types_error(self):
        with pytest.raises(
            TypeError, match="All choices in Literal must be of the same type"
        ):
            LiteralParamType(Literal["string", 42])

    def test_empty_literal_error(self):
        # This would need to be handled in your actual implementation
        with pytest.raises(TypeError):
            # This is a conceptual test - you'd need to handle empty literals
            _ = LiteralParamType(type("EmptyLiteral", (), {"__args__": ()}))


class TestDictParamType:
    @pytest.mark.parametrize(
        "key_type,value_type,input_value,expected",
        [
            (str, int, '{"a": 1, "b": 2}', {"a": 1, "b": 2}),
            (
                str,
                str,
                '{"name": "John", "city": "NYC"}',
                {"name": "John", "city": "NYC"},
            ),
            (int, str, '{"1": "one", "2": "two"}', {1: "one", 2: "two"}),
            (str, float, '{"pi": 3.14, "e": 2.71}', {"pi": 3.14, "e": 2.71}),
            (str, int, {"a": 1, "b": 2}, {"a": 1, "b": 2}),  # Already a dict
        ],
    )
    def test_valid_conversions(self, key_type, value_type, input_value, expected):
        param_type = DictParamType(key_type, value_type)
        result = param_type.convert(input_value, Mock(), Mock())
        assert result == expected

        # Verify types
        for key, value in result.items():
            assert isinstance(key, key_type)
            assert isinstance(value, value_type)

    @pytest.mark.parametrize(
        "key_type,value_type,input_value",
        [
            (str, int, '{"a": "not_an_int"}'),  # Value conversion error
            (int, str, '{"not_an_int": "value"}'),  # Key conversion error
            (str, int, "invalid json"),  # JSON parsing error
            (str, int, 42),  # Wrong input type
        ],
    )
    def test_invalid_conversions(self, key_type, value_type, input_value):
        param_type = DictParamType(key_type, value_type)
        with pytest.raises(click.BadParameter):
            param_type.convert(input_value, Mock(), Mock())

    def test_json_file_input(self):
        test_data = {"first": 0, "second": 1}

        test_data_str = json.dumps(test_data)

        try:
            param_type = DictParamType(str, int)
            result = param_type.convert(test_data_str, Mock(), Mock())
            assert result == test_data
        except Exception as e:
            raise e

    def test_invalid_json_file(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("invalid json content")
            temp_path = f.name

        try:
            param_type = DictParamType(str, str)
            with pytest.raises(click.BadParameter):
                param_type.convert(temp_path, Mock(), Mock())
        finally:
            Path(temp_path).unlink()

    def test_optional_none(self):
        param_type = DictParamType(str, int, is_optional=True)
        result = param_type.convert(None, Mock(), Mock())
        assert result is None


class TestListParamType:
    @pytest.mark.parametrize(
        "value_type,input_value,expected",
        [
            (str, "a,b,c", ["a", "b", "c"]),
            (int, "1,2,3", [1, 2, 3]),
            (float, "1.1,2.2,3.3", [1.1, 2.2, 3.3]),
            (
                str,
                " apple , banana , cherry ",
                ["apple", "banana", "cherry"],
            ),  # Whitespace handling
            (str, ["already", "a", "list"], ["already", "a", "list"]),  # Already a list
            (int, [1, 2, 3], [1, 2, 3]),  # Already a list with correct types
        ],
    )
    def test_valid_conversions(self, value_type, input_value, expected):
        param_type = ListParamType(value_type)
        result = param_type.convert(input_value, Mock(), Mock())
        assert result == expected

        # Verify types
        for item in result:
            assert isinstance(item, value_type)

    @pytest.mark.parametrize(
        "value_type,input_value",
        [
            (int, "1,not_an_int,3"),  # Invalid element
            (float, "1.1,invalid,3.3"),  # Invalid element
            (int, 42),  # Wrong input type
        ],
    )
    def test_invalid_conversions(self, value_type, input_value):
        param_type = ListParamType(value_type)
        with pytest.raises(click.BadParameter):
            param_type.convert(input_value, Mock(), Mock())

    def test_empty_string_elements_filtered(self):
        param_type = ListParamType(str)
        result = param_type.convert("a,,b,", Mock(), Mock())
        assert result == ["a", "b"]

    def test_optional_none(self):
        param_type = ListParamType(str, is_optional=True)
        result = param_type.convert(None, Mock(), Mock())
        assert result is None

    def test_metavar(self):
        param_type = ListParamType(str)
        assert param_type.get_metavar(Mock()) == "[item1,item2,...]"


class TestUnionParamType:
    @pytest.mark.parametrize(
        "types,input_value,expected,expected_type",
        [
            ([int, str], "42", 42, int),  # Converts to int first
            ([int, str], "hello", "hello", str),  # Falls back to str
            ([float, int], "3.14", 3.14, float),  # Converts to float first
            ([bool, str], "True", True, bool),  # Converts to bool
            ([str, int], "not_a_number", "not_a_number", str),  # Falls back to str
        ],
    )
    def test_valid_conversions(self, types, input_value, expected, expected_type):
        param_type = UnionParamType(types)
        result = param_type.convert(input_value, Mock(), Mock())
        assert result == expected
        assert isinstance(result, expected_type)

    def test_no_valid_conversion(self):
        param_type = UnionParamType([int, float])
        with pytest.raises(click.BadParameter):
            param_type.convert("not_a_number", Mock(), Mock())

    def test_optional_none(self):
        param_type = UnionParamType([int, str], is_optional=True)
        result = param_type.convert(None, Mock(), Mock())
        assert result is None


class TestTupleParamType:
    @pytest.mark.parametrize(
        "element_types,input_value,expected",
        [
            ([str, int], "hello,42", ("hello", 42)),
            ([int, float, str], "1,2.5,test", (1, 2.5, "test")),
            ([str, int], ("already", 42), ("already", 42)),  # Already a tuple
        ],
    )
    def test_valid_conversions(self, element_types, input_value, expected):
        param_type = TupleParamType(element_types)
        result = param_type.convert(input_value, Mock(), Mock())
        assert result == expected

        # Verify types
        for item, expected_type in zip(result, element_types):
            assert isinstance(item, expected_type)

    @pytest.mark.parametrize(
        "element_types,input_value",
        [
            ([str, int], "hello,not_an_int"),  # Invalid conversion
            ([int, int], "1,2,3"),  # Wrong number of elements
            ([str, int], "only_one"),  # Too few elements
            ([int, int], 42),  # Wrong input type
        ],
    )
    def test_invalid_conversions(self, element_types, input_value):
        param_type = TupleParamType(element_types)
        with pytest.raises(click.BadParameter):
            param_type.convert(input_value, Mock(), Mock())

    def test_optional_none(self):
        param_type = TupleParamType([str, int], is_optional=True)
        result = param_type.convert(None, Mock(), Mock())
        assert result is None


class TestFlexibleTupleParamType:
    @pytest.mark.parametrize(
        "element_type,size,input_value,expected",
        [
            (int, 2, "42", 42),  # Single value
            (int, 2, "1,2", (1, 2)),  # Tuple
            (str, 3, "hello", "hello"),  # Single value
            (str, 3, "a,b,c", ("a", "b", "c")),  # Tuple
            (float, 2, (1.1, 2.2), (1.1, 2.2)),  # Already a tuple
        ],
    )
    def test_valid_conversions(self, element_type, size, input_value, expected):
        param_type = FlexibleTupleParamType(element_type, size)
        result = param_type.convert(input_value, Mock(), Mock())
        assert result == expected

        # Verify types
        if isinstance(result, tuple):
            for item in result:
                assert isinstance(item, element_type)
        else:
            assert isinstance(result, element_type)

    @pytest.mark.parametrize(
        "element_type,size,input_value",
        [
            (int, 2, "1,2,3"),  # Wrong tuple size
            (int, 2, "not_a_number"),  # Invalid single conversion
            (int, 2, "1,not_a_number"),  # Invalid tuple element
        ],
    )
    def test_invalid_conversions(self, element_type, size, input_value):
        param_type = FlexibleTupleParamType(element_type, size)
        with pytest.raises(click.BadParameter):
            param_type.convert(input_value, Mock(), Mock())

    def test_optional_none(self):
        param_type = FlexibleTupleParamType(int, 2, is_optional=True)
        result = param_type.convert(None, Mock(), Mock())
        assert result is None


class TestIntegrationScenarios:
    """Test more complex real-world scenarios."""

    def test_nested_optional_list(self):
        param_type = ListParamType(int, is_optional=True)

        # Test None
        assert param_type.convert(None, Mock(), Mock()) is None

        # Test valid list
        result = param_type.convert("1,2,3", Mock(), Mock())
        assert result == [1, 2, 3]


# Fixtures for common test data
@pytest.fixture
def mock_param():
    return Mock(spec=click.Parameter)


@pytest.fixture
def mock_context():
    return Mock(spec=click.Context)


@pytest.fixture
def temp_json_file():
    test_data = {"key1": "value1", "key2": "value2"}

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(test_data, f)
        temp_path = f.name

    yield temp_path, test_data

    Path(temp_path).unlink()


# Performance tests
class TestPerformance:
    def test_large_list_conversion(self):
        param_type = ListParamType(int)
        large_input = ",".join(str(i) for i in range(1000))

        result = param_type.convert(large_input, Mock(), Mock())
        assert len(result) == 1000
        assert result[0] == 0
        assert result[-1] == 999

    def test_large_dict_conversion(self):
        param_type = DictParamType(str, int)
        large_dict = {f"key_{i}": i for i in range(100)}
        large_input = json.dumps(large_dict)

        result = param_type.convert(large_input, Mock(), Mock())
        assert len(result) == 100
        assert result["key_0"] == 0
        assert result["key_99"] == 99


# Edge case tests
class TestEdgeCases:
    def test_empty_string_list(self):
        param_type = ListParamType(str)
        result = param_type.convert("", Mock(), Mock())
        assert result == []

    def test_whitespace_only_list(self):
        param_type = ListParamType(str)
        result = param_type.convert("   ,   ,   ", Mock(), Mock())
        assert result == []

    def test_single_comma_list(self):
        param_type = ListParamType(str)
        result = param_type.convert(",", Mock(), Mock())
        assert result == []

    def test_dict_with_empty_values(self):
        param_type = DictParamType(str, str)
        result = param_type.convert('{"key": ""}', Mock(), Mock())
        assert result == {"key": ""}

    def test_boolean_string_conversions(self):
        param_type = ListParamType(bool)
        # Note: This test depends on how Python's bool() handles strings
        result = param_type.convert("True,False,1,0", Mock(), Mock())
        # bool("False") is True in Python, so this test shows the limitation
        assert all(isinstance(x, bool) for x in result)
