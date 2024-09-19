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

LightLang is a lightweight, ergonomic framework designed to help developers quickly build and manage workflows powered by Large Language Models (LLMs). Whether you're working with OpenAI's models, Anthropic's Claude, or other models available via OpenRouter, LightLang provides a simple and direct way to integrate these models into your applications.

### Why LightLang

**LightLang** is designed for developers who want simplicity and flexibility. It stands apart from other frameworks like LangChain and LlamaIndex by focusing on:

- **Lightweight Design**: LightLang is lean, with fewer dependencies, making it faster to install and easier to integrate into existing projects.
- **Fine Control**: While other frameworks introduce high-level abstractions that can obscure LLM interactions, LightLang gives developers direct access to model configurations and workflows.
- **Extensibility**: LightLang goes beyond just LLM interactions, offering built-in tools for web scraping, Google searches, and PDF ingestion. This makes it a one-stop solution for building data-driven LLM applications.
- **Ergonomic API**: Designed with developers in mind, LightLang provides an intuitive interface that minimizes boilerplate and focuses on the essentials, allowing for rapid prototyping and development.

### Features

- **Multi-Provider Support**: Seamless integration with popular LLM providers like OpenAI and OpenRouter, enabling access to models such as GPT-4o, Claude, and many others.
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

To configure these environment variables, you can set them directly in your shell or add them to a `.env` file in your project. In the latter case, you'll need to use a package like `python-dotenv` to load the variables into your environment.

## Usage

### Getting Started with LLM Responses

This section walks you through progressively more advanced examples of interacting with LLMs using LightLang. We start with simple single prompts and move to more complex scenarios, including dynamic prompts, streaming, and multi-turn conversations.

#### Basic Single Prompt

The `LLM` class provides a simple unified interface for calling models from multiple providers, such as OpenAI and OpenRouter (which itself provides access to hundreds of top models). To start, let's show a simple example of sending a single prompt and getting a response.

```python
from lightlang.llms.llm import LLM

# Initialize the LLM for OpenAI with the 'gpt-4o-mini' model
llm = LLM(provider="openai", model="gpt-4o-mini")

# Send a single user message to the assistant
print("USER:", msg := "Write a dad joke about ducks.")
response = llm.invoke(msg)
print("AI:", response.content)
```

#### System Message, Model Settings, Streaming, and Multi-Turn Conversation

This example demonstrates several features together:

- Using OpenRouter as a provider to access models such as Claude 3.5 Sonnet, Gemini, etc.
- Setting a system message to control the assistant's behavior.
- Setting the `temperature` to control creativity.
- Streaming the response in real-time.
- Maintaining context across multiple turns in a conversation.

```python
from lightlang.llms.llm import LLM

# Initialize the LLM and set the temperature
llm = LLM(provider="openrouter", model="anthropic/claude-3.5-sonnet", temperature=0.7)

# System message, followed by a user prompt
messages = [
    {"role": "system", "content": "You are an expert at writing very funny stories."},
    {"role": "user", "content": "Start a story about a coding duck, just one sentence."}
]

# Stream the response
for chunk in llm.stream(messages):
    if chunk.content:
        print(chunk.content, end="", flush=True) # Flush the buffer to print immediately

# Add the response and a new user message to the chat history
messages += [
    {"role": "assistant", "content": llm.stream_content},
    {"role": "user", "content": "Continue with the next sentence."}
]

# Get a new response (we could also stream it here)
response = llm.invoke(messages)
print(response.content)
```

#### Dynamic Prompt Creation Using `PromptTemplate` and Additional LLM Call Parameters

`PromptTemplate` allows you to create a prompt template with placeholders that get filled at runtime.

What's the benefit of using `PromptTemplate` over regular string formatting, such as `"my name is {name}".format(name="Alice")`? The main benefit is that you are free to **oversupply** the parameters and `PromptTemplate` will simply ignore the extra ones. By contrast, calling `"my name is {name}".format(name="Alice", age=30)` will raise an error.

