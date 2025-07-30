# 🧠 NineBit CIQ Python SDK

![](banner.png)
[![Version](https://img.shields.io/pypi/v/ninebit-ciq)](https://pypi.org/project/ninebit-ciq)
[![License](https://img.shields.io/github/license/NineBit-Computing/ciq-py-client)](https://github.com/NineBit-Computing/ciq-py-client/blob/main/LICENSE)
[![build](https://img.shields.io/github/actions/workflow/status/NineBit-Computing/ciq-py-client/ci.yml?branch=main)](https://github.com/NineBit-Computing/ciq-py-client/actions)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Linting: flake8](https://img.shields.io/badge/linting-flake8-blue)](https://flake8.pycqa.org/)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://pre-commit.com/)

Official Python client for interacting with [NineBit CIQ](https://ciq.ninebit.in), a Retrieval-Augmented Generation (RAG) workflow orchestration platform for rapid prototyping of AI/ML ideas using enterprise data and open-source models.

---

## 🚀 Features

- Retrieval-Augmented Generation (RAG)
  Perform semantic search and intelligent query answering using hybrid retrieval techniques.
- Flexible Query Interface
  Send queries with configurable similarity thresholds and top_k result tuning.
- Callback Support for Asynchronous Workflows
  Pass in callbacks to handle results or errors once workflows complete — ideal for event-driven applications.
- Workflow Polling with Timeout Control
  Monitor long-running workflows with built-in polling, status checking, and customizable timeouts.
- Simple, Extensible API
  Clean, Pythonic interfaces with support for both synchronous returns and optional callbacks.
- Error-Handled Execution Flow
  Graceful handling of task failures, timeouts, and unexpected states with descriptive exceptions.
- Logging Support
  Integrated logging for easy debugging and transparency during polling or querying.

---

## 📦 Installation

```bash
pip install ninebit-ciq
```

Or clone and install locally:

```
git clone https://github.com/NineBit-Computing/ciq-py-client.git
cd ciq-py-client
pip install .
```

## 🧪 Quickstart (Python)

```python
from ninebit_ciq import NineBitCIQClient

client = NineBitCIQClient(
    api_key="YOUR_API_KEY"
)

def on_done(error, data):
    if error:
        print(f"Ingest_file failed: {error}")
    else:
        print(f"Ingest_file succeeded: {str(data)}")

# 1. Ingest file as datasource for performing RAG
client.ingest_file(file="files/my_file.pdf", callback=on_done)

# 2. Ask your query
query = "What are land breeze?"
response = client.rag_query(query=query)
print(f"Query response is {response}")

```

## 🔐 Authentication

Pass your API Key using the X-API-Key header:

Python SDK: NineBitCIQClient(api_key)

## 📚 SDK Reference

| Method          | Description                                                                     |
| --------------- | ------------------------------------------------------------------------------- |
| `ingest_file()` | Reads and uploads a PDF or DOCX file to the backend for processing.             |
| `rag_query()`   | Performs a Retrieval-Augmented Generation (RAG) query using the provided input. |
|                 |

## 🛠️ Logging

You can control logging verbosity:

```python
from ninebit_ciq import NineBitCIQClient
import logging

client = NineBitCIQClient(api_key, log_level=logging.INFO)
```

## 📁 Project Structure

```
ciq-py-client/
├── src/ninebit_ciq/
│ ├── client.py # Core SDK logic
│ ├── logger.py # Logger setup
│ ├── cli.py # CLI interface
│ └── **init**.py # Version info
├── examples/usage.py
├── examples/usage_with_thread.py
├── README.md
├── setup.py
└── version.txt
```

## 📄 License

MIT License © NineBit Computing

## ✉️ Contact

Questions? Reach out via ninebit.in or raise an issue in the GitHub repo.

## Contributing

While we value open-source contributions to this SDK, the code is generated programmatically. Additions made directly would have to be moved over to our generation code, otherwise they would be overwritten upon the next generated release. Feel free to open a PR as a proof of concept, but know that we will not be able to merge it as-is. We suggest opening an issue first to discuss with us!
