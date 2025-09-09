#!/usr/bin/env python3
"""
Retro Writer Launcher
Professional Mac Book Writing Application with Retro Writer Theme
"""

import sys
import os
from pathlib import Path

# Add the workspace to the path
workspace_path = Path(__file__).parent
sys.path.insert(0, str(workspace_path))

def main():
    """Main launcher function."""
    try:
        # Import and run the retro writer app
        from retro_writer_app import main as run_app
        return run_app()
    except ImportError as e:
        print(f"Error importing Retro Writer: {e}")
        print("Please ensure all dependencies are installed:")
        print("pip install PyQt6 chromadb sentence-transformers openai pydantic")
        return 1
    except Exception as e:
        print(f"Error running Retro Writer: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())