import json
import os
from typing import Dict, List, Type, TypeVar, get_args

import click

from cotyper.log import log

T = TypeVar("T")


class BaseOptionalParamType(click.ParamType):
    """Base class for parameter types that support optional values."""

    def __init__(self, is_optional: bool = False):
        self.is_optional = is_optional

    def handle_optional(self, value, convert_func, param, ctx):
        """Handle optional value conversion."""
        if value is None and self.is_optional:
            return None

        return convert_func(value, param, ctx)


class LiteralParamType(BaseOptionalParamType):
    name = "literal"

    def __init__(self, literal_type: Type[T], is_optional: bool = False):
        super().__init__(is_optional)
        self.choices = get_args(literal_type)

        if not self.choices:
            raise TypeError("Literal type must have at least one choice")

        # Validate all choices are of the same type
        first_type = type(self.choices[0])
        if not all(isinstance(choice, first_type) for choice in self.choices):
            raise TypeError(
                f"All choices in Literal must be of the same type, got: {self.choices}"
            )

        self.choice_type = first_type
        self.__name__ = f"Literal[{', '.join(map(repr, self.choices))}]"
        self.name = self.__name__

    def convert(self, value, param, ctx):
        return self.handle_optional(value, self._convert_value, param, ctx)

    def _convert_value(self, value, param, ctx):
        # Try to cast to expected type
        if self.choice_type is bool and isinstance(value, str):
            # Special case for boolean strings
            if value.lower() in ("true", "1"):
                value = True
            elif value.lower() in ("false", "0"):
                value = False
            else:
                self.fail(f"{value!r} is not a valid boolean", param, ctx)
        try:
            value = self.choice_type(value)
        except (ValueError, TypeError):
            self.fail(
                f"{value!r} cannot be converted to {self.choice_type.__name__}",
                param,
                ctx,
            )

        if value not in self.choices:
            choices_str = ", ".join(map(repr, self.choices))
            self.fail(f"{value!r} is not one of {choices_str}", param, ctx)

        return value


class DictParamType(BaseOptionalParamType):
    name = "dict"

    def __init__(self, key_type: Type, value_type: Type, is_optional: bool = False):
        super().__init__(is_optional)
        self.key_type = key_type
        self.value_type = value_type
        name = f"Dict[{key_type.__name__}, {value_type.__name__}]"
        if is_optional:
            name = f"Optional[{name}]"
        self.__name__ = name
        self.name = self.__name__

    def convert(self, value, param, ctx):
        return self.handle_optional(value, self._convert_value, param, ctx)

    def _convert_value(self, value, param, ctx):
        # Parse JSON from string or file
        parsed_dict = self._parse_json_input(value, param, ctx)

        # Validate and convert keys/values
        return self._validate_dict_types(parsed_dict, param, ctx)

    def _parse_json_input(self, value, param, ctx) -> Dict:
        """Parse JSON input from string, file, or existing dict."""
        if isinstance(value, dict):
            return value

        if not isinstance(value, str):
            self.fail(
                f"Expected JSON string, file path, or dict, got {type(value).__name__}",
                param,
                ctx,
            )

        # Try as file path first

        if os.path.isfile(str(self)):
            try:
                with open(value, "r") as file_path:
                    return json.load(file_path)
            except json.JSONDecodeError as e:
                self.fail(f"Invalid JSON in file {value}: {e}", param, ctx)
            except Exception as e:
                self.fail(f"Error reading file {value}: {e}", param, ctx)

        # Try as JSON string
        try:
            return json.loads(value)
        except json.JSONDecodeError as e:
            self.fail(f"Invalid JSON string: {e}", param, ctx)

    def _validate_dict_types(self, data: Dict, param, ctx) -> Dict:
        """Validate and convert dictionary keys and values to expected types."""
        if not isinstance(data, dict):
            self.fail(f"Expected dictionary, got {type(data).__name__}", param, ctx)

        validated_dict = {}
        for key, val in data.items():
            # Convert key type
            converted_key = self._convert_type(
                key, self.key_type, f"key {key!r}", param, ctx
            )
            # Convert value type
            converted_val = self._convert_type(
                val, self.value_type, f"value {val!r}", param, ctx
            )
            validated_dict[converted_key] = converted_val

        return validated_dict

    def _convert_type(self, value, target_type, description, param, ctx):
        """Helper to convert a value to target type."""
        if isinstance(value, target_type):
            return value

        try:
            return target_type(value)
        except (ValueError, TypeError) as e:
            self.fail(
                f"{description} cannot be converted to {target_type.__name__}: {e}",
                param,
                ctx,
            )


class ListParamType(BaseOptionalParamType):
    name = "list"

    def __init__(self, value_type: Type, is_optional: bool = False):
        super().__init__(is_optional)
        self.value_type = value_type
        self.name = f"List[{value_type.__name__}]"
        self.__name__ = self.name

    def convert(self, value, param, ctx):
        return self.handle_optional(value, self._convert_value, param, ctx)

    def _convert_value(self, value, param, ctx) -> List:
        if isinstance(value, list):
            if (
                len(value) == 1
                and isinstance(value[0], str)
                and self.value_type is not str
            ):
                value = value[0].split(",")
            # Validate existing list elements
            return [self._convert_element(item, param, ctx) for item in value]

        if not isinstance(value, str):
            self.fail(
                f"Expected comma-separated string or list, got {type(value).__name__}",
                param,
                ctx,
            )

        try:
            # Parse comma-separated string
            items = [item.strip() for item in value.split(",") if item.strip()]
            return [self._convert_element(item, param, ctx) for item in items]
        except Exception as e:
            self.fail(f"Could not parse list: {e}", param, ctx)

    def _convert_element(self, item, param, ctx):
        """Convert individual list element to expected type."""
        try:
            return self.value_type(item)
        except (ValueError, TypeError) as e:
            self.fail(
                f"List element {item!r} cannot be converted to {self.value_type.__name__}: {e}",
                param,
                ctx,
            )

    def get_metavar(self, param):
        return "[item1,item2,...]"


