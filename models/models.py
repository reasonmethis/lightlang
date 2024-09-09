from typing import Any

from pydantic import BaseModel


class Doc(BaseModel):
    """Pydantic-compatible version of Langchain's Document."""

    text: str
    metadata: dict[str, Any]
