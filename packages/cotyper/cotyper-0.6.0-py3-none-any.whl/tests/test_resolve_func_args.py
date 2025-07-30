import inspect
from typing import Any, Dict, List, Literal, Optional, Tuple, Union

import pytest

from cotyper.compose.decompile import (
    TYPE_PROCESSORS,
    ParameterConfig,
    TypeProcessingResult,
    create_inspect_parameter,
    create_parameter_config,
    process_default_type,
    process_list_basic_type,
    process_literal_click_param_type,
    process_tuple_union_type,
    process_type_annotation,
    register_type_processor,
    resolve_func_args,
)
from cotyper.type_system.custom_click_types import (
    FlexibleTupleParamType,
    LiteralParamType,
)
from cotyper.type_system.type_checking import (
    is_dict,
    is_list_basic_type,
    is_optional,
    is_optional_dict,
)

# Import both versions (assuming old version is in old_module and new is in new_module)
# from old_module import resolve_func_args as old_resolve_func_args
# from new_module import resolve_func_args as new_resolve_func_args, register_type_processor


# Mock dependencies for testing
class MockLiteralChoice:
    def __init__(self, choices):
        self.choices = choices


class MockParam:
    def __init__(self, annotation, doc="", default=None):
        self.annotation = annotation
        self.doc = doc
        self.default = default


class TestParameterConfig:
    """Test the ParameterConfig dataclass."""

    def test_parameter_config_creation(self):
        config = ParameterConfig(
            name="test_param",
            annotation=str,
            doc="Test documentation",
            default="default_value",
        )

        assert config.name == "test_param"
        assert config.annotation is str
        assert config.doc == "Test documentation"
        assert config.default == "default_value"
        assert config.callback is None
        assert config.parser is None

    def test_parameter_config_immutable(self):
        config = ParameterConfig(
            name="test_param",
            annotation=str,
            doc="Test documentation",
            default="default_value",
        )

        with pytest.raises(AttributeError):
            config.name = "new_name"


class TestTypeProcessingResult:
    """Test the TypeProcessingResult dataclass."""

    def test_type_processing_result_creation(self):
        result = TypeProcessingResult(
            annotation=str, callback=lambda x: x, parser=None, doc_suffix=" (processed)"
        )

        assert result.annotation is str
        assert result.callback is not None
        assert result.parser is None
        assert result.doc_suffix == " (processed)"


class TestTypePredicates:
    """Test type predicate functions."""

    def test_is_list_basic_type(self):
        assert is_list_basic_type(List[str])

    def test_is_optional(self):
        assert is_optional(Optional[str])


class TestTypeProcessors:
    """Test individual type processors."""

    def test_process_list_basic_type(self):
        annotation = List[str]
        result = process_list_basic_type(annotation)

        assert result.annotation == List[str]
        assert result.click_type is not None
        assert "use `,` separated arguments" in result.doc_suffix

    def test_process_default_type(self):
        annotation = str
        result = process_default_type(annotation)

        assert result.annotation is str
        assert result.callback is None
        assert result.parser is None
        assert result.doc_suffix == ""

    def test_process_tuple_union_type_valid(self):
        annotation = Union[Tuple[float, float], float]

        result = process_tuple_union_type(annotation)

        assert result.annotation == Any
        assert result.click_type.name == FlexibleTupleParamType(float, 2).name

    def test_process_tuple_union_type_invalid(self):
        annotation = Union[Tuple[str, int], float]

        with pytest.raises(
            TypeError, match="All inner types of a tuple union should be the same"
        ):
            process_tuple_union_type(annotation)

    def test_process_literal_choice_type_regular(self):
        literal_choice = LiteralParamType(Literal["a", "b", "c"])

        result = process_literal_click_param_type(literal_choice)

        assert result.annotation is type("a")  # str
        assert result.click_type == literal_choice

    def test_process_literal_choice_type_optional(self):
        literal_choice = LiteralParamType(Literal["a", "b", "c"])
        annotation = Optional[literal_choice]

        result = process_literal_click_param_type(annotation)

        assert result.annotation is Optional[str]  # str
        assert result.click_type == literal_choice


class TestProcessTypeAnnotation:
    """Test the main type annotation processing function."""

    def test_process_type_annotation_list_basic(self):
        annotation = List[str]

        expected_result = TypeProcessingResult(annotation=List[str])
        result = process_type_annotation(annotation)

        assert result.annotation == expected_result.annotation
        assert result.doc_suffix == "(typing.List[str] use `,` separated arguments)"
        assert result.click_type is not None

    def test_process_type_annotation_default(self):
        annotation = str

        result = process_type_annotation(annotation)

        assert result.annotation is str
        assert result.callback is None


