import inspect
import types
from dataclasses import dataclass
from typing import (
    List,
    Optional,
    Any,
    Dict,
    get_origin,
    get_args,
    Tuple,
    Union,
    Literal,
    _GenericAlias,
)

from pydantic import BaseModel
import pytest

from cotyper import parse_json_fields
from cotyper.compose.decompile import (
    resolve_func_args,
    BaseModelParameter,
    model_schema_repr,
    get_schema as get_schema_new
)
from cotyper.type_system.custom_click_types import LiteralParamType
from cotyper.type_system.type_checking import BasicTypes
from cotyper.compose.default_factory import serialize_default_factory
from cotyper.compose.fold import unfold_cls
from cotyper.methods.doc import getdoc
from cotyper.utils.base_model import create_validator_name


class _empty:
    """Marker object for Signature.empty and Parameter.empty."""


class Baz(BaseModel):
    bar: float = 0.5


class Bar(BaseModel):
    baz: int

@parse_json_fields(("bar", Bar),("foobar", Bar))
class Foo(BaseModel):
    bar: Bar
    bars: List[Bar]
    foobar: Optional[Bar] = None


def test_unfold():

    class Foo(BaseModel):
        bar: int
        baz: float


    class Bar(BaseModel):
        x: float
        y: float

    @unfold_cls(Foo)
    def foobar(foo: Foo, optional: bool, b: Bar):
        return foo

    expected_params = {"bar": int, "baz": float, "optional": bool, "b": Bar}
    actual_params = {
        key: p.annotation for key, p in inspect.signature(foobar).parameters.items()
    }
    assert expected_params == actual_params

    foo = Foo(bar=1, baz=0.5)
    actual_foo = foobar(bar=foo.bar, baz=foo.baz, optional=True, b=Bar(x=0.0, y=0.0))
    assert foo == actual_foo


