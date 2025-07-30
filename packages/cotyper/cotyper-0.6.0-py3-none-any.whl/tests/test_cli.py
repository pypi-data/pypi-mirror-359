from typing import Dict, List, Literal, Optional, Tuple, Union

import pytest
import typer
from pydantic import BaseModel
from typer.testing import CliRunner

from cotyper import App, parse_json_fields, unfold_cls

app = App()
cli_runner = CliRunner()


class ListBasicTypeStrConfig(BaseModel):
    list_basic_type_str: List[str]


class ListBasicTypeIntConfig(BaseModel):
    list_basic_type_int: List[int]


class ListBasicTypeFloatConfig(BaseModel):
    list_basic_type_float: List[float]


class TupleBasicTypeFloatConfig(BaseModel):
    tuple_basic_type_float: Tuple[float, float]


class TupleBasicTypeIntConfig(BaseModel):
    tuple_basic_type_int: Tuple[int, int, int]


class TupleBasicTypeStrConfig(BaseModel):
    tuple_basic_type_str: Tuple[str, str, str]


class TupleUnionTypeConfig(BaseModel):
    tuple_union_type: Union[Tuple[float, float], float]


class LiteralStrConfig(BaseModel):
    literal_str: Literal["foo", "bar"]


class LiteralIntConfig(BaseModel):
    literal_int: Literal[1, 2, 3]


class DictTypeConfig(BaseModel):
    dict_type: Dict[int, str]


# Optional fields


class OptionalListBasicTypeStrConfig(BaseModel):
    optional_list_basic_type_str: Optional[List[str]] = None


class OptionalListBasicTypeIntConfig(BaseModel):
    optional_list_basic_type_int: Optional[List[int]] = None


class OptionalListBasicTypeFloatConfig(BaseModel):
    optional_list_basic_type_float: Optional[List[float]] = None


class OptionalTupleBasicTypeFloatConfig(BaseModel):
    optional_tuple_basic_type_float: Optional[Tuple[float, float]] = None


class OptionalTupleBasicTypeIntConfig(BaseModel):
    optional_tuple_basic_type_int: Optional[Tuple[int, int, int]] = None


class OptionalTupleBasicTypeStrConfig(BaseModel):
    optional_tuple_basic_type_str: Optional[Tuple[str, str, str]] = None


class OptionalTupleUnionTypeConfig(BaseModel):
    optional_tuple_union_type: Optional[Union[Tuple[float, float], float]] = None


class OptionalLiteralStrConfig(BaseModel):
    optional_literal_str: Optional[Literal["foo", "bar"]] = None


class OptionalLiteralIntConfig(BaseModel):
    optional_literal_int: Optional[Literal[1, 2, 3]] = None


class OptionalDictTypeConfig(BaseModel):
    optional_dict_type: Optional[Dict[int, str]] = None


class Bar(BaseModel):
    baz: str


class Foo(BaseModel):
    bar: Bar
    foo: int


class Config(BaseModel):
    bar: Bar
    foo: int


@parse_json_fields("bars", Bar)
class DictConfig(BaseModel):
    bars: List[Bar]


# Commands


@app.struct_command(name="list_basic_type_str")
def list_basic_type_str_command(config: ListBasicTypeStrConfig):
    """
    Command that accepts a list of basic type strings.
    """
    typer.echo(config.list_basic_type_str)


@app.struct_command(name="list_basic_type_int")
def list_basic_type_int_command(config: ListBasicTypeIntConfig):
    """
    Command that accepts a list of basic type integers.
    """
    typer.echo(config.list_basic_type_int)


@app.struct_command(name="list_basic_type_float")
def list_basic_type_float_command(config: ListBasicTypeFloatConfig):
    """
    Command that accepts a list of basic type floats.
    """
    typer.echo(config.list_basic_type_float)


@app.struct_command(name="tuple_basic_type_float")
def tuple_basic_type_float_command(config: TupleBasicTypeFloatConfig):
    """
    Command that accepts a tuple of basic type floats.
    """
    typer.echo(config.tuple_basic_type_float)


@app.struct_command(name="tuple_basic_type_int")
def tuple_basic_type_int_command(config: TupleBasicTypeIntConfig):
    """
    Command that accepts a tuple of basic type integers.
    """
    typer.echo(config.tuple_basic_type_int)


@app.struct_command(name="tuple_basic_type_str")
def tuple_basic_type_str_command(config: TupleBasicTypeStrConfig):
    """
    Command that accepts a tuple of basic type strings.
    """
    typer.echo(config.tuple_basic_type_str)


