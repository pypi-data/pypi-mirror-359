from typing import Literal, Optional, Tuple, Union

import pytest

from cotyper.type_system.extract_types import (
    get_choices_from_literal,
    get_flexible_tuple_size,
    get_flexible_tuple_types,
    get_key_value_type_from_dict,
    get_list_value_type,
    get_tuple_size,
    get_tuple_types,
    get_union_types,
)


@pytest.mark.parametrize(
    "typ,expected",
    [
        (Literal["foo", "bar"], {"foo", "bar"}),
        (Literal[1, 2, 3], {1, 2, 3}),
        (Optional[Literal["foo", "bar"]], {"foo", "bar"}),
    ],
)
def test_get_choices_from_literal(typ, expected):
    assert get_choices_from_literal(typ) == expected


@pytest.mark.parametrize(
    "typ,expected",
    [
        (dict[int, str], (int, str)),
        (Optional[dict[int, str]], (int, str)),
        (dict[str, float], (str, float)),
        (Optional[dict[str, float]], (str, float)),
    ],
)
def test_get_key_value_type_from_dict(typ, expected):
    assert get_key_value_type_from_dict(typ) == expected


@pytest.mark.parametrize(
    "typ,expected",
    [
        (list[int], int),
        (Optional[list[int]], int),
        (list[str], str),
        (Optional[list[str]], str),
    ],
)
def test_get_list_value_type(typ, expected):
    assert get_list_value_type(typ) == expected


@pytest.mark.parametrize(
    "typ,expected",
    [
        (Optional[Union[int, str]], (int, str)),
        (Union[int, str], (int, str)),
        (Optional[Union[float, str]], (float, str)),
        (Union[float, str], (float, str)),
    ],
)
def test_get_union_types(typ, expected):
    assert get_union_types(typ) == expected


@pytest.mark.parametrize(
    "typ,expected",
    [
        (tuple[int, str], (int, str)),
        (Optional[tuple[int, str]], (int, str)),
        (tuple[float, str], (float, str)),
        (Optional[tuple[float, str]], (float, str)),
    ],
)
def test_get_tuple_types(typ, expected):
    assert get_tuple_types(typ) == expected


@pytest.mark.parametrize(
    "typ,expected",
    [
        (Union[Tuple[int, int], int], int),
        (Optional[Union[Tuple[int, int], int]], int),
        (Union[Tuple[float, float], float], float),
        (Optional[Union[Tuple[float, float], float]], float),
    ],
)
def test_get_flexible_tuple_types(typ, expected):
    assert get_flexible_tuple_types(typ) == expected


@pytest.mark.parametrize(
    "typ,expected",
    [
        (tuple[int, str], 2),
        (Optional[tuple[int, str]], 2),
        (tuple[float, str], 2),
        (Optional[tuple[float, str]], 2),
        (tuple[int, int, int], 3),
        (Optional[tuple[int, int, int]], 3),
    ],
)
def test_get_tuple_size(typ, expected):
    assert get_tuple_size(typ) == expected


@pytest.mark.parametrize(
    "typ,expected",
    [
        (tuple[int, str], 2),
        (Optional[tuple[int, str]], 2),
        (tuple[float, str], 2),
        (Optional[tuple[float, str]], 2),
        (tuple[int, int, int], 3),
        (Optional[tuple[int, int, int]], 3),
        (Union[Tuple[int, int], int], 2),
        (Optional[Union[Tuple[int, int], int]], 2),
        (Union[Tuple[float, float], float], 2),
        (Optional[Union[Tuple[float, float], float]], 2),
        (Union[Tuple[int, int, int], int], 3),
        (Optional[Union[Tuple[int, int, int], int]], 3),
    ],
)
def test_get_flexible_tuple_size(typ, expected):
    assert get_flexible_tuple_size(typ) == expected
