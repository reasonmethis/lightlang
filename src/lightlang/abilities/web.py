import asyncio
import importlib.resources
import io
import logging
import os
from collections.abc import Iterable
from enum import Enum
from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

from lightlang.utils.import_utils import get_missing_dep_message

# Optional dependencies (some are not needed here for type checking but let's put
# them all here for completeness)
if TYPE_CHECKING:
    import aiohttp
    import trafilatura  # type: ignore # noqa: F401
    from bs4 import BeautifulSoup  # noqa: F401
    from fake_useragent import UserAgent  # type: ignore # noqa: F401
    from firecrawl import FirecrawlApp  # type: ignore # noqa: F401
    from serpapi import GoogleSearch  # type: ignore # noqa: F401

from lightlang.utils.async_utils import make_sync
from lightlang.utils.ingest import get_text_from_pdf
from lightlang.utils.output import format_error

from .config.web_config import default_header_template

logger = logging.getLogger(__name__)

TRAFILATURA_OUTPUT_FORMAT = os.getenv("TRAFILATURA_OUTPUT_FORMAT", "txt")

DEFAULT_URL_SCRAPE_METHOD = os.getenv("DEFAULT_URL_SCRAPE_METHOD", "REGULAR")
FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")


class LinkData(BaseModel):
    text: str | None = None
    error: str | None = None
    num_tokens: int | None = None

    @classmethod
    def from_raw_content(cls, content: str):
        """
        Return a LinkData instance from the HTML or plain text content of a URL.
        """
        if content.startswith("Error: "):
            return cls(error=content)
        if content.startswith(PDF_TEXT_PREFIX):
            return cls(text=content[len(PDF_TEXT_PREFIX) :])
        text = get_text_from_html(content)
        if is_html_text_ok(text):
            return cls(text=text)
        return cls(text=text, error="UNACCEPTABLE_EXTRACTED_TEXT")


class URLRetrievalData(BaseModel):
    urls: list[str]
    link_data_dict: dict[str, LinkData] = Field(default_factory=dict)
    num_ok_urls: int = 0
    idx_first_not_tried: int = 0  # different from len(link_data_dict) if urls repeat


#       "position": 1,
#       "title": "Coffee - Wikipedia",
#       "link": "https://en.wikipedia.org/wiki/Coffee",
#       "snippet": "Coffee is a brewed drink prepared from roasted coffee beans, the seeds of berries from certain Coffea species. From the coffee fruit, the seeds are ...",


SERP_API_DEFAULT_PARAMS = {
    "engine": "google",
    # "q": "groupm",
    # "location": "Austin, Texas, United States",
    "google_domain": "google.com",
    "gl": "us",
    "hl": "en",
    "api_key": os.getenv("SERP_API_KEY"),
}


def search_with_serp_api(queries: list[str], params: dict | None = None):
    """Perform a Google search using the SerpApi library."""
    try:
        from serpapi import GoogleSearch
    except ImportError:
        raise ImportError(get_missing_dep_message("serpapi", "web"))
    
    params = SERP_API_DEFAULT_PARAMS | (params or {})
    res: dict[str, list] = {}
    for query in queries:
        params["q"] = query
        logger.debug(f"Searching for: {query}")
        search = GoogleSearch(params)
        results = search.get_dict().get("organic_results")
        if results:
            for result in results[:3]:
                logger.info(f"Title: {result.get('title')}")
                logger.info(f"Link: {result.get('link')}")
                logger.info(f"Snippet: {result.get('snippet')}")
        else:
            logger.warning(f"No results found for: {query}")

        res[query] = results or []
    return res


BATCH_SIZE = 10


def get_url_content_or_error(url: str) -> LinkData:
    try:
        content_data = get_content_from_urls([url])
    except Exception as e:
        return LinkData(error=str(e))

    return content_data.link_data_dict[url]


def add_https_if_missing(url: str) -> str:
    if url.startswith("https:") or url.startswith("http:"):
        return url
    return "https://" + url


