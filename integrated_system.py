"""
Integrated Book Writing System

Connects all modules and provides a working system that can be used
immediately without complex dependencies.
"""

import sys
import os
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
import json
import asyncio
import threading
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IntegratedSystem:
    """
    Integrated book writing system that connects all modules.
    
    Features:
    - Document processing and ingestion
    - Memory management and storage
    - Research capabilities
    - Export functionality
    - Template system
    - Style management
    """
    
    def __init__(self, data_dir: str = "./data"):
        """Initialize the integrated system."""
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self._initialize_components()
        
        logger.info("Integrated system initialized")
    
    def _initialize_components(self):
        """Initialize all system components."""
        try:
            # Initialize memory manager (simplified)
            self.memory_manager = self._create_memory_manager()
            
            # Initialize document processor (simplified)
            self.document_processor = self._create_document_processor()
            
            # Initialize research assistant (simplified)
            self.research_assistant = self._create_research_assistant()
            
            # Initialize template manager (simplified)
            self.template_manager = self._create_template_manager()
            
            # Initialize export manager (simplified)
            self.export_manager = self._create_export_manager()
            
            logger.info("All components initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize components: {e}")
            raise
    
    def _create_memory_manager(self):
        """Create a simplified memory manager."""
        class SimpleMemoryManager:
            def __init__(self, data_dir):
                self.data_dir = data_dir
                self.documents = {}
                self.chunks = {}
            
            def store_document(self, doc_id: str, content: str, metadata: Dict[str, Any]):
                """Store a document."""
                self.documents[doc_id] = {
                    "content": content,
                    "metadata": metadata,
                    "timestamp": datetime.now().isoformat()
                }
                self._save_to_file()
            
            def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
                """Get a document."""
                return self.documents.get(doc_id)
            
            def search_documents(self, query: str) -> List[Dict[str, Any]]:
                """Search documents."""
                results = []
                for doc_id, doc in self.documents.items():
                    if query.lower() in doc["content"].lower():
                        results.append({"doc_id": doc_id, **doc})
                return results
            
            def _save_to_file(self):
                """Save to file."""
                try:
                    with open(self.data_dir / "memory.json", 'w') as f:
                        json.dump(self.documents, f, indent=2, default=str)
                except Exception as e:
                    logger.error(f"Failed to save memory: {e}")
        
        return SimpleMemoryManager(self.data_dir)
    
    def _create_document_processor(self):
        """Create a simplified document processor."""
        class SimpleDocumentProcessor:
            def __init__(self, data_dir):
                self.data_dir = data_dir
            
            def process_text_file(self, file_path: str) -> Dict[str, Any]:
                """Process a text file."""
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    return {
                        "success": True,
                        "content": content,
                        "metadata": {
                            "file_path": file_path,
                            "file_size": len(content),
                            "word_count": len(content.split()),
                            "processed_at": datetime.now().isoformat()
                        }
                    }
                except Exception as e:
                    return {
                        "success": False,
                        "error": str(e),
                        "content": "",
                        "metadata": {}
                    }
            
            def chunk_text(self, text: str, chunk_size: int = 1000) -> List[str]:
                """Chunk text into smaller pieces."""
                words = text.split()
                chunks = []
                
                for i in range(0, len(words), chunk_size):
                    chunk = ' '.join(words[i:i + chunk_size])
                    chunks.append(chunk)
                
                return chunks
        
        return SimpleDocumentProcessor(self.data_dir)
    
    def _create_research_assistant(self):
        """Create a simplified research assistant."""
        class SimpleResearchAssistant:
            def __init__(self, data_dir):
                self.data_dir = data_dir
                self.search_history = []
            
            def search(self, query: str) -> List[Dict[str, Any]]:
                """Perform a search."""
                # Simulate search results
                results = [
                    {
                        "title": f"Research Result for: {query}",
                        "snippet": f"This is a sample research result for the query '{query}'. It contains relevant information that could be useful for your book.",
                        "url": "https://example.com/result1",
                        "source": "web_search"
                    },
                    {
                        "title": f"Academic Paper: {query}",
                        "snippet": f"An academic paper discussing {query} and its implications for modern research.",
                        "url": "https://example.com/paper1",
                        "source": "academic_search"
                    }
                ]
                
                self.search_history.append({
                    "query": query,
                    "results": results,
                    "timestamp": datetime.now().isoformat()
                })
                
                return results
            
            def get_search_history(self) -> List[Dict[str, Any]]:
                """Get search history."""
                return self.search_history
        
        return SimpleResearchAssistant(self.data_dir)
    
    def _create_template_manager(self):
        """Create a simplified template manager."""
        class SimpleTemplateManager:
            def __init__(self, data_dir):
                self.data_dir = data_dir
                self.templates = {
                    "business_report": {
                        "name": "Business Report",
                        "content": "# Business Report\n\n## Executive Summary\n\n## Introduction\n\n## Analysis\n\n## Conclusion\n\n## Recommendations\n",
                        "description": "Template for business reports and white papers"
                    },
                    "academic_paper": {
                        "name": "Academic Paper",
                        "content": "# Academic Paper\n\n## Abstract\n\n## Introduction\n\n## Literature Review\n\n## Methodology\n\n## Results\n\n## Discussion\n\n## Conclusion\n\n## References\n",
                        "description": "Template for academic papers and research"
                    },
                    "technical_guide": {
                        "name": "Technical Guide",
                        "content": "# Technical Guide\n\n## Overview\n\n## Prerequisites\n\n## Installation\n\n## Usage\n\n## Examples\n\n## Troubleshooting\n",
                        "description": "Template for technical documentation"
                    },
                    "creative_writing": {
                        "name": "Creative Writing",
                        "content": "# Creative Writing\n\n## Chapter 1\n\n*Begin your story here...*\n\n## Chapter 2\n\n*Continue your narrative...*\n",
                        "description": "Template for creative writing and fiction"
                    }
                }
            
            def get_template(self, template_id: str) -> Optional[Dict[str, Any]]:
                """Get a template."""
                return self.templates.get(template_id)
            
            def list_templates(self) -> List[Dict[str, Any]]:
                """List all templates."""
                return list(self.templates.values())
        
        return SimpleTemplateManager(self.data_dir)
    
    def _create_export_manager(self):
        """Create a simplified export manager."""
        class SimpleExportManager:
            def __init__(self, data_dir):
                self.data_dir = data_dir
                self.output_dir = data_dir / "exports"
                self.output_dir.mkdir(exist_ok=True)
            
            def export_text(self, content: str, filename: str) -> str:
                """Export content as text."""
                file_path = self.output_dir / f"{filename}.txt"
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    return str(file_path)
                except Exception as e:
                    logger.error(f"Failed to export text: {e}")
                    return ""
            
            def export_markdown(self, content: str, filename: str) -> str:
                """Export content as markdown."""
                file_path = self.output_dir / f"{filename}.md"
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    return str(file_path)
                except Exception as e:
                    logger.error(f"Failed to export markdown: {e}")
                    return ""
            
            def export_html(self, content: str, filename: str) -> str:
                """Export content as HTML."""
                html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>{filename}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
        h1, h2, h3 {{ color: #333; }}
        p {{ margin-bottom: 16px; }}
    </style>
</head>
<body>
    <pre>{content}</pre>
</body>
</html>
                """
                
                file_path = self.output_dir / f"{filename}.html"
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(html_content)
                    return str(file_path)
                except Exception as e:
                    logger.error(f"Failed to export HTML: {e}")
                    return ""
        
        return SimpleExportManager(self.data_dir)
    
    # Public API methods
    def process_document(self, file_path: str) -> Dict[str, Any]:
        """Process a document."""
        try:
            result = self.document_processor.process_text_file(file_path)
            
            if result["success"]:
                # Store in memory
                doc_id = f"doc_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                self.memory_manager.store_document(doc_id, result["content"], result["metadata"])
                
                return {
                    "success": True,
                    "doc_id": doc_id,
                    "content": result["content"],
                    "metadata": result["metadata"]
                }
            else:
                return result
                
        except Exception as e:
            logger.error(f"Document processing failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "content": "",
                "metadata": {}
            }
    
    def search_research(self, query: str) -> List[Dict[str, Any]]:
        """Search for research information."""
        try:
            return self.research_assistant.search(query)
        except Exception as e:
            logger.error(f"Research search failed: {e}")
            return []
    
    def get_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """Get a template."""
        try:
            return self.template_manager.get_template(template_id)
        except Exception as e:
            logger.error(f"Template retrieval failed: {e}")
            return None
    
    def export_content(self, content: str, filename: str, format_type: str = "text") -> str:
        """Export content in specified format."""
        try:
            if format_type == "text":
                return self.export_manager.export_text(content, filename)
            elif format_type == "markdown":
                return self.export_manager.export_markdown(content, filename)
            elif format_type == "html":
                return self.export_manager.export_html(content, filename)
            else:
                return self.export_manager.export_text(content, filename)
        except Exception as e:
            logger.error(f"Export failed: {e}")
            return ""
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get system statistics."""
        try:
            return {
                "documents_stored": len(self.memory_manager.documents),
                "search_history_count": len(self.research_assistant.search_history),
                "templates_available": len(self.template_manager.templates),
                "data_directory": str(self.data_dir),
                "system_status": "operational"
            }
        except Exception as e:
            logger.error(f"Statistics retrieval failed: {e}")
            return {"system_status": "error", "error": str(e)}


def main():
    """Main entry point for the integrated system."""
    try:
        # Initialize system
        system = IntegratedSystem()
        
        print("BookWriter Pro - Integrated System")
        print("=" * 40)
        
        # Interactive menu
        while True:
            print("\nAvailable commands:")
            print("1. Process document")
            print("2. Search research")
            print("3. Get template")
            print("4. Export content")
            print("5. Show statistics")
            print("6. Exit")
            
            choice = input("\nEnter your choice (1-6): ").strip()
            
            if choice == "1":
                file_path = input("Enter file path: ").strip()
                if file_path and Path(file_path).exists():
                    result = system.process_document(file_path)
                    if result["success"]:
                        print(f"✓ Document processed successfully")
                        print(f"Content length: {len(result['content'])} characters")
                        print(f"Word count: {result['metadata']['word_count']}")
                    else:
                        print(f"✗ Processing failed: {result['error']}")
                else:
                    print("✗ File not found")
            
            elif choice == "2":
                query = input("Enter search query: ").strip()
                if query:
                    results = system.search_research(query)
                    print(f"\nFound {len(results)} results:")
                    for i, result in enumerate(results, 1):
                        print(f"{i}. {result['title']}")
                        print(f"   {result['snippet']}")
                        print(f"   URL: {result['url']}\n")
                else:
                    print("✗ Please enter a search query")
            
            elif choice == "3":
                print("\nAvailable templates:")
                templates = system.template_manager.list_templates()
                for i, template in enumerate(templates, 1):
                    print(f"{i}. {template['name']} - {template['description']}")
                
                template_choice = input("\nEnter template number: ").strip()
                try:
                    template_index = int(template_choice) - 1
                    if 0 <= template_index < len(templates):
                        template_id = list(system.template_manager.templates.keys())[template_index]
                        template = system.get_template(template_id)
                        if template:
                            print(f"\nTemplate: {template['name']}")
                            print("Content preview:")
                            print(template['content'][:200] + "..." if len(template['content']) > 200 else template['content'])
                        else:
                            print("✗ Template not found")
                    else:
                        print("✗ Invalid template number")
                except ValueError:
                    print("✗ Please enter a valid number")
            
            elif choice == "4":
                content = input("Enter content to export: ").strip()
                filename = input("Enter filename (without extension): ").strip()
                format_type = input("Enter format (text/markdown/html): ").strip().lower()
                
                if content and filename:
                    file_path = system.export_content(content, filename, format_type)
                    if file_path:
                        print(f"✓ Content exported to: {file_path}")
                    else:
                        print("✗ Export failed")
                else:
                    print("✗ Please enter content and filename")
            
            elif choice == "5":
                stats = system.get_statistics()
                print("\nSystem Statistics:")
                for key, value in stats.items():
                    print(f"  {key}: {value}")
            
            elif choice == "6":
                print("Goodbye!")
                break
            
            else:
                print("✗ Invalid choice. Please enter 1-6.")
    
    except KeyboardInterrupt:
        print("\nGoodbye!")
    except Exception as e:
        logger.error(f"System error: {e}")
        print(f"System error: {e}")


if __name__ == "__main__":
    main()