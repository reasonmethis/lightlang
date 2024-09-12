# LightLang: A Lightweight Framework for LLM Workflows

[![PyPI version](https://img.shields.io/pypi/v/lightlang.svg)](https://pypi.python.org/pypi/lightlang)
[![License](https://img.shields.io/github/license/reasonmethis/lightlang)](LICENSE)[![Python versions](https://img.shields.io/pypi/pyversions/lightlang.svg)](https://pypi.python.org/pypi/lightlang)


A lightweight, ergonomic, close-to-the-metal framework for using Large Language Models (LLMs) and building agentic workflows.

## Table of Contents

- [Introduction](#introduction)
    - [Features](#features)
    - [Why LightLang](#why-lightlang)
- [Getting Started](#getting-started)
    - [Prerequisites](#prerequisites)
    - [Installation](#installation)
    - [Configuration](#configuration)
- [Usage](#usage)
    - [Getting Started with LLM Responses](#getting-started-with-llm-responses)
        - [Basic Single Prompt](#basic-single-prompt)
        - [System Message, Temperature Control, Streaming, and Multi-Turn Conversation](#system-message-temperature-control-streaming-and-multi-turn-conversation)
        - [Dynamic Prompt Creation Using `PromptTemplate`](#dynamic-prompt-creation-using-prompttemplate)
    - [Multi-Turn Templating with `ChatPromptTemplate`](#multi-turn-templating-with-chatprompttemplate)
        - [Example 1: Initializing with a List of Messages](#example-1-initializing-with-a-list-of-messages)
        - [Example 2: Initializing from a Template String](#example-2-initializing-from-a-template-string)
    - [Performing Google Searches, Web Scraping, and PDF Ingestion](#performing-google-searches-web-scraping-and-pdf-ingestion)
        - [Performing Google Searches](#performing-google-searches)
        - [Web Scraping](#web-scraping)
        - [Ingesting PDF Content](#ingesting-pdf-content)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Introduction

LightLang is a lightweight, ergonomic framework designed to help developers quickly build and manage workflows powered by Large Language Models (LLMs). Whether you're working with OpenAI's GPT models, Anthropic's Claude, or other models available via OpenRouter, LightLang provides a simple and direct way to integrate these models into your applications. 

### Why LightLang

**LightLang** is designed for developers who want simplicity and flexibility without sacrificing power. It stands apart from other frameworks like LangChain and LlamaIndex by focusing on:

- **Lightweight Design**: LightLang is lean, with fewer dependencies, making it faster to install and easier to integrate into existing projects.
- **Fine Control**: While other frameworks introduce high-level abstractions that can obscure LLM interactions, LightLang gives developers direct access to model configurations and workflows.
- **Extensibility**: LightLang goes beyond just LLM interactions, offering built-in tools for web scraping, Google searches, and PDF ingestion. This makes it a one-stop solution for building data-driven LLM applications.
- **Ergonomic API**: Designed with developers in mind, LightLang provides an intuitive interface that minimizes boilerplate and focuses on the essentials, allowing for rapid prototyping and development.

### Features

- **Multi-Provider Support**: Seamless integration with popular LLM providers like OpenAI and OpenRouter, enabling access to models such as GPT-4, Claude, and many others.
- **Dynamic Prompting**: Create reusable, dynamic prompts with `PromptTemplate` and `ChatPromptTemplate`, allowing you to easily format and adjust prompts on the fly.
- **Multi-Turn Conversations**: Manage context and multi-turn conversations with LLMs, making it easier to build interactive agents and assistants.
- **Extended Capabilities**: Perform web scraping, Google searches, and PDF ingestion to enhance LLM workflows with external data.
- **Close-to-the-Metal Design**: LightLang offers a simple interface, giving developers full control over LLM parameters (like temperature and max tokens), streaming, and system messages without unnecessary abstractions.
- **Agentic Workflow Support**: Build complex agent-based workflows that maintain state and context across multiple interactions.

## Getting Started

### Prerequisites

- Python 3.11+
- An API key for a provider like OpenAI or OpenRouter

### Installation

You can install LightLang from PyPI using `pip`:

```bash
pip install lightlang
```

### Configuration

LightLang uses environment variables to configure access to various LLM providers and external services:

- **`OPENAI_API_KEY`**: Set this to your OpenAI API key if you want to use models from OpenAI (e.g., GPT-4o).
- **`OPENROUTER_API_KEY`**: Set this to your OpenRouter API key if you want to access multiple LLMs available via the OpenRouter API (e.g., Claude, LLaMA).
- **`SERPAPI_API_KEY`**: Set this if you'd like to perform Google searches via the SerpAPI service.
- **`FIRECRAWL_API_KEY`**: Required for scraping web pages the Firecrawl API (note: there is an alternative method for web scraping without an API key).

To configure these environment variables, you can set them directly in your shell or add them to a `.env` file in your project.

## Usage

### Getting Started with LLM Responses

This section walks you through progressively more advanced examples of interacting with LLMs using LightLang. We start with simple single prompts and move to more complex scenarios, including dynamic prompts, streaming, and multi-turn conversations.

#### Basic Single Prompt

The `LLM` class provides a simple unified interface for calling models from multiple providers, such as OpenAI and OpenRouter (which itself provides access to hundreds of top models). To start, let's show a simple example of sending a single prompt and getting a response.

```python
from lightlang.llms.llm import LLM

# Initialize the LLM for OpenAI with the 'gpt-4o-mini' model
llm = LLM(provider="openai", model="gpt-4o-mini")

# Single user message
response = llm.invoke("What is the capital of France?")
print(response.content)
```

#### System Message, Temperature Control, Streaming, and Multi-Turn Conversation

This example demonstrates several features together:
- Using OpenRouter as a provider to access Claude 3.5 Sonnet 
- Setting a system message to control the assistant's behavior.
- Adjusting the `temperature` to control creativity.
- Streaming the response in real-time.
- Maintaining context across multiple turns in a conversation.

```python
from lightlang.llms.llm import LLM

# Initialize the LLM with temperature control
llm = LLM(provider="openrouter", model="anthropic/claude-3.5-sonnet", temperature=0.7)

# System message for context, followed by a user prompt
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Tell me a short story about a brave knight."}
]

# Stream the response in real-time
for chunk in llm.stream(messages):
    if chunk.content:
        print(chunk.content, end="")

# Follow-up message to continue the conversation
messages.append({"role": "user", "content": "What happens to the knight at the end?"})

# Get the next part of the story while maintaining context
response = llm.invoke(messages) # We can also stream the response here
print(response.content)
```

#### Dynamic Prompt Creation Using `PromptTemplate`

Here we use `PromptTemplate` to dynamically create a prompt with placeholders that get filled at runtime. Additionally, we set parameters like `temperature` and `max_tokens` to control the model's behavior.

```python
from lightlang.llms.llm import LLM
from lightlang.prompts.prompt_template import PromptTemplate

# Initialize the LLM with model configuration
llm = LLM(
    provider="openai", 
    model="gpt-4o-mini", 
    temperature=0.5,  # Balanced creativity
    model_config={"max_tokens": 150}  # Limit the response to 150 tokens
)

# Define a prompt template with placeholders
template = PromptTemplate("Explain the importance of {concept} in {field}.")

# Dynamically substitute the placeholders
prompt = template.format(concept="machine learning", field="healthcare")

# Invoke the LLM with the dynamically generated prompt
response = llm.invoke(prompt)
print(response.content)
```

### Multi-Turn Templating with `ChatPromptTemplate`

The `ChatPromptTemplate` class allows you to define and structure multi-turn conversations with Large Language Models (LLMs), including system messages. You can initialize it in two ways—either with a list of chat messages or from a template string. Both methods support the use of placeholders (denoted by curly braces) for dynamically inserting values into the messages at runtime. If you need to include actual curly braces in the message content, simply use double braces (`{{` and `}}`).

#### Example 1: Initializing with a List of Messages

You can directly pass a list of messages to `ChatPromptTemplate`, where each message contains a `role` (such as `system`, `user`, or `assistant`) and `content` with optional placeholders for dynamic insertion. Any text in curly braces will be treated as a placeholder.

```python
from lightlang.llms.llm import LLM
from lightlang.prompts.chat_prompt_template import ChatPromptTemplate

# Initialize the LLM
llm = LLM(provider="openrouter", model="meta-llama/llama-3-8b-instruct:free")

# Initialize the template
messages = [
    {"role": "system", "content": "You are an assistant specialized in {specialty}."},
    {"role": "user", "content": "What are some best practices in {field}?"}
]

chat_prompt = ChatPromptTemplate(message_templates=messages)

# Format the template with dynamic values
formatted_messages = chat_prompt.format(specialty="software engineering", field="DevOps")

# Invoke the LLM with the formatted messages
response = llm.invoke(formatted_messages)
print(response.content)
```

#### Example 2: Initializing from a Template String

You can also initialize a `ChatPromptTemplate` from a structured template string where messages are enclosed within `<system>...</system>`, `<user>...</user>`, and `<assistant>...</assistant>` tags. Placeholders are inserted the same way, using curly braces.

```python
from lightlang.prompts.chat_prompt_template import ChatPromptTemplate

# Template string for multi-step conversation
template_str = '''
<name support_flow>
<system>
You are a customer support assistant specialized in {specialty}.
</system>
<user>
I am having trouble with {issue}. Can you help?
</user>
'''

# Initialize the template from the string
chat_prompt = ChatPromptTemplate.from_string(template_str)

# Format the template with dynamic values
messages = chat_prompt.format(specialty="password resets", issue="resetting my password")

# Invoke the LLM as before ...
```

### Performing Google Searches, Web Scraping, and PDF Ingestion

This section walks through examples of how to use LightLang's capabilities for performing Google searches, web scraping (both regular and Firecrawl methods), and ingesting content from PDFs.

#### Performing Google Searches

LightLang integrates with SerpAPI to perform Google searches and retrieve search results. You can use the `search_with_serp_api` function to search for queries and get top results.

Example: Performing a Google Search

```python
from lightlang.abilities.web import search_with_serp_api

# Search for queries using SerpAPI
queries = ["Artificial Intelligence", "Latest Machine Learning trends"]
results = search_with_serp_api(queries)

# Print the first result for each query
for query, result in results.items():
    if result:
        print(f"Results for {query}:")
        print(f"Title: {result[0].get('title')}")
        print(f"Link: {result[0].get('link')}")
        print(f"Snippet: {result[0].get('snippet')}")
```

#### Web Scraping

LightLang provides capabilities to scrape content from web pages. You can either use the regular scraping method or integrate with the Firecrawl API.

Example: Scraping a Web Page Using Firecrawl.

Firecrawl provides a convenient way to scrape web pages and return clean Markdown content. To use it, ensure that you have a Firecrawl API key and set the `FIRECRAWL_API_KEY` environment variable.

```python
from lightlang.abilities.web import get_content_from_urls

# List of URLs to scrape
urls = ["https://en.wikipedia.org/wiki/Artificial_intelligence"]

# Fetch content from the URLs using Firecrawl
scraped_data = get_content_from_urls(urls, url_scrape_method="FIRECRAWL")

# Print the scraped content
for url, link_data in scraped_data.link_data_dict.items():
    if link_data.text:
        print(f"Content from {url}:\n{link_data.text}")
    else:
        print(f"Error scraping {url}: {link_data.error}")
```

Scraping the content of a web page using the regular method is similar to the Firecrawl method. You can use the `get_content_from_urls` function with the `url_scrape_method` parameter set to `"REGULAR"`. The regular method uses the powerful `trafilatura` library to extract content from web pages without "fluff" like ads and navigation links.

#### Ingesting PDF Content

LightLang can ingest content from PDF files using the `get_text_from_pdf` utility. This allows you to extract text from each page of a PDF and use it for further processing.

Example: Extracting Text from a PDF

```python
from lightlang.utils.ingest import get_text_from_pdf

# Open the PDF file
with open("path/to/your/document.pdf", "rb") as pdf_file:
    # Extract text from the PDF
    extracted_text = get_text_from_pdf(pdf_file)

# Print the extracted text
print(extracted_text)
```

## Contributing

We welcome contributions from the community! To contribute, please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Commit your changes.
4. Push your changes to your fork and submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

## Contact

For any questions, issues, or feedback, please feel free to open an issue on GitHub.