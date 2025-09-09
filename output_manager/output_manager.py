"""
Enhanced Output Manager Module

Provides comprehensive output management for generated books with clear folder structure,
metadata management, version control, and asset management.

Features:
- Hierarchical folder structure
- Book metadata management
- Version control and history
- Asset management (images, charts, references)
- Export organization
- Template management
- Archive system
"""

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import logging

import pydantic

logger = logging.getLogger(__name__)


class BookMetadata(pydantic.BaseModel):
    """Metadata model for books."""
    book_id: str
    title: str
    subtitle: Optional[str] = None
    author: str
    description: str
    target_audience: str
    genre: Optional[str] = None
    language: str = "en"
    created_at: datetime
    updated_at: datetime
    status: str = "draft"  # draft, in_progress, completed, published
    total_word_count: int = 0
    chapter_count: int = 0
    version: str = "1.0.0"
    tags: List[str] = []
    isbn: Optional[str] = None
    publisher: Optional[str] = None
    publication_date: Optional[datetime] = None
    cover_image: Optional[str] = None
    custom_fields: Dict[str, Any] = {}


class VersionHistory(pydantic.BaseModel):
    """Version history model."""
    versions: List[Dict[str, Any]] = []
    
    def add_version(self, version: str, description: str, changes: List[str], author: str = "system"):
        """Add a new version entry."""
        version_entry = {
            "version": version,
            "description": description,
            "changes": changes,
            "author": author,
            "timestamp": datetime.now().isoformat(),
            "word_count": 0,  # Will be updated by caller
            "chapter_count": 0  # Will be updated by caller
        }
        self.versions.append(version_entry)
    
    def get_latest_version(self) -> Optional[Dict[str, Any]]:
        """Get the latest version."""
        return self.versions[-1] if self.versions else None


class BuildLog(pydantic.BaseModel):
    """Build log model for tracking generation process."""
    book_id: str
    build_id: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    status: str = "running"  # running, completed, failed
    steps: List[Dict[str, Any]] = []
    errors: List[str] = []
    warnings: List[str] = []
    statistics: Dict[str, Any] = {}
    
    def add_step(self, step_name: str, status: str, details: str = "", duration: float = 0.0):
        """Add a build step."""
        step = {
            "step_name": step_name,
            "status": status,
            "details": details,
            "duration": duration,
            "timestamp": datetime.now().isoformat()
        }
        self.steps.append(step)
    
    def complete_build(self, status: str = "completed"):
        """Mark build as completed."""
        self.completed_at = datetime.now()
        self.status = status


