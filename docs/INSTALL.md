# Installation Guide

This guide provides comprehensive installation instructions for the Book Writing System on macOS and other platforms.

## 📋 Prerequisites

### System Requirements
- **macOS**: 10.15 (Catalina) or later
- **Python**: 3.8 or later
- **Memory**: 8GB RAM minimum, 16GB recommended
- **Storage**: 2GB free space for dependencies

### Required Software
- Python 3.8+
- pip (Python package manager)
- Git
- Xcode Command Line Tools (macOS)

## 🚀 Quick Installation

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/book-writing-system.git
cd book-writing-system
```

### 2. Create Virtual Environment
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate     # On Windows
```

### 3. Install Dependencies
```bash
# Install core dependencies
pip install -r requirements.txt

# Install optional GUI dependencies (if using GUI)
pip install PyQt6
```

### 4. Initialize System
```bash
# Initialize with OpenAI
python run.py --cli init --openai-key YOUR_OPENAI_API_KEY

# Or initialize with Ollama (local)
python run.py --cli init
```

## 🔧 Detailed Installation

### macOS Installation

#### 1. Install Xcode Command Line Tools
```bash
xcode-select --install
```

#### 2. Install Python
```bash
# Using Homebrew (recommended)
brew install python@3.11

# Or download from python.org
# https://www.python.org/downloads/macos/
```

#### 3. Install System Dependencies
```bash
# Install ChromaDB dependencies
brew install cmake

# Install PDF processing dependencies
brew install poppler

# Install pandoc for document conversion
brew install pandoc
```

#### 4. Set Up Environment
```bash
# Create project directory
mkdir ~/book-writing-system
cd ~/book-writing-system

# Clone repository
git clone <repository-url> .

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip
```

#### 5. Install Python Dependencies
```bash
# Install core dependencies
pip install -r requirements.txt

# Install development dependencies (optional)
pip install -r requirements-dev.txt

# Install GUI dependencies (optional)
pip install PyQt6
```

### Windows Installation