This feature is very useful for building LLM workflows, where we can keep all available data items in a single dictionary and freely pass it to multiple templates without worrying about extra parameters. 

Additionally, `PromptTemplate` allows you to **undersupply** the parameters to create a partially filled template as a string or a new `PromptTemplate` instance.

The example below demonstrates the following features:

- Using `PromptTemplate` to dynamically generate prompts
- Setting additional parameters for LLM calls, such as `stop` and `max_tokens`, to customize completions

```python
from lightlang.llms.llm import LLM

# Define the model config. Possible parameters are described in the API documentation:
#     - for OpenAI: https://platform.openai.com/docs/api-reference/chat/create)
#     - for OpenRouter: https://openrouter.ai/docs/parameters
#     - for OpenRouter, by model: https://openrouter.ai/docs/parameters-api
model_config = {"temperature": 0.9, "stop": "\n"}

# Initialize the LLM with the model specified in .env (or default) and above settings
llm = LLM(provider="openai", model="gpt-4o-mini", model_config=model_config)

# Define a prompt template with placeholders
template = PromptTemplate("Write a one-liner stand-up comedy joke about a {adjective} {noun}")

# Dynamically substitute the placeholders
adjective = random.choice(["huge", "tiny", "sleepy", "hungry", "squishy", "fluffy"])
noun = random.choice(["duck", "dog", "dodo", "dolphin", "dinosaur", "donkey"])
prompt = template.format(adjective=adjective, noun=noun, blah="This will be ignored")

# Invoke the LLM with the dynamically generated prompt
print("USER:", prompt)
print("AI:", llm.invoke(prompt).content)
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

### Prompt-chaining Workflows with `SequentialWorkflow`

In this example, we create a `SequentialWorkflow` with three prompts, which generates a random thesis for debating, provides the affirmative case for the thesis, and prepares a rebuttal.

```python
from lightlang.llms.llm import LLM
from shared.constants import PROVIDER, MODEL
from lightlang.workflows.sequential_workflow import SequentialWorkflow

# Define the input data for the workflow
workflow_data = {"topic": "philosopy of mind"}  # Each task will add its output to this

# Define the first prompt
# This prompt instructs the assistant to generate a random thesis for debating.
prompt1 = """
<system>
You are a creative organizer of a debating competition.
</system>
<user>
Generate a random thesis on the topic of '{topic}' for competitors to debate. \
Respond in one sentence in the format: "Thesis: <thesis>".
</user>
"""

# Define the second prompt
# It asks the assistant to provide the affirmative case for the thesis generated in the first prompt.
prompt2 = """
<system>
You are a debate expert participating in a competition.
</system>
<user>
Provide the affirmative case for the following thesis in just one short paragraph:

{task_1_output}
</user>
"""

# Define the third prompt
# This prompt instructs the assistant to prepare a rebuttal.
# It provides both the thesis and the affirmative case (from previous prompts).
prompt3 = """
<system>
You are a debate expert preparing a rebuttal.
</system>
<user>
Given the thesis and the affirmative case below, generate a rebuttal in just one short paragraph.

Thesis:
{task_1_output}

Affirmative Case:
{task_2_output}
</user>
"""

# Initialize LLM with the model specified in .env (or default) and set the temperature
llm = LLM(provider="openai", model="gpt-4o-mini", temperature=0.8)

# Create the SequentialWorkflow with the string prompt templates
workflow = SequentialWorkflow(
    tasks=[prompt1, prompt2, prompt3], default_llm=llm, workflow_data=workflow_data
)

# Run the workflow
for chunk in workflow.stream():
    if chunk.event_type != "DEFAULT":
        print(f"\n--- Task {workflow.task_id}: event '{chunk.event_type}' ---\n")
    elif chunk.content is not None:
        print(chunk.content, end="", flush=True)
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

This project is licensed under the MIT License. See the [LICENSE](https://github.com/reasonmethis/lightlang/blob/main/LICENSE) file for more details.

## Contact

For any questions, issues, or feedback, please feel free to open an issue on GitHub.
