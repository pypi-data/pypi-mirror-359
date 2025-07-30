from typing import Any, Dict, List, Literal, Optional, Tuple, Union

import typer
from pydantic import BaseModel
from rich import print

from cotyper import App, parse_json_fields, unfold_cls
from cotyper.type_system.custom_click_types import (
    FlexibleTupleParamType,
)

app = App()


class Bar(BaseModel):
    baz: str
    foobar: bool = True


class Foo(BaseModel):
    bar: Bar


class Config(BaseModel):
    list_basic_type_str: list[str]
    list_basic_type_int: list[int]
    list_basic_type_float: list[float]

    tuple_basic_type_float: tuple[float, float]
    tuple_basic_type_int: tuple[int, int, int]
    tuple_basic_type_str: tuple[str, str, str]

    tuple_union_type: Union[tuple[float, float], float]

    literal_str: Literal["foo", "bar"]
    literal_int: Literal[1, 2, 3]

    dict_type: Dict[int, str]

    # optional fields
    optional_list_basic_type_str: Optional[list[str]] = None
    optional_list_basic_type_int: Optional[list[int]] = None
    optional_list_basic_type_float: Optional[list[float]] = None

    optional_tuple_basic_type_float: Optional[tuple[float, float]] = None
    optional_tuple_basic_type_int: Optional[tuple[int, int, int]] = None
    optional_tuple_basic_type_str: Optional[tuple[str, str, str]] = None

    optional_tuple_union_type: Optional[Union[tuple[float, float], float]] = None

    optional_literal_str: Optional[Literal["foo", "bar"]] = None
    optional_literal_int: Optional[Literal[1, 2, 3]] = None

    optional_dict_type: Optional[Dict[int, str]] = None


@app.struct_command("struct")
def some_struct_command(config: Config):
    """
    Example command that accepts a structured configuration object.
    """
    print(config)


@app.struct_command("unstruct")
@unfold_cls(Config)
def some_unstruct_command(config: Config):
    """
    Example command that accepts a structured configuration object.
    """
    print(config)


@app.struct_command("nested")
def nested_command(foo: Foo):
    """
    Example command that accepts a nested structured configuration object.
    """
    print(foo)


class UnionConfig(BaseModel):
    foo: Union[Tuple[int, int], int]
    bar: float


@app.struct_command("union")
@unfold_cls(UnionConfig)
def union_command(config: UnionConfig):
    print(config)


# @app.command("simple_union")
def simple_union_command(
    u: Any = typer.Option(..., "-u", parser=FlexibleTupleParamType(int, 2)),
):
    print(u)


class ListConfig(BaseModel):
    foo: List[int]


@app.struct_command("list")
def list_command(config: ListConfig):
    print(config)


class TupleConfig(BaseModel):
    foo: Tuple[int, int]


@app.struct_command("tuple")
def tuple_command(config: TupleConfig):
    print(config)


@parse_json_fields("bars", Bar)
class DictConfig(BaseModel):
    bars: List[Bar]


@app.struct_command("dict-model")
def dict_model_command(config: DictConfig):
    """
    Example command that accepts a structured configuration object with a list of Bar models.
    """
    print(config)


class OptionalDictConfig(BaseModel):
    optional_bars: Optional[Dict[str, str]] = None


@app.struct_command("optional-dict")
def optional_dict_command(config: OptionalDictConfig):
    """
    Example command that accepts a structured configuration object with an optional dictionary.
    """
    print(config)


if __name__ == "__main__":
    app()
