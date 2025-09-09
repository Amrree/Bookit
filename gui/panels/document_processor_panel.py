"""
Document Processor Panel

A specialized panel for document processing features including
OCR, layout analysis, table extraction, and batch processing.
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import asyncio
from pathlib import Path
from typing import List, Dict, Any
import logging

from document_processor.unified_parser import UnifiedDocumentParser, ProcessingOptions
from document_ingestor.enhanced_ingestor import EnhancedDocumentIngestor

logger = logging.getLogger(__name__)


class DocumentProcessorPanel(ctk.CTkFrame):
    """
    Document processor panel with advanced processing capabilities.
    
    Features:
    - Document import and processing
    - OCR processing with configuration
    - Layout analysis and structure recognition
    - Table extraction and formatting
    - Batch processing capabilities
    - Real-time progress tracking
    """
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        # Initialize processors
        self.document_parser = UnifiedDocumentParser()
        self.document_ingestor = EnhancedDocumentIngestor()
        
        # Processing state
        self.processing_files = []
        self.current_processing = None
        
        # Create UI
        self._create_ui()
    
    def _create_ui(self):
        """Create the document processor UI."""
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=20)
        
        title = ctk.CTkLabel(
            header,
            text="Document Processor",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(anchor="w")
        
        subtitle = ctk.CTkLabel(
            header,
            text="Process documents with OCR, layout analysis, and table extraction",
            font=ctk.CTkFont(size=14),
            text_color=("#666666", "#cccccc")
        )
        subtitle.pack(anchor="w", pady=(5, 0))
        
        # Main content area
        content_frame = ctk.CTkFrame(self)
        content_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Left panel - Controls
        self._create_controls_panel(content_frame)
        
        # Right panel - Results
        self._create_results_panel(content_frame)
    
    def _create_controls_panel(self, parent):
        """Create the controls panel."""
        controls_frame = ctk.CTkFrame(parent)
        controls_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # File selection section
        file_section = ctk.CTkFrame(controls_frame)
        file_section.pack(fill="x", padx=20, pady=20)
        
        file_title = ctk.CTkLabel(
            file_section,
            text="Document Selection",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        file_title.pack(anchor="w", pady=(0, 15))
        
        # File selection buttons
        file_buttons_frame = ctk.CTkFrame(file_section, fg_color="transparent")
        file_buttons_frame.pack(fill="x")
        
        self.import_single_btn = ctk.CTkButton(
            file_buttons_frame,
            text="Import Single Document",
            command=self._import_single_document,
            width=200,
            height=40,
            font=ctk.CTkFont(size=14)
        )
        self.import_single_btn.pack(fill="x", pady=(0, 10))
        
        self.import_batch_btn = ctk.CTkButton(
            file_buttons_frame,
            text="Import Multiple Documents",
            command=self._import_multiple_documents,
            width=200,
            height=40,
            font=ctk.CTkFont(size=14)
        )
        self.import_batch_btn.pack(fill="x", pady=(0, 15))
        
        # File list
        self.file_list_frame = ctk.CTkFrame(file_section)
        self.file_list_frame.pack(fill="both", expand=True)
        
        file_list_title = ctk.CTkLabel(
            self.file_list_frame,
            text="Selected Files",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        file_list_title.pack(anchor="w", padx=15, pady=10)
        
        # File listbox with scrollbar
        listbox_frame = ctk.CTkFrame(self.file_list_frame)
        listbox_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        self.file_listbox = tk.Listbox(
            listbox_frame,
            font=("Arial", 11),
            bg="#ffffff",
            fg="#1a1a1a",
            selectbackground="#007bff",
            selectforeground="#ffffff"
        )
        self.file_listbox.pack(side="left", fill="both", expand=True)
        
        scrollbar = tk.Scrollbar(listbox_frame, orient="vertical")
        scrollbar.pack(side="right", fill="y")
        
        self.file_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.file_listbox.yview)
        
        # Processing options section
        options_section = ctk.CTkFrame(controls_frame)
        options_section.pack(fill="x", padx=20, pady=20)
        
        options_title = ctk.CTkLabel(
            options_section,
            text="Processing Options",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        options_title.pack(anchor="w", pady=(0, 15))
        
        # Processing checkboxes
        self.extract_text_var = tk.BooleanVar(value=True)
        self.extract_metadata_var = tk.BooleanVar(value=True)
        self.extract_images_var = tk.BooleanVar(value=True)
        self.extract_tables_var = tk.BooleanVar(value=True)
        self.perform_ocr_var = tk.BooleanVar(value=False)
        self.analyze_layout_var = tk.BooleanVar(value=True)
        self.preprocess_images_var = tk.BooleanVar(value=True)
        
        checkboxes = [
            ("Extract Text", self.extract_text_var),
            ("Extract Metadata", self.extract_metadata_var),
            ("Extract Images", self.extract_images_var),
            ("Extract Tables", self.extract_tables_var),
            ("Perform OCR", self.perform_ocr_var),
            ("Analyze Layout", self.analyze_layout_var),
            ("Preprocess Images", self.preprocess_images_var)
        ]
        
        for text, var in checkboxes:
            checkbox = ctk.CTkCheckBox(
                options_section,
                text=text,
                variable=var,
                font=ctk.CTkFont(size=12)
            )
            checkbox.pack(anchor="w", pady=2)
        
        # OCR settings
        ocr_frame = ctk.CTkFrame(options_section)
        ocr_frame.pack(fill="x", pady=15)
        
        ocr_title = ctk.CTkLabel(
            ocr_frame,
            text="OCR Settings",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        ocr_title.pack(anchor="w", padx=15, pady=10)
        
        # Language selection
        lang_frame = ctk.CTkFrame(ocr_frame, fg_color="transparent")
        lang_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        ctk.CTkLabel(
            lang_frame,
            text="Language:",
            font=ctk.CTkFont(size=12)
        ).pack(side="left")
        
        self.language_var = tk.StringVar(value="eng")
        self.language_combo = ctk.CTkComboBox(
            lang_frame,
            values=["eng", "spa", "fra", "deu", "ita", "por", "rus", "chi", "jpn", "kor"],
            variable=self.language_var,
            width=100
        )
        self.language_combo.pack(side="right")
        
        # Confidence threshold
        conf_frame = ctk.CTkFrame(ocr_frame, fg_color="transparent")
        conf_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        ctk.CTkLabel(
            conf_frame,
            text="Confidence Threshold:",
            font=ctk.CTkFont(size=12)
        ).pack(side="left")
        
        self.confidence_var = tk.DoubleVar(value=0.5)
        self.confidence_slider = ctk.CTkSlider(
            conf_frame,
            from_=0.0,
            to=1.0,
            number_of_steps=20,
            variable=self.confidence_var,
            width=150
        )
        self.confidence_slider.pack(side="right")
        
        # Process button
        self.process_btn = ctk.CTkButton(
            options_section,
            text="Process Documents",
            command=self._process_documents,
            width=200,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#28a745",
            hover_color="#218838"
        )
        self.process_btn.pack(pady=20)
    
    def _create_results_panel(self, parent):
        """Create the results panel."""
        results_frame = ctk.CTkFrame(parent)
        results_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        # Results header
        results_header = ctk.CTkFrame(results_frame, fg_color="transparent")
        results_header.pack(fill="x", padx=20, pady=20)
        
        results_title = ctk.CTkLabel(
            results_header,
            text="Processing Results",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        results_title.pack(anchor="w")
        
        # Progress section
        progress_frame = ctk.CTkFrame(results_frame)
        progress_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        progress_title = ctk.CTkLabel(
            progress_frame,
            text="Progress",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        progress_title.pack(anchor="w", padx=15, pady=10)
        
        self.progress_bar = ctk.CTkProgressBar(
            progress_frame,
            width=400,
            height=20
        )
        self.progress_bar.pack(fill="x", padx=15, pady=(0, 10))
        self.progress_bar.set(0)
        
        self.progress_label = ctk.CTkLabel(
            progress_frame,
            text="Ready to process",
            font=ctk.CTkFont(size=12),
            text_color=("#666666", "#cccccc")
        )
        self.progress_label.pack(anchor="w", padx=15, pady=(0, 15))
        
        # Results display
        results_display_frame = ctk.CTkFrame(results_frame)
        results_display_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        results_display_title = ctk.CTkLabel(
            results_display_frame,
            text="Results",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        results_display_title.pack(anchor="w", padx=15, pady=10)
        
        # Results text area
        self.results_text = ctk.CTkTextbox(
            results_display_frame,
            width=400,
            height=300,
            font=ctk.CTkFont(size=11)
        )
        self.results_text.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        # Export buttons
        export_frame = ctk.CTkFrame(results_display_frame, fg_color="transparent")
        export_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        self.export_text_btn = ctk.CTkButton(
            export_frame,
            text="Export Text",
            command=self._export_text,
            width=100,
            height=30
        )
        self.export_text_btn.pack(side="left", padx=(0, 10))
        
        self.export_json_btn = ctk.CTkButton(
            export_frame,
            text="Export JSON",
            command=self._export_json,
            width=100,
            height=30
        )
        self.export_json_btn.pack(side="left", padx=(0, 10))
        
        self.clear_results_btn = ctk.CTkButton(
            export_frame,
            text="Clear",
            command=self._clear_results,
            width=80,
            height=30,
            fg_color="#dc3545",
            hover_color="#c82333"
        )
        self.clear_results_btn.pack(side="right")
    
    def _import_single_document(self):
        """Import a single document."""
        file_path = filedialog.askopenfilename(
            title="Select Document",
            filetypes=[
                ("PDF Files", "*.pdf"),
                ("Word Documents", "*.docx"),
                ("Text Files", "*.txt"),
                ("Markdown Files", "*.md"),
                ("Image Files", "*.png *.jpg *.jpeg"),
                ("All Files", "*.*")
            ]
        )
        if file_path:
            self.processing_files = [file_path]
            self._update_file_list()
    
    def _import_multiple_documents(self):
        """Import multiple documents."""
        file_paths = filedialog.askopenfilenames(
            title="Select Documents",
            filetypes=[
                ("PDF Files", "*.pdf"),
                ("Word Documents", "*.docx"),
                ("Text Files", "*.txt"),
                ("Markdown Files", "*.md"),
                ("Image Files", "*.png *.jpg *.jpeg"),
                ("All Files", "*.*")
            ]
        )
        if file_paths:
            self.processing_files = list(file_paths)
            self._update_file_list()
    
    def _update_file_list(self):
        """Update the file list display."""
        self.file_listbox.delete(0, tk.END)
        for file_path in self.processing_files:
            filename = Path(file_path).name
            self.file_listbox.insert(tk.END, filename)
    
    def _process_documents(self):
        """Process all selected documents."""
        if not self.processing_files:
            messagebox.showwarning("Warning", "Please select documents to process")
            return
        
        # Create processing options
        options = ProcessingOptions(
            extract_text=self.extract_text_var.get(),
            extract_metadata=self.extract_metadata_var.get(),
            extract_images=self.extract_images_var.get(),
            extract_tables=self.extract_tables_var.get(),
            perform_ocr=self.perform_ocr_var.get(),
            analyze_layout=self.analyze_layout_var.get(),
            preprocess_images=self.preprocess_images_var.get(),
            language=self.language_var.get(),
            confidence_threshold=self.confidence_var.get()
        )
        
        # Start processing in separate thread
        threading.Thread(
            target=self._process_documents_async,
            args=(self.processing_files, options),
            daemon=True
        ).start()
    
    def _process_documents_async(self, file_paths: List[str], options: ProcessingOptions):
        """Process documents asynchronously."""
        try:
            self.progress_label.configure(text="Starting processing...")
            self.progress_bar.set(0.1)
            
            results = []
            total_files = len(file_paths)
            
            for i, file_path in enumerate(file_paths):
                try:
                    # Update progress
                    progress = (i / total_files) * 0.8 + 0.1
                    self.progress_bar.set(progress)
                    self.progress_label.configure(text=f"Processing {Path(file_path).name}...")
                    
                    # Process document
                    result = self.document_parser.parse_document(file_path, options)
                    results.append(result)
                    
                    # Update results display
                    self._update_results_display(result)
                    
                except Exception as e:
                    error_msg = f"Error processing {Path(file_path).name}: {e}"
                    self.results_text.insert("end", f"{error_msg}\n")
                    logger.error(error_msg)
            
            # Complete processing
            self.progress_bar.set(1.0)
            self.progress_label.configure(text=f"Completed processing {total_files} documents")
            
            # Store results
            self.current_processing = results
            
        except Exception as e:
            self.progress_label.configure(text=f"Processing error: {e}")
            messagebox.showerror("Error", f"Processing failed: {e}")
        finally:
            self.progress_bar.set(0)
    
    def _update_results_display(self, result):
        """Update the results display with processing result."""
        filename = Path(result.file_path).name
        
        self.results_text.insert("end", f"=== {filename} ===\n")
        self.results_text.insert("end", f"Status: {'Success' if result.success else 'Failed'}\n")
        self.results_text.insert("end", f"Processing time: {result.processing_time:.2f}s\n")
        
        if result.text_content:
            self.results_text.insert("end", f"Text length: {len(result.text_content)} characters\n")
        
        if result.tables:
            self.results_text.insert("end", f"Tables extracted: {len(result.tables)}\n")
        
        if result.images:
            self.results_text.insert("end", f"Images extracted: {len(result.images)}\n")
        
        if result.errors:
            self.results_text.insert("end", f"Errors: {len(result.errors)}\n")
            for error in result.errors:
                self.results_text.insert("end", f"  - {error}\n")
        
        self.results_text.insert("end", "\n")
        self.results_text.see("end")
    
    def _export_text(self):
        """Export results as text."""
        if not self.current_processing:
            messagebox.showwarning("Warning", "No results to export")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Export Text Results",
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    for result in self.current_processing:
                        f.write(f"=== {Path(result.file_path).name} ===\n")
                        f.write(f"Status: {'Success' if result.success else 'Failed'}\n")
                        f.write(f"Processing time: {result.processing_time:.2f}s\n\n")
                        
                        if result.text_content:
                            f.write("TEXT CONTENT:\n")
                            f.write(result.text_content)
                            f.write("\n\n")
                        
                        if result.tables:
                            f.write("TABLES:\n")
                            for i, table in enumerate(result.tables):
                                f.write(f"Table {i+1}:\n")
                                f.write(f"Rows: {table.rows}, Columns: {table.columns}\n")
                                f.write(f"Confidence: {table.confidence:.2f}\n\n")
                
                messagebox.showinfo("Success", f"Results exported to {file_path}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export results: {e}")
    
    def _export_json(self):
        """Export results as JSON."""
        if not self.current_processing:
            messagebox.showwarning("Warning", "No results to export")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Export JSON Results",
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
        )
        
        if file_path:
            try:
                import json
                
                # Convert results to serializable format
                export_data = []
                for result in self.current_processing:
                    export_data.append({
                        "file_path": result.file_path,
                        "success": result.success,
                        "processing_time": result.processing_time,
                        "text_content": result.text_content,
                        "metadata": result.metadata,
                        "tables": [table.dict() for table in result.tables],
                        "images": result.images,
                        "errors": result.errors
                    })
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, default=str)
                
                messagebox.showinfo("Success", f"Results exported to {file_path}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export results: {e}")
    
    def _clear_results(self):
        """Clear the results display."""
        self.results_text.delete("1.0", "end")
        self.current_processing = None
        self.progress_bar.set(0)
        self.progress_label.configure(text="Ready to process")