@app.struct_command(name="tuple_union_type")
def tuple_union_type_command(config: TupleUnionTypeConfig):
    """
    Command that accepts a tuple of union type.
    """
    typer.echo(config.tuple_union_type)


@app.struct_command(name="literal_str")
def literal_str_command(config: LiteralStrConfig):
    """
    Command that accepts a literal string.
    """
    typer.echo(config.literal_str)


@app.struct_command(name="literal_int")
def literal_int_command(config: LiteralIntConfig):
    """
    Command that accepts a literal integer.
    """
    typer.echo(config.literal_int)


@app.struct_command(name="dict_type")
def dict_type_command(config: DictTypeConfig):
    """
    Command that accepts a dictionary type.
    """
    typer.echo(config.dict_type)


@app.struct_command(name="optional_list_basic_type_str")
def optional_list_basic_type_str_command(config: OptionalListBasicTypeStrConfig):
    """
    Command that accepts an optional list of basic type string.
    """
    typer.echo(config.optional_list_basic_type_str)


@app.struct_command(name="optional_list_basic_type_int")
def optional_list_basic_type_int_command(config: OptionalListBasicTypeIntConfig):
    """
    Command that accepts an optional list of basic type integer.
    """
    typer.echo(config.optional_list_basic_type_int)


@app.struct_command(name="optional_list_basic_type_float")
def optional_list_basic_type_float_command(config: OptionalListBasicTypeFloatConfig):
    """
    Command that accepts an optional list of basic type float.
    """
    typer.echo(config.optional_list_basic_type_float)


@app.struct_command(name="optional_tuple_basic_type_float")
def optional_tuple_basic_type_float_command(config: OptionalTupleBasicTypeFloatConfig):
    """
    Command that accepts an optional tuple of basic type float.
    """
    typer.echo(config.optional_tuple_basic_type_float)


@app.struct_command(name="optional_tuple_basic_type_int")
def optional_tuple_basic_type_int_command(config: OptionalTupleBasicTypeIntConfig):
    """
    Command that accepts an optional tuple of basic type int.
    """
    typer.echo(config.optional_tuple_basic_type_int)


@app.struct_command(name="optional_tuple_basic_type_str")
def optional_tuple_basic_type_str_command(config: OptionalTupleBasicTypeStrConfig):
    """
    Command that accepts an optional tuple of basic type string.
    """
    typer.echo(config.optional_tuple_basic_type_str)


@app.struct_command(name="optional_tuple_union_type")
def optional_tuple_union_type_command(config: OptionalTupleUnionTypeConfig):
    """
    Command that accepts an optional tuple of union type.
    """
    typer.echo(config.optional_tuple_union_type)


@app.struct_command(name="optional_literal_str")
def optional_literal_str_command(config: OptionalLiteralStrConfig):
    """
    Command that accepts an optional literal string.
    """
    typer.echo(config.optional_literal_str)


@app.struct_command(name="optional_literal_int")
def optional_literal_int_command(config: OptionalLiteralIntConfig):
    """
    Command that accepts an optional literal integer.
    """
    typer.echo(config.optional_literal_int)


@app.struct_command(name="optional_dict_type")
def optional_dict_type_command(config: OptionalDictTypeConfig):
    """
    Command that accepts an optional dictionary type.
    """
    typer.echo(config.optional_dict_type)


@app.struct_command(name="optional_dict_config")
def optional_dict_config_command(config: OptionalDictTypeConfig):
    """
    Command that accepts a dictionary configuration.
    """
    typer.echo(config.model_dump())


@app.struct_command("nested_base_model")
def nested_base_model_command(foo: Foo):
    """
    Command that accepts a nested structured configuration object.
    """
    typer.echo(foo.model_dump())


@app.struct_command("parse_json_fields")
def parse_json_fields_command(config: DictConfig):
    """
    Command that accepts a structured configuration object with parsed JSON fields.
    """
    typer.echo(config.model_dump())


@app.struct_command("fold-class")
@unfold_cls(Config)
def fold_class_command(config: Config):
    """
    Command that accepts a folded class configuration.
    """
    typer.echo(config.model_dump())


