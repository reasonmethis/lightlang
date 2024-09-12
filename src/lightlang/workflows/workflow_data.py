from typing import Any

# TODO: Turn into a class, so that a sub-workflow-data is also a WorkflowData instance
WorkflowData = dict[str, Any]


def get_sub_workflow_data(
    workflow_data: WorkflowData, field_path: str | None
) -> WorkflowData:
    if not field_path:
        return workflow_data

    for field in field_path.split("."):
        workflow_data = workflow_data[field]

    return workflow_data


def set_workflow_data_field(
    workflow_data: WorkflowData, field_path: str, value: Any
) -> None:
    fields = field_path.split(".")
    for field in fields[:-1]:
        workflow_data = workflow_data.setdefault(field, {})
    workflow_data[fields[-1]] = value
