import copy
import json
import re
from typing import Literal

from lightlang.prompts.prompt_template import PromptTemplate
from lightlang.types.common import ChatMessage


class ChatPromptTemplate:
    """Template for a list of chat messages with named placeholders.

    This class represents a template for chat messages where placeholders can be replaced
    with actual values. The class supports formatting the messages by replacing named
    placeholders in the message content and parsing messages from a template string.
    """

    def __init__(
        self,
        message_templates: list[ChatMessage],
        name: str | None = None,
        input_field_base: str = "",
        input_field_map: dict[str, str] | None = None,
    ) -> None:
        """
        Initializes the ChatPromptTemplate with a list of message templates.

        Args:
            message_templates (list[ChatMessage]): A list of message templates where each
                message is represented by a ChatMessage object. Each message may contain
                placeholders for dynamic content.
        """
        self.message_templates = message_templates
        self.name = name
        self.input_field_base = input_field_base
        self.input_field_map = input_field_map or {}

    def format(self, *args, **kwargs) -> list[ChatMessage]:
        """Format the chat messages with the given inputs to replace placeholders.

        Most of the time, you will want to call this method either with a single dictionary
        containing the values to substitute for the placeholders or with keyword arguments
        representing the values to substitute for the placeholders. If you pass both or if you
        include more than one dictionary in the positional arguments, the dictionaries will be
        merged into a single dictionary before filling in the template.

        Args:
            *args: Dictionaries of key-value pairs of fields to be filled in the template.
            **kwargs: Key-value pairs of fields to be filled in the template.
                placeholders in the chat message content.

        Returns:
            list[ChatMessage]: A list of ChatMessage objects with the placeholders replaced
            by the values provided in arguments.
        """
        message_templates = copy.deepcopy(self.message_templates)
        for message_template in message_templates:
            # If the message is a "typical" message (e.g. system, user, assistant), format it
            if isinstance(template_str := message_template.get("content"), str):
                prompt_template = PromptTemplate(
                    template_str,
                    input_field_base=self.input_field_base,
                    input_field_map=self.input_field_map,
                )
                message_template["content"] = prompt_template.format(*args, **kwargs)

        return message_templates

    @classmethod
    def from_string(
        cls, template_str: str, tag_format: Literal["auto", "literal", "newlines"] = "auto"
    ) -> "ChatPromptTemplate":
        """Create a ChatPromptTemplate from a string with messages defined in tags.

        The method parses a string where messages are defined within tags such as
        <system...>, <user...>, or <assistant...>. The content of each message is parsed
        and converted into a list of ChatMessage objects with the respective role and content.

        Args:
            template_str (str): A string containing the chat message templates, where each
                message is wrapped in a tag such as <system...>...</system...>,
                <user...>...</user...>, or <assistant...>...</assistant...>, where the dots
                represent arbitrary characters. The closing tags must match the opening tags exactly.
            tag_format (Literal["auto", "literal", "newlines"], optional): The expected format
            of the tags:
                - "literal": The content between the tags is kept as is.
                - "newlines": The tags are expected to take up a whole line each, otherwise an
                    error is raised.
                - "auto" (default): If the tags are on their own lines, they are treated as
                    "newlines", otherwise as "literal". Additionally, if no tags are found, the
                    whole string is treated as a single user message.

        Returns:
            ChatPromptTemplate: An instance of ChatPromptTemplate containing the
            parsed (optional) name and messages as ChatMessage objects, each with a
            `role` and `content`.

        Example 1 (most common case):
            template_str = '''
            <system>You are a helpful assistant with a {attitude} attitude.</system>
            <user>Explain {topic}.</user>
            '''

        Example 2 (advanced, uses all available features):
            template_str = '''
            <name cool_analysis> # Optional name for the output of the prompt
            <input_field_base user.profile> # Optional base path for extracting data from inputs
            <input_field_map {"last_name": "basics.lastName"}>  # Optional mapping of the fields
            # in the (nested) inputs dictionary (aka workflow data) to the fields in the template.

            # System, user, and assistant messages. Note that the tags allow for arbitrary
            characters after the role name, which can be helpful for some use cases, e.g. when the
            messages themselves contain tags (e.g. if a user message itself contains "</user>").

            <system-abc>You are a helpful assistant with a {attitude} attitude.</system-abc>
            <user xyz>Hello, my name is {name}. /user xyz>
            <assistant>Hi, {name}! How can I help you today?</assistant>
            <user>My last name is {last_name}.</user>
            '''
            chat_prompt = ChatPromptTemplate.from_string(template_str)
        """
        # Regex to find the name of the template
        name_pattern = r"<name\s+(.*?)>"
        name_match = re.search(name_pattern, template_str)
        name = name_match.group(1) if name_match else None

        # Regex to find input field base and map
        input_field_base_pattern = r"<input_field_base\s+(.*?)>"
        input_field_base_match = re.search(input_field_base_pattern, template_str, re.DOTALL)
        input_field_base = input_field_base_match.group(1) if input_field_base_match else ""

        input_field_map_pattern = r"<input_field_map\s+(.*?)>"
        input_field_map_match = re.search(input_field_map_pattern, template_str, re.DOTALL)
        input_field_map = (
            json.loads(input_field_map_match.group(1)) if input_field_map_match else None
        )

        # Regex to match the opening and closing tags exactly
        message_pattern = r"<(system|user|assistant)([^>]*)>(.*?)</\1\2>"

        # Find all matches in the template string
        matches = re.findall(message_pattern, template_str, re.DOTALL)

        # If no tags found and the tag format is "auto", treat the whole string as a user message
        # If the tag format is something else, raise an error.
        if not (matches or name_match or input_field_base_match or input_field_map_match):
            if tag_format == "auto":
                return cls([{"role": "user", "content": template_str}])
            raise ValueError(f"No tags found in the template string: {template_str}")

        # Create message templates from matches
        message_templates = []
        for role, extra_chars, content in matches:
            # If the expected format is "literal", keep the message content as is, otherwise strip
            # leading and trailing newlines. If the format is "newlines", throw if not found.
            if tag_format != "literal":
                if content.startswith("\n") and content.endswith("\n"):
                    content = content[1:-1]
                elif tag_format == "newlines":
                    raise ValueError(
                        "Expected message content to be separated from tags by newlines, "
                        f"instead got: {content}"
                    )

            message_templates.append({"role": role, "content": content})

        return cls(message_templates, name, input_field_base, input_field_map)  # type: ignore

    def to_string(self, tag_format: Literal["literal", "newlines"] = "literal") -> str:
        """Convert the ChatPromptTemplate instance into a template string with tags.

        The method serializes the list of ChatMessage objects into a template string.
        Each message's content is wrapped in its corresponding role's opening and
        closing tags. Only messages with string content are supported.

        Args:
            tag_format (Literal["literal", "newlines"], optional): The format of the tags:
                - "literal" (default): Message content is placed directly between the tags.
                - "newlines": Each tag is placed on its own line.
            
        Returns:
            str: A template string where each message's content is enclosed in tags such as
            <system>...</system>, <user>...</user>, or <assistant>...</assistant>.

        Example:
            chat_prompt = ChatPromptTemplate([...])
            template_str = chat_prompt.to_string()
        """
        template_str = "" if self.name is None else f"<name {self.name}>\n"
        if self.input_field_base:
            template_str += f"<input_field_base {self.input_field_base}>\n"
        if self.input_field_map:
            template_str += f"<input_field_map {json.dumps(self.input_field_map)}>\n"

        maybe_newline = "\n" if tag_format == "newlines" else ""
        for message in self.message_templates:
            role = message.get("role")
            content = message.get("content")
            if not isinstance(content, str):
                raise ValueError("Message content must be a string.")

            template_str += f"<{role}>{maybe_newline}{content}{maybe_newline}</{role}>\n"

        return template_str