class TestParameterCreation:
    """Test parameter creation functions."""

    def test_create_parameter_config(self):
        param = MockParam(annotation=str, doc="Test doc", default="default")

        config = create_parameter_config("test_name", param)

        assert config.name == "test_name"
        assert config.annotation is str
        assert config.doc == "Test doc"
        assert config.default == "default"
        assert config.rich_help_panel == "Test"

    def test_create_inspect_parameter(self):
        import typer

        config = ParameterConfig(
            name="test_param", annotation=str, doc="Test doc", default="default"
        )

        param = create_inspect_parameter(config)

        assert param.name == "test_param"
        assert param.kind == inspect.Parameter.KEYWORD_ONLY
        assert isinstance(param.default, typer.models.OptionInfo)
        assert param.default.default == "default"


class TestFunctionComparison:
    """Test that new and old functions produce equivalent results."""

    def create_test_function(self, param_types):
        """Create a test function with specified parameter types."""

        def test_func(**kwargs):
            return kwargs

        # Mock the schema for this function
        schema = {}
        for i, param_type in enumerate(param_types):
            param_name = f"param_{i}"
            schema[param_name] = MockParam(
                annotation=param_type,
                doc=f"Documentation for {param_name}",
                default=None,
            )

        return test_func, schema

    def test_function_execution_equivalence(self):
        """Test that the wrapped function executes correctly."""

        def original_func(param1: str, param2: int):
            return f"{param1}_{param2}"

        wrapped_func = resolve_func_args(original_func)
        result = wrapped_func(param1="test", param2=42)

        # The recompile_arguments mock returns the test values
        assert result == "test_42"


class TestExtensibility:
    """Test the extensibility features."""

    def test_register_type_processor(self):
        """Test registering a new type processor."""

        # Create a custom type
        class CustomType:
            pass

        # Create predicate and processor
        def is_custom_type(annotation):
            return annotation == CustomType

        def process_custom_type(annotation):
            return TypeProcessingResult(annotation=str, doc_suffix=" (custom type)")

        # Register the processor
        original_length = len(TYPE_PROCESSORS)
        register_type_processor(is_custom_type, process_custom_type)

        # Verify it was added
        assert len(TYPE_PROCESSORS) == original_length + 1
        assert TYPE_PROCESSORS[0] == (is_custom_type, process_custom_type)

        # Test that it's used
        result = process_type_annotation(CustomType)
        assert result.annotation is str
        assert result.doc_suffix == " (custom type)"


class TestErrorHandling:
    """Test error handling scenarios."""

    def test_tuple_union_type_error(self):
        """Test error handling in tuple union processing."""
        annotation = Union[Tuple[str, int], float]

        with pytest.raises(TypeError) as exc_info:
            process_tuple_union_type(annotation)

        assert "All inner types of a tuple union should be the same" in str(
            exc_info.value
        )

    def test_missing_schema(self):
        """Test behavior when schema is empty."""

        def test_func():
            pass

        result = resolve_func_args(test_func)

        assert callable(result)
        assert len(inspect.signature(result).parameters) == 0


def test_is_optional_dict():
    tp = Optional[Dict[str, Any]]
    assert is_optional_dict(tp)


def test_is_dict():
    tp = Dict[int, int]
    assert is_dict(tp)


class TestIntegration:
    """Integration tests with realistic scenarios."""

    def test_complex_function_signature(self):
        """Test with a complex function signature."""

        def complex_func(
            basic_str: str,
            basic_list: List[str],
            optional_param: Optional[int],
            tuple_union: Union[Tuple[float, float], float],
        ):
            return "complex_result"

        result = resolve_func_args(complex_func)

        # Verify the result
        assert callable(result)
        assert result.__name__ == complex_func.__name__

        sig = inspect.signature(result)
        assert len(sig.parameters) == 4

        # Verify parameter names are preserved
        param_names = list(sig.parameters.keys())
        expected_names = [
            "basic_str",
            "basic_list",
            "optional_param",
            "tuple_union",
        ]
        assert param_names == expected_names


# Fixtures for running tests
@pytest.fixture
def sample_functions():
    """Provide sample functions for testing."""

    def simple_func(param1: str, param2: int):
        return f"{param1}_{param2}"

    def complex_func(
        basic_param: str,
        list_param: List[str],
        optional_param: Optional[int],
        literal_param: MockLiteralChoice(["a", "b", "c"]),
    ):
        return "complex_result"

    return {"simple": simple_func, "complex": complex_func}
