"""
Research Assistant Panel

A specialized panel for research capabilities including web search,
academic paper analysis, fact-checking, and citation management.
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import threading
import asyncio
from typing import List, Dict, Any
import logging

from research_assistant.research_assistant import ResearchAssistant

logger = logging.getLogger(__name__)


class ResearchPanel(ctk.CTkFrame):
    """
    Research assistant panel with advanced research capabilities.
    
    Features:
    - Web search with multiple engines
    - Academic paper analysis
    - Fact-checking and verification
    - Citation management
    - Research notes and organization
    - Real-time search suggestions
    """
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        # Initialize research assistant
        self.research_assistant = ResearchAssistant()
        
        # Research state
        self.current_research = []
        self.search_history = []
        self.saved_notes = []
        
        # Create UI
        self._create_ui()
    
    def _create_ui(self):
        """Create the research panel UI."""
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=20)
        
        title = ctk.CTkLabel(
            header,
            text="Research Assistant",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(anchor="w")
        
        subtitle = ctk.CTkLabel(
            header,
            text="Search, analyze, and organize research materials",
            font=ctk.CTkFont(size=14),
            text_color=("#666666", "#cccccc")
        )
        subtitle.pack(anchor="w", pady=(5, 0))
        
        # Main content area
        content_frame = ctk.CTkFrame(self)
        content_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Left panel - Search and controls
        self._create_search_panel(content_frame)
        
        # Right panel - Results and notes
        self._create_results_panel(content_frame)
    
    def _create_search_panel(self, parent):
        """Create the search panel."""
        search_frame = ctk.CTkFrame(parent)
        search_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Search section
        search_section = ctk.CTkFrame(search_frame)
        search_section.pack(fill="x", padx=20, pady=20)
        
        search_title = ctk.CTkLabel(
            search_section,
            text="Search",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        search_title.pack(anchor="w", pady=(0, 15))
        
        # Search input
        self.search_entry = ctk.CTkEntry(
            search_section,
            placeholder_text="Enter your research query...",
            width=400,
            height=40,
            font=ctk.CTkFont(size=14)
        )
        self.search_entry.pack(fill="x", pady=(0, 10))
        self.search_entry.bind("<Return>", lambda e: self._perform_search())
        
        # Search options
        options_frame = ctk.CTkFrame(search_section, fg_color="transparent")
        options_frame.pack(fill="x", pady=(0, 15))
        
        # Search engine selection
        engine_frame = ctk.CTkFrame(options_frame, fg_color="transparent")
        engine_frame.pack(side="left")
        
        ctk.CTkLabel(
            engine_frame,
            text="Engine:",
            font=ctk.CTkFont(size=12)
        ).pack(side="left")
        
        self.search_engine_var = tk.StringVar(value="google")
        self.search_engine_combo = ctk.CTkComboBox(
            engine_frame,
            values=["google", "bing", "duckduckgo", "academic"],
            variable=self.search_engine_var,
            width=120
        )
        self.search_engine_combo.pack(side="left", padx=(5, 0))
        
        # Number of results
        results_frame = ctk.CTkFrame(options_frame, fg_color="transparent")
        results_frame.pack(side="right")
        
        ctk.CTkLabel(
            results_frame,
            text="Results:",
            font=ctk.CTkFont(size=12)
        ).pack(side="left")
        
        self.num_results_var = tk.StringVar(value="10")
        self.num_results_combo = ctk.CTkComboBox(
            results_frame,
            values=["5", "10", "20", "50"],
            variable=self.num_results_var,
            width=60
        )
        self.num_results_combo.pack(side="left", padx=(5, 0))
        
        # Search buttons
        search_buttons_frame = ctk.CTkFrame(search_section, fg_color="transparent")
        search_buttons_frame.pack(fill="x")
        
        self.search_btn = ctk.CTkButton(
            search_buttons_frame,
            text="Search",
            command=self._perform_search,
            width=100,
            height=35,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.search_btn.pack(side="left", padx=(0, 10))
        
        self.clear_search_btn = ctk.CTkButton(
            search_buttons_frame,
            text="Clear",
            command=self._clear_search,
            width=80,
            height=35,
            font=ctk.CTkFont(size=14)
        )
        self.clear_search_btn.pack(side="left")
        
        # Search history
        history_section = ctk.CTkFrame(search_frame)
        history_section.pack(fill="both", expand=True, padx=20, pady=20)
        
        history_title = ctk.CTkLabel(
            history_section,
            text="Search History",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        history_title.pack(anchor="w", pady=(0, 10))
        
        # History listbox
        history_listbox_frame = ctk.CTkFrame(history_section)
        history_listbox_frame.pack(fill="both", expand=True)
        
        self.history_listbox = tk.Listbox(
            history_listbox_frame,
            font=("Arial", 11),
            bg="#ffffff",
            fg="#1a1a1a",
            selectbackground="#007bff",
            selectforeground="#ffffff"
        )
        self.history_listbox.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        history_scrollbar = tk.Scrollbar(history_listbox_frame, orient="vertical")
        history_scrollbar.pack(side="right", fill="y")
        
        self.history_listbox.config(yscrollcommand=history_scrollbar.set)
        history_scrollbar.config(command=self.history_listbox.yview)
        
        # History actions
        history_actions = ctk.CTkFrame(history_section, fg_color="transparent")
        history_actions.pack(fill="x", pady=(10, 0))
        
        self.clear_history_btn = ctk.CTkButton(
            history_actions,
            text="Clear History",
            command=self._clear_history,
            width=120,
            height=30
        )
        self.clear_history_btn.pack(side="right")
    
    def _create_results_panel(self, parent):
        """Create the results panel."""
        results_frame = ctk.CTkFrame(parent)
        results_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        # Results header
        results_header = ctk.CTkFrame(results_frame, fg_color="transparent")
        results_header.pack(fill="x", padx=20, pady=20)
        
        results_title = ctk.CTkLabel(
            results_header,
            text="Search Results",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        results_title.pack(anchor="w")
        
        # Results count
        self.results_count_label = ctk.CTkLabel(
            results_header,
            text="No results yet",
            font=ctk.CTkFont(size=12),
            text_color=("#666666", "#cccccc")
        )
        self.results_count_label.pack(anchor="w", pady=(5, 0))
        
        # Results display
        self.results_display = ctk.CTkScrollableFrame(
            results_frame,
            width=500,
            height=400
        )
        self.results_display.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Notes section
        notes_section = ctk.CTkFrame(results_frame)
        notes_section.pack(fill="x", padx=20, pady=(0, 20))
        
        notes_title = ctk.CTkLabel(
            notes_section,
            text="Research Notes",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        notes_title.pack(anchor="w", padx=15, pady=10)
        
        # Notes text area
        self.notes_text = ctk.CTkTextbox(
            notes_section,
            width=500,
            height=150,
            font=ctk.CTkFont(size=11)
        )
        self.notes_text.pack(fill="x", padx=15, pady=(0, 10))
        
        # Notes actions
        notes_actions = ctk.CTkFrame(notes_section, fg_color="transparent")
        notes_actions.pack(fill="x", padx=15, pady=(0, 15))
        
        self.save_notes_btn = ctk.CTkButton(
            notes_actions,
            text="Save Notes",
            command=self._save_notes,
            width=100,
            height=30
        )
        self.save_notes_btn.pack(side="left", padx=(0, 10))
        
        self.clear_notes_btn = ctk.CTkButton(
            notes_actions,
            text="Clear Notes",
            command=self._clear_notes,
            width=100,
            height=30
        )
        self.clear_notes_btn.pack(side="left")
    
    def _perform_search(self):
        """Perform a search query."""
        query = self.search_entry.get().strip()
        if not query:
            messagebox.showwarning("Warning", "Please enter a search query")
            return
        
        # Add to search history
        if query not in self.search_history:
            self.search_history.insert(0, query)
            self.history_listbox.insert(0, query)
        
        # Start search in separate thread
        threading.Thread(
            target=self._search_async,
            args=(query,),
            daemon=True
        ).start()
    
    def _search_async(self, query: str):
        """Perform search asynchronously."""
        try:
            # Update UI
            self.search_btn.configure(text="Searching...", state="disabled")
            
            # Perform search
            engine = self.search_engine_var.get()
            num_results = int(self.num_results_var.get())
            
            if engine == "academic":
                results = self.research_assistant.search_academic_papers(query, num_results)
            else:
                results = self.research_assistant.search_web(query, num_results)
            
            # Update results display
            self._display_results(results)
            
            # Store current research
            self.current_research = results
            
        except Exception as e:
            messagebox.showerror("Search Error", f"Search failed: {e}")
            logger.error(f"Search error: {e}")
        finally:
            self.search_btn.configure(text="Search", state="normal")
    
    def _display_results(self, results: List[Dict[str, Any]]):
        """Display search results."""
        # Clear previous results
        for widget in self.results_display.winfo_children():
            widget.destroy()
        
        # Update results count
        self.results_count_label.configure(text=f"Found {len(results)} results")
        
        # Display each result
        for i, result in enumerate(results):
            self._create_result_widget(result, i)
    
    def _create_result_widget(self, result: Dict[str, Any], index: int):
        """Create a widget for a single search result."""
        result_frame = ctk.CTkFrame(
            self.results_display,
            fg_color=("#f8f9fa", "#2b2b2b"),
            corner_radius=8
        )
        result_frame.pack(fill="x", pady=5, padx=5)
        
        # Result content
        content_frame = ctk.CTkFrame(result_frame, fg_color="transparent")
        content_frame.pack(fill="x", padx=15, pady=10)
        
        # Title
        title = result.get("title", "No title")
        title_label = ctk.CTkLabel(
            content_frame,
            text=title,
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        title_label.pack(fill="x", pady=(0, 5))
        
        # URL
        url = result.get("url", "")
        if url:
            url_label = ctk.CTkLabel(
                content_frame,
                text=url,
                font=ctk.CTkFont(size=11),
                text_color=("#007bff", "#66b3ff"),
                anchor="w"
            )
            url_label.pack(fill="x", pady=(0, 5))
        
        # Snippet
        snippet = result.get("snippet", result.get("abstract", ""))
        if snippet:
            snippet_label = ctk.CTkLabel(
                content_frame,
                text=snippet,
                font=ctk.CTkFont(size=11),
                anchor="w",
                wraplength=450
            )
            snippet_label.pack(fill="x", pady=(0, 10))
        
        # Actions
        actions_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        actions_frame.pack(fill="x")
        
        # Add to notes button
        add_notes_btn = ctk.CTkButton(
            actions_frame,
            text="Add to Notes",
            command=lambda: self._add_to_notes(result),
            width=100,
            height=25,
            font=ctk.CTkFont(size=10)
        )
        add_notes_btn.pack(side="left", padx=(0, 10))
        
        # Copy URL button
        copy_url_btn = ctk.CTkButton(
            actions_frame,
            text="Copy URL",
            command=lambda: self._copy_url(url),
            width=80,
            height=25,
            font=ctk.CTkFont(size=10)
        )
        copy_url_btn.pack(side="left")
    
    def _add_to_notes(self, result: Dict[str, Any]):
        """Add a result to research notes."""
        title = result.get("title", "No title")
        snippet = result.get("snippet", result.get("abstract", ""))
        url = result.get("url", "")
        
        note_text = f"\n--- {title} ---\n"
        if snippet:
            note_text += f"{snippet}\n"
        if url:
            note_text += f"URL: {url}\n"
        note_text += "\n"
        
        self.notes_text.insert("end", note_text)
    
    def _copy_url(self, url: str):
        """Copy URL to clipboard."""
        self.clipboard_clear()
        self.clipboard_append(url)
        messagebox.showinfo("Copied", "URL copied to clipboard")
    
    def _clear_search(self):
        """Clear the search input."""
        self.search_entry.delete(0, "end")
    
    def _clear_history(self):
        """Clear search history."""
        self.search_history.clear()
        self.history_listbox.delete(0, tk.END)
    
    def _save_notes(self):
        """Save research notes."""
        notes = self.notes_text.get("1.0", "end-1c")
        if notes.strip():
            self.saved_notes.append(notes)
            messagebox.showinfo("Success", "Notes saved successfully")
        else:
            messagebox.showwarning("Warning", "No notes to save")
    
    def _clear_notes(self):
        """Clear research notes."""
        if messagebox.askyesno("Confirm", "Are you sure you want to clear all notes?"):
            self.notes_text.delete("1.0", "end")