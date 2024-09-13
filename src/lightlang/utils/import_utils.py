from typing import Literal

from lightlang.utils.core import DELIMITER80
from lightlang.utils.strings import overwrite_middle

Feature = Literal["web", "ingest"]


def get_missing_dep_message(module_name: str, feature: Feature) -> str:
    return (
        "  \n"  # Use double space in case it's rendered as Markdown
        + overwrite_middle(DELIMITER80, "  Please Install Optional Feature  ")
        + "  \nYou are trying to use an optional feature of LightLang called "
        f"'{feature}'. It needs additional dependencies (such as `{module_name}`) "
        "beyond the core LightLang dependencies. To install them, please run:\n"
        f"```\npip install lightlang[{feature}]\n```\n" + DELIMITER80
    )
