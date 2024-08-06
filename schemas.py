from typing import Any

from pydantic import BaseModel

class Doc(BaseModel):
    """A text document along with its associated metadata."""

    text: str
    metadata: dict[str, Any]