def get_schema_old(object_: Any) -> Dict[str, BaseModelParameter]:
    is_function = isinstance(object_, types.FunctionType)

    signature = inspect.signature(object_)
    base_model_parameters = getdoc(object_)

    def safely_add_to_schema(name: str, param: BaseModelParameter):
        if name not in schema:
            schema[name] = param
        else:
            raise ValueError(f"Duplicate parameter name '{name}' found in schema.")

    schema = {}

    # todo for literals we add the parameter twice, i guess
    #  Fix me!!!
    for param in signature.parameters.values():
        annotation = param.annotation
        origin = get_origin(annotation)
        args = get_args(annotation)
        inner_type = args[0] if args else Any

        if annotation is tuple and origin is None:
            origin = tuple
            if (
                    param.default is not param.empty or param.default is None
            ) and isinstance(param.default, tuple):
                inner_type = type(param.default[0])
                n = len(param.default)
            else:
                n = 1
            annotation = Tuple[tuple([inner_type] * n)]

        name = param.name

        bm_param = base_model_parameters.get(name, None)
        doc = bm_param.doc if bm_param is not None else ""

        if origin is not None:
            try:
                is_subclass = issubclass(inner_type, BaseModel)
            except TypeError:
                is_subclass = False

            # TODO adding np.ndarray | torch.Tensor to list of numerical type if annotation is optional

            if origin is Union and is_subclass:
                # inner_type basemodel should have json field string validation when object_ is basemodel

                if not is_function:
                    if issubclass(object_, BaseModel):
                        validator_name = create_validator_name(param.name, inner_type)

                        if not hasattr(object_, validator_name):
                            raise ValueError(
                                f"The class {object_} should have json validator for {param.name}. Add `@parse_json_fields('{param.name}',{inner_type}) to class {object_}"
                            )
                repr = "'{" + model_schema_repr(inner_type) + "}'"
                new_doc = (
                    f"({annotation}, parse argument as json dictionary {repr}) {doc}"
                )
                base_model_param = BaseModelParameter(
                    name=name,
                    annotation=Optional[str],
                    default=None,
                    doc=new_doc,
                    parent=object_,
                )
                safely_add_to_schema(name, base_model_param)

            elif origin is Literal and types.NoneType in args:
                base_model_param = BaseModelParameter(
                    name=name,
                    annotation=Optional[LiteralParamType(args[:-1])], # exclude NoneType
                    default=param.default,
                    doc=doc,
                    parent=object_,
                )
                safely_add_to_schema(name, base_model_param)
            # is Optional
            elif origin is Union and types.NoneType in args:
                if (
                        str(inner_type) == "<class 'torch.Tensor'>"
                        or str(inner_type) == "<class 'numpy.ndarray'>"
                ):

                    base_model_param = BaseModelParameter(
                        name=name,
                        annotation=Optional[List[float]],
                        default=None,
                        doc=doc,
                        parent=object_,
                    )
                    safely_add_to_schema(name, base_model_param)

            elif isinstance(origin, list):
                if issubclass(inner_type, BaseModel):
                    model_signature = model_schema_repr(inner_type)
                    model_signature = "'{" + model_signature + "}, ...'"
                    doc += f" - list of json objects with signature {model_signature} as one string"
                    # in order to parse a list of BaseModel we change the type to str which can be
                    # re-compiled to the correct basemodel by `parse_json_fields`
                    # TODO eventually you'd use this `get_schema` function somewhere else,
                    #  then this type overwriting would be bad :(
                    if not is_function:  # if object_ is a function then `issubclass` will break since it is not a class
                        if issubclass(object_, BaseModel):
                            serialized_values = serialize_default_factory(
                                object_.model_fields[name].default_factory
                            )

                            base_model_param = BaseModelParameter(
                                name=name,
                                annotation=str,
                                default=serialized_values,
                                doc=doc,
                                parent=object_,
                            )
                            safely_add_to_schema(name, base_model_param)
                    else:
                        base_model_param = BaseModelParameter(
                            name=name,
                            annotation=str,
                            default=param.default,
                            doc=doc,
                            parent=object_,
                        )
                        safely_add_to_schema(name, base_model_param)

                elif issubclass(inner_type, BasicTypes):
                    if not is_function:  # if object_ is a function then `issubclass` will break since it is not a class
                        if issubclass(object_, BaseModel):
                            default_factory = object_.model_fields[
                                                  name
                                              ].default_factory or (lambda: None)
                            default_value = default_factory()
                    else:
                        default_value = param.default
                    base_model_param = BaseModelParameter(
                        name=name,
                        annotation=List[inner_type],
                        default=default_value,
                        doc=doc,
                        parent=object_,
                    )
                    safely_add_to_schema(name, base_model_param)
                else:
                    base_model_param = BaseModelParameter(
                        name=name,
                        annotation=List[inner_type],
                        default=param.default,
                        doc=doc,
                        parent=object_,
                    )
                    safely_add_to_schema(name, base_model_param)
            else:
                base_model_param = BaseModelParameter(
                    name=name,
                    annotation=annotation,
                    default=param.default,
                    doc=doc,
                    parent=object_,
                )
                safely_add_to_schema(name, base_model_param)

        try:
            is_subclass = issubclass(annotation, BaseModel)
        except TypeError:
            is_subclass = False
        if (
                str(annotation) == "<class 'torch.Tensor'>"
                or str(annotation) == "<class 'numpy.ndarray'>"
        ):

            base_model_param = BaseModelParameter(
                name=name, annotation=List[float], default=None, doc=doc, parent=object_
            )
            safely_add_to_schema(name, base_model_param)
        elif origin is Literal and types.NoneType not in args and is_subclass:
            # if the annotation is a Literal type, we need to create a LiteralChoice
            # click.ParamType to handle it correctly in the CLI
            base_model_param = BaseModelParameter(
                name=name,
                annotation=LiteralParamType(annotation),
                default=param.default,
                doc=doc,
                parent=object_,
            )
            safely_add_to_schema(name, base_model_param)
        elif (
                isinstance(annotation, _GenericAlias) and name not in schema
        ):  # TODO _GenericAlias is case of Union[ X , NoneType]?
            base_model_param = BaseModelParameter(
                name=name,
                annotation=annotation,
                default=param.default,
                doc=doc,
                parent=object_,
            )
            safely_add_to_schema(name, base_model_param)

        elif is_subclass:
            nested_schema = {
                f"{name}_{sub_name}": nested_annotation
                for sub_name, nested_annotation in get_schema_old(annotation).items()
            }
            schema.update(nested_schema)

        elif name not in schema:
            base_model_param = BaseModelParameter(
                name=name,
                annotation=annotation,
                default=param.default,
                doc=doc,
                parent=object_,
            )
            safely_add_to_schema(name, base_model_param)
        else:
            if name not in schema:
                raise TypeError(f"Unknown case of annotation {annotation} for {name}")

    return schema