class UnionParamType(BaseOptionalParamType):
    name = "union"

    def __init__(self, types: List[Type], is_optional: bool = False):
        super().__init__(is_optional)
        self.types = types
        type_names = ", ".join(t.__name__ for t in types)
        self.name = f"Union[{type_names}]"
        self.__name__ = self.name

    def convert(self, value, param, ctx):
        return self.handle_optional(value, self._convert_value, param, ctx)

    def _convert_value(self, value, param, ctx):
        # Try each type in order
        errors = []
        for type_ in self.types:
            try:
                return type_(value)
            except (ValueError, TypeError) as e:
                errors.append(f"{type_.__name__}: {e}")

        # If all conversions failed
        error_details = "; ".join(errors)
        self.fail(
            f"Value {value!r} cannot be converted to any of {self.name}: {error_details}",
            param,
            ctx,
        )


class TupleParamType(BaseOptionalParamType):
    name = "tuple"

    def __init__(self, element_types: List[Type], is_optional: bool = False):
        super().__init__(is_optional)
        self.element_types = element_types
        self.size = len(element_types)
        type_names = ", ".join(t.__name__ for t in element_types)
        self.name = f"Tuple[{type_names}]"
        self.__name__ = self.name

    def convert(self, value, param, ctx):
        return self.handle_optional(value, self._convert_value, param, ctx)

    def _convert_value(self, value, param, ctx):
        log.debug(f"Converting value {value} to {self.name} ({param}, {ctx})")
        if isinstance(value, tuple) and len(value) == self.size:
            return self._validate_tuple_elements(value, param, ctx)

        if isinstance(value, str):
            parts = [part.strip() for part in value.split(",")]
            if len(parts) != self.size:
                self.fail(
                    f"Expected {self.size} comma-separated values, got {len(parts)} ({value}, {param}, {ctx})",
                    param,
                    ctx,
                )
            return self._validate_tuple_elements(parts, param, ctx)

        self.fail(
            f"Expected tuple or comma-separated string, got {type(value).__name__}",
            param,
            ctx,
        )

    def _validate_tuple_elements(self, elements, param, ctx):
        """Validate and convert tuple elements to expected types."""
        converted = []
        for i, (element, expected_type) in enumerate(zip(elements, self.element_types)):
            try:
                converted.append(expected_type(element))
            except (ValueError, TypeError) as e:
                self.fail(
                    f"Element {i + 1} ({element!r}) cannot be converted to {expected_type.__name__}: {e}",
                    param,
                    ctx,
                )
        return tuple(converted)


class FlexibleTupleParamType(BaseOptionalParamType):
    """Supports Union[Tuple[T, T, ...], T] - either a tuple or single value."""

    name = "flexible_tuple"

    def __init__(self, element_type: Type, size: int = 2, is_optional: bool = False):
        super().__init__(is_optional)
        self.element_type = element_type
        self.size = size
        type_repetition = ", ".join([element_type.__name__] * size)
        self.name = f"Union[Tuple[{type_repetition}], {element_type.__name__}]"
        self.__name__ = self.name

    def convert(self, value, param, ctx):
        return self.handle_optional(value, self._convert_value, param, ctx)

    def _convert_value(self, value, param, ctx):
        # Try single value first
        if not isinstance(value, (tuple, str)) or (
            isinstance(value, str) and "," not in value
        ):
            try:
                return self.element_type(value)
            except (ValueError, TypeError):
                pass

        # Try tuple conversion
        if isinstance(value, tuple):
            if len(value) != self.size:
                self.fail(
                    f"Expected tuple of {self.size} elements, got {len(value)}",
                    param,
                    ctx,
                )
            return self._convert_tuple_elements(value, param, ctx)

        if isinstance(value, str):
            parts = [part.strip() for part in value.split(",")]
            if len(parts) == self.size:
                return self._convert_tuple_elements(parts, param, ctx)
            elif len(parts) == 1:
                try:
                    return self.element_type(parts[0])
                except (ValueError, TypeError) as e:
                    self.fail(
                        f"Single value {parts[0]!r} cannot be converted to {self.element_type.__name__}: {e}",
                        param,
                        ctx,
                    )

        self.fail(
            f"Expected single {self.element_type.__name__} or {self.size}-tuple",
            param,
            ctx,
        )

    def _convert_tuple_elements(self, elements, param, ctx):
        """Convert tuple elements to expected type."""
        try:
            return tuple(self.element_type(elem) for elem in elements)
        except (ValueError, TypeError) as e:
            self.fail(
                f"Tuple element cannot be converted to {self.element_type.__name__}: {e}",
                param,
                ctx,
            )
