from typing import Any

import pandas as pd


def transform_rows_to_csv(rows: list[dict[str, Any]]) -> str:
    return pd.DataFrame(rows).to_csv(index=False)


def save_row_dicts_as_csv(rows: list[dict[str, Any]], output_path: str):
    csv_output = transform_rows_to_csv(rows)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(csv_output)