# Tests
@pytest.mark.parametrize(
    "command_fn, args, expected_output",
    [
        (
            "list_basic_type_str",
            ["--config-list-basic-type-str", "foo,bar,baz"],
            "['foo', 'bar', 'baz']",
        ),
        ("list_basic_type_int", ["--config-list-basic-type-int", "1,2,3"], "[1, 2, 3]"),
        (
            "list_basic_type_float",
            ["--config-list-basic-type-float", "1.1,2.2,3.3"],
            "[1.1, 2.2, 3.3]",
        ),
        (
            "tuple_basic_type_float",
            ["--config-tuple-basic-type-float", "1.1,2.2"],
            "(1.1, 2.2)",
        ),
        (
            "tuple_basic_type_int",
            ["--config-tuple-basic-type-int", "1,2,3"],
            "(1, 2, 3)",
        ),
        (
            "tuple_basic_type_str",
            ["--config-tuple-basic-type-str", "foo,bar,baz"],
            "('foo', 'bar', 'baz')",
        ),
        (
            "tuple_union_type",
            ["--config-tuple-union-type", "1.1,2.2"],
            "(1.1, 2.2)",
        ),
        ("tuple_union_type", ["--config-tuple-union-type", "1.1"], "1.1"),
        (
            "literal_str",
            ["--config-literal-str", "foo"],
            "foo",
        ),
        (
            "literal_int",
            ["--config-literal-int", "1"],
            "1",
        ),
        (
            "dict_type",
            ["--config-dict-type", '{"1": "one", "2": "two"}'],
            "{1: 'one', 2: 'two'}",
        ),
        (
            "optional_list_basic_type_str",
            ["--config-optional-list-basic-type-str", "foo,bar,baz"],
            "['foo', 'bar', 'baz']",
        ),
        (
            "optional_list_basic_type_str",
            [],
            "",
        ),
        (
            "optional_list_basic_type_int",
            ["--config-optional-list-basic-type-int", "1,2,3"],
            "[1, 2, 3]",
        ),
        ("optional_list_basic_type_int", [], ""),
        (
            "optional_list_basic_type_float",
            ["--config-optional-list-basic-type-float", "1.1,2.2,3.3"],
            "[1.1, 2.2, 3.3]",
        ),
        ("optional_list_basic_type_float", [], ""),
        (
            "optional_tuple_basic_type_float",
            ["--config-optional-tuple-basic-type-float", "1.1,2.2"],
            "(1.1, 2.2)",
        ),
        (
            "optional_tuple_basic_type_float",
            [],
            "",
        ),
        (
            "optional_tuple_basic_type_int",
            ["--config-optional-tuple-basic-type-int", "1,2,3"],
            "(1, 2, 3)",
        ),
        ("optional_tuple_basic_type_int", [], ""),
        (
            "optional_tuple_basic_type_str",
            ["--config-optional-tuple-basic-type-str", "foo,bar,baz"],
            "('foo', 'bar', 'baz')",
        ),
        (
            "optional_tuple_basic_type_str",
            [],
            "",
        ),
        (
            "optional_tuple_union_type",
            ["--config-optional-tuple-union-type", "1.1,2.2"],
            "(1.1, 2.2)",
        ),
        (
            "optional_tuple_union_type",
            [],
            "",
        ),
        (
            "optional_tuple_union_type",
            ["--config-optional-tuple-union-type", "1.1"],
            "1.1",
        ),
        (
            "optional_tuple_union_type",
            [],
            "",
        ),
        (
            "optional_literal_str",
            ["--config-optional-literal-str", "foo"],
            "foo",
        ),
        (
            "optional_literal_str",
            [],
            "",
        ),
        (
            "optional_literal_int",
            ["--config-optional-literal-int", "1"],
            "1",
        ),
        (
            "optional_literal_int",
            [],
            "",
        ),
        (
            "optional_dict_type",
            ["--config-optional-dict-type", '{"1": "one", "2": "two"}'],
            "{1: 'one', 2: 'two'}",
        ),
        (
            "optional_dict_type",
            [],
            "",
        ),
        (
            "nested_base_model",
            ["--foo-foo", 1, "--foo-bar-baz", "baz"],
            "{'bar': {'baz': 'baz'}, 'foo': 1}",
        ),
        (
            "parse_json_fields",
            ["--config-bars", '{"baz":"foo"},{"baz":"bar"}'],
            "{'bars': [{'baz': 'foo'}, {'baz': 'bar'}]}",
        ),
        (
            "fold-class",
            ["--bar-baz", "baz", "--foo", "1"],
            "{'bar': {'baz': 'baz'}, 'foo': 1}",
        ),
    ],
)
def test_cli(command_fn: str, args: List[str], expected_output: str):
    """
    Helper function to test CLI commands.
    """
    result = cli_runner.invoke(app, [command_fn] + args)

    assert result.exit_code == 0, f"Command failed with error: {result.output}"
    assert result.output.strip() == expected_output, (
        f"Expected '{expected_output}', got '{result.output.strip()}'"
    )


if __name__ == "__main__":
    app()
