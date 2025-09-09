#!/usr/bin/env python3
"""
Script to create the new repository structure and reorganize files.
"""

import os
import shutil
from pathlib import Path

def create_directory_structure():
    """Create the new directory structure."""
    
    directories = [
        "agents",
        "memory_manager", 
        "llm_client",
        "tool_manager",
        "document_ingestor",
        "book_builder",
        "cli",
        "gui",
        "tests/fixtures",
        "docs",
        "research"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {directory}")

def move_core_modules():
    """Move core modules to their new locations."""
    
    moves = [
        ("agent_manager.py", "agents/agent_manager.py"),
        ("research_agent.py", "agents/research_agent.py"),
        ("writer_agent.py", "agents/writer_agent.py"),
        ("editor_agent.py", "agents/editor_agent.py"),
        ("tool_agent.py", "agents/tool_agent.py"),
        ("memory_manager.py", "memory_manager/memory_manager.py"),
        ("llm_client.py", "llm_client/llm_client.py"),
        ("tool_manager.py", "tool_manager/tool_manager.py"),
        ("document_ingestor.py", "document_ingestor/document_ingestor.py"),
        ("book_builder.py", "book_builder/book_builder.py"),
        ("book_workflow.py", "book_builder/book_workflow.py"),
        ("cli.py", "cli/cli.py"),
        ("gui.py", "gui/gui.py"),
    ]
    
    for source, destination in moves:
        if os.path.exists(source):
            # Create destination directory if it doesn't exist
            os.makedirs(os.path.dirname(destination), exist_ok=True)
            shutil.move(source, destination)
            print(f"Moved {source} -> {destination}")
        else:
            print(f"Source not found: {source}")

def move_test_files():
    """Move test files to tests directory."""
    
    test_files = [
        "test_book_workflow.py",
        "test_full_book_generator.py",
        "test_book_simple.py"
    ]
    
    for test_file in test_files:
        if os.path.exists(test_file):
            shutil.move(test_file, f"tests/{test_file}")
            print(f"Moved {test_file} -> tests/{test_file}")

def move_documentation():
    """Move documentation files to docs directory."""
    
    doc_files = [
        ("README.md", "docs/README.md"),
        ("INTEGRATION_SUMMARY.md", "docs/INTEGRATIONS.md"),
        ("Editor.md", "docs/Editor.md"),
        ("FEATURES_CHECKLIST.md", "docs/FEATURES_CHECKLIST.md"),
        ("Bookstart_HANDOFF.md", "docs/Bookstart_HANDOFF.md")
    ]
    
    for source, destination in doc_files:
        if os.path.exists(source):
            shutil.move(source, destination)
            print(f"Moved {source} -> {destination}")

def move_research_docs():
    """Move research documentation."""
    
    if os.path.exists("research"):
        for item in os.listdir("research"):
            source = f"research/{item}"
            destination = f"research/{item}"
            if os.path.isfile(source):
                print(f"Research doc already in place: {source}")

def create_init_files():
    """Create __init__.py files for Python packages."""
    
    packages = [
        "agents",
        "memory_manager",
        "llm_client", 
        "tool_manager",
        "document_ingestor",
        "book_builder",
        "cli",
        "gui",
        "tests"
    ]
    
    for package in packages:
        init_file = f"{package}/__init__.py"
        if not os.path.exists(init_file):
            with open(init_file, 'w') as f:
                f.write(f'"""\n{package.title()} module.\n"""\n')
            print(f"Created {init_file}")

def remove_unused_directories():
    """Remove unused directories and files."""
    
    to_remove = [
        "unfucked",
        "backups", 
        "__pycache__",
        "venv",
        "apps",  # Will be reorganized
        "Books",  # Will be reorganized
        "scripts"  # Will be reorganized
    ]
    
    for item in to_remove:
        if os.path.exists(item):
            if os.path.isdir(item):
                shutil.rmtree(item)
                print(f"Removed directory: {item}")
            else:
                os.remove(item)
                print(f"Removed file: {item}")

def main():
    """Main reorganization function."""
    
    print("Starting repository reorganization...")
    
    # Create directory structure
    print("\n1. Creating directory structure...")
    create_directory_structure()
    
    # Move core modules
    print("\n2. Moving core modules...")
    move_core_modules()
    
    # Move test files
    print("\n3. Moving test files...")
    move_test_files()
    
    # Move documentation
    print("\n4. Moving documentation...")
    move_documentation()
    
    # Move research docs
    print("\n5. Moving research documentation...")
    move_research_docs()
    
    # Create __init__.py files
    print("\n6. Creating __init__.py files...")
    create_init_files()
    
    # Remove unused directories
    print("\n7. Removing unused directories...")
    remove_unused_directories()
    
    print("\nReorganization completed!")

if __name__ == "__main__":
    main()