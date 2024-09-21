import pytest
from lightlang.prompts.prompt_template import PromptTemplate


def test_format():
    template = PromptTemplate("Hello, {name}! You are {age} years old.")
    result = template.format({"name": "John"}, age=30)
    assert result == "Hello, John! You are 30 years old."


def test_format_partial():
    template = PromptTemplate("Hello, {name}! You are {age} {units} old.")
    result = template.format_partial({"name": "John"}, age=30)
    assert result == "Hello, John! You are 30 {units} old."


def test_make_partial():
    template = PromptTemplate("Hello, {name}! You are {age} {units} old.")
    partial_template = template.make_partial({"name": "John"}, units="years")
    result = partial_template.format(age=30)
    assert result == "Hello, John! You are 30 years old."


def test_invalid_field_name():
    with pytest.raises(ValueError):
        PromptTemplate("Hello, {not a valid identifier}!")


def test_merge_inputs():
    template = PromptTemplate("Hello, {name}! You are {age} years old.")
    result = template._merge_inputs({"name": "John"}, age=30)
    assert result == {"name": "John", "age": 30}


def test_format_with_missing_field():
    template = PromptTemplate("Hello, {name}! You are {age} years old.")
    with pytest.raises(KeyError):
        template.format(name="John")
