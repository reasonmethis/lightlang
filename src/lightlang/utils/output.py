import math
from typing import Literal


def print_no_newline(*args, **kwargs) -> None:
    """
    Print a string without a newline character.

    Args:
    *args: The strings to be printed.
    **kwargs: Additional keyword arguments to be passed to the print function.

    Example:
        print_no_newline("Hello,", "world!")  # Output: "Hello, world!"
    """
    print(*args, end="", **kwargs)


def format_error(e: Exception) -> str:
    """
    Format an exception to include both its type and message.

    Args:
    e (Exception): The exception to be formatted.

    Returns:
    str: A string representation of the exception, including its type and message.

    Example:
        try:
            raise ValueError("An example error")
        except ValueError as e:
            formatted_exception = format_exception(e)
            print(formatted_exception)  # Output: "ValueError: An example error"
    """
    try:
        return f"{type(e).__name__}: {e}"
    except Exception:
        return f"Unknown error: {e}"


class ProgressTracker:
    def __init__(
        self,
        expected_final_val: float,
        thresh_val_adjust: float | Literal["half"] = "half",
        curr_val: float = 0.0,
    ) -> None:
        self.curr_val = curr_val
        self._expected_final_val = expected_final_val
        self._thresh_val_adjust = (
            expected_final_val * 0.5 if thresh_val_adjust == "half" else thresh_val_adjust
        )

        self._tot_val_past_thresh = expected_final_val - self._thresh_val_adjust
        self._progress_at_thresh = self._thresh_val_adjust / expected_final_val
        self._tot_progress_past_thresh = 1.0 - self._progress_at_thresh

    def get_frac_progress(self, new_curr_val: float | None = None) -> float:
        if new_curr_val is not None:
            self.curr_val = new_curr_val

        # If the current value is less than the threshold, use a simple formula
        if self.curr_val < self._thresh_val_adjust:
            return self.curr_val / self._expected_final_val

        # Otherwise, use an inverse exponential formula to smoothly taper off the rate
        # NOTE: Using e specifically ensures the derivatives match at the threshold
        val_past_thresh = self.curr_val - self._thresh_val_adjust
        naive_progress_past_thresh = val_past_thresh / self._tot_val_past_thresh
        progress_past_thresh = 1.0 - 1 / math.exp(naive_progress_past_thresh)
        progress_past_thresh *= 1.0 - self._progress_at_thresh

        return self._progress_at_thresh + progress_past_thresh

    def get_pct_progress(self, new_curr_val: float | None = None) -> float:
        return self.get_frac_progress(new_curr_val) * 100

    def increment_and_get_frac_progress(self, val_increment: float = 1.0) -> float:
        return self.get_frac_progress(self.curr_val + val_increment)

    def increment_and_get_pct_progress(self, val_increment: float = 1.0) -> float:
        return self.get_frac_progress(self.curr_val + val_increment) * 100.0
