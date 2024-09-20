import logging
from typing import Any, Callable, Generator

from lightlang.llms.llm import LLM
from lightlang.llms.utils import get_user_message
from lightlang.prompts.chat_prompt_template import ChatPromptTemplate
from lightlang.prompts.prompt_template import PromptTemplate
from lightlang.tasks.task_streaming import stream_llm_call_with_retries
from lightlang.types.common import TaskStreamResult
from lightlang.types.models import GeneralTaskResponseChunk
from lightlang.workflows.workflow_data import WorkflowData, set_workflow_data_field

logger = logging.getLogger(__name__)


class GeneralTask:
    def __init__(
        self,
        handler: Callable[[], Any],
        task_id: int | str | None = None,
    ):
        self.task_id = task_id
        self.handler = handler

    def set_task_id(self, task_id: int | str):
        self.task_id = task_id

    def _invoke_handler(self):
        return self.handler()

    def _stream_handler(self):
        result = self.handler()
        if isinstance(result, Generator):
            yield from result
        else:
            yield result

    def stream(self):
        # Check if we have a task_id
        if self.task_id is None:
            raise ValueError("Task ID required for running an LLMTask.")

        logger.info(f"Running General Task {self.task_id}...")
        yield GeneralTaskResponseChunk(
            event_type="BEGIN_TASK", event_data={"task_id": self.task_id}
        )

        # Stream the output of the task, capturing the final result
        g = self._stream_handler()
        try:
            while True:
                chunk = next(g)
                yield GeneralTaskResponseChunk(content_chunk=chunk)
        except StopIteration as e:
            task_result = e.value

        yield GeneralTaskResponseChunk(
            event_type="END_TASK",
            event_data={"task_id": self.task_id, "task_result": task_result},
        )

        logger.info(f"Finished Task {self.task_id}.")
        return TaskStreamResult(task_result=task_result)  # REVIEW: Redundant?


class LLMTask:
    def __init__(
        self,
        prompt_template: ChatPromptTemplate | PromptTemplate | str,
        *,
        task_id: int | str | None = None,
        llm: LLM | None = None,
        output_parser: Callable | None = None,
        output_handler: Callable | None = None,
        max_retries: int | None = None,
    ):
        self.output_parser = output_parser
        self.output_handler = output_handler
        self.task_id = task_id
        self.llm = llm
        self.max_retries = max_retries

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
                [get_user_message(prompt_template.get_template())],
                input_field_base=input_field_base,
                input_field_map=input_field_map,
            )

        self.chat_prompt_template = prompt_template

    def set_task_id(self, task_id: int | str):
        self.task_id = task_id

    def get_output_name(self, output_name_template: str = "task_{task_id}_output"):
        return self.chat_prompt_template.name or output_name_template.format(task_id=self.task_id)

    def stream(self, workflow_data: WorkflowData, default_llm: LLM | None = None):
        # Check if we have an LLM instance to use
        llm = self.llm or default_llm
        if llm is None:
            raise ValueError("LLM instance required for running an LLMTask.")

        # Check if we have a task_id
        if self.task_id is None:
            raise ValueError("Task ID required for running an LLMTask.")

        # Stream the output of the current task
        stream_res = yield from stream_llm_call_with_retries(
            messages=self.chat_prompt_template.format(**workflow_data),
            task_id=self.task_id,
            llm=llm,
            parser=self.output_parser,
            max_retries=self.max_retries,
        )

        if self.output_handler is None:
            # Update the workflow engine's inputs with the parsed output
            output_name = self.get_output_name()
            set_workflow_data_field(workflow_data, output_name, stream_res.task_result)
        else:
            self.output_handler(stream_res)

        logger.info(f"Finished Task {self.task_id}.")
        return stream_res
