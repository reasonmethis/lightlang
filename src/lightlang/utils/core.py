import json
import os
from pprint import pprint
from typing import Literal, overload

DELIMITER80 = "-" * 80
DELIMITER80_NL = DELIMITER80 + "\n"
DELIMITER80_NLNL = DELIMITER80 + "\n\n"
DELIMITER80_EQ = "=" * 80


@overload
def load_text_file(file_path: str) -> str: ...


@overload
def load_text_file(file_path: str, default_to_none: Literal[False]) -> str: ...


@overload
def load_text_file(file_path: str, default_to_none: Literal[True]) -> str | None: ...


def load_text_file(file_path: str, default_to_none: bool = False) -> str | None:
    try:
        with open(file_path, encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        if default_to_none:
            return None
        raise e


def save_text_to_file(text: str, file_path: str, ensure_dir: bool = False):
    if ensure_dir:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(text)


def load_json_file(file_path: str) -> dict:
    with open(file_path, encoding="utf-8") as f:
        return json.load(f)


def save_json_file(data: dict, file_path: str, ensure_dir: bool = False):
    if ensure_dir:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def ensure_dir_exists(*path_parts):
    dir_path = os.path.join(*path_parts)
    os.makedirs(dir_path, exist_ok=True)
    return dir_path


def pprint_and_wait(*args):
    for arg in args:
        pprint(arg)
    input("Press Enter to continue...")


def format_model_name(model_name: str) -> str:
    return model_name.lower().split("/")[-1].replace(":", "-")
