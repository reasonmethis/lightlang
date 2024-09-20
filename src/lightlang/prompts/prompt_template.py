from string import Formatter
from typing import Any

from pydantic import BaseModel, Field

from lightlang.workflows.workflow_data import WorkflowData, get_sub_workflow_data


class PromptInputConverter(BaseModel):
    """Converts and maps input data for use in prompt templates.

    Extracts values from nested dictionary and renames fields as needed.

    Attributes:
        input_field_base: Starting point for extracting data (e.g. "user.profile").
        input_field_map: Maps output keys to input data paths (e.g. {"name": "fullName"}).

    Example:
        converter = PromptInputConverter(
            input_field_base="user.profile",
            input_field_map={"name": "fullName", "age": "info.age"}
        )
        result = converter.get_inputs({"user": {"profile": {"fullName": "John", "info": {"age": 30}}}})
        # result: {"name": "John", "age": 30}
        # NOTE: "info." would also be interpreted as "info.age" in the input_field_map.
    """

    input_field_base: str = ""
    input_field_map: dict[str, str] = Field(default_factory=dict)

    def get_inputs(self, inputs: WorkflowData) -> WorkflowData:
        """Convert nested input data for use in prompt templates."""
        # Get the base fields (NOTE: Can be precomputed)
        inputs = get_sub_workflow_data(inputs, self.input_field_base)

        # Make a copy, then augment with the mapped fields
        inputs = inputs.copy()  # No need to deep copy since we're only adding new keys
        for field_name, field_path in self.input_field_map.items():
            # Parse the field path (NOTE: Can be precomputed)
            field_path = field_path.split(".") if field_path else []  # type: ignore
            # Traverse the field path to get the value
            val = inputs
            for field in field_path:
                val = val[field or field_name]  # Use field name if nothing after "."
            inputs[field_name] = val

        return inputs


class PromptTemplate:
    """Template for handling and formatting strings with named placeholders.

    Attributes:
        template: The template string.
        fields: List of fields (placeholders) in the template.
        input_converter: Converts and maps input data for use in the template.
    """

    def __init__(
        self,
        template_string: str,
        input_field_base: str = "",
        input_field_map: dict[str, str] | None = None,
    ) -> None:
        """Initialize the PromptTemplate with a template string.

        Args:
            template_string: The template string with placeholders.
            input_field_base: Starting point for extracting data (e.g. "user.profile").
            input_field_map: Maps output keys to input data paths (e.g. {"name": "fullName"}).

        Raises:
            ValueError: If a field name is not a valid identifier.
        """
        self._template = template_string
        self._fields = get_template_fields(template_string)

        # Check for invalid fields (e.g. "{not a valid identifier}")
        for field in self._fields:
            if not field.isidentifier():
                raise ValueError(
                    f"Invalid field name: {field}\n"
                    "If you want to include curly braces in the prompt, use double "
                    "curly braces ({{}})."
                )

        self.set_input_converter(input_field_base, input_field_map)

    def get_template(self) -> str:
        """Get the template string."""
        return self._template
    
    def get_fields(self) -> list[str]:
        """Get the fields (placeholders) in the template string."""
        return self._fields
    
    def set_input_converter(
        self, input_field_base: str = "", input_field_map: dict[str, str] | None = None
    ):
        """Set the input converter for this template.

        Args:
            input_field_base: Starting point for extracting data (e.g. "user.profile").
            input_field_map: Maps output keys to input data paths (e.g. {"name": "fullName"}).
        """
        self.input_converter = (
            PromptInputConverter(
                input_field_base=input_field_base, input_field_map=input_field_map or {}
            )
            if input_field_base or input_field_map
            else None
        )

    def _merge_inputs(self, *args, **kwargs) -> dict:
        """Merge multiple dictionaries of inputs into a single dictionary.

        Args:
            *args: Dictionaries of key-value pairs of fields to be filled in the template.
            **kwargs: Key-value pairs of fields to be filled in the template.

        Returns:
            A single dictionary of all inputs.
        """
        inputs: dict = {}
        for input_data in args:
            if isinstance(input_data, dict):
                inputs.update(input_data)
            else:
                raise TypeError("Positional arguments must be dictionaries.")
        inputs.update(kwargs)
        return inputs

    def _format(self, inputs: dict) -> str:
        """Fill in the provided fields and raise an error if any field is missing.

        Args:
            inputs: A dictionary of key-value pairs of fields to be filled in the template.

        Returns:
            The formatted string.

        Raises:
            KeyError: If a field is missing in the inputs.
        """
        if self.input_converter:
            inputs = self.input_converter.get_inputs(inputs)
        return self._template.format(**inputs)

    def format(self, *args: dict[str, Any], **kwargs: Any) -> str:
        """Fill in the provided fields and raise an error if any field is missing.

        Most of the time, you will want to call this method either with a single dictionary 
        containing the values to substitute for the placeholders or with keyword arguments
        representing the values to substitute for the placeholders. If you pass both or if you 
        include more than one dictionary in the positional arguments, the dictionaries will be
        merged into a single dictionary before filling in the template.

        Args:
            *args: Dictionaries of key-value pairs of fields to be filled in the template.
            **kwargs: Key-value pairs of fields to be filled in the template.

        Returns:
            The formatted string.

        Raises:
            KeyError: If a field is missing in the inputs.
        """
        # Consolidate all inputs into a single dictionary and format the string
        return self._format(self._merge_inputs(*args, **kwargs))

    def format_partial(self, *args, **kwargs) -> str:
        """Fill in the provided fields and leave missing fields as they are.

        Most of the time, you will want to call this method either with a single dictionary
        containing the values to substitute for the placeholders or with keyword arguments
        representing the values to substitute for the placeholders. If you pass both or if you
        include more than one dictionary in the positional arguments, the dictionaries will be
        merged into a single dictionary before filling in the template.

        Args:
            *args: Dictionaries of key-value pairs of fields to be filled in the template.
            **kwargs: Key-value pairs of fields to be filled in the template.

        Returns:
            The formatted string.
        """
        inputs = self._merge_inputs(*args, **kwargs)
        inputs = inputs | {k: "{" + k + "}" for k in self._fields if k not in inputs}
        return self._format(inputs)

    def make_partial(self, *args, **kwargs) -> "PromptTemplate":
        """Return a new PromptTemplate instance with some fields filled in.

        Most of the time, you will want to call this method either with a single dictionary
        containing the values to substitute for the placeholders or with keyword arguments
        representing the values to substitute for the placeholders. If you pass both or if you
        include more than one dictionary in the positional arguments, the dictionaries will be
        merged into a single dictionary before filling in the template.

        Args:
            *args: Dictionaries of key-value pairs of fields to be filled in the template.
            **kwargs: Key-value pairs of fields to be filled in the template.

        Returns:
            A new instance with partially filled fields.
        """
        return PromptTemplate(self.format_partial(*args, **kwargs))


def get_template_fields(template_string: str) -> list[str]:
    """Get the fields (placeholders) in a template string.

    Args:
        template_string: The template string.

    Returns:
        A list of field names.
    """
    return [field for _, field, _, _ in Formatter().parse(template_string) if field]
