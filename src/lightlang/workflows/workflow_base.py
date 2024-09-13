from abc import ABC, abstractmethod


class BaseWorkflow(ABC):
    """Abstract base class for different types of workflows."""

    @abstractmethod
    def stream(self, task_id: int | str | None = None):
        """Stream the result of tasks according to the specific workflow type."""
        pass
