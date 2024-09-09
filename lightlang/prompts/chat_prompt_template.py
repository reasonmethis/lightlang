import copy
import json
import re

from lightlang.models import ChatMessage
from lightlang.prompts.prompt_template import PromptTemplate


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

    def format(self, **inputs) -> list[ChatMessage]:
        """Format the chat messages with the given inputs to replace placeholders.

        The method takes keyword arguments that are used to replace placeholders in the
        message content. The placeholders in the content are formatted using the values
        passed via `inputs`.

        Args:
            **inputs: Arbitrary keyword arguments representing the values to substitute for
                placeholders in the chat message content.

        Returns:
            list[ChatMessage]: A list of ChatMessage objects with the placeholders replaced
            by the values provided in `inputs`. Each message is deep-copied from the original
            template, so the original message templates are not modified.
        """
        message_templates = copy.deepcopy(self.message_templates)
        for message_template in message_templates:
            if isinstance(template_str := message_template.get("content"), str):
                prompt_template = PromptTemplate(
                    template_str,
                    input_field_base=self.input_field_base,
                    input_field_map=self.input_field_map,
                )
                message_template["content"] = prompt_template.format(**inputs)

        return message_templates

    @classmethod
    def from_string(cls, template_str: str) -> "ChatPromptTemplate":
        """Create a ChatPromptTemplate from a string with messages defined in tags.

        The method parses a string where messages are defined within tags such as
        <system...>, <user...>, or <assistant...>. The content of each message is parsed
        and converted into a list of ChatMessage objects with the respective role and content.

        Args:
            template_str (str): A string containing the chat message templates, where each
                message is wrapped in a tag such as <system...>...</system...>,
                <user...>...</user...>, or <assistant...>...</assistant...>. The closing
                tags must match the opening tags exactly, and the content must start on
                a new line after the opening tag.

        Returns:
            ChatPromptTemplate: An instance of ChatPromptTemplate containing the
            parsed (optional) name and messages as ChatMessage objects, each with a
            `role` and `content`.

        Example:
            template_str = '''
            <name cool_analysis>
            <input_field_base user.profile>
            <input_field_map {"last_name": "basics.lastName"}>
            <systemabc>
            You are a helpful assistant with a {attitude} attitude.
            </systemabc>
            <userxyz>
            Hello, my name is {name}.
            </userxyz>
            '''
            chat_prompt = ChatPromptTemplate.from_string(template_str)
        """
        # Regex to find the name of the template
        name_pattern = r"<name\s+(.*?)>"
        name_match = re.search(name_pattern, template_str)
        name = name_match.group(1) if name_match else None

        # Regex to find input field base and map
        input_field_base_pattern = r"<input_field_base\s+(.*?)>"
        input_field_base_match = re.search(
            input_field_base_pattern, template_str, re.DOTALL
        )
        input_field_base = (
            input_field_base_match.group(1) if input_field_base_match else ""
        )

        input_field_map_pattern = r"<input_field_map\s+(.*?)>"
        input_field_map_match = re.search(
            input_field_map_pattern, template_str, re.DOTALL
        )
        input_field_map = (
            json.loads(input_field_map_match.group(1)) if input_field_map_match else None
        )

        # Regex to match the opening and closing tags exactly
        message_pattern = r"<(system|user|assistant)([^>]*)>\n(.*?)\n</\1\2>"

        # Find all matches in the template string
        matches = re.findall(message_pattern, template_str, re.DOTALL)

        # Create message templates from matches
        message_templates = []
        for role, extra_chars, content in matches:
            message_templates.append({"role": role, "content": content})

        return cls(message_templates, name, input_field_base, input_field_map)  # type: ignore

    def to_string(self) -> str:
        """Convert the ChatPromptTemplate instance into a template string with tags.

        The method serializes the list of ChatMessage objects into a template string.
        Each message's content is wrapped in its corresponding role's opening and
        closing tags. Only messages with string content are supported.

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

        for message in self.message_templates:
            role = message.get("role")
            content = message.get("content")
            if not isinstance(content, str):
                raise ValueError("Message content must be a string.")

            template_str += f"<{role}>\n{content}\n</{role}>\n"

        return template_str
