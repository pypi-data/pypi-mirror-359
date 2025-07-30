def test_remove_parentheses():
    from cotyper.utils.string import remove_parentheses

    # Test cases
    assert remove_parentheses("Hello (World)") == "Hello "
    assert remove_parentheses("No parentheses here") == "No parentheses here"
    assert remove_parentheses("(Just a test)") == ""
    assert (
        remove_parentheses("Multiple (parentheses) in (one) string")
        == "Multiple  in  string"
    )
    assert remove_parentheses("Nested (parentheses (inside)) test") == "Nested  test"


def test_camel_to_snake_case():
    from cotyper.utils.string import camel_to_snake_case

    # Test cases
    assert camel_to_snake_case("CamelCase") == "camel_case"
    assert camel_to_snake_case("camelCase") == "camel_case"
    assert (
        camel_to_snake_case("CamelCaseWithNumbers123") == "camel_case_with_numbers123"
    )
    assert camel_to_snake_case("already_snake_case") == "already_snake_case"
    assert camel_to_snake_case("Mixed123Case") == "mixed123_case"


def test_model_name_to_snake():
    from pydantic import BaseModel

    from cotyper.utils.string import model_name_to_snake

    class SampleModel(BaseModel):
        pass

    # Test case
    assert model_name_to_snake(SampleModel) == "sample_model"
