from dataclasses import dataclass
from typing import Dict, List, Literal, Optional, Tuple, Union

import pytest
from pydantic import BaseModel

from cotyper.type_system.type_checking import (
    is_base_model_subclass,
    is_dict,
    is_list,
    is_list_basic_type,
    is_literal,
    is_optional_base_model_subclass,
    is_optional_dict,
    is_optional_list,
    is_optional_list_basic_types,
    is_optional_literal,
    is_optional_tuple,
    is_optional_tuple_union,
    is_tuple,
    is_tuple_union,
    is_union,
)


@pytest.mark.parametrize(
    "typ,expected",
    [
        (list, True),
        (tuple, False),
        (int, False),
        (str, False),
        (dict, False),
        (set, False),
        (List[int], True),
        (List[str], True),
        (Union[List[int], str], False),
        (Optional[List[int]], False),
        (Union[int, str], False),
    ],
)
def test_is_list(typ, expected):
    assert is_list(typ) is expected


@pytest.mark.parametrize(
    "typ,expected",
    [
        (Optional[List[int]], True),
        (Optional[List[str]], True),
        (Union[Optional[List[int]], str], False),
        (Union[int, str], False),
        (Union[Optional[List[int]], Optional[List[str]]], False),
        (Union[List[int], Optional[List[str]]], False),
        (Union[Optional[List[int]], List[str]], False),
    ],
)
def test_is_optional_list(typ, expected):
    assert is_optional_list(typ) is expected


@pytest.mark.parametrize(
    "typ,expected",
    [
        (List[int], True),
        (List[str], True),
        (List[float], True),
        (List[Union[int, str]], False),
        (List[bool], False),
    ],
)
def test_is_list_basic_type_builtin(typ, expected):
    assert is_list_basic_type(typ) is expected


def test_is_list_basic_type_custom():
    @dataclass
    class CustomType:
        pass

    assert is_list_basic_type(List[CustomType]) is False


@pytest.mark.parametrize(
    "typ,expected",
    [
        (Optional[List[int]], True),
        (Optional[List[str]], True),
        (Optional[List[float]], True),
        (Optional[List[Union[int, str]]], False),
        (Optional[List[bool]], False),
    ],
)
def test_is_optional_list_basic_type_builtin(typ, expected):
    assert is_optional_list_basic_types(typ) is expected


def test_is_optional_list_basic_type_custom():
    @dataclass
    class CustomType:
        pass

    assert is_optional_list_basic_types(Optional[List[CustomType]]) is False


class Foo(BaseModel):
    pass


@pytest.mark.parametrize(
    "typ,expected",
    [
        (Foo, True),
        (BaseModel, True),
        (list, False),
        (int, False),
        (str, False),
        (Union[Foo, int], False),
        (Optional[Foo], False),
        (List[Foo], False),
        (List[int], False),
    ],
)
def test_is_base_model_subclass(typ, expected):
    assert is_base_model_subclass(typ) is expected


@pytest.mark.parametrize(
    "typ,expected",
    [
        (Optional[Foo], True),
        (Optional[BaseModel], True),
        (Optional[list], False),
        (Optional[int], False),
        (Optional[str], False),
        (Optional[Union[Foo, int]], False),
        (Optional[List[Foo]], False),
        (Optional[List[int]], False),
    ],
)
def test_is_optional_base_model_subclass(typ, expected):
    assert is_optional_base_model_subclass(typ) is expected


@pytest.mark.parametrize(
    "typ,expected",
    [
        (Union[int, str], True),
        (Union[int, None], False),
        (Optional[int], False),
        (Union[str, float, bool], True),
        (int, False),
    ],
)
def test_is_union(typ, expected):
    assert is_union(typ) is expected


@pytest.mark.parametrize(
    "typ,expected",
    [
        (Tuple[int, str], True),
        (Tuple[()], False),  # empty Tuple
        (Tuple, False),  # raw Tuple type
        (tuple, False),
        (List[Tuple[int, str]], False),
    ],
)
def test_is_tuple(typ, expected):
    assert is_tuple(typ) is expected


@pytest.mark.parametrize(
    "typ,expected",
    [
        (Optional[Tuple[int, str]], True),
        (Union[Tuple[int], None], True),
        (Union[int, Tuple[int]], False),
        (Union[Tuple[int], str, None], False),
        (Tuple[int, str], False),
    ],
)
def test_is_optional_tuple(typ, expected):
    assert is_optional_tuple(typ) is expected


@pytest.mark.parametrize(
    "typ,expected",
    [
        (Union[Tuple[int], Tuple[str]], True),
        (Union[Tuple[int], int], True),
        (Union[str, int], False),
        (Tuple[int], False),
    ],
)
def test_is_tuple_union(typ, expected):
    assert is_tuple_union(typ) is expected


@pytest.mark.parametrize(
    "typ,expected",
    [
        (Optional[Union[Tuple[int], Tuple[str]]], True),
        (Optional[Union[Tuple[int], int]], True),
        (Optional[Union[int, str]], False),
        (Union[Tuple[int], Tuple[str]], False),  # not optional
        (Tuple[int], False),
    ],
)
def test_is_optional_tuple_union(typ, expected):
    assert is_optional_tuple_union(typ) is expected


@pytest.mark.parametrize(
    "typ,expected",
    [
        (int, False),
        (str, False),
        (Literal[1, 2, 3], True),
        (Literal["foo", "bar"], True),
        (Literal[1.0, 2.0], True),
        (Optional[Literal[1, 2, 3]], False),
        (List[Literal[1, 2, 3]], False),
    ],
)
def test_is_literal(typ, expected):
    assert is_literal(typ) is expected


@pytest.mark.parametrize(
    "typ,expected",
    [
        (Optional[Literal[1, 2, 3]], True),
        (Optional[Literal["foo", "bar"]], True),
        (Optional[Literal[1.0, 2.0]], True),
        (Optional[int], False),
        (Literal[1, 2, 3], False),
        (List[Optional[Literal[1, 2, 3]]], False),
        (float, False),
    ],
)
def test_is_optional_literal(typ, expected):
    assert is_optional_literal(typ) is expected


@pytest.mark.parametrize(
    "typ,expected",
    [
        (dict, False),
        (Dict[int, str], True),
        (Dict[str, int], True),
        (Dict[str, str], True),
        (Dict[int, int], True),
        (Dict[str, List[int]], True),
        (Dict[str, Optional[int]], True),
        (Dict[str, Union[int, str]], True),
        (List[Dict[str, int]], False),
        (Optional[Dict[str, int]], False),
    ],
)
def test_is_dict(typ, expected):
    assert is_dict(typ) is expected


@pytest.mark.parametrize(
    "typ,expected",
    [
        (Optional[dict], False),
        (Optional[Dict[int, str]], True),
        (Optional[Dict[str, int]], True),
        (Optional[Dict[str, str]], True),
        (Optional[Dict[int, int]], True),
        (Optional[Dict[str, List[int]]], True),
        (Optional[Dict[str, Optional[int]]], True),
        (Optional[Dict[str, Union[int, str]]], True),
        (List[Optional[Dict[str, int]]], False),
        (List[str], False),
        (float, False),
    ],
)
def test_is_optional_dict(typ, expected):
    assert is_optional_dict(typ) is expected
