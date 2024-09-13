from typing import Literal

from lightlang.utils.core import DELIMITER80

Feature = Literal["web", "ingest"]


def get_missing_dep_message(module_name: str, feature: Feature) -> str:
    return (
        DELIMITER80 + "\nYou are trying to use an optional feature of lightlang, which "
        f"needs additional dependencies (such as `{module_name}`) beyond the core "
        "lightlang dependencies. To install them, please run:\n\n"
        f"pip install lightlang[{feature}]\n" + DELIMITER80
    )