#### 1. Install Python
- Download Python 3.11+ from [python.org](https://www.python.org/downloads/windows/)
- Make sure to check "Add Python to PATH" during installation

#### 2. Install Git
- Download Git from [git-scm.com](https://git-scm.com/download/win)
- Install with default settings

#### 3. Install Visual Studio Build Tools
- Download from [Microsoft](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
- Install "C++ build tools" workload

#### 4. Set Up Project
```cmd
# Create project directory
mkdir C:\book-writing-system
cd C:\book-writing-system

# Clone repository
git clone <repository-url> .

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Linux Installation

#### Ubuntu/Debian
```bash
# Update package list
sudo apt update

# Install Python and dependencies
sudo apt install python3.11 python3.11-venv python3.11-dev

# Install system dependencies
sudo apt install cmake build-essential
sudo apt install poppler-utils pandoc

# Install Git
sudo apt install git

# Set up project
git clone <repository-url> book-writing-system
cd book-writing-system
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### CentOS/RHEL/Fedora
```bash
# Install Python and dependencies
sudo dnf install python3.11 python3.11-devel

# Install system dependencies
sudo dnf install cmake gcc gcc-c++
sudo dnf install poppler-utils pandoc

# Install Git
sudo dnf install git

# Set up project
git clone <repository-url> book-writing-system
cd book-writing-system
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 🔑 API Key Setup

### OpenAI API Key
1. Visit [OpenAI Platform](https://platform.openai.com/)
2. Create an account or sign in
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key and set it as an environment variable:

```bash
# macOS/Linux
export OPENAI_API_KEY="your-api-key-here"

# Windows
set OPENAI_API_KEY=your-api-key-here
```

### Anthropic API Key (Optional)
1. Visit [Anthropic Console](https://console.anthropic.com/)
2. Create an account or sign in
3. Generate an API key
4. Set environment variable:

```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

### Google AI Studio API Key (Optional)
1. Visit [Google AI Studio](https://aistudio.google.com/)
2. Create an account or sign in
3. Generate an API key
4. Set environment variable:

```bash
export GOOGLE_AI_API_KEY="your-api-key-here"
```

## 🐳 Docker Installation

### Using Docker Compose
```bash
# Clone repository
git clone <repository-url> book-writing-system
cd book-writing-system

# Create environment file
echo "OPENAI_API_KEY=your-api-key-here" > .env

# Start services
docker-compose up -d
```

### Using Docker
```bash
# Build image
docker build -t book-writing-system .

# Run container
docker run -it --rm \
  -e OPENAI_API_KEY=your-api-key-here \
  -v $(pwd)/books:/app/books \
  -v $(pwd)/memory_db:/app/memory_db \
  book-writing-system
```

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the project root:

```bash
# LLM Configuration
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key
GOOGLE_AI_API_KEY=your-google-key

# System Configuration
MEMORY_DIR=./memory_db
OUTPUT_DIR=./books
LOG_LEVEL=INFO

# Optional: Custom LLM endpoints
OPENAI_BASE_URL=https://api.openai.com/v1
OLLAMA_URL=http://localhost:11434
```

### Configuration File
Create `config.yaml`:

```yaml
# LLM Configuration
llm:
  provider: "openai"  # openai, ollama, anthropic, google
  openai_api_key: "your-key"
  ollama_url: "http://localhost:11434"
  anthropic_api_key: "your-key"
  google_api_key: "your-key"

# Memory Configuration
memory:
  persist_directory: "./memory_db"
  embedding_model: "all-MiniLM-L6-v2"
  use_remote_embeddings: true
  chunk_size: 1000
  chunk_overlap: 200

# Book Builder Configuration
book_builder:
  output_directory: "./books"
  default_author: "Unknown Author"
  default_audience: "General Readers"

# Agent Configuration
agents:
  research:
    max_iterations: 3
    timeout: 300
  writer:
    max_tokens: 2000
    temperature: 0.7
  editor:
    style_guide: "academic"
    max_iterations: 2

# Tool Configuration
tools:
  sandbox_directory: "./sandbox"
  max_execution_time: 30
  allowed_categories: ["safe", "restricted"]
```

## 🧪 Verification

### Test Installation
```bash
# Run basic tests
python -m pytest tests/test_basic.py -v

# Test CLI
python run.py --cli --help

# Test GUI (if installed)
python run.py --gui --help

# Test system initialization
python run.py --cli init --openai-key YOUR_KEY
```

### Verify Dependencies
```bash
# Check Python version
python --version

# Check installed packages
pip list

# Test ChromaDB
python -c "import chromadb; print('ChromaDB OK')"

# Test OpenAI
python -c "import openai; print('OpenAI OK')"

# Test PyQt6 (if installed)
python -c "from PyQt6.QtWidgets import QApplication; print('PyQt6 OK')"
```

## 🚨 Troubleshooting

### Common Issues

#### 1. Python Version Issues
```bash
# Check Python version
python --version

# If wrong version, reinstall
brew uninstall python@3.11
brew install python@3.11
```

#### 2. ChromaDB Installation Issues
```bash
# Install system dependencies
brew install cmake  # macOS
sudo apt install cmake  # Ubuntu

# Reinstall ChromaDB
pip uninstall chromadb
pip install chromadb
```

#### 3. PyQt6 Installation Issues
```bash
# macOS
brew install pyqt6
pip install PyQt6

# Ubuntu
sudo apt install python3-pyqt6
pip install PyQt6
```

#### 4. Memory Issues
```bash
# Increase virtual memory
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:128

# Use CPU-only mode
export CUDA_VISIBLE_DEVICES=""
```

#### 5. API Key Issues
```bash
# Check environment variables
echo $OPENAI_API_KEY

# Test API key
python -c "import openai; openai.api_key='$OPENAI_API_KEY'; print('API Key OK')"
```

### Getting Help

1. **Check Logs**: Look at the console output for error messages
2. **Verify Dependencies**: Run the verification commands above
3. **Check Configuration**: Ensure all required environment variables are set
4. **Update Dependencies**: Try updating to the latest versions
5. **Report Issues**: Create an issue on GitHub with error details

## 🔄 Updates

### Updating the System
```bash
# Pull latest changes
git pull origin main

# Update dependencies
pip install -r requirements.txt --upgrade

# Reinitialize if needed
python run.py --cli init --openai-key YOUR_KEY
```

### Updating Dependencies
```bash
# Update all packages
pip install --upgrade -r requirements.txt

# Update specific package
pip install --upgrade package-name

# Check for outdated packages
pip list --outdated
```

## 📚 Next Steps

After successful installation:

1. **Read the Documentation**: Check out [README.md](README.md) for usage instructions
2. **Try the Examples**: Run through the example commands
3. **Create Your First Book**: Use the CLI or GUI to create a test book
4. **Explore Integrations**: Check out [INTEGRATIONS.md](INTEGRATIONS.md) for advanced features
5. **Join the Community**: Participate in discussions and contribute

---

**Need Help?** Check our [FAQ](FAQ.md) or create an issue on GitHub.