def get_content_from_urls(
    urls: list[str],
    batch_size: int = BATCH_SIZE,
    url_scrape_method: str = DEFAULT_URL_SCRAPE_METHOD,
) -> URLRetrievalData:
    match url_scrape_method:
        case "FIRECRAWL":
            return get_content_from_urls_firecrawl(urls, batch_size)
        case "REGULAR":
            return get_content_from_urls_regular(urls, batch_size)
        case _:
            raise ValueError(f"Invalid URL scrape method: {url_scrape_method}")


def get_content_from_urls_firecrawl(
    urls: list[str], batch_size: int = BATCH_SIZE
) -> URLRetrievalData:
    logger.info(
        f"Will fetch {len(urls)} urls using Firecrawl (batch size {batch_size} ignored)"
    )
    try:
        from firecrawl import FirecrawlApp
    except ImportError:
        raise ImportError(get_missing_dep_message("firecrawl", "web"))

    res = URLRetrievalData(urls=urls)

    app = FirecrawlApp(api_key=FIRECRAWL_API_KEY)

    while res.idx_first_not_tried < len(urls):
        url = add_https_if_missing(raw_url := urls[res.idx_first_not_tried])
        scrape_result = app.scrape_url(url, params={"formats": ["markdown"]})

        if markdown := scrape_result.get("markdown"):
            link_data = LinkData(text=markdown)
            res.num_ok_urls += 1
            logger.info(f"Fetched URL: {raw_url}, {len(markdown)} characters")
        else:
            error = scrape_result.get(
                "error", "Content was retrieved with no error but was empty."
            )
            link_data = LinkData(error=error)
            logger.info(f"Error fetching URL: {raw_url}, error: {error}")
        res.link_data_dict[raw_url] = link_data
        res.idx_first_not_tried += 1

    return res


def get_content_from_urls_regular(
    urls: list[str], batch_size: int = BATCH_SIZE
) -> URLRetrievalData:
    logger.info(f"Will fetch {len(urls)} urls")
    res = URLRetrievalData(urls=urls)

    # Fetch content from urls in batches
    batch_fetcher = get_batch_url_fetcher()

    while res.idx_first_not_tried < len(urls):
        batch_urls = urls[
            res.idx_first_not_tried : res.idx_first_not_tried + batch_size
        ]

        logger.info(f"Fetching batch of {len(batch_urls)} urls")
        batch_htmls = batch_fetcher([add_https_if_missing(url) for url in batch_urls])

        # Process fetched content
        for url, html in zip(batch_urls, batch_htmls):
            link_data = LinkData.from_raw_content(html)
            res.link_data_dict[url] = link_data
            res.idx_first_not_tried += 1
            if not link_data.error:
                res.num_ok_urls += 1
        logger.info("Fetched and processed batch of urls")

    return res


def get_batch_url_fetcher():
    return make_sync(afetch_urls_in_parallel_aiohttp)
    # def link_fetcher(links):
    #     return make_sync(afetch_urls_in_parallel_playwright)(
    #         links, callback=lambda url, html: print_no_newline(".")
    #     )
    # return link_fetcher


AIOHTTP_TIMEOUT_MS = 10000


async def afetch_urls_in_parallel_aiohttp(urls: list[str]) -> list[str]:
    """
    Asynchronously fetch multiple URLs in parallel using aiohttp.
    Return the HTML content of each URL. If there is an error in a particular URL,
    return the error message instead of that URL's content, starting with "Error: ".
    """
    try:
        import aiohttp
    except ImportError:
        raise ImportError(get_missing_dep_message("aiohttp", "web"))

    timeout = aiohttp.ClientTimeout(total=AIOHTTP_TIMEOUT_MS / 1000)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        tasks = [afetch_url_aiohttp(session, url) for url in urls]
        htmls = await asyncio.gather(*tasks)

    return htmls


PDF_TEXT_PREFIX = "PLAIN_TEXT[PDF]: "


