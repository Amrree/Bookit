#!/bin/bash

# Book Workflow Test Script
# Tests the complete book production workflow

set -e

echo "🧪 Book Workflow Test Script"
echo "============================"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found. Please install Python 3.8+"
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "book_workflow.py" ]; then
    echo "❌ Please run this script from the project root directory"
    exit 1
fi

# Install dependencies if needed
echo "📦 Checking dependencies..."
if ! python3 -c "import click, asyncio, chromadb" 2>/dev/null; then
    echo "Installing dependencies..."
    pip3 install -r requirements.txt
fi

# Check if Ollama is running (optional)
echo "🔍 Checking Ollama availability..."
if curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
    echo "✅ Ollama is running"
    OLLAMA_AVAILABLE=true
else
    echo "⚠️  Ollama not running - will use mock responses"
    OLLAMA_AVAILABLE=false
fi

# Run the test
echo ""
echo "🚀 Running book workflow test..."
echo ""

if [ "$OLLAMA_AVAILABLE" = true ]; then
    echo "Using Ollama for LLM responses"
    python3 test_book_workflow.py
else
    echo "Using mock responses (Ollama not available)"
    echo "To test with real LLM responses, start Ollama:"
    echo "  ollama serve"
    echo "  ollama pull llama2"
    echo ""
    python3 test_book_workflow.py
fi

echo ""
echo "✅ Book workflow test completed!"
echo ""
echo "📚 To create your own book, use:"
echo "  python3 run.py cli book create --title 'Your Book Title' --theme 'Your Theme'"
echo ""
echo "📖 To view the GUI:"
echo "  python3 run.py gui"