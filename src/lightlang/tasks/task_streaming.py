import logging
from collections.abc import Callable
from typing import Any, Generator, Literal

from pydantic import BaseModel

from lightlang.llms.llm import LLM
from lightlang.types.common import ChatMessage
from lightlang.tasks.task import GeneralTask
from lightlang.types.models import LLMResponseChunk

logger = logging.getLogger(__name__)


class TaskEvent(BaseModel):
    """Data that can be yielded in place of a token to signal any kind of event."""

    event: Literal["RESTART_TASK", "BEGIN_TASK", "END_TASK"]
    data: dict[str, Any] | None = None


class TaskStreamResult(BaseModel):
    """Result of a general task."""

    task_result: Any


class StreamResult(TaskStreamResult):
    """Result of a streaming task."""

    llm_output: str


DEFAULT_MAX_LLM_CALL_TRIES = 3


def stream_general_task(task: GeneralTask, task_id: int | str | None = None):
    """Stream the result of a general task."""
    task_id = task_id or task.task_id  # REVIEW: What if discrepancy?
    logger.info(f"Running General Task {task_id}...")
    yield TaskEvent(event="BEGIN_TASK", data={"task_id": task_id})

    # Stream the output of the task
    task_result = yield from task.stream()
    yield TaskEvent(
        event="END_TASK",
        data={"task_id": task_id, "task_result": task_result},
    )

    logger.info(f"Finished Task {task_id}.")
    return TaskStreamResult(task_result=task_result)  # REVIEW: Redundant?


def stream_llm_call_with_retries(
    messages: list[ChatMessage],
    task_id: int | str,
    llm: LLM,
    parser: Callable | None = None,  # Parser for the output (e.g. JSON extractor)
    max_tries: int = DEFAULT_MAX_LLM_CALL_TRIES,
) -> Generator[TaskEvent | LLMResponseChunk, None, StreamResult]: # TODO: Clean up
    # Call the LLM and yield as well as collect the streaming output
    for attempt in range(1, max_tries + 1):
        log_msg = f"Calling LLM for Task {task_id}"
        if attempt == 1:
            yield TaskEvent(event="BEGIN_TASK", data={"task_id": task_id})
        else:
            # Since this is a retry, signal the retry event
            yield TaskEvent(
                event="RESTART_TASK", data={"task_id": task_id, "attempt": attempt}
            )
            log_msg += f" (attempt {attempt}/{max_tries})"
        logger.info(log_msg)

        # Call the LLM and retry if there is an error
        llm_output = ""
        try:
            for chunk in llm.stream(messages=messages):
                if chunk.content is not None:
                    llm_output += chunk.content
                yield chunk
        except Exception as e:
            logger.warning(f"Error calling LLM: {(last_error:=e)}")
            continue  # Retry the call if there are more attempts left

        # Parse the output, break if successful, retry if there is an error
        try:
            parsed_output = llm_output if parser is None else parser(llm_output)
            break
        except Exception as e:
            logger.warning(f"Error parsing output: {(last_error:=e)}")
            print(messages)
            print(llm_output)

    else:  # No break = all attempts failed
        logger.error(f"Failed to parse output after {max_tries} attempts")
        raise last_error  # Will be defined if no break occurred

    # Signal the end of the task and return the parsed output
    event_data = {"llm_output": llm_output, "task_id": task_id}
    event_data |= {"parsed_output": parsed_output} if parser is not None else {}
    yield TaskEvent(event="END_TASK", data=event_data)

    logger.info(f"Finished Task {task_id}.")
    return StreamResult(llm_output=llm_output, task_result=parsed_output)
