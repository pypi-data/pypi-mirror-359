import inspect

import pytest
from pydantic import BaseModel, ValidationError

from cotyper.compose.decompile import (
    build_kwargs_from_signature,
    extract_complex_parameters,
    extract_direct_parameters,
    normalize_string_value,
    recompile_arguments,
    recompile_basemodel,
    resolve_complex_parameters,
)

# Assuming the refactored functions are imported from your module
# from your_module import (
#     normalize_string_value,
#     extract_direct_parameters,
#     extract_complex_parameters,
#     resolve_complex_parameters,
#     build_kwargs_from_signature,
#     recompile_basemodel,
#     recompile_arguments
# )


# Test models for testing
class Address(BaseModel):
    street: str
    city: str
    zipcode: str


class Person(BaseModel):
    name: str
    age: int
    address: Address


class Company(BaseModel):
    name: str
    employees: int


def sample_function(person: Person, company: Company, simple_param: str):
    """Sample function for testing recompile_arguments"""
    return f"{person.name} works at {company.name}"


@pytest.mark.parametrize(
    "input_value,expected",
    [
        ("hello 'world'", 'hello "world"'),
        ("test 'single' and 'double'", 'test "single" and "double"'),
        ("no quotes here", "no quotes here"),
        (123, 123),
        (True, True),
        (None, None),
        (["list", "values"], ["list", "values"]),
    ],
)
def test_normalize_string_value(input_value, expected):
    result = normalize_string_value(input_value)
    assert result == expected


@pytest.mark.parametrize(
    "kwargs,expected_keys",
    [
        ({"name": "John", "age": 30}, {"name", "age"}),
        ({"name": "John", "address_street": "123 Main"}, {"name"}),
        ({"age": 25, "company_name": "Tech Corp"}, {"age"}),
        ({}, set()),
        ({"name": "John", "age": 30, "address_street": "Main St"}, {"name", "age"}),
    ],
)
def test_extract_direct_parameters(kwargs, expected_keys):
    signature = inspect.signature(Person)
    result = extract_direct_parameters(signature, kwargs)
    assert set(result.keys()) == expected_keys


@pytest.mark.parametrize(
    "kwargs,expected_complex_keys",
    [
        ({"person_name": "John", "person_age": 30}, {"person"}),
        ({"company_name": "Tech Corp", "company_employees": 100}, {"company"}),
        ({"person_name": "John", "company_name": "Tech"}, {"person", "company"}),
        (
            {
                "person_name": "John",
                "person_age": 30,
                "company_name": "Tech",
                "company_employees": 50,
            },
            {"person", "company"},
        ),
        ({}, set()),
        (
            {"simple_param": "direct"},
            set(),
        ),  # Direct params shouldn't appear in complex
    ],
)
def test_extract_complex_parameters(kwargs, expected_complex_keys):
    signature = inspect.signature(sample_function)
    result = extract_complex_parameters(signature, kwargs)
    assert set(result.keys()) == expected_complex_keys


def test_extract_complex_parameters_nested_values():
    kwargs = {
        "address_street": "123 Main St",
        "address_city": "New York",
        "address_zipcode": "10001",
    }
    signature = inspect.signature(Person)
    result = extract_complex_parameters(signature, kwargs)

    expected = {
        "address": {"street": "123 Main St", "city": "New York", "zipcode": "10001"}
    }
    assert result == expected


def test_resolve_complex_parameters():
    signature = inspect.signature(Person)
    complex_types = {
        "address": {"street": "123 Main St", "city": "New York", "zipcode": "10001"}
    }

    result = resolve_complex_parameters(signature, complex_types)

    assert "address" in result
    assert isinstance(result["address"], Address)
    assert result["address"].street == "123 Main St"
    assert result["address"].city == "New York"
    assert result["address"].zipcode == "10001"


@pytest.mark.parametrize(
    "kwargs,expected_keys",
    [
        (
            {
                "name": "John",
                "age": 30,
                "address_street": "Main",
                "address_city": "NYC",
                "address_zipcode": "10001",
            },
            {"name", "age", "address"},
        ),
        (
            {
                "name": "John",
                "address_street": "Main",
                "address_city": "NYC",
                "address_zipcode": "10001",
            },
            {"name", "address"},
        ),
        ({"name": "John", "age": 30}, {"name", "age"}),
        ({}, set()),
    ],
)
def test_build_kwargs_from_signature(kwargs, expected_keys):
    signature = inspect.signature(Person)
    result = build_kwargs_from_signature(signature, kwargs)
    assert set(result.keys()) == expected_keys


