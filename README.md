# Non-Fiction Book-Writing System

A production-capable non-fiction book-writing system with full RAG (retrieval-augmented generation), persistent memory, cooperating agents (Research, Writer, Editor, Tool), an MCP-style tool registry, and both GUI and CLI entry points.

## Features

- **Document Ingestion**: Support for PDF, DOCX, EPUB, TXT, and MD files
- **RAG Pipeline**: ChromaDB vector storage with SentenceTransformers embeddings
- **Multi-Agent System**: Specialized agents for research, writing, editing, and tool execution
- **LLM Integration**: Support for both local (Ollama) and remote (OpenAI) language models
- **Book Generation**: Complete workflow from outline to final export
- **Multiple Export Formats**: Markdown, DOCX, and PDF
- **Tool Registry**: MCP-style tool management with safety controls
- **Dual Interface**: Both command-line and web-based GUI

## Installation

### Prerequisites

- Python 3.8 or higher
- macOS (primary target platform)
- Ollama (for local LLM) or OpenAI API key (for remote LLM)

### Install Dependencies

```bash
# Clone the repository
git clone <repository-url>
cd nonfiction-book-writer

# Install dependencies
pip install -r requirements.txt

# Or install in development mode
pip install -e .
```

### Optional Dependencies

For PDF export, install LaTeX:
```bash
# macOS with Homebrew
brew install --cask mactex

# Or install BasicTeX (smaller)
brew install --cask basictex
```

## Configuration

### Environment Variables

Set the following environment variables:

```bash
# Required for remote LLM
export LLM_REMOTE_API_KEY="your-openai-api-key"

# Optional: Local Ollama URL (default: http://localhost:11434)
export OLLAMA_LOCAL_URL="http://localhost:11434"

# Optional: Remote embeddings (if not using local)
export EMBEDDING_API_KEY="your-embedding-api-key"

# Optional: Vector database path (default: ./memory_db)
export VECTOR_DB_PATH="./memory_db"

# Optional: Allow unsafe tools (default: false)
export TOOL_MANAGER_ALLOW_UNSAFE="false"
```

### Local LLM Setup (Ollama)

If using local LLM with Ollama:

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama service
ollama serve

# Pull a model (in another terminal)
ollama pull llama2
# or
ollama pull codellama
```

## Usage

### Command Line Interface

```bash
# Initialize the system
python run.py cli init

# Ingest documents
python run.py cli ingest document path/to/document.pdf
python run.py cli ingest directory path/to/documents/

# Start research
python run.py cli research start "Artificial Intelligence" --description "AI trends and applications"

# Create a book
python run.py cli book create "My Book" --author "John Doe" --description "A book about AI"

# Generate book outline
python run.py cli book outline <book-id> --chapters 10

# Build the book
python run.py cli book build <book-id>

# Export book
python run.py cli book export <book-id> --format markdown

# Check system status
python run.py cli status
```

### Graphical User Interface

```bash
# Start the native Mac GUI
python run.py gui
```

This launches a native Mac application with a clean, Zed-inspired interface featuring:
- Dark theme with modern design
- Sidebar navigation
- Document management
- Research tools
- Book creation and management
- Tool execution interface
- Real-time system status

### Complete Book Production Workflow

```bash
# Create a complete book with full workflow
python run.py cli book create \
  --title "The Future of Artificial Intelligence" \
  --theme "AI and Machine Learning" \
  --author "AI Book Writer" \
  --word-count 50000 \
  --chapters 10 \
  --references document1.pdf document2.docx

# Check book production status
python run.py cli book status

# List all completed books
python run.py cli book list

# Test the complete workflow
./scripts/run_book_workflow.sh
```

### Python API

```python
import asyncio
from book_workflow import BookWorkflow
from memory_manager import MemoryManager
from llm_client import LLMClient
from agent_manager import AgentManager

async def create_book():
    # Initialize system components
    memory_manager = MemoryManager()
    llm_client = LLMClient()
    agent_manager = AgentManager()
    await agent_manager.start()
    
    # Initialize workflow
    workflow = BookWorkflow(
        memory_manager=memory_manager,
        llm_client=llm_client,
        # ... other components
    )
    
    # Create complete book
    book = await workflow.start_book_production(
        title="My Book",
        theme="Technology",
        target_word_count=50000,
        chapters_count=10
    )
    
    print(f"Book created: {book.title} ({book.word_count:,} words)")
    await agent_manager.stop()

asyncio.run(create_book())
```

## Architecture

### Core Modules

- **`document_ingestor`**: Handles parsing, chunking, and metadata extraction
- **`memory_manager`**: Vector store integration with ChromaDB
- **`llm_client`**: Provider adapters for OpenAI and Ollama
- **`tool_manager`**: MCP-style tool registry with safety controls
- **`agent_manager`**: Task routing and agent orchestration

### Agent Modules

- **`research_agent`**: Autonomous research using RAG and web search
- **`writer_agent`**: RAG-driven content generation
- **`editor_agent`**: Content review and quality assurance
- **`tool_agent`**: Tool execution and management

### Book Building

- **`book_builder`**: Complete book generation workflow
- **`cli`**: Command-line interface
- **`gui`**: Web-based graphical interface

## Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run specific test categories
pytest -m unit
pytest -m integration

# Run with coverage
pytest --cov=. --cov-report=html
```

## Development

### Code Style

This project uses Black for code formatting and flake8 for linting:

```bash
# Format code
black .

# Lint code
flake8 .

# Type checking
mypy .
```

### Adding New Tools

1. Create a new tool class inheriting from `Tool`
2. Implement the `execute` method
3. Register the tool with `ToolManager`
4. Add tests for the new tool

### Adding New LLM Providers

1. Create a new provider class inheriting from `LLMProvider`
2. Implement required methods (`generate`, `generate_stream`, `get_available_models`)
3. Add the provider to `LLMClient`
4. Update configuration and documentation

## Troubleshooting

### Common Issues

1. **ChromaDB connection errors**: Ensure the vector database directory is writable
2. **Ollama connection errors**: Verify Ollama is running and accessible
3. **OpenAI API errors**: Check your API key and rate limits
4. **Memory issues**: Reduce chunk size or use smaller embedding models

### Logs

Check the logs for detailed error information:
- System logs: Console output
- Tool execution logs: `tool_executions.log`
- Provenance logs: `memory_db/provenance.log`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

This project builds upon several open-source libraries and research:

- [ChromaDB](https://github.com/chroma-core/chroma) for vector storage
- [SentenceTransformers](https://github.com/UKPLab/sentence-transformers) for embeddings
- [LangChain](https://github.com/langchain-ai/langchain) for LLM integration patterns
- [Streamlit](https://github.com/streamlit/streamlit) for the web interface
- [Click](https://github.com/pallets/click) for the CLI framework

## Research References

See `research/RESEARCH.md` and `research/REPOS.md` for detailed research documentation and repository analyses.