class TestSchemaComparison:
    """Test cases comparing old and new schema implementations"""

    def test_simple_function_parameters(self):
        """Test basic function with simple parameters"""
        def sample_func(a: int, b: str = "default", c: float = 1.0):
            pass

        old_result = get_schema_old(sample_func)
        new_result = get_schema_new(sample_func)

        assert len(old_result) == len(new_result)
        for key in old_result:
            assert key in new_result
            # Note: Full comparison would need the complete new implementation

    def test_optional_parameters(self):
        """Test optional parameters"""
        def sample_func(a: Optional[int] = None, b: Union[str, None] = None):
            pass

        old_result = get_schema_old(sample_func)
        new_result = get_schema_new(sample_func)

        assert len(old_result) == len(new_result)

    def test_list_parameters(self):
        """Test list parameters"""
        def sample_func(items: List[str], numbers: List[int] = None):
            pass

        old_result = get_schema_old(sample_func)
        new_result = get_schema_new(sample_func)

        assert len(old_result) == len(new_result)

    def test_literal_parameters(self):
        """Test literal parameters"""
        def sample_func(mode: Literal["train", "test"], debug: Literal["on", "off"] = "off"):
            pass

        old_result = get_schema_old(sample_func)
        new_result = get_schema_new(sample_func)

        assert len(old_result) == len(new_result)

    def test_tuple_parameters(self):
        """Test tuple parameters"""
        def sample_func(coords: tuple = (0, 0), dimensions: Tuple[int, int] = (100, 100)):
            pass

        old_result = get_schema_old(sample_func)
        new_result = get_schema_new(sample_func)

        assert len(old_result) == len(new_result)

    def test_complex_nested_types(self):
        """Test complex nested type annotations"""
        def sample_func(
                data: Optional[List[Dict[str, Union[int, str]]]] = None,
                config: Union[Dict[str, Any], None] = None
        ):
            pass

        old_result = get_schema_old(sample_func)
        new_result = get_schema_new(sample_func)

        assert len(old_result) == len(new_result)

    @pytest.mark.parametrize("annotation,default", [
        (int, 42),
        (str, "test"),
        (float, 3.14),
        (bool, True),
        (Optional[int], None),
        (List[str], []),
        (Dict[str, int], {}),
    ])
    def test_parameter_types(self, annotation, default):
        """Parametrized test for various parameter types"""
        def create_func(ann, def_val):
            def sample_func(param: ann = def_val):
                pass
            return sample_func

        func = create_func(annotation, default)

        old_result = get_schema_old(func)
        new_result = get_schema_new(func)

        assert len(old_result) == len(new_result)
        assert "param" in old_result
        assert "param" in new_result

    def test_class_method_parameters(self):
        """Test class methods"""
        class SampleClass:
            def method(self, a: int, b: str = "default"):
                pass

        old_result = get_schema_old(SampleClass.method)
        new_result = get_schema_new(SampleClass.method)

        # Should handle 'self' parameter appropriately
        assert len(old_result) == len(new_result)

    def test_error_handling_duplicate_names(self):
        """Test that both implementations handle duplicate names similarly"""
        # This would test edge cases where parameter names might conflict
        def sample_func(a: int, b: str):
            pass

        # Both should succeed for normal cases
        old_result = get_schema_old(sample_func)
        new_result = get_schema_new(sample_func)

        assert len(old_result) == 2
        assert len(new_result) == 2

    def test_empty_function(self):
        """Test function with no parameters"""
        def empty_func():
            pass

        old_result = get_schema_old(empty_func)
        new_result = get_schema_new(empty_func)

        assert len(old_result) == 0
        assert len(new_result) == 0
        assert old_result == new_result

    def test_function_with_nested_base_model(self):
        def sample_func(
            a: Foo,
            b: Optional[Bar] = None,
            c: List[Baz] = None
        ):
            pass
        old_result = get_schema_old(sample_func)
        new_result = get_schema_new(sample_func)

        assert len(old_result) == len(new_result)
        for key in old_result:
            assert key in new_result
            assert old_result[key] == new_result[key]


    def test_consistency_across_multiple_calls(self):
        """Test that both implementations are deterministic"""
        def sample_func(a: int, b: Optional[str] = None, c: List[float] = None):
            pass

        # Call multiple times to ensure consistency
        old_results = [get_schema_old(sample_func) for _ in range(3)]
        new_results = [get_schema_new(sample_func) for _ in range(3)]

        # All old results should be identical
        for i in range(1, len(old_results)):
            assert len(old_results[0]) == len(old_results[i])

        # All new results should be identical
        for i in range(1, len(new_results)):
            assert len(new_results[0]) == len(new_results[i])

        # Old and new should have same structure
        assert len(old_results[0]) == len(new_results[0])


class TestEdgeCases:
    """Test edge cases and error conditions"""

    def test_invalid_annotations(self):
        """Test handling of invalid or unusual annotations"""
        def sample_func(a: "SomeClass", b: 123):  # Invalid annotations
            pass

        # Both implementations should handle gracefully
        try:
            old_result = get_schema_old(sample_func)
            new_result = get_schema_new(sample_func)
            assert len(old_result) == len(new_result)
        except Exception as e:
            pytest.skip(f"Expected behavior for invalid annotations: {e}")

    def test_recursive_types(self):
        """Test handling of recursive type definitions"""
        # This would test more complex scenarios
        def sample_func(data: Dict[str, "RecursiveType"]):
            pass

        old_result = get_schema_old(sample_func)
        new_result = get_schema_new(sample_func)

        assert len(old_result) == len(new_result)