def test_build_kwargs_from_signature_with_string_normalization():
    kwargs = {"name": "John 'Doe'", "age": 30}
    signature = inspect.signature(Person)
    result = build_kwargs_from_signature(signature, kwargs)

    assert result["name"] == 'John "Doe"'
    assert result["age"] == 30


def test_recompile_basemodel_simple():
    kwargs = {
        "name": "John Doe",
        "age": 30,
        "address_street": "123 Main St",
        "address_city": "New York",
        "address_zipcode": "10001",
    }

    result = recompile_basemodel(Person, kwargs)

    assert isinstance(result, Person)
    assert result.name == "John Doe"
    assert result.age == 30
    assert isinstance(result.address, Address)
    assert result.address.street == "123 Main St"
    assert result.address.city == "New York"
    assert result.address.zipcode == "10001"


def test_recompile_basemodel_with_string_quotes():
    kwargs = {
        "name": "John 'Johnny' Doe",
        "age": 25,
        "address_street": "456 Oak 'Street'",
        "address_city": "Boston",
        "address_zipcode": "02101",
    }

    result = recompile_basemodel(Person, kwargs)

    assert result.name == 'John "Johnny" Doe'
    assert result.address.street == '456 Oak "Street"'


def test_recompile_arguments_simple():
    kwargs = {
        "person_name": "Jane Doe",
        "person_age": 28,
        "person_address_street": "789 Pine St",
        "person_address_city": "Seattle",
        "person_address_zipcode": "98101",
        "company_name": "Tech Corp",
        "company_employees": 500,
        "simple_param": "test value",
    }

    result = recompile_arguments(kwargs, sample_function)

    assert "person" in result
    assert "company" in result
    assert "simple_param" in result

    assert isinstance(result["person"], Person)
    assert result["person"].name == "Jane Doe"
    assert result["person"].age == 28
    assert result["person"].address.street == "789 Pine St"

    assert isinstance(result["company"], Company)
    assert result["company"].name == "Tech Corp"
    assert result["company"].employees == 500

    assert result["simple_param"] == "test value"


def test_recompile_arguments_with_direct_params():
    kwargs = {
        "simple_param": "direct value",
        "company_name": "Direct Corp",
        "company_employees": 100,
    }

    result = recompile_arguments(kwargs, sample_function)

    assert result["simple_param"] == "direct value"
    assert isinstance(result["company"], Company)
    assert result["company"].name == "Direct Corp"


@pytest.mark.parametrize(
    "kwargs",
    [
        {},
        {"unknown_param": "value"},
        {"person_unknown": "value"},
    ],
)
def test_recompile_arguments_empty_or_invalid_params(kwargs):
    # this should raise a pydantic validation error
    if kwargs == {"person_unknown": "value"}:
        with pytest.raises(ValidationError):
            _ = recompile_arguments(kwargs, sample_function)
    else:
        result = recompile_arguments(kwargs, sample_function)
        assert isinstance(result, dict)
        assert result == {}


def test_integration_recompile_basemodel_and_arguments():
    """Test that both functions work together correctly"""
    # First, test recompile_arguments
    kwargs = {
        "person_name": "Integration Test",
        "person_age": 35,
        "person_address_street": "Integration St",
        "person_address_city": "Test City",
        "person_address_zipcode": "12345",
        "company_name": "Test Company",
        "company_employees": 50,
        "simple_param": "integration",
    }

    function_args = recompile_arguments(kwargs, sample_function)

    # Then verify we can call the function with the result
    result = sample_function(**function_args)
    assert result == "Integration Test works at Test Company"

    # Also test that we can recreate the same Person object directly
    person_kwargs = {
        "name": "Integration Test",
        "age": 35,
        "address_street": "Integration St",
        "address_city": "Test City",
        "address_zipcode": "12345",
    }

    person = recompile_basemodel(Person, person_kwargs)
    assert person.name == function_args["person"].name
    assert person.age == function_args["person"].age
    assert person.address.street == function_args["person"].address.street
