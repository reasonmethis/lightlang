# LightLang: A Lightweight Framework for LLM Workflows

[![License](https://img.shields.io/github/license/reasonmethis/lightlang)](LICENSE)

An open-source mini-framework for using Large Language Models (LLMs) and building agentic workflows.

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Configuration](#configuration)
- [Usage](#usage)
  - [Basic Workflow](#basic-workflow)
  - [Advanced Usage](#advanced-usage)
  - [Google Search Integration](#google-search-integration)
  - [Web Scraping](#web-scraping)
- [Modules Overview](#modules-overview)
  - [Core](#core)
  - [LLM Interaction](#llm-interaction)
  - [Web Utilities](#web-utilities)
  - [Utilities](#utilities)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Introduction

LightLang provides a robust structure for integrating LLMs into workflows, enabling complex task automation, information retrieval, and data processing. It is designed for developers and researchers who want to leverage LLMs for diverse applications.

## Features

- **Agentic Workflows**: Create and manage sequential and complex workflows with LLMs.
- **Google Search**: Perform and utilize Google searches within workflows.
- **Web Scraping**: Extract and process data from web pages and documents.
- **Streaming and Async Support**: Handle real-time data processing and asynchronous operations.

## Getting Started

### Prerequisites

- Python 3.11+
- pip (Python package installer)

### Installation

1. **Clone the repository:**

   ```sh
   git clone https://github.com/reasonmethis/lightlang.git
   cd lightlang
   ```

2. **Create a virtual environment (optional but recommended):**

   ```sh
   python -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**

   ```sh
   pip install -r requirements.txt
   ```

### Configuration

1. **Environment Variables:**
   - Create a `.env` file in the root directory and add the following variables:

     ```
     MODEL=<Your Default Model>
     TEMPERATURE=<Default Temperature>
     OPENROUTER_API_KEY=<Your OpenRouter API Key>
     SERP_API_KEY=<Your SerpAPI Key>
     ```

2. **Custom Settings:**
   - Adjust settings in the `config/` directory as needed, such as model configurations in `openrouter.py` or web scraping configurations in `trafilatura.cfg`.

## Usage

### Basic Workflow

To create a basic workflow, define a sequence of tasks using `Task` or `PromptTemplate` objects and execute them using the `WorkflowEngine`.

```python
from workflow_engine import WorkflowEngine, Task
from utils.prompt_template import PromptTemplate

llm = OpenRouterLLM(model="openai/gpt-4o-mini", temperature=0.7)  # Initialize the LLM model
workflow_engine = WorkflowEngine(llm=llm, inputs={"country": "France"})

tasks = [
    Task(prompt_template=PromptTemplate("What is the capital of {country}?")),
    Task(prompt_template=PromptTemplate("Tell me more about:\n{task_1_output}."))
]

workflow = SequentialWorkflow(workflow_engine=workflow_engine, tasks=tasks)

# Execute the workflow
for output in workflow.stream():
    if isinstance(output, str):
        print(output, end="")
    else:
        print(f"\n\nTask event received for task {workflow.task_id}: {output}\n\n")
```

### Advanced Usage

- **Custom Task Handlers:**
  - Define custom output handlers to process or store task results.

```python
def custom_handler(workflow, curr_task, response):
    # Custom logic for handling task outputs
    print(f"Task {curr_task.task_id} completed with output: {response.llm_output}")

workflow = SequentialWorkflow(
    workflow_engine=workflow_engine,
    tasks=tasks,
    handle_task_end=custom_handler
)
```

### Google Search Integration

Perform Google searches using the integrated SerpAPI and utilize the results in workflows.

```python
from utils.web import search_with_serp_api

queries = ["latest AI research", "top Python frameworks"]
results = search_with_serp_api(queries)

for query, result in results.items():
    print(f"Results for {query}:")
    for item in result:
        print(f"- {item['title']}: {item['link']}")
```

### Web Scraping

Extract content from websites and use it as input for LLM tasks.

```python
from utils.web import get_content_from_urls

urls = ["https://example.com"]
url_retrieval_data = get_content_from_urls(urls)

for url, link_data in url_retrieval_data.link_data_dict.items():
    print(f"Content from {url}:")
    print(link_data.text)
```

## Modules Overview

### Core

- **schemas.py**: Data models for structured data.
- **workflow_engine.py**: Manages task execution and workflow control.

### LLM Interaction

- **utils/llm.py**: Handles LLM interactions, including streaming and invoking models.
- **config/openrouter.py**: Configuration for different LLM models and providers.

### Web Utilities

- **utils/web.py**: Functions for web scraping and Google Search integration.
- **config/trafilatura.cfg**: Settings for content extraction.

### Utilities

- **utils/core.py**: Core utility functions for file and directory management.
- **utils/async_utils.py**: Asynchronous utility functions.
- **utils/prompt_template.py**: Template handling for prompt generation.

## Contributing

We welcome contributions from the community! To contribute, please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Commit your changes with clear and concise messages.
4. Push your changes to your fork and submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

## Contact

For any questions, issues, or feedback, please feel free to open an issue on GitHub.