import os
from typing import Callable

from utils.core import save_text_to_file
from utils.log import setup_logger
from utils.prompt_template import PromptTemplate
from workflow_engine import Task, WorkflowEngine

logger = setup_logger()


class SequentialWorkflow:
    """Agentic workflow with sequential tasks (no branching or loops)."""

    def __init__(
        self,
        workflow_engine: WorkflowEngine,
        tasks: list[Task | PromptTemplate],
        handle_task_end: Callable | None = None,
        init_task_id: int = 1,
        output_name_template: str = "task_{task_id}_output",  # For tasks w/o output_name
        output_dir: str | None = None,
    ):
        self.workflow_engine = workflow_engine

        # Convert PromptTemplate instances to Task instances
        self.tasks = [
            Task(prompt_template=t) if isinstance(t, PromptTemplate) else t
            for t in tasks
        ]

        self.handle_task_end = handle_task_end  # Takes this instance and stream result
        self.task_id = None
        self.output_name_template = output_name_template
        self.output_dir = output_dir

    def stream(self):
        for task in self.tasks:
            self.task_id = task.task_id or ((self.task_id or 0) + 1)
            prompt = task.prompt_template.format(**self.workflow_engine.inputs)
            parser = task.output_parser

            # Stream the output of the current task
            stream_res = yield from self.workflow_engine.stream(
                prompt, self.task_id, parser=task.output_parser
            )

            # Update the inputs with the output of the current task, save output etc.
            if task.output_handler is not None:  # First, run the task's output handler
                task.output_handler(stream_res.parsed_output)
            if self.handle_task_end is not None:  # Then, the overall handler or...
                self.handle_task_end(workflow=self, curr_task=task, response=stream_res)
            else:  # ... or the default behavior
                output_name = task.output_name or self.output_name_template.format(
                    task_id=self.task_id
                )
                self.workflow_engine.inputs[output_name] = str(stream_res.parsed_output)

                # Save output or parsed output (if an output directory is provided)
                if (dir := self.output_dir) is not None:
                    output_path = output_name.replace("_", "-")
                    if parser is None:
                        output_path = os.path.join(dir, f"{output_path}.txt")
                        save_text_to_file(stream_res.llm_output, output_path)
                        logger.info(f"Saved LLM output to '{output_path}'")
                    else:
                        # Assume it's JSON (otherwise should use handle_task_end)
                        output_path = os.path.join(dir, f"{output_path}.json")
                        save_text_to_file(str(stream_res.parsed_output), output_path)
                        logger.info(f"Saved parsed output to '{output_path}'")