from typing import TYPE_CHECKING

from lightlang.utils.import_utils import get_missing_dep_message

# Optional dependencies (some may not be needed here for type checking but let's put
# them all here for completeness)
if TYPE_CHECKING:
    import docx2txt  # type: ignore # noqa: F401
    from pypdf import PdfReader  # noqa: F401


def get_page_texts_from_pdf(file):
    try:
        from pypdf import PdfReader
    except ImportError:
        raise ImportError(get_missing_dep_message("pypdf", "ingest"))

    reader = PdfReader(file)
    return [page.extract_text() for page in reader.pages]


DEFAULT_PAGE_START = "PAGE {page_num}:\n"
DEFAULT_PAGE_SEP = "\n" + "-" * 3 + "\n\n"


def get_text_from_pdf(file, page_start=DEFAULT_PAGE_START, page_sep=DEFAULT_PAGE_SEP):
    return page_sep.join(
        [
            page_start.replace("{page_num}", str(i)) + x
            for i, x in enumerate(get_page_texts_from_pdf(file), start=1)
        ]
    )


def get_text_from_docx(file):
    try:
        from docx2txt import process
    except ImportError:
        raise ImportError(get_missing_dep_message("docx2txt", "ingest"))

    return process(file)
