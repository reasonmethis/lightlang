import logging
from collections.abc import Callable
from typing import Generator

from lightlang.llms.llm import LLM
from lightlang.types.common import (
    ChatMessage,
    StreamResult,
    TaskEvent,
)
from lightlang.types.models import LLMTaskResponseChunk

logger = logging.getLogger(__name__)

DEFAULT_MAX_LLM_CALL_TRIES = 3


def stream_llm_call_with_retries(
    messages: list[ChatMessage],
    task_id: int | str,
    llm: LLM,
    parser: Callable | None = None,  # Parser for the output (e.g. JSON extractor)
    max_retries: int | None = None,  # Defaults to DEFAULT_MAX_LLM_CALL_TRIES
) -> Generator[LLMTaskResponseChunk, None, StreamResult]:
    # Call the LLM and yield as well as collect the streaming output
    for attempt in range(1, (max_retries or DEFAULT_MAX_LLM_CALL_TRIES) + 1):
        log_msg = f"Calling LLM for Task {task_id}"
        if attempt == 1:
            yield LLMTaskResponseChunk(
                task_event=TaskEvent(event="BEGIN_TASK", data={"task_id": task_id})
            )
        else:
            # Since this is a retry, signal the retry event
            yield LLMTaskResponseChunk(
                task_event=TaskEvent(
                    event="RESTART_TASK", data={"task_id": task_id, "attempt": attempt}
                )
            )
            log_msg += f" (attempt {attempt}/{max_retries})"
        logger.info(log_msg)

        # Call the LLM and retry if there is an error
        llm_output = ""
        try:
            for chunk in llm.stream(messages=messages):
                if chunk.content is not None:
                    llm_output += chunk.content
                yield LLMTaskResponseChunk.from_llm_response_chunk(chunk)
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
        logger.error(
            f"Failed to parse output after {max_retries} attempts",
            extra={"llm_output": llm_output},
        )
        raise last_error  # Will be defined if no break occurred

    # Signal the end of the task and return the parsed output
    event_data = {"llm_output": llm_output, "task_id": task_id}
    event_data |= {"parsed_output": parsed_output} if parser is not None else {}
    yield LLMTaskResponseChunk(task_event=TaskEvent(event="END_TASK", data=event_data))

    return StreamResult(llm_output=llm_output, task_result=parsed_output)
