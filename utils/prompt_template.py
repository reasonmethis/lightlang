from string import Formatter


class PromptTemplate:
    """Template for handling and formatting strings with named placeholders.

    Attributes:
        template: The template string.
        fields: List of fields (placeholders) in the template.
    """

    def __init__(self, template_string: str) -> None:
        """Initialize the PromptTemplate with a template string.

        Args:
            template_string: The template string with placeholders.

        Raises:
            ValueError: If a field name is not a valid identifier.
        """
        self.template = template_string
        self.fields = [f for _, f, _, _ in Formatter().parse(template_string) if f]

        # Check for invalid fields (e.g. "{not a valid identifier}")
        for field in self.fields:
            if not field.isidentifier():
                raise ValueError(
                    f"Invalid field name: {field}\n"
                    "If you want to include curly braces in the prompt, use double "
                    "curly braces ({{}})."
                )

    def format(self, **inputs) -> str:
        """Fill in the provided fields and raise an error if any field is missing.

        Args:
            **inputs: Key-value pairs of fields to be filled in the template.

        Returns:
            The formatted string.

        Raises:
            KeyError: If a field is missing in the inputs.
        """
        return self.template.format(**inputs)
    
    def format_partial(self, **inputs) -> str:
        """Fill in the provided fields and leave missing fields as they are.

        Args:
            **inputs: Key-value pairs of fields to be filled in the template.

        Returns:
            The formatted string.
        """
        new_inputs = inputs | {k: "{" + k + "}" for k in self.fields if k not in inputs}
        return self.template.format(**new_inputs)

    def make_partial(self, **inputs) -> "PromptTemplate":
        """Return a new PromptTemplate instance with some fields filled in.

        Args:
            **inputs: Key-value pairs of fields to be filled in the template.

        Returns:
            A new instance with partially filled fields.
        """
        return PromptTemplate(self.format_partial(**inputs))