class OutputManager:
    """
    Enhanced output manager for comprehensive book generation management.
    
    Features:
    - Hierarchical folder structure
    - Book metadata management
    - Version control and history
    - Asset management
    - Export organization
    - Template management
    - Archive system
    """
    
    def __init__(self, base_output_dir: str = "./output"):
        """
        Initialize output manager.
        
        Args:
            base_output_dir: Base directory for all outputs
        """
        self.base_dir = Path(base_output_dir)
        self.books_dir = self.base_dir / "books"
        self.templates_dir = self.base_dir / "templates"
        self.styles_dir = self.base_dir / "styles"
        self.archives_dir = self.base_dir / "archives"
        self.temp_dir = self.base_dir / "temp"
        
        # Create base directories
        self._create_base_structure()
        
        logger.info(f"Output manager initialized with base directory: {self.base_dir}")
    
    def _create_base_structure(self):
        """Create base directory structure."""
        directories = [
            self.base_dir,
            self.books_dir,
            self.templates_dir,
            self.styles_dir,
            self.archives_dir,
            self.temp_dir
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
        
        # Create template subdirectories
        (self.templates_dir / "book_templates").mkdir(exist_ok=True)
        (self.templates_dir / "chapter_templates").mkdir(exist_ok=True)
        (self.templates_dir / "style_templates").mkdir(exist_ok=True)
        
        # Create style subdirectories
        (self.styles_dir / "academic").mkdir(exist_ok=True)
        (self.styles_dir / "business").mkdir(exist_ok=True)
        (self.styles_dir / "creative").mkdir(exist_ok=True)
        (self.styles_dir / "technical").mkdir(exist_ok=True)
    
    def create_book_structure(self, book_id: str, title: str, author: str, 
                            description: str, target_audience: str) -> Path:
        """
        Create comprehensive book folder structure.
        
        Args:
            book_id: Unique book identifier
            title: Book title
            author: Book author
            description: Book description
            target_audience: Target audience
            
        Returns:
            Path to created book directory
        """
        book_dir = self.books_dir / book_id
        book_dir.mkdir(parents=True, exist_ok=True)
        
        # Create main subdirectories
        subdirs = [
            "drafts",
            "final",
            "exports",
            "exports/pdf",
            "exports/docx",
            "exports/epub",
            "exports/markdown",
            "exports/html",
            "assets",
            "assets/images",
            "assets/charts",
            "assets/references",
            "assets/audio",
            "collaboration",
            "collaboration/comments",
            "collaboration/versions",
            "research",
            "research/sources",
            "research/notes",
            "templates"
        ]
        
        for subdir in subdirs:
            (book_dir / subdir).mkdir(parents=True, exist_ok=True)
        
        # Create metadata
        metadata = BookMetadata(
            book_id=book_id,
            title=title,
            author=author,
            description=description,
            target_audience=target_audience,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        self._save_metadata(book_dir, metadata)
        
        # Create version history
        version_history = VersionHistory()
        version_history.add_version(
            version="1.0.0",
            description="Initial book creation",
            changes=["Book structure created", "Metadata initialized"],
            author="system"
        )
        self._save_version_history(book_dir, version_history)
        
        # Create initial build log
        build_log = BuildLog(
            book_id=book_id,
            build_id=f"build_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            started_at=datetime.now()
        )
        self._save_build_log(book_dir, build_log)
        
        # Create README for the book
        self._create_book_readme(book_dir, metadata)
        
        logger.info(f"Created book structure for '{title}' at {book_dir}")
        
        return book_dir
    
    def get_book_directory(self, book_id: str) -> Optional[Path]:
        """Get book directory path."""
        book_dir = self.books_dir / book_id
        return book_dir if book_dir.exists() else None
    
    def list_books(self) -> List[Dict[str, Any]]:
        """List all books with metadata."""
        books = []
        
        for book_dir in self.books_dir.iterdir():
            if book_dir.is_dir():
                metadata_path = book_dir / "metadata.json"
                if metadata_path.exists():
                    try:
                        with open(metadata_path, 'r', encoding='utf-8') as f:
                            metadata_data = json.load(f)
                            books.append(metadata_data)
                    except Exception as e:
                        logger.warning(f"Failed to load metadata for {book_dir.name}: {e}")
        
        return sorted(books, key=lambda x: x.get('updated_at', ''), reverse=True)
    
    def update_book_metadata(self, book_id: str, **updates) -> bool:
        """Update book metadata."""
        book_dir = self.get_book_directory(book_id)
        if not book_dir:
            return False
        
        metadata_path = book_dir / "metadata.json"
        if not metadata_path.exists():
            return False
        
        try:
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata_data = json.load(f)
            
            # Update fields
            for key, value in updates.items():
                if key in metadata_data:
                    metadata_data[key] = value
            
            metadata_data['updated_at'] = datetime.now().isoformat()
            
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata_data, f, indent=2, default=str)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to update metadata for {book_id}: {e}")
            return False
    
    def add_asset(self, book_id: str, asset_type: str, file_path: Union[str, Path], 
                  asset_name: Optional[str] = None) -> Optional[Path]:
        """
        Add asset to book.
        
        Args:
            book_id: Book identifier
            asset_type: Type of asset (images, charts, references, audio)
            file_path: Path to asset file
            asset_name: Optional custom name for asset
            
        Returns:
            Path to copied asset or None if failed
        """
        book_dir = self.get_book_directory(book_id)
        if not book_dir:
            return None
        
        asset_dir = book_dir / "assets" / asset_type
        asset_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = Path(file_path)
        if not file_path.exists():
            logger.error(f"Asset file not found: {file_path}")
            return None
        
        # Generate asset name if not provided
        if not asset_name:
            asset_name = file_path.name
        
        # Ensure unique name
        counter = 1
        original_name = asset_name
        while (asset_dir / asset_name).exists():
            name_parts = original_name.rsplit('.', 1)
            if len(name_parts) == 2:
                asset_name = f"{name_parts[0]}_{counter}.{name_parts[1]}"
            else:
                asset_name = f"{original_name}_{counter}"
            counter += 1
        
        # Copy asset
        dest_path = asset_dir / asset_name
        try:
            shutil.copy2(file_path, dest_path)
            logger.info(f"Added asset {asset_name} to {book_id}")
            return dest_path
        except Exception as e:
            logger.error(f"Failed to copy asset {file_path}: {e}")
            return None
    
    def export_book(self, book_id: str, format: str, content: str, 
                   filename: Optional[str] = None) -> Optional[Path]:
        """
        Export book content to specified format.
        
        Args:
            book_id: Book identifier
            format: Export format (pdf, docx, epub, markdown, html)
            content: Book content
            filename: Optional custom filename
            
        Returns:
            Path to exported file or None if failed
        """
        book_dir = self.get_book_directory(book_id)
        if not book_dir:
            return None
        
        export_dir = book_dir / "exports" / format
        export_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename if not provided
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{book_id}_{timestamp}.{format}"
        
        export_path = export_dir / filename
        
        try:
            with open(export_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"Exported {book_id} to {format} format: {export_path}")
            return export_path
            
        except Exception as e:
            logger.error(f"Failed to export {book_id} to {format}: {e}")
            return None
    
    def archive_book(self, book_id: str, reason: str = "completed") -> bool:
        """Archive a book."""
        book_dir = self.get_book_directory(book_id)
        if not book_dir:
            return False
        
        try:
            # Create archive directory
            archive_dir = self.archives_dir / f"{book_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            archive_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy book directory to archive
            shutil.copytree(book_dir, archive_dir / book_id)
            
            # Add archive metadata
            archive_metadata = {
                "book_id": book_id,
                "archived_at": datetime.now().isoformat(),
                "reason": reason,
                "original_path": str(book_dir)
            }
            
            with open(archive_dir / "archive_metadata.json", 'w', encoding='utf-8') as f:
                json.dump(archive_metadata, f, indent=2)
            
            # Remove original book directory
            shutil.rmtree(book_dir)
            
            logger.info(f"Archived book {book_id} to {archive_dir}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to archive book {book_id}: {e}")
            return False
    
    def _save_metadata(self, book_dir: Path, metadata: BookMetadata):
        """Save book metadata."""
        metadata_path = book_dir / "metadata.json"
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata.dict(), f, indent=2, default=str)
    
    def _save_version_history(self, book_dir: Path, version_history: VersionHistory):
        """Save version history."""
        history_path = book_dir / "version_history.json"
        with open(history_path, 'w', encoding='utf-8') as f:
            json.dump(version_history.dict(), f, indent=2, default=str)
    
    def _save_build_log(self, book_dir: Path, build_log: BuildLog):
        """Save build log."""
        log_path = book_dir / "build_log.json"
        with open(log_path, 'w', encoding='utf-8') as f:
            json.dump(build_log.dict(), f, indent=2, default=str)
    
    def _create_book_readme(self, book_dir: Path, metadata: BookMetadata):
        """Create README file for book."""
        readme_content = f"""# {metadata.title}

**Author:** {metadata.author}  
**Created:** {metadata.created_at.strftime('%Y-%m-%d %H:%M:%S')}  
**Status:** {metadata.status}  
**Word Count:** {metadata.total_word_count:,}  
**Chapters:** {metadata.chapter_count}

## Description
{metadata.description}

## Target Audience
{metadata.target_audience}

## Directory Structure
- `drafts/` - Work in progress versions
- `final/` - Completed versions
- `exports/` - Exported files in various formats
- `assets/` - Images, charts, references, and other assets
- `collaboration/` - Comments, versions, and collaboration files
- `research/` - Research materials and sources
- `templates/` - Book-specific templates

## Files
- `metadata.json` - Book metadata
- `version_history.json` - Version control history
- `build_log.json` - Build and generation logs
- `README.md` - This file

## Usage
This book was generated using the Book Writing System.
"""
        
        readme_path = book_dir / "README.md"
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get output manager statistics."""
        stats = {
            "total_books": len(list(self.books_dir.iterdir())) if self.books_dir.exists() else 0,
            "total_archives": len(list(self.archives_dir.iterdir())) if self.archives_dir.exists() else 0,
            "total_templates": len(list(self.templates_dir.rglob("*.json"))) if self.templates_dir.exists() else 0,
            "total_styles": len(list(self.styles_dir.rglob("*.json"))) if self.styles_dir.exists() else 0,
            "base_directory": str(self.base_dir),
            "books_directory": str(self.books_dir),
            "archives_directory": str(self.archives_dir)
        }
        
        return stats