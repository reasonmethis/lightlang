import pytest
from lightlang.prompts.chat_prompt_template import ChatPromptTemplate

template_str = """
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
<user>My last name is {last_name}.</user>
"""    
new_template_str = """<name>cool_analysis</name>
<input_field_base>user.profile</input_field_base>
<input_field_map>{"last_name": "basics.lastName"}</input_field_map>
<system>You are a helpful assistant with a {attitude} attitude.</system>
<user>Hello, my name is {name}. </user>
<assistant>Hi, {name}! How can I help you today?</assistant>
<user>My last name is {last_name}.</user>
"""
def test_chat_prompt_template():
    chat_prompt_template = ChatPromptTemplate.from_string(template_str)
    assert chat_prompt_template.name == "cool_analysis"
    assert chat_prompt_template.input_field_base == "user.profile"
    assert chat_prompt_template.input_field_map == {"last_name": "basics.lastName"}
    assert len(chat_prompt_template.message_templates) == 4
    template_0 = chat_prompt_template.message_templates[0]
    assert template_0["role"] == "system"
    assert template_0["content"] == "You are a helpful assistant with a {attitude} attitude."
    template_1 = chat_prompt_template.message_templates[1]
    assert template_1["role"] == "user"
    assert template_1["content"] == "Hello, my name is {name}. "
    template_2 = chat_prompt_template.message_templates[2]
    assert template_2["role"] == "assistant"
    assert template_2["content"] == "Hi, {name}! How can I help you today?"
    template_3 = chat_prompt_template.message_templates[3]
    assert template_3["role"] == "user"
    assert template_3["content"] == "My last name is {last_name}."
    
    assert chat_prompt_template.to_string() == new_template_str

def test_tag_format_error():
    with pytest.raises(ValueError):
        ChatPromptTemplate.from_string("<system>blah</system>", tag_format="newlines")