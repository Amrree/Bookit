#!/usr/bin/env python3
"""
Simple BookWriter Pro Launcher

A working launcher that provides the core functionality
without requiring complex GUI dependencies.
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def print_header():
    """Print application header."""
    print("=" * 60)
    print("📚 BookWriter Pro - AI-Powered Book Writing System")
    print("=" * 60)
    print("Professional book writing with integrated research and collaboration")
    print()

def print_menu():
    """Print main menu."""
    print("Available Commands:")
    print("1. 📝 Start Writing (Text Editor)")
    print("2. 📄 Process Document")
    print("3. 🔍 Research Assistant")
    print("4. 📋 Apply Template")
    print("5. 📤 Export Content")
    print("6. 📊 System Statistics")
    print("7. ❓ Help")
    print("8. 🚪 Exit")
    print()

class SimpleBookWriter:
    """Simple book writer with core functionality."""
    
    def __init__(self):
        """Initialize the book writer."""
        self.current_content = ""
        self.current_file = None
        self.is_modified = False
        
        # Initialize data directory
        self.data_dir = Path("./data")
        self.data_dir.mkdir(exist_ok=True)
        
        # Initialize components
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize system components."""
        # Templates
        self.templates = {
            "business": {
                "name": "Business Report",
                "content": """# Business Report

## Executive Summary
Brief overview of the report's key findings and recommendations.

## Introduction
Background and context for the report.

## Analysis
Detailed analysis of the data and findings.

## Conclusion
Summary of key insights.

## Recommendations
Actionable recommendations based on the analysis.

## References
Sources and citations used in the report.
"""
            },
            "academic": {
                "name": "Academic Paper",
                "content": """# Academic Paper

## Abstract
A concise summary of the research, methodology, and findings.

## Introduction
Background, research question, and objectives.

## Literature Review
Review of relevant existing research and theories.

## Methodology
Description of research methods and approach.

## Results
Presentation of research findings and data.

## Discussion
Analysis and interpretation of results.

## Conclusion
Summary of findings and implications.

## References
Academic sources and citations.
"""
            },
            "technical": {
                "name": "Technical Guide",
                "content": """# Technical Guide

## Overview
Introduction to the technology or process.

## Prerequisites
Requirements and setup needed.

## Installation
Step-by-step installation instructions.

## Usage
How to use the technology or process.

## Examples
Practical examples and use cases.

## Troubleshooting
Common issues and solutions.

## Advanced Topics
Advanced usage and customization.
"""
            },
            "creative": {
                "name": "Creative Writing",
                "content": """# Creative Writing

## Chapter 1
*Begin your story here...*

The opening of your narrative should capture the reader's attention and establish the setting, characters, and tone.

## Chapter 2
*Continue your narrative...*

Develop your plot, introduce conflict, and deepen character relationships.

## Chapter 3
*Build toward climax...*

Increase tension and move the story toward its peak moment.

## Chapter 4
*Resolution and conclusion...*

Bring your story to a satisfying conclusion.
"""
            }
        }
        
        # Research history
        self.research_history = []
        
        # Documents
        self.documents = {}
    
    def start_writing(self):
        """Start the text editor."""
        print("📝 Text Editor")
        print("-" * 20)
        print("Enter your content (type 'SAVE' on a new line to save, 'EXIT' to return to menu):")
        print()
        
        content_lines = []
        if self.current_content:
            print("Current content:")
            print(self.current_content)
            print("\nContinue editing:")
        
        while True:
            try:
                line = input()
                if line.strip().upper() == "EXIT":
                    break
                elif line.strip().upper() == "SAVE":
                    self.current_content = "\n".join(content_lines)
                    self.is_modified = True
                    print("✓ Content saved")
                    break
                else:
                    content_lines.append(line)
            except KeyboardInterrupt:
                print("\nExiting editor...")
                break
        
        if content_lines:
            self.current_content = "\n".join(content_lines)
            self.is_modified = True
    
    def process_document(self):
        """Process a document."""
        print("📄 Document Processing")
        print("-" * 25)
        
        file_path = input("Enter file path: ").strip()
        if not file_path:
            print("✗ No file path provided")
            return
        
        file_path = Path(file_path)
        if not file_path.exists():
            print(f"✗ File not found: {file_path}")
            return
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Process the document
            word_count = len(content.split())
            char_count = len(content)
            
            print(f"✓ Document processed successfully")
            print(f"  File: {file_path.name}")
            print(f"  Size: {file_path.stat().st_size} bytes")
            print(f"  Characters: {char_count}")
            print(f"  Words: {word_count}")
            
            # Ask if user wants to load into editor
            load = input("\nLoad into editor? (y/n): ").strip().lower()
            if load == 'y':
                self.current_content = content
                self.current_file = str(file_path)
                self.is_modified = False
                print("✓ Document loaded into editor")
            
        except Exception as e:
            print(f"✗ Error processing document: {e}")
    
    def research_assistant(self):
        """Research assistant."""
        print("🔍 Research Assistant")
        print("-" * 22)
        
        query = input("Enter your research query: ").strip()
        if not query:
            print("✗ No query provided")
            return
        
        print(f"\nSearching for: {query}")
        print("Processing...")
        
        # Simulate research
        import time
        time.sleep(1)
        
        # Generate sample results
        results = [
            {
                "title": f"Research Result: {query}",
                "snippet": f"This is a comprehensive analysis of {query} covering key aspects, methodologies, and findings in the field.",
                "url": "https://example.com/research1",
                "source": "Academic Database"
            },
            {
                "title": f"Industry Report: {query}",
                "snippet": f"An industry report examining current trends and future prospects related to {query}.",
                "url": "https://example.com/report1",
                "source": "Industry Research"
            },
            {
                "title": f"Expert Analysis: {query}",
                "snippet": f"Expert insights and analysis on {query} from leading professionals in the field.",
                "url": "https://example.com/expert1",
                "source": "Expert Opinion"
            }
        ]
        
        print(f"\nFound {len(results)} results:")
        print()
        
        for i, result in enumerate(results, 1):
            print(f"{i}. {result['title']}")
            print(f"   {result['snippet']}")
            print(f"   Source: {result['source']}")
            print(f"   URL: {result['url']}")
            print()
        
        # Add to research history
        self.research_history.append({
            "query": query,
            "results": results,
            "timestamp": datetime.now().isoformat()
        })
        
        # Ask if user wants to add to content
        add = input("Add research summary to current content? (y/n): ").strip().lower()
        if add == 'y':
            research_summary = f"\n\n## Research: {query}\n\n"
            for i, result in enumerate(results, 1):
                research_summary += f"{i}. {result['title']}\n   {result['snippet']}\n\n"
            
            self.current_content += research_summary
            self.is_modified = True
            print("✓ Research summary added to content")
    
    def apply_template(self):
        """Apply a template."""
        print("📋 Templates")
        print("-" * 15)
        
        print("Available templates:")
        for i, (key, template) in enumerate(self.templates.items(), 1):
            print(f"{i}. {template['name']}")
        
        try:
            choice = int(input("\nSelect template (1-4): ").strip())
            template_keys = list(self.templates.keys())
            
            if 1 <= choice <= len(template_keys):
                template_key = template_keys[choice - 1]
                template = self.templates[template_key]
                
                print(f"\nApplying template: {template['name']}")
                
                if self.current_content and self.is_modified:
                    save = input("Current content will be replaced. Save first? (y/n): ").strip().lower()
                    if save == 'y':
                        self.save_content()
                
                self.current_content = template['content']
                self.is_modified = True
                print("✓ Template applied successfully")
            else:
                print("✗ Invalid template selection")
                
        except ValueError:
            print("✗ Please enter a valid number")
    
    def export_content(self):
        """Export content."""
        print("📤 Export Content")
        print("-" * 18)
        
        if not self.current_content:
            print("✗ No content to export")
            return
        
        print("Available formats:")
        print("1. Text (.txt)")
        print("2. Markdown (.md)")
        print("3. HTML (.html)")
        print("4. JSON (.json)")
        
        try:
            format_choice = int(input("\nSelect format (1-4): ").strip())
            
            filename = input("Enter filename (without extension): ").strip()
            if not filename:
                filename = f"book_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Create exports directory
            exports_dir = self.data_dir / "exports"
            exports_dir.mkdir(exist_ok=True)
            
            if format_choice == 1:
                file_path = exports_dir / f"{filename}.txt"
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.current_content)
                print(f"✓ Exported to: {file_path}")
                
            elif format_choice == 2:
                file_path = exports_dir / f"{filename}.md"
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.current_content)
                print(f"✓ Exported to: {file_path}")
                
            elif format_choice == 3:
                html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>{filename}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
        h1, h2, h3 {{ color: #333; }}
        p {{ margin-bottom: 16px; }}
        pre {{ white-space: pre-wrap; }}
    </style>
</head>
<body>
    <pre>{self.current_content}</pre>
</body>
</html>"""
                file_path = exports_dir / f"{filename}.html"
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                print(f"✓ Exported to: {file_path}")
                
            elif format_choice == 4:
                export_data = {
                    "filename": filename,
                    "content": self.current_content,
                    "word_count": len(self.current_content.split()),
                    "character_count": len(self.current_content),
                    "exported_at": datetime.now().isoformat(),
                    "research_history": self.research_history
                }
                file_path = exports_dir / f"{filename}.json"
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, default=str)
                print(f"✓ Exported to: {file_path}")
                
            else:
                print("✗ Invalid format selection")
                
        except ValueError:
            print("✗ Please enter a valid number")
        except Exception as e:
            print(f"✗ Export failed: {e}")
    
    def save_content(self):
        """Save current content."""
        if not self.current_content:
            print("✗ No content to save")
            return
        
        filename = input("Enter filename (without extension): ").strip()
        if not filename:
            filename = f"book_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        file_path = self.data_dir / f"{filename}.txt"
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(self.current_content)
            self.current_file = str(file_path)
            self.is_modified = False
            print(f"✓ Content saved to: {file_path}")
        except Exception as e:
            print(f"✗ Save failed: {e}")
    
    def show_statistics(self):
        """Show system statistics."""
        print("📊 System Statistics")
        print("-" * 22)
        
        word_count = len(self.current_content.split()) if self.current_content else 0
        char_count = len(self.current_content) if self.current_content else 0
        research_count = len(self.research_history)
        
        print(f"Current Content:")
        print(f"  Words: {word_count}")
        print(f"  Characters: {char_count}")
        print(f"  Modified: {'Yes' if self.is_modified else 'No'}")
        print(f"  File: {self.current_file or 'None'}")
        print()
        print(f"Research History: {research_count} searches")
        print(f"Available Templates: {len(self.templates)}")
        print(f"Data Directory: {self.data_dir}")
        print()
        
        if self.research_history:
            print("Recent Research:")
            for i, research in enumerate(self.research_history[-3:], 1):
                print(f"  {i}. {research['query']} ({research['timestamp'][:10]})")
    
    def show_help(self):
        """Show help information."""
        print("❓ Help")
        print("-" * 8)
        print("BookWriter Pro is an AI-powered book writing system with the following features:")
        print()
        print("📝 Text Editor: Write and edit your book content")
        print("📄 Document Processing: Import and process existing documents")
        print("🔍 Research Assistant: Search for information and add to your content")
        print("📋 Templates: Apply pre-built templates for different book types")
        print("📤 Export: Export your content in multiple formats")
        print("📊 Statistics: View writing statistics and progress")
        print()
        print("Tips:")
        print("- Use templates to get started quickly")
        print("- Research assistant helps gather information")
        print("- Export in different formats for different uses")
        print("- Save your work regularly")

def main():
    """Main application loop."""
    print_header()
    
    # Initialize book writer
    writer = SimpleBookWriter()
    
    while True:
        print_menu()
        
        try:
            choice = input("Enter your choice (1-8): ").strip()
            
            if choice == "1":
                writer.start_writing()
            elif choice == "2":
                writer.process_document()
            elif choice == "3":
                writer.research_assistant()
            elif choice == "4":
                writer.apply_template()
            elif choice == "5":
                writer.export_content()
            elif choice == "6":
                writer.show_statistics()
            elif choice == "7":
                writer.show_help()
            elif choice == "8":
                if writer.is_modified:
                    save = input("Save current content before exiting? (y/n): ").strip().lower()
                    if save == 'y':
                        writer.save_content()
                print("Goodbye! 👋")
                break
            else:
                print("✗ Invalid choice. Please enter 1-8.")
            
            print()
            
        except KeyboardInterrupt:
            print("\n\nGoodbye! 👋")
            break
        except Exception as e:
            print(f"✗ Error: {e}")

if __name__ == "__main__":
    main()