import logging
import os
from typing import Callable

from lightlang.llms.llm import LLM
from lightlang.prompts.chat_prompt_template import ChatPromptTemplate
from lightlang.prompts.prompt_template import PromptTemplate
from lightlang.tasks.task import GeneralTask, LLMTask
from lightlang.tasks.task_streaming import (
    stream_general_task,
    stream_llm_call_with_retries,
)
from lightlang.utils.core import save_text_to_file
from lightlang.workflows.workflow_base import BaseWorkflow
from lightlang.workflows.workflow_data import WorkflowData, set_workflow_data_field

logger = logging.getLogger(__name__)
TaskCompatible = str | PromptTemplate | ChatPromptTemplate | LLMTask | GeneralTask


class SequentialWorkflow(BaseWorkflow):
    """Agentic workflow with sequential tasks (no branching or loops)."""

    def __init__(
        self,
        workflow_data: WorkflowData,
        default_llm: LLM,
        tasks: list[TaskCompatible],
        handle_task_end: Callable | None = None,
        output_name_template: str = "task_{task_id}_output",  # For tasks w/o output_name
        output_dir: str | None = None,
    ):
        self.workflow_data = workflow_data
        self.default_llm = default_llm

        # Convert prompt templates or strings to LLMTask instances
        self.tasks = [
            LLMTask(t)
            if isinstance(t, str)
            or isinstance(t, PromptTemplate)
            or isinstance(t, ChatPromptTemplate)
            else t
            for t in tasks
        ]
        self.task_by_id = {
            i if task.task_id is None else task.task_id: task
            for i, task in enumerate(self.tasks, start=1)
        }

        self.handle_task_end = handle_task_end  # Takes this instance and stream_res
        self.task_id: str | int | None = None
        self.output_name_template = output_name_template
        self.output_dir = output_dir

    def stream(self, task_id: int | str | None = None):
        """Stream the result of a specific task or the entire workflow."""

        # If a task ID is given, stream its results; otherwise, stream all tasks
        task_ids = self.task_by_id.keys() if task_id is None else [task_id]
        for task_id in task_ids:
            task = self.task_by_id[task_id]
            self.task_id = task_id

            # If the task is a non-LLM task, just yield its results
            if isinstance(task, GeneralTask):
                yield from stream_general_task(task, task_id)
                continue

            # Otherwise, it's an LLM task. Start by constructing the prompt
            messages = task.chat_prompt_template.format(**self.workflow_data)

            # Stream the output of the current task (including event signals)
            stream_res = yield from stream_llm_call_with_retries(
                messages,
                self.task_id,
                llm=task.llm or self.default_llm,
                parser=task.output_parser,
            )

            # Update the inputs with the output of the current task, save output etc.
            if task.output_handler is not None:  # First, run the task's output handler
                task.output_handler(stream_res.task_result)
            if self.handle_task_end is not None:  # Then, the overall handler or...
                self.handle_task_end(
                    workflow=self, task_id=task_id, response=stream_res
                )
            else:  # ... or the default behavior
                # Update the workflow engine's inputs with the parsed output
                output_name = (
                    task.get_output_name()
                    or self.output_name_template.format(task_id=self.task_id)
                )
                set_workflow_data_field(
                    self.workflow_data, output_name, stream_res.task_result
                )

                # Save output or parsed output (if an output directory is provided)
                if (dir := self.output_dir) is not None:
                    output_path = output_name.replace("_", "-")
                    if task.output_parser is None:
                        output_path = os.path.join(dir, f"{output_path}.txt")
                        save_text_to_file(stream_res.llm_output, output_path)
                        logger.info(f"Saved LLM output to '{output_path}'")
                    else:
                        # Assume it's JSON (otherwise should use handle_task_end)
                        output_path = os.path.join(dir, f"{output_path}.json")
                        save_text_to_file(str(stream_res.task_result), output_path)
                        logger.info(f"Saved parsed output to '{output_path}'")
