# Retro Writer - Professional Book Writing Studio

A completely reimagined professional Mac book writing application with a retro writer theme, featuring AI-powered research, multi-agent coordination, and comprehensive book generation capabilities.

## 🎨 Design Philosophy

**Retro Writer Theme**: Inspired by vintage typewriters and classic writing aesthetics
- **Color Palette**: Sepia tones, cream backgrounds, saddle brown accents
- **Typography**: Courier New typewriter font throughout
- **UI Elements**: Rounded corners, subtle shadows, vintage button styles
- **Professional Mac Integration**: Native Mac app feel with retro styling

## 🚀 Features

### 📚 Complete Book Management
- **New Book Creation**: Start projects with title, theme, and author
- **Chapter Management**: Add, edit, delete, and organize chapters
- **Project Persistence**: Save and load book projects
- **Recent Projects**: Quick access to recently worked on books

### 🔍 AI-Powered Research
- **Document Import**: PDF, TXT, MD, DOCX, EPUB support
- **Memory Management**: ChromaDB vector storage with RAG
- **Research Topics**: Organize and manage research themes
- **Source Management**: View and manage research sources
- **Context Assembly**: Automatic relevant context for writing

### ✍️ Intelligent Writing
- **AI Writing Assistant**: Generate chapters with AI assistance
- **Style Controls**: Academic, Journalistic, Narrative, Technical, Creative
- **Tone Management**: Formal, Informal, Conversational, Authoritative, Friendly
- **Real-time Editing**: Rich text editor with formatting tools
- **Writing Statistics**: Word count, character count, reading time

### 🤖 Multi-Agent System
- **Research Agent**: Gathers and organizes research materials
- **Writer Agent**: Generates content based on research and style
- **Editor Agent**: Reviews and improves writing quality
- **Tool Agent**: Manages external tools and integrations
- **Agent Coordination**: Seamless workflow between agents

### 🛠️ Professional Tools
- **System Monitor**: Real-time agent and system status
- **Tool Testing**: Comprehensive system diagnostics
- **Export Options**: Markdown, DOCX, PDF, HTML, EPUB
- **Settings Management**: Comprehensive configuration options
- **Progress Tracking**: Visual progress indicators for all operations

## 🏗️ Architecture

### Core Components
```
RetroWriterApp (Main Application)
├── RetroWriterMainWindow (Main Window)
├── WorkspaceTab (Book Management)
├── ResearchTab (Research Management)
├── WritingTab (Writing Tools)
├── ToolsTab (System Tools)
└── SettingsTab (Configuration)

Content Pages
├── DashboardPage (Overview & Quick Actions)
├── BookEditorPage (Rich Text Editor)
├── ResearchPage (Research Interface)
├── WritingPage (AI Writing Tools)
├── ToolsPage (System Monitoring)
└── SettingsPage (Configuration)
```

### System Integration
- **Memory Manager**: ChromaDB vector storage
- **LLM Client**: OpenAI and Ollama integration
- **Tool Manager**: MCP-style tool registry
- **Agent Manager**: Multi-agent coordination
- **Document Ingestor**: Multi-format document processing
- **Book Workflow**: Complete book generation pipeline

## 🎯 User Interface

### Layout Structure
```
┌─────────────────────────────────────────────────────────────┐
│ Menu Bar (File, Edit, Research, Writing, Tools, Help)      │
├─────────┬─────────────────────────────┬─────────────────────┤
│         │                             │                     │
│ Left    │        Center Area          │    Right Sidebar    │
│ Sidebar │     (Main Content)          │   (Status & Info)   │
│         │                             │                     │
│ 📚 Workspace │ Dashboard Page          │ 📊 System Status    │
│ 🔍 Research  │ Book Editor Page        │ 📈 Progress Track   │
│ ✍️ Writing   │ Research Page           │ 📝 Recent Activity  │
│ 🛠️ Tools     │ Writing Page            │                     │
│ ⚙️ Settings  │ Tools Page              │                     │
│         │ Settings Page               │                     │
└─────────┴─────────────────────────────┴─────────────────────┘
│ Status Bar (Ready | Progress Bar | Word Count)              │
└─────────────────────────────────────────────────────────────┘
```

### Navigation
- **Left Sidebar**: Tabbed navigation for different functional areas
- **Center Area**: Stacked content pages that change based on navigation
- **Right Sidebar**: Status information, progress tracking, recent activity
- **Menu Bar**: Traditional Mac menu with all major functions
- **Status Bar**: Current status, progress indicators, word count

## 🎨 Retro Writer Theme

### Color Scheme
- **Background**: Cream (#faf8f0) - Vintage paper color
- **Paper**: Off-white (#fffdf5) - Slightly yellowed paper
- **Text**: Dark charcoal (#2d2d2d) - Classic typewriter ink
- **Accent**: Saddle brown (#8b4513) - Vintage leather
- **Secondary**: Sienna (#a0522d) - Warm earth tone
- **Highlight**: Burlywood (#deb887) - Soft highlight
- **Border**: Tan (#d2b48c) - Subtle borders

### Typography
- **Font Family**: Courier New (typewriter font)
- **Heading**: 16pt Bold
- **Subheading**: 14pt Bold
- **Body**: 12pt Regular
- **Monospace**: 11pt Regular
- **Small**: 10pt Regular
- **Large**: 18pt Regular

### Styling Elements
- **Border Radius**: 8px for modern rounded corners
- **Border Width**: 2px for definition
- **Shadow Offset**: 3px for depth
- **Animation Duration**: 200ms for smooth transitions

## 🚀 Getting Started

### Installation
```bash
# Clone the repository
git clone <repository-url>
cd retro-writer

# Install dependencies
pip install -r requirements.txt

# Run the application
python run_retro_writer.py
```

### First Launch
1. **Create New Book**: Click "New Book" or use File → New Book
2. **Enter Details**: Provide title, theme, and author information
3. **Import Documents**: Add research materials via File → Import Documents
4. **Start Research**: Use Research tab to begin gathering information
5. **Generate Content**: Use Writing tab to create chapters with AI assistance
6. **Export Book**: Use Tools tab to export in various formats

### Quick Start Workflow
1. **Dashboard**: Overview and quick actions
2. **Workspace**: Create and manage your book project
3. **Research**: Import documents and organize research topics
4. **Writing**: Generate and edit chapters with AI assistance
5. **Tools**: Monitor system and export your completed book

## 🔧 Configuration

### LLM Settings
- **Provider**: OpenAI, Ollama, or Local
- **Model**: GPT-4, GPT-3.5-turbo, Llama2, Mistral
- **Temperature**: Control creativity (0.0-1.0)
- **Max Tokens**: Control response length

### Memory Settings
- **Provider**: ChromaDB, Local, or Remote
- **Max Chunks**: Maximum memory chunks (100-10,000)
- **Chunk Size**: Text chunk size (100-2,000 characters)
- **Embedding Model**: Sentence-transformers, OpenAI, or Local

### Writing Settings
- **Default Style**: Academic, Journalistic, Narrative, Technical, Creative
- **Default Tone**: Formal, Informal, Conversational, Authoritative, Friendly
- **Auto-save**: Automatic saving of work
- **Auto-backup**: Regular backup creation

### Appearance Settings
- **Theme**: Retro Writer, Classic, Modern, Dark
- **Font Family**: Any system font
- **Font Size**: 8-24pt range
- **UI Elements**: Line numbers, word count, reading time

## 📊 System Requirements

### Minimum Requirements
- **OS**: macOS 10.15+ (Catalina or later)
- **Python**: 3.8+
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 2GB free space
- **Display**: 1400x900 minimum resolution

### Recommended Setup
- **OS**: macOS 12+ (Monterey or later)
- **Python**: 3.10+
- **RAM**: 16GB for optimal performance
- **Storage**: 10GB free space for documents and models
- **Display**: 1600x1000 or higher for best experience

### Dependencies
- **PyQt6**: Native Mac GUI framework
- **ChromaDB**: Vector database for memory
- **SentenceTransformers**: Local embedding generation
- **OpenAI**: Remote LLM access
- **Pydantic**: Data validation
- **Click**: CLI framework
- **Markdown**: Export formatting
- **python-docx**: Word document export
- **weasyprint**: PDF generation

## 🎯 Use Cases

### Academic Writing
- **Research Papers**: Comprehensive research and citation management
- **Theses**: Long-form academic writing with proper structure
- **Journal Articles**: Professional academic publication format

### Non-Fiction Books
- **Technical Manuals**: Step-by-step documentation with examples
- **Biographies**: Research-driven life stories
- **How-To Guides**: Practical instruction with clear structure

### Business Writing
- **Reports**: Data-driven business analysis
- **Proposals**: Professional business proposals
- **Documentation**: Technical and user documentation

### Creative Non-Fiction
- **Memoirs**: Personal stories with research backing
- **Travel Writing**: Location-based content with cultural research
- **Essays**: Thoughtful analysis and commentary

## 🔮 Future Enhancements

### Planned Features
- **Collaborative Writing**: Multi-user editing and review
- **Version Control**: Git-like versioning for book projects
- **Template Library**: Pre-built book templates and structures
- **Advanced Analytics**: Writing patterns and productivity metrics
- **Cloud Sync**: Automatic backup and synchronization
- **Mobile Companion**: iOS app for research and note-taking

### Integration Opportunities
- **Reference Managers**: Zotero, Mendeley integration
- **Publishing Platforms**: Direct publishing to Amazon, Apple Books
- **Research Databases**: Academic database integration
- **Citation Tools**: Automatic citation generation and formatting

## 🤝 Contributing

### Development Setup
```bash
# Clone repository
git clone <repository-url>
cd retro-writer

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On macOS/Linux

# Install development dependencies
pip install -r requirements.txt
pip install pytest pytest-qt black flake8

# Run tests
pytest tests/

# Format code
black .

# Lint code
flake8 .
```

### Code Style
- **PEP 8**: Python style guide compliance
- **Type Hints**: Full type annotation
- **Docstrings**: Comprehensive documentation
- **Testing**: 100% test coverage maintained
- **Retro Theme**: Consistent styling throughout

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **PyQt6**: Professional GUI framework
- **ChromaDB**: Vector database technology
- **OpenAI**: Advanced language models
- **SentenceTransformers**: Embedding generation
- **Vintage Typewriter Community**: Design inspiration

---

**Retro Writer** - Where classic writing meets modern AI technology.

*Professional book writing studio with a retro writer soul.*