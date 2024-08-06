import os
from typing import Any, Callable, Literal

from dotenv import load_dotenv
from pydantic import BaseModel

from utils.llm import ChatMessage, OpenRouterLLM
from utils.log import setup_logger
from utils.prompt_template import PromptTemplate

load_dotenv()
logger = setup_logger()


MODEL = os.getenv("MODEL")
TEMPERATURE = float(os.getenv("TEMPERATURE"))


class StreamEvent(BaseModel):
    """Data that can be yielded in place of a token to signal any kind of event."""

    event: Literal["RESTART_TASK", "BEGIN_TASK", "END_TASK"]
    data: dict[str, Any] | None = None


class StreamResult(BaseModel):
    """Result of a streaming task."""

    llm_output: str
    parsed_output: Any


class Task:
    def __init__(
        self,
        prompt_template: PromptTemplate,
        *,
        output_parser: Callable | None = None,
        output_handler: Callable | None = None,
        output_name: str | None = None,
        task_id: int | str | None = None,
    ):
        self.prompt_template = prompt_template
        self.output_parser = output_parser
        self.output_name = output_name
        self.output_handler = output_handler
        self.task_id = task_id


DEFAULT_MAX_LLM_CALL_TRIES = 3


class WorkflowEngine:
    """Engine for running a workflow of tasks using an LLM."""

    def __init__(self, llm: OpenRouterLLM, inputs: dict[str, str]):
        self.llm = llm

        # inputs is a dict of initial variables available for use in tasks' prompts.
        # After each task, the result of the task is added to the inputs dict.
        # Since the same workflow engine can be used for multiple workflows, tasks
        # from one workflow can use the outputs of tasks from another workflow.
        self.inputs = inputs

    def stream(
        self,
        messages: str | list[ChatMessage],
        task_id: int,
        parser: Callable | None = None,  # Parser for the output (e.g. JSON extractor)
        max_tries: int = DEFAULT_MAX_LLM_CALL_TRIES,
    ):
        # Call the LLM and yield as well as collect the streaming output
        for attempt in range(1, max_tries + 1):
            log_msg = f"Calling LLM for Task {task_id}"
            if attempt == 1:
                yield StreamEvent(event="BEGIN_TASK", data={"task_id": task_id})
            else:
                # Since this is a retry, signal the retry event
                yield StreamEvent(event="RESTART_TASK", data={"attempt": attempt})
                log_msg += f" (attempt {attempt}/{max_tries})"
            logger.info(log_msg)

            # Call the LLM and retry if there is an error
            llm_output = ""
            try:
                for content in self.llm.stream(messages=messages):
                    llm_output += content
                    yield content
            except Exception as e:
                logger.warning(f"Error calling LLM: {(last_error:=e)}")
                continue  # Retry the call if there are more attempts left

            # Parse the output, break if successful, retry if there is an error
            try:
                parsed_output = llm_output if parser is None else parser(llm_output)
                break
            except Exception as e:
                logger.warning(f"Error parsing output: {(last_error:=e)}")
        else:  # No break = all attempts failed
            logger.error(f"Failed to parse output after {max_tries} attempts")
            raise last_error  # Will be defined if no break occurred

        # Signal the end of the task and return the parsed output
        event_data = {"llm_output": llm_output, "task_id": task_id}
        event_data |= {"parsed_output": parsed_output} if parser is not None else {}
        yield StreamEvent(event="END_TASK", data=event_data)

        logger.info(f"Finished Task {task_id}.")
        return StreamResult(llm_output=llm_output, parsed_output=parsed_output)