async def afetch_url_aiohttp(
    session: "aiohttp.ClientSession", url: str, retries=3, backoff_factor=0.5
) -> str:
    """
    Asynchronously fetch a URL using an aiohttp session with retry and exponential backoff.
    It extracts text from PDFs and returns HTML content otherwise.
    """
    try:
        from fake_useragent import UserAgent
    except ImportError:
        raise ImportError(get_missing_dep_message("fake_useragent", "web"))

    header_template = default_header_template
    header_template["User-Agent"] = UserAgent().random

    for attempt in range(retries):
        try:
            async with session.get(url, headers=header_template) as response:
                response.raise_for_status()  # Raises exception for 4xx/5xx errors

                content_type = response.headers.get("Content-Type", "")
                if "application/pdf" in content_type:
                    # Handle PDF content
                    pdf_content = await response.read()
                    with io.BytesIO(pdf_content) as pdf_file:
                        res = PDF_TEXT_PREFIX + get_text_from_pdf(pdf_file)
                else:
                    res = await response.text()
                logger.info(f"Fetched URL: {url}")
                return res

        except Exception as e:
            # NOTE: specialize to ClientError, asyncio.TimeoutError, etc.
            if attempt == retries - 1:
                logger.info(f"Error fetching URL: {url}")
                logger.info(res := f"Error: {format_error(e)}")
                return res
            # Wait for a bit before retrying
            sleep_time = backoff_factor * (2**attempt)  # Exponential backoff
            await asyncio.sleep(sleep_time)
    raise Exception("Should not reach here")


class TextFromHtmlMode(Enum):
    BASIC = "BASIC"
    TRAFILATURA = "TRAFILATURA"


def get_text_from_html(
    html_content: str,
    mode=TextFromHtmlMode.TRAFILATURA,
    clean=True,
    break_multi_headlines=False,
) -> str:
    """
    Extract text from an HTML string.
    """
    if html_content.startswith("Error: "):
        return html_content

    if mode == TextFromHtmlMode.TRAFILATURA:
        try:
            import trafilatura
        except ImportError:
            raise ImportError(get_missing_dep_message("trafilatura", "web"))

        # Ensure we get a valid local path to the config file even in a zipapp context
        config_resource = importlib.resources.files(
            "lightlang.abilities.config"
        ).joinpath("trafilatura.cfg")
        with importlib.resources.as_file(config_resource) as config_file:
            text = trafilatura.extract(
                html_content,
                include_links=True,
                favor_recall=True,
                config=None,
                settingsfile=str(config_file),
                output_format=TRAFILATURA_OUTPUT_FORMAT,
            )
        # NOTE: can try extracting with different settings till get the length we want
        clean = False  # trafilatura already does some cleaning
    else:
        try:
            from bs4 import BeautifulSoup
        except ImportError:
            raise ImportError(get_missing_dep_message("beautifulsoup4", "web"))

        soup = BeautifulSoup(html_content, "html.parser")
        # Remove script and style elements
        for script_or_style in soup(["script", "style"]):
            script_or_style.extract()
        text = soup.get_text()

    if not text:  # it could be None
        text = ""
    elif clean:
        text = clean_text(text, break_multi_headlines=break_multi_headlines)
    return text


MIN_WORDS_PER_URL_CONTENT = 80


def is_html_text_ok(text: str) -> bool:
    """
    Return True if the text extracted from an HTML string appears to be from a
    successfully fetched website.

    Specifically, return True if it has at least MIN_WORDS_PER_URL_CONTENT words.
    """
    return len(text.split()) >= MIN_WORDS_PER_URL_CONTENT


def clean_text(text: str, break_multi_headlines=False):
    """
    Perform some basic cleaning on text extracted from HTML, such as removing
    consecutive blank lines and other unwanted whitespace.
    """
    # Break into lines and remove leading/trailing whitespace
    lines = (line.strip() for line in text.splitlines())

    if break_multi_headlines:
        # Break multi-headlines (2+ spaces) into a line each
        lines = (phrase.strip() for line in lines for phrase in line.split("  "))

    lines = remove_consecutive_blank_lines(lines)  # type: ignore
    text = "\n".join(lines)
    return text


def remove_consecutive_blank_lines(
    lines: Iterable[str], max_consecutive_blank_lines=1
) -> list[str]:
    """Remove consecutive blank lines from a list of lines."""
    new_lines = []
    num_consecutive_blank_lines = 0
    for line in lines:
        if line:
            # Non-blank line
            num_consecutive_blank_lines = 0
            new_lines.append(line)
        else:
            # Blank line
            num_consecutive_blank_lines += 1
            if num_consecutive_blank_lines <= max_consecutive_blank_lines:
                new_lines.append(line)
    return new_lines
