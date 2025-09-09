#!/bin/bash

# Test runner script for the Non-Fiction Book-Writing System

set -e

echo "🧪 Running Non-Fiction Book-Writing System Tests"
echo "================================================"

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Install development dependencies
echo "📥 Installing development dependencies..."
pip install pytest pytest-asyncio pytest-cov black flake8 mypy

# Run linting
echo "🔍 Running code linting..."
echo "  - Black (code formatting)"
black --check .

echo "  - Flake8 (style checking)"
flake8 .

echo "  - MyPy (type checking)"
mypy . --ignore-missing-imports

# Run tests
echo "🧪 Running tests..."
echo "  - Unit tests"
pytest tests/test_document_ingestor.py tests/test_memory_manager.py tests/test_llm_client.py -v

echo "  - Integration tests"
pytest tests/test_integration.py -v

echo "  - All tests with coverage"
pytest --cov=. --cov-report=html --cov-report=term-missing

# Check test results
if [ $? -eq 0 ]; then
    echo "✅ All tests passed!"
    echo "📊 Coverage report generated in htmlcov/index.html"
else
    echo "❌ Some tests failed!"
    exit 1
fi

echo "🎉 Test run completed successfully!"