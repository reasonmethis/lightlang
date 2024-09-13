from typing import Any, Callable, Generator

from lightlang.llms.llm import LLM
from lightlang.llms.utils import get_user_message
from lightlang.prompts.chat_prompt_template import ChatPromptTemplate
from lightlang.prompts.prompt_template import PromptTemplate


class GeneralTask:
    def __init__(
        self,
        handler: Callable[[], Any],
        task_id: int | str | None = None,
    ):
        self.task_id = task_id
        self.handler = handler

    def invoke(self):
        return self.handler()

    def stream(self):
        result = self.handler()
        if isinstance(result, Generator):
            yield from result
        else:
            yield result


class LLMTask:  # TODO: Move running the task to this class
    def __init__(
        self,
        prompt_template: ChatPromptTemplate | PromptTemplate | str,
        *,
        task_id: int | str | None = None,
        llm: LLM | None = None,
        output_parser: Callable | None = None,
        output_handler: Callable | None = None,
    ):
        self.output_parser = output_parser
        self.output_handler = output_handler
        self.task_id = task_id
        self.llm = llm

        # Convert the prompt template to a ChatPromptTemplate instance
        if isinstance(prompt_template, str):
            prompt_template = ChatPromptTemplate.from_string(prompt_template)
        elif isinstance(prompt_template, PromptTemplate):
            if prompt_template.input_converter is None:
                input_field_base = ""
                input_field_map = None
            else:
                input_field_base = prompt_template.input_converter.input_field_base
                input_field_map = prompt_template.input_converter.input_field_map
            prompt_template = ChatPromptTemplate(
                [get_user_message(prompt_template.template)],
                input_field_base=input_field_base,
                input_field_map=input_field_map,
            )

        self.chat_prompt_template = prompt_template

    def get_output_name(self):
        return self.chat_prompt_template.name
