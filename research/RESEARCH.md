# Research Document

## 1. Purpose

Implement a system that can generate entire non-fiction books chapter-by-chapter from a user prompt, ingest and learn from user references (PDF, MD, TXT, DOCX, EPUB), and use research, writer, and editor agents to produce, revise, and export books.

## 2. Autonomous Research and Tech Selection

### Vector Store / Retrieval Engine

**Candidates Considered:**

- **FAISS**: A library for efficient similarity search and clustering of dense vectors.
- **ChromaDB**: An open-source embedding database optimized for large-scale similarity search and vector storage.
- **Qdrant**: A high-performance, scalable vector search engine.
- **Pinecone**: A managed vector database service.

**Final Choice: ChromaDB**

**Justification:**

ChromaDB offers a user-friendly API, seamless integration with Python, and is optimized for large-scale similarity search, making it suitable for our RAG pipeline. It provides persistent storage, metadata filtering, and efficient retrieval capabilities. The active community and comprehensive documentation further support its adoption. ([ChromaDB Documentation](https://docs.trychroma.com/))

### Embedding Models/Providers

**Local Candidates:**

- **SentenceTransformers**: A Python framework for state-of-the-art sentence, text, and image embeddings.
- **Hugging Face Transformers**: Provides a wide array of pre-trained models for generating embeddings.

**Remote Candidates:**

- **OpenAI Embeddings API**: Offers high-quality embeddings through a simple API.
- **Cohere API**: Provides language models capable of generating embeddings for various tasks.

**Final Choice: SentenceTransformers (Local) and OpenAI Embeddings API (Remote)**

**Justification:**

Using SentenceTransformers locally allows for quick, cost-effective embedding generation without external dependencies, which is beneficial during development and for users with privacy concerns. The OpenAI Embeddings API serves as a robust remote option, offering high-quality embeddings with minimal setup, suitable for production environments requiring scalability. ([SentenceTransformers Documentation](https://www.sbert.net/))

### LLM Backends/Adapters

**Local Candidates:**

- **Ollama**: A tool for running large language models locally.
- **Hugging Face Transformers**: Open-source models that can be run locally.
- **GPT4All**: An ecosystem for running LLMs on local machines.

**Remote Candidates:**

- **OpenAI GPT-4 API**: Provides access to OpenAI's GPT-4 model via API.
- **Anthropic's Claude API**: Offers access to Anthropic's language models.

**Final Choice: Ollama (Local) and OpenAI GPT-4 API (Remote)**

**Justification:**

Ollama enables running LLMs locally, ensuring data privacy and offline capabilities, which is advantageous for users with sensitive data or limited internet access. The OpenAI GPT-4 API offers state-of-the-art language generation capabilities, suitable for tasks requiring high-quality outputs and scalability. ([Ollama Documentation](https://ollama.ai/))

### GUI Framework

**Candidates Considered:**

- **PyQt6**: A set of Python bindings for the Qt6 application framework with native Mac support.
- **Tkinter**: Python's standard GUI package (limited Mac native support).
- **Kivy**: An open-source Python library for rapid development of applications with innovative user interfaces.
- **Streamlit**: A framework for creating web applications with Python.
- **Cocoa (PyObjC)**: Native Mac development with Python bindings.

**Final Choice: PyQt6**

**Justification:**

PyQt6 was selected for its excellent Mac native support, modern UI capabilities, and ability to create clean, professional interfaces similar to Zed. It provides native Mac look and feel, proper window management, and supports modern design patterns. The framework allows for creating a clean, well-planned interface with proper Mac integration including native menus, toolbars, and window behaviors. ([PyQt6 Documentation](https://doc.qt.io/qtforpython/))

### CLI Tooling

**Candidates Considered:**

- **Click**: A Python package for creating command-line interfaces.
- **Argparse**: Python's standard library for parsing command-line arguments.
- **Typer**: A library for building CLI applications that draws upon Python's type hints.

**Final Choice: Click**

**Justification:**

Click offers a balance between simplicity and functionality, allowing for the creation of complex command-line interfaces with minimal boilerplate code. Its support for nested commands, automatic help page generation, and decorator-based approach enhances user experience and developer productivity. ([Click Documentation](https://click.palletsprojects.com/))

### Concurrency/Orchestration Approach

**Candidates Considered:**

- **Celery**: An asynchronous task queue/job queue based on distributed message passing.
- **AsyncIO**: Python's standard library for writing single-threaded concurrent code using coroutines.
- **Ray**: A framework for building and running distributed applications.
- **LangGraph**: A framework for building stateful, multi-actor applications with LLMs.

**Final Choice: AsyncIO**

**Justification:**

AsyncIO is part of Python's standard library, reducing external dependencies. It provides a straightforward approach to writing concurrent code, suitable for managing the cooperative agents within our system. Its integration with other Python libraries ensures compatibility and ease of use. For more complex orchestration needs, LangGraph could be integrated in the future.

## 3. Tradeoff Analysis

**MacOS Suitability:**

All selected tools and libraries are compatible with macOS, ensuring a smooth development and deployment experience for macOS users.

**Installation Complexity:**

- **ChromaDB**: Requires installation via pip and may need additional dependencies for optimal performance.
- **SentenceTransformers**: Easily installable via pip, with pre-trained models available for immediate use.
- **Ollama**: Installation involves downloading the binary and setting up the environment, which may be complex for non-technical users.
- **Click**: Simple installation via pip with minimal dependencies.
- **AsyncIO**: Included in Python's standard library, requiring no additional installation.

**RAG Support:**

The chosen stack supports the implementation of a robust RAG pipeline:

- **ChromaDB**: Efficient storage and retrieval of embeddings with metadata filtering.
- **SentenceTransformers**: Generation of high-quality embeddings for text data.
- **Ollama/OpenAI GPT-4 API**: Processing and generating text based on retrieved information.

This combination ensures efficient ingestion, embedding, retrieval, and generation processes essential for a production-capable non-fiction book-writing system.

## 4. Citations and References

- [ChromaDB Documentation](https://docs.trychroma.com/)
- [SentenceTransformers Documentation](https://www.sbert.net/)
- [Ollama Documentation](https://ollama.ai/)
- [Click Documentation](https://click.palletsprojects.com/)
- [Python AsyncIO Documentation](https://docs.python.org/3/library/asyncio.html)