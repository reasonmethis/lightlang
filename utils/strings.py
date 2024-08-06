import json


def extract_json(text: str):
    """
    Extract a single JSON object or array from a string. Determines the first
    occurrence of '{' or '[', and the last occurrence of '}' or ']', then
    extracts the JSON structure accordingly. Returns a dictionary or list on
    success, throws on parse errors, including a bracket mismatch.
    """
    length = len(text)
    first_curly_brace = text.find("{")
    last_curly_brace = text.rfind("}")
    first_square_brace = text.find("[")
    last_square_brace = text.rfind("]")

    assert (
        first_curly_brace + first_square_brace > -2
    ), "No opening curly or square bracket found"

    if first_curly_brace == -1:
        first_curly_brace = length
    elif first_square_brace == -1:
        first_square_brace = length

    assert (first_curly_brace < first_square_brace) == (
        last_curly_brace > last_square_brace
    ), "Mismatched curly and square brackets"

    first = min(first_curly_brace, first_square_brace)
    last = max(last_curly_brace, last_square_brace)

    assert first < last, "No closing bracket found"

    return json.loads(text[first : last + 1])


def extract_json_object(text: str) -> dict:
    """
    Extract a single JSON object from a string. Determines the first
    occurrence of '{' and the last occurrence of '}', then
    extracts the JSON structure accordingly. Returns a dictionary on
    success, throws on parse errors, including a bracket mismatch.
    """
    first_curly_brace = text.find("{")
    last_curly_brace = text.rfind("}")

    if first_curly_brace == -1 or last_curly_brace == -1:
        raise ValueError("No JSON object found")

    if first_curly_brace > last_curly_brace:
        raise ValueError("Mismatched curly brackets")

    try:
        return json.loads(text[first_curly_brace : last_curly_brace + 1])
    except json.JSONDecodeError as e:
        raise ValueError(f"Error parsing JSON: {e}")


def extract_json_text(text: str, is_object=True) -> str:
    return json.dumps(
        extract_json_object(text) if is_object else extract_json(text), indent=2
    )


def format_with_dashes(input_string: str) -> str:
    return input_string.lower().replace(" ", "-").replace("_", "-")
