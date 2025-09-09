"""
Modern Mac-Style GUI Application

A professional, modern GUI application built with CustomTkinter
that provides a comprehensive interface for the book writing system.

Features:
- Modern Mac-style interface design
- Modular architecture connecting all system modules
- Real-time document processing and editing
- Collaborative features
- Research integration
- Advanced export capabilities
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import asyncio
import threading
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

# Import system modules
from memory_manager.memory_manager import MemoryManager
from llm_client.llm_client import LLMClient
from tool_manager.tool_manager import ToolManager
from document_ingestor.enhanced_ingestor import EnhancedDocumentIngestor
from document_processor.unified_parser import UnifiedDocumentParser, ProcessingOptions
from output_manager.output_manager import OutputManager
from template_manager.template_manager import TemplateManager
from export_manager.export_manager import ExportManager
from style_manager.style_manager import StyleManager
from research_assistant.research_assistant import ResearchAssistant
from collaboration.collaboration_manager import CollaborationManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set appearance mode and color theme
ctk.set_appearance_mode("light")  # "light" or "dark"
ctk.set_default_color_theme("blue")  # "blue", "green", "dark-blue"


class ModernBookWriterApp:
    """
    Modern Mac-style book writing application.
    
    Features:
    - Professional interface design
    - Modular architecture
    - Real-time collaboration
    - Advanced document processing
    - Research integration
    - Export capabilities
    """
    
    def __init__(self):
        """Initialize the modern book writer application."""
        self.root = ctk.CTk()
        self.root.title("BookWriter Pro")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 800)
        
        # Configure window
        self.root.configure(fg_color=("#f0f0f0", "#1a1a1a"))
        
        # Initialize system modules
        self._initialize_modules()
        
        # Create UI components
        self._create_ui()
        
        # Setup event handlers
        self._setup_event_handlers()
        
        logger.info("Modern BookWriter App initialized")
    
    def _initialize_modules(self):
        """Initialize all system modules."""
        try:
            # Core modules
            self.memory_manager = MemoryManager()
            self.llm_client = LLMClient()
            self.tool_manager = ToolManager()
            
            # Document processing
            self.document_ingestor = EnhancedDocumentIngestor()
            self.document_parser = UnifiedDocumentParser()
            
            # Output and templates
            self.output_manager = OutputManager()
            self.template_manager = TemplateManager()
            self.export_manager = ExportManager()
            self.style_manager = StyleManager()
            
            # Research and collaboration
            self.research_assistant = ResearchAssistant()
            self.collaboration_manager = CollaborationManager()
            
            logger.info("All system modules initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize modules: {e}")
            messagebox.showerror("Initialization Error", f"Failed to initialize system modules: {e}")
    
    def _create_ui(self):
        """Create the main UI components."""
        # Create main container
        self.main_container = ctk.CTkFrame(self.root, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create top toolbar
        self._create_toolbar()
        
        # Create main content area
        self._create_main_content()
        
        # Create status bar
        self._create_status_bar()
    
    def _create_toolbar(self):
        """Create the top toolbar."""
        self.toolbar = ctk.CTkFrame(
            self.main_container, 
            height=60, 
            fg_color=("#ffffff", "#2b2b2b"),
            corner_radius=10
        )
        self.toolbar.pack(fill="x", pady=(0, 10))
        self.toolbar.pack_propagate(False)
        
        # Left side - App title and main actions
        left_frame = ctk.CTkFrame(self.toolbar, fg_color="transparent")
        left_frame.pack(side="left", fill="x", expand=True, padx=15, pady=10)
        
        # App title
        self.title_label = ctk.CTkLabel(
            left_frame,
            text="BookWriter Pro",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=("#1a1a1a", "#ffffff")
        )
        self.title_label.pack(side="left", padx=(0, 20))
        
        # Main action buttons
        self.new_book_btn = ctk.CTkButton(
            left_frame,
            text="New Book",
            command=self._new_book,
            width=100,
            height=35,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.new_book_btn.pack(side="left", padx=(0, 10))
        
        self.open_book_btn = ctk.CTkButton(
            left_frame,
            text="Open Book",
            command=self._open_book,
            width=100,
            height=35,
            font=ctk.CTkFont(size=14)
        )
        self.open_book_btn.pack(side="left", padx=(0, 10))
        
        self.save_book_btn = ctk.CTkButton(
            left_frame,
            text="Save",
            command=self._save_book,
            width=80,
            height=35,
            font=ctk.CTkFont(size=14)
        )
        self.save_book_btn.pack(side="left", padx=(0, 20))
        
        # Right side - User actions and settings
        right_frame = ctk.CTkFrame(self.toolbar, fg_color="transparent")
        right_frame.pack(side="right", padx=15, pady=10)
        
        # Research button
        self.research_btn = ctk.CTkButton(
            right_frame,
            text="Research",
            command=self._open_research_panel,
            width=100,
            height=35,
            font=ctk.CTkFont(size=14)
        )
        self.research_btn.pack(side="right", padx=(10, 0))
        
        # Collaboration button
        self.collaborate_btn = ctk.CTkButton(
            right_frame,
            text="Collaborate",
            command=self._open_collaboration_panel,
            width=100,
            height=35,
            font=ctk.CTkFont(size=14)
        )
        self.collaborate_btn.pack(side="right", padx=(10, 0))
        
        # Settings button
        self.settings_btn = ctk.CTkButton(
            right_frame,
            text="Settings",
            command=self._open_settings,
            width=80,
            height=35,
            font=ctk.CTkFont(size=14)
        )
        self.settings_btn.pack(side="right", padx=(10, 0))
    
    def _create_main_content(self):
        """Create the main content area."""
        # Create main content container
        self.content_container = ctk.CTkFrame(
            self.main_container,
            fg_color=("#ffffff", "#2b2b2b"),
            corner_radius=10
        )
        self.content_container.pack(fill="both", expand=True)
        
        # Create sidebar and main workspace
        self._create_sidebar()
        self._create_workspace()
    
    def _create_sidebar(self):
        """Create the left sidebar."""
        self.sidebar = ctk.CTkFrame(
            self.content_container,
            width=250,
            fg_color=("#f8f9fa", "#1e1e1e"),
            corner_radius=0
        )
        self.sidebar.pack(side="left", fill="y", padx=(0, 1))
        self.sidebar.pack_propagate(False)
        
        # Sidebar header
        sidebar_header = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        sidebar_header.pack(fill="x", padx=15, pady=15)
        
        self.sidebar_title = ctk.CTkLabel(
            sidebar_header,
            text="Project",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=("#1a1a1a", "#ffffff")
        )
        self.sidebar_title.pack(anchor="w")
        
        # Project info
        self.project_info = ctk.CTkLabel(
            sidebar_header,
            text="No project loaded",
            font=ctk.CTkFont(size=12),
            text_color=("#666666", "#cccccc")
        )
        self.project_info.pack(anchor="w", pady=(5, 0))
        
        # Navigation buttons
        self._create_navigation()
        
        # Document processing section
        self._create_document_processing_section()
        
        # Templates section
        self._create_templates_section()
    
    def _create_navigation(self):
        """Create navigation buttons."""
        nav_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        nav_frame.pack(fill="x", padx=15, pady=20)
        
        # Navigation buttons
        nav_buttons = [
            ("📝 Editor", self._show_editor),
            ("📚 Chapters", self._show_chapters),
            ("🔍 Research", self._show_research),
            ("📊 Analytics", self._show_analytics),
            ("⚙️ Settings", self._show_settings)
        ]
        
        self.nav_buttons = {}
        for text, command in nav_buttons:
            btn = ctk.CTkButton(
                nav_frame,
                text=text,
                command=command,
                width=220,
                height=40,
                font=ctk.CTkFont(size=14),
                anchor="w",
                fg_color=("transparent", "transparent"),
                hover_color=("#e9ecef", "#3a3a3a")
            )
            btn.pack(fill="x", pady=2)
            self.nav_buttons[text] = btn
    
    def _create_document_processing_section(self):
        """Create document processing section."""
        doc_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        doc_frame.pack(fill="x", padx=15, pady=20)
        
        # Section title
        doc_title = ctk.CTkLabel(
            doc_frame,
            text="Document Processing",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=("#1a1a1a", "#ffffff")
        )
        doc_title.pack(anchor="w", pady=(0, 10))
        
        # Import document button
        self.import_doc_btn = ctk.CTkButton(
            doc_frame,
            text="Import Document",
            command=self._import_document,
            width=220,
            height=35,
            font=ctk.CTkFont(size=12)
        )
        self.import_doc_btn.pack(fill="x", pady=2)
        
        # Process with OCR button
        self.ocr_btn = ctk.CTkButton(
            doc_frame,
            text="Process with OCR",
            command=self._process_with_ocr,
            width=220,
            height=35,
            font=ctk.CTkFont(size=12)
        )
        self.ocr_btn.pack(fill="x", pady=2)
        
        # Extract tables button
        self.extract_tables_btn = ctk.CTkButton(
            doc_frame,
            text="Extract Tables",
            command=self._extract_tables,
            width=220,
            height=35,
            font=ctk.CTkFont(size=12)
        )
        self.extract_tables_btn.pack(fill="x", pady=2)
    
    def _create_templates_section(self):
        """Create templates section."""
        template_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        template_frame.pack(fill="x", padx=15, pady=20)
        
        # Section title
        template_title = ctk.CTkLabel(
            template_frame,
            text="Templates",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=("#1a1a1a", "#ffffff")
        )
        template_title.pack(anchor="w", pady=(0, 10))
        
        # Template buttons
        template_buttons = [
            ("Business Report", "business_white_paper"),
            ("Academic Paper", "academic_paper"),
            ("Technical Guide", "technical_guide"),
            ("Creative Writing", "creative_writing")
        ]
        
        for text, template_id in template_buttons:
            btn = ctk.CTkButton(
                template_frame,
                text=text,
                command=lambda t=template_id: self._apply_template(t),
                width=220,
                height=30,
                font=ctk.CTkFont(size=11),
                fg_color=("transparent", "transparent"),
                hover_color=("#e9ecef", "#3a3a3a")
            )
            btn.pack(fill="x", pady=1)
    
    def _create_workspace(self):
        """Create the main workspace area."""
        self.workspace = ctk.CTkFrame(
            self.content_container,
            fg_color=("transparent", "transparent")
        )
        self.workspace.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        # Create tabbed interface
        self._create_tabbed_interface()
    
    def _create_tabbed_interface(self):
        """Create tabbed interface for different views."""
        # Create notebook for tabs
        self.notebook = ctk.CTkTabview(
            self.workspace,
            width=800,
            height=600,
            fg_color=("#ffffff", "#2b2b2b")
        )
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create tabs
        self._create_editor_tab()
        self._create_chapters_tab()
        self._create_research_tab()
        self._create_analytics_tab()
    
    def _create_editor_tab(self):
        """Create the main editor tab."""
        self.editor_tab = self.notebook.add("Editor")
        
        # Editor toolbar
        editor_toolbar = ctk.CTkFrame(self.editor_tab, fg_color="transparent")
        editor_toolbar.pack(fill="x", padx=10, pady=(10, 5))
        
        # Formatting buttons
        format_buttons = [
            ("Bold", self._format_bold),
            ("Italic", self._format_italic),
            ("Heading", self._format_heading),
            ("List", self._format_list)
        ]
        
        for text, command in format_buttons:
            btn = ctk.CTkButton(
                editor_toolbar,
                text=text,
                command=command,
                width=60,
                height=30,
                font=ctk.CTkFont(size=11)
            )
            btn.pack(side="left", padx=(0, 5))
        
        # Main text editor
        self.text_editor = ctk.CTkTextbox(
            self.editor_tab,
            width=800,
            height=500,
            font=ctk.CTkFont(size=14),
            fg_color=("#ffffff", "#1e1e1e"),
            text_color=("#1a1a1a", "#ffffff")
        )
        self.text_editor.pack(fill="both", expand=True, padx=10, pady=5)
    
    def _create_chapters_tab(self):
        """Create the chapters management tab."""
        self.chapters_tab = self.notebook.add("Chapters")
        
        # Chapters list
        chapters_frame = ctk.CTkFrame(self.chapters_tab)
        chapters_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Chapters listbox
        self.chapters_listbox = tk.Listbox(
            chapters_frame,
            font=("Arial", 12),
            bg="#ffffff",
            fg="#1a1a1a",
            selectbackground="#007bff",
            selectforeground="#ffffff"
        )
        self.chapters_listbox.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Chapter actions
        chapter_actions = ctk.CTkFrame(chapters_frame)
        chapter_actions.pack(fill="x", padx=10, pady=(0, 10))
        
        ctk.CTkButton(
            chapter_actions,
            text="Add Chapter",
            command=self._add_chapter,
            width=100
        ).pack(side="left", padx=(0, 10))
        
        ctk.CTkButton(
            chapter_actions,
            text="Delete Chapter",
            command=self._delete_chapter,
            width=100
        ).pack(side="left", padx=(0, 10))
    
    def _create_research_tab(self):
        """Create the research assistant tab."""
        self.research_tab = self.notebook.add("Research")
        
        # Research interface
        research_frame = ctk.CTkFrame(self.research_tab)
        research_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Search bar
        search_frame = ctk.CTkFrame(research_frame)
        search_frame.pack(fill="x", padx=10, pady=10)
        
        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Search for information...",
            width=400,
            height=35,
            font=ctk.CTkFont(size=14)
        )
        self.search_entry.pack(side="left", padx=(0, 10))
        
        ctk.CTkButton(
            search_frame,
            text="Search",
            command=self._perform_research,
            width=80,
            height=35
        ).pack(side="left")
        
        # Research results
        self.research_results = ctk.CTkTextbox(
            research_frame,
            width=800,
            height=400,
            font=ctk.CTkFont(size=12)
        )
        self.research_results.pack(fill="both", expand=True, padx=10, pady=10)
    
    def _create_analytics_tab(self):
        """Create the analytics tab."""
        self.analytics_tab = self.notebook.add("Analytics")
        
        # Analytics content
        analytics_frame = ctk.CTkFrame(self.analytics_tab)
        analytics_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Analytics widgets
        ctk.CTkLabel(
            analytics_frame,
            text="Writing Analytics",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=20)
        
        # Word count
        self.word_count_label = ctk.CTkLabel(
            analytics_frame,
            text="Word Count: 0",
            font=ctk.CTkFont(size=16)
        )
        self.word_count_label.pack(pady=10)
        
        # Progress tracking
        self.progress_label = ctk.CTkLabel(
            analytics_frame,
            text="Progress: 0%",
            font=ctk.CTkFont(size=16)
        )
        self.progress_label.pack(pady=10)
    
    def _create_status_bar(self):
        """Create the status bar."""
        self.status_bar = ctk.CTkFrame(
            self.main_container,
            height=30,
            fg_color=("#f8f9fa", "#1e1e1e")
        )
        self.status_bar.pack(fill="x", pady=(10, 0))
        self.status_bar.pack_propagate(False)
        
        # Status text
        self.status_label = ctk.CTkLabel(
            self.status_bar,
            text="Ready",
            font=ctk.CTkFont(size=12),
            text_color=("#666666", "#cccccc")
        )
        self.status_label.pack(side="left", padx=15, pady=5)
        
        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(
            self.status_bar,
            width=200,
            height=20
        )
        self.progress_bar.pack(side="right", padx=15, pady=5)
        self.progress_bar.set(0)
    
    def _setup_event_handlers(self):
        """Setup event handlers."""
        # Text editor events
        self.text_editor.bind("<KeyRelease>", self._on_text_change)
        
        # Window events
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    # Event handlers
    def _on_text_change(self, event):
        """Handle text change in editor."""
        # Update word count
        text = self.text_editor.get("1.0", "end-1c")
        word_count = len(text.split())
        self.word_count_label.configure(text=f"Word Count: {word_count}")
    
    def _on_closing(self):
        """Handle application closing."""
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.root.destroy()
    
    # Action methods
    def _new_book(self):
        """Create a new book project."""
        self.text_editor.delete("1.0", "end")
        self.project_info.configure(text="New Book Project")
        self.status_label.configure(text="New book created")
    
    def _open_book(self):
        """Open an existing book project."""
        file_path = filedialog.askopenfilename(
            title="Open Book Project",
            filetypes=[("BookWriter Files", "*.bwp"), ("All Files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.text_editor.delete("1.0", "end")
                self.text_editor.insert("1.0", content)
                self.project_info.configure(text=f"Project: {Path(file_path).name}")
                self.status_label.configure(text="Book opened successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open book: {e}")
    
    def _save_book(self):
        """Save the current book project."""
        file_path = filedialog.asksaveasfilename(
            title="Save Book Project",
            defaultextension=".bwp",
            filetypes=[("BookWriter Files", "*.bwp"), ("All Files", "*.*")]
        )
        if file_path:
            try:
                content = self.text_editor.get("1.0", "end-1c")
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.status_label.configure(text="Book saved successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save book: {e}")
    
    def _import_document(self):
        """Import a document for processing."""
        file_path = filedialog.askopenfilename(
            title="Import Document",
            filetypes=[
                ("PDF Files", "*.pdf"),
                ("Word Documents", "*.docx"),
                ("Text Files", "*.txt"),
                ("Markdown Files", "*.md"),
                ("All Files", "*.*")
            ]
        )
        if file_path:
            self._process_document(file_path)
    
    def _process_document(self, file_path: str):
        """Process a document with the enhanced ingestor."""
        def process_async():
            try:
                self.status_label.configure(text="Processing document...")
                self.progress_bar.set(0.2)
                
                # Process document
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                metadata = loop.run_until_complete(
                    self.document_ingestor.ingest_document(file_path)
                )
                
                self.progress_bar.set(0.8)
                
                # Update UI with processed content
                self.text_editor.delete("1.0", "end")
                self.text_editor.insert("1.0", f"Processed document: {metadata.original_filename}\n\n")
                
                self.progress_bar.set(1.0)
                self.status_label.configure(text="Document processed successfully")
                
            except Exception as e:
                self.status_label.configure(text=f"Error processing document: {e}")
                messagebox.showerror("Error", f"Failed to process document: {e}")
            finally:
                self.progress_bar.set(0)
        
        # Run in separate thread
        threading.Thread(target=process_async, daemon=True).start()
    
    def _process_with_ocr(self):
        """Process document with OCR."""
        file_path = filedialog.askopenfilename(
            title="Select Document for OCR",
            filetypes=[
                ("Image Files", "*.png *.jpg *.jpeg"),
                ("PDF Files", "*.pdf"),
                ("All Files", "*.*")
            ]
        )
        if file_path:
            self._process_document_with_ocr(file_path)
    
    def _process_document_with_ocr(self, file_path: str):
        """Process document with OCR."""
        def process_async():
            try:
                self.status_label.configure(text="Processing with OCR...")
                self.progress_bar.set(0.3)
                
                # Process with OCR
                processing_options = ProcessingOptions(
                    perform_ocr=True,
                    extract_text=True,
                    analyze_layout=True
                )
                
                result = self.document_parser.parse_document(file_path, processing_options)
                
                self.progress_bar.set(0.8)
                
                # Update UI
                self.text_editor.delete("1.0", "end")
                self.text_editor.insert("1.0", f"OCR Results:\n\n{result.text_content}")
                
                self.progress_bar.set(1.0)
                self.status_label.configure(text="OCR processing completed")
                
            except Exception as e:
                self.status_label.configure(text=f"OCR error: {e}")
                messagebox.showerror("Error", f"OCR processing failed: {e}")
            finally:
                self.progress_bar.set(0)
        
        threading.Thread(target=process_async, daemon=True).start()
    
    def _extract_tables(self):
        """Extract tables from document."""
        file_path = filedialog.askopenfilename(
            title="Select Document for Table Extraction",
            filetypes=[
                ("PDF Files", "*.pdf"),
                ("Image Files", "*.png *.jpg *.jpeg"),
                ("All Files", "*.*")
            ]
        )
        if file_path:
            self._process_table_extraction(file_path)
    
    def _process_table_extraction(self, file_path: str):
        """Process table extraction."""
        def process_async():
            try:
                self.status_label.configure(text="Extracting tables...")
                self.progress_bar.set(0.3)
                
                # Extract tables
                processing_options = ProcessingOptions(
                    extract_tables=True,
                    extract_text=True
                )
                
                result = self.document_parser.parse_document(file_path, processing_options)
                
                self.progress_bar.set(0.8)
                
                # Display tables
                table_text = "Extracted Tables:\n\n"
                for i, table in enumerate(result.tables):
                    table_text += f"Table {i+1}:\n"
                    table_text += f"Rows: {table.rows}, Columns: {table.columns}\n"
                    table_text += f"Confidence: {table.confidence:.2f}\n\n"
                
                self.text_editor.delete("1.0", "end")
                self.text_editor.insert("1.0", table_text)
                
                self.progress_bar.set(1.0)
                self.status_label.configure(text="Table extraction completed")
                
            except Exception as e:
                self.status_label.configure(text=f"Table extraction error: {e}")
                messagebox.showerror("Error", f"Table extraction failed: {e}")
            finally:
                self.progress_bar.set(0)
        
        threading.Thread(target=process_async, daemon=True).start()
    
    def _perform_research(self):
        """Perform research using the research assistant."""
        query = self.search_entry.get()
        if not query:
            messagebox.showwarning("Warning", "Please enter a search query")
            return
        
        def research_async():
            try:
                self.status_label.configure(text="Researching...")
                self.progress_bar.set(0.3)
                
                # Perform research
                results = self.research_assistant.search_web(query)
                
                self.progress_bar.set(0.8)
                
                # Display results
                self.research_results.delete("1.0", "end")
                self.research_results.insert("1.0", f"Research Results for: {query}\n\n")
                
                for i, result in enumerate(results[:5]):  # Show top 5 results
                    self.research_results.insert("end", f"{i+1}. {result.get('title', 'No title')}\n")
                    self.research_results.insert("end", f"   {result.get('snippet', 'No snippet')}\n")
                    self.research_results.insert("end", f"   URL: {result.get('url', 'No URL')}\n\n")
                
                self.progress_bar.set(1.0)
                self.status_label.configure(text="Research completed")
                
            except Exception as e:
                self.status_label.configure(text=f"Research error: {e}")
                messagebox.showerror("Error", f"Research failed: {e}")
            finally:
                self.progress_bar.set(0)
        
        threading.Thread(target=research_async, daemon=True).start()
    
    def _apply_template(self, template_id: str):
        """Apply a template to the current book."""
        try:
            template = self.template_manager.get_template(template_id)
            if template:
                self.text_editor.delete("1.0", "end")
                self.text_editor.insert("1.0", template.content)
                self.status_label.configure(text=f"Applied template: {template.name}")
            else:
                messagebox.showerror("Error", "Template not found")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply template: {e}")
    
    # Navigation methods
    def _show_editor(self):
        """Show the editor tab."""
        self.notebook.set("Editor")
    
    def _show_chapters(self):
        """Show the chapters tab."""
        self.notebook.set("Chapters")
    
    def _show_research(self):
        """Show the research tab."""
        self.notebook.set("Research")
    
    def _show_analytics(self):
        """Show the analytics tab."""
        self.notebook.set("Analytics")
    
    def _show_settings(self):
        """Show the settings tab."""
        self._open_settings()
    
    # Formatting methods
    def _format_bold(self):
        """Format selected text as bold."""
        # Implementation for bold formatting
        pass
    
    def _format_italic(self):
        """Format selected text as italic."""
        # Implementation for italic formatting
        pass
    
    def _format_heading(self):
        """Format selected text as heading."""
        # Implementation for heading formatting
        pass
    
    def _format_list(self):
        """Format selected text as list."""
        # Implementation for list formatting
        pass
    
    # Chapter management methods
    def _add_chapter(self):
        """Add a new chapter."""
        chapter_name = tk.simpledialog.askstring("Add Chapter", "Enter chapter name:")
        if chapter_name:
            self.chapters_listbox.insert(tk.END, chapter_name)
            self.status_label.configure(text=f"Added chapter: {chapter_name}")
    
    def _delete_chapter(self):
        """Delete selected chapter."""
        selection = self.chapters_listbox.curselection()
        if selection:
            chapter_name = self.chapters_listbox.get(selection[0])
            self.chapters_listbox.delete(selection[0])
            self.status_label.configure(text=f"Deleted chapter: {chapter_name}")
    
    # Panel methods
    def _open_research_panel(self):
        """Open the research panel."""
        self.notebook.set("Research")
    
    def _open_collaboration_panel(self):
        """Open the collaboration panel."""
        messagebox.showinfo("Collaboration", "Collaboration features coming soon!")
    
    def _open_settings(self):
        """Open the settings dialog."""
        messagebox.showinfo("Settings", "Settings panel coming soon!")
    
    def run(self):
        """Run the application."""
        self.root.mainloop()


def main():
    """Main entry point for the modern GUI application."""
    try:
        app = ModernBookWriterApp()
        app.run()
    except Exception as e:
        logger.error(f"Application error: {e}")
        messagebox.showerror("Application Error", f"Failed to start application: {e}")


if __name__ == "__main__":
    main()