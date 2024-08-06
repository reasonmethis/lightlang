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
