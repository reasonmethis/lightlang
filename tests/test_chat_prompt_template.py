import pytest

from lightlang.prompts.chat_prompt_template import ChatPromptTemplate

TEMPLATE_STR = """
# Optional name for the output of the prompt
<name>cool_analysis</name>

# Optional base path for extracting data from inputs
<input_field_base>user.profile</input_field_base>

# Optional mapping of the fields in the (nested) inputs dictionary (aka workflow data)
# to the fields in the template.
<input_field_map>{"last_name": "basics.lastName"}</input_field_map>

# System, user, and assistant messages. Note that the tags allow for arbitrary
# characters after the role name, which can be helpful for some use cases, e.g. when the
# messages themselves contain tags (e.g. if a user message itself contains "</user>").

<system-abc>You are a helpful assistant with a {attitude} attitude.</system-abc>
<user xyz>Hello, my name is {name}. </user xyz>
<assistant>Hi, {name}! How can I help you today?</assistant>
<user>
My last name is {last_name}.
</user>
"""

NEW_TEMPLATE_STR = """<name>cool_analysis</name>
<input_field_base>user.profile</input_field_base>
<input_field_map>{"last_name": "basics.lastName"}</input_field_map>
<system>You are a helpful assistant with a {attitude} attitude.</system>
<user>Hello, my name is {name}. </user>
<assistant>Hi, {name}! How can I help you today?</assistant>
<user>My last name is {last_name}.</user>
"""


def test_from_and_to_string():
    chat_prompt_template = ChatPromptTemplate.from_string(TEMPLATE_STR)

    # Assertions
    assert chat_prompt_template.name == "cool_analysis"
    assert chat_prompt_template.input_field_base == "user.profile"
    assert chat_prompt_template.input_field_map == {"last_name": "basics.lastName"}
    assert len(chat_prompt_template.message_templates) == 4

    # Check individual message templates
    expected_messages = [
        {"role": "system", "content": "You are a helpful assistant with a {attitude} attitude."},
        {"role": "user", "content": "Hello, my name is {name}. "},
        {"role": "assistant", "content": "Hi, {name}! How can I help you today?"},
        {"role": "user", "content": "My last name is {last_name}."},
    ]

    for i, expected in enumerate(expected_messages):
        assert chat_prompt_template.message_templates[i] == expected

    # Test template string conversion
    assert chat_prompt_template.to_string() == NEW_TEMPLATE_STR


def test_tag_format_error():
    # Test for expected exceptions
    with pytest.raises(ValueError):
        ChatPromptTemplate.from_string("<system>blah</system>", tag_format="newlines")


def test_format_with_correct_input_structure():
    """Test format method with input data consistent with input_field_base and input_field_map."""
    chat_prompt_template = ChatPromptTemplate.from_string(TEMPLATE_STR)

    input_data = {
        "user": {
            "profile": {"name": "Bob", "basics": {"lastName": "Smith"}, "attitude": "cheerful"}
        }
    }
    formatted_messages = chat_prompt_template.format(input_data)

    expected_messages = [
        {"role": "system", "content": "You are a helpful assistant with a cheerful attitude."},
        {"role": "user", "content": "Hello, my name is Bob. "},
        {"role": "assistant", "content": "Hi, Bob! How can I help you today?"},
        {"role": "user", "content": "My last name is Smith."},
    ]

    assert formatted_messages == expected_messages


def test_format_with_incorrect_input_structure():
    """Test format method with input data inconsistent with input_field_base and input_field_map."""
    chat_prompt_template = ChatPromptTemplate.from_string(TEMPLATE_STR)

    input_data = {
        "profile": {"name": "Alice", "details": {"surname": "Doe"}, "attitude": "helpful"}
    }  # Incorrect structure

    with pytest.raises(KeyError):
        chat_prompt_template.format(input_data)


def test_setting_empty_input_field_map_and_base():
    """Test format method with empty input_field_map, expecting no nested mapping."""
    chat_prompt_template = ChatPromptTemplate.from_string(TEMPLATE_STR)
    chat_prompt_template.input_field_map = {}
    chat_prompt_template.input_field_base = ""

    input_data = {"name": "Charlie", "last_name": "Brown", "attitude": "friendly"}
    formatted_messages = chat_prompt_template.format(input_data)

    expected_messages = [
        {"role": "system", "content": "You are a helpful assistant with a friendly attitude."},
        {"role": "user", "content": "Hello, my name is Charlie. "},
        {"role": "assistant", "content": "Hi, Charlie! How can I help you today?"},
        {"role": "user", "content": "My last name is Brown."},
    ]

    assert formatted_messages == expected_messages
