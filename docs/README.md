# Book Writing System

A modern, AI-powered non-fiction book writing system with multi-agent architecture, RAG (Retrieval-Augmented Generation), and comprehensive export capabilities.

## 🚀 Features

### Core Capabilities
- **Multi-Agent System**: Research, Writer, Editor, and Tool agents working in coordination
- **RAG Pipeline**: ChromaDB-based vector storage with local and remote embedding support
- **Memory Management**: Persistent memory with provenance tracking and metadata
- **Document Processing**: Support for PDF, DOCX, TXT, MD, and EPUB formats
- **Book Generation**: Complete book creation from outline to publication-ready output
- **Export Formats**: Markdown, DOCX, and PDF export with professional formatting

### Advanced Features
- **Full Book Generator**: LibriScribe integration for complete 50,000+ word books
- **Chapter-by-Chapter Generation**: Incremental book building with continuity tracking
- **Tool Integration**: MCP-style tool registry with safety controls
- **CLI & GUI**: Both command-line and graphical interfaces
- **Async Operations**: Full asynchronous support for optimal performance
- **Provenance Tracking**: Complete audit trail of content generation

## 📁 Project Structure

```
/<repo-root>  
    /full_book_generator          # LibriScribe integration module
    /book_builder                 # Book building functionality
    /agents                       # All agent modules
        research_agent.py  
        writer_agent.py  
        editor_agent.py  
        tool_agent.py  
    /memory_manager               # Memory and RAG functionality
    /llm_client                   # LLM client functionality
    /tool_manager                 # Tool management
    /document_ingestor            # Document processing
    /cli                          # CLI interface
    /gui                          # GUI interface
    /tests                        # All test files
        /fixtures                 # Test fixtures
    /docs                         # All documentation
        README.md
        INSTALL.md
        INTEGRATIONS.md
    /research                     # Research documentation
        RESEARCH.md
        REPOS.md
    pyproject.toml                # Project configuration
    requirements.txt              # Dependencies
    LICENSE
    run.py                        # Main entry point
    .gitignore
```

## 🛠 Installation

### Prerequisites
- Python 3.8+
- pip or conda
- Git

### Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd book-writing-system
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Initialize the system**
   ```bash
   python run.py --cli init --openai-key YOUR_API_KEY
   ```

4. **Start using the system**
   ```bash
   # CLI interface
   python run.py --cli
   
   # GUI interface (requires PyQt6)
   python run.py --gui
   ```

### Detailed Installation

See [INSTALL.md](INSTALL.md) for comprehensive installation instructions including:
- macOS setup
- Environment configuration
- API key setup
- Optional dependencies

## 🚀 Usage

### CLI Interface

The CLI provides full access to all system capabilities:

```bash
# Initialize system
python run.py --cli init --openai-key YOUR_API_KEY

# Create a new book
python run.py --cli book create "My Book" --author "John Doe" --description "A great book" --audience "General readers"

# Add chapters
python run.py --cli book add-chapter BOOK_ID "Chapter 1" --description "Introduction"

# Generate content
python run.py --cli generate BOOK_ID

# Export book
python run.py --cli book export BOOK_ID --format pdf

# Search memory
python run.py --cli memory search "artificial intelligence"

# Run agents
python run.py --cli agent run research "machine learning trends"
```

### GUI Interface

The GUI provides a modern, intuitive interface:

```bash
python run.py --gui
```

Features:
- Visual book management
- Memory search interface
- Agent execution panel
- Real-time progress tracking
- Export management

### Python API

Use the system programmatically:

```python
from memory_manager import MemoryManager
from llm_client import LLMClient
from book_builder import BookBuilder
from agents import ResearchAgent, WriterAgent, EditorAgent

# Initialize components
memory_manager = MemoryManager()
llm_client = LLMClient(provider="openai", openai_api_key="your-key")
book_builder = BookBuilder()

# Create book outline
outline = await book_builder.create_book_outline(
    title="AI and Society",
    author="Jane Smith",
    description="Exploring the impact of AI on modern society",
    target_audience="General readers"
)

# Generate content
research_agent = ResearchAgent(memory_manager, llm_client)
writer_agent = WriterAgent(memory_manager, llm_client)

for chapter in outline.chapters:
    research = await research_agent.research_topic(chapter.title)
    content = await writer_agent.write_content(f"Write about {chapter.title}", research)
    await book_builder.add_chapter_content(outline.book_id, chapter.chapter_id, content)

# Export book
await book_builder.export_to_pdf(outline.book_id)
```

## 🤖 Agents

### Research Agent
- Conducts web research and information gathering
- Integrates with memory system for context
- Provides structured research results

### Writer Agent
- Generates high-quality content based on research
- Supports multiple writing styles (academic, journalistic, conversational)
- Maintains consistency and coherence

### Editor Agent
- Reviews and refines generated content
- Applies style guides and quality standards
- Ensures grammatical correctness and flow

### Tool Agent
- Executes various tools and utilities
- Manages tool safety and execution policies
- Provides tool results to other agents

## 🧠 Memory System

The memory system provides:
- **Vector Storage**: ChromaDB-based embedding storage
- **Provenance Tracking**: Complete audit trail of content sources
- **Metadata Management**: Rich metadata for content organization
- **Retrieval**: Semantic search and context assembly
- **Persistence**: Long-term storage and retrieval

## 📚 Book Generation

### Chapter-by-Chapter Generation
1. Create book outline with chapters
2. Research each chapter topic
3. Generate chapter content
4. Edit and refine content
5. Export to desired format

### Full Book Generation
1. Use the integrated LibriScribe module
2. Generate complete 50,000+ word books
3. Multi-agent coordination
4. Professional formatting and export

## 🔧 Configuration

### Environment Variables
```bash
export OPENAI_API_KEY="your-openai-key"
export ANTHROPIC_API_KEY="your-anthropic-key"
export GOOGLE_AI_API_KEY="your-google-key"
```

### Configuration File
Create `config.yaml`:
```yaml
llm:
  provider: "openai"  # or "ollama"
  openai_api_key: "your-key"
  ollama_url: "http://localhost:11434"

memory:
  persist_directory: "./memory_db"
  embedding_model: "all-MiniLM-L6-v2"

book_builder:
  output_directory: "./books"
  chunk_size: 1000
  chunk_overlap: 200
```

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
python -m pytest tests/

# Run specific test categories
python -m pytest tests/test_agents.py
python -m pytest tests/test_memory.py
python -m pytest tests/test_book_builder.py

# Run with coverage
python -m pytest --cov=. tests/
```

## 📖 Documentation

- [Installation Guide](INSTALL.md) - Detailed setup instructions
- [Integrations](INTEGRATIONS.md) - External integrations and dependencies
- [API Reference](api/) - Complete API documentation
- [Examples](examples/) - Usage examples and tutorials

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **LibriScribe**: Multi-agent book generation system
- **ChromaDB**: Vector database for embeddings
- **OpenAI**: LLM API services
- **PyQt6**: GUI framework
- **Click**: CLI framework

## 🆘 Support

- **Issues**: Report bugs and request features on GitHub
- **Discussions**: Join community discussions
- **Documentation**: Check the docs folder for detailed guides

## 🔄 Changelog

### Version 1.0.0
- Initial release
- Multi-agent architecture
- RAG pipeline integration
- CLI and GUI interfaces
- LibriScribe integration
- Comprehensive export capabilities

---

**Built with ❤️ for the AI and writing community**