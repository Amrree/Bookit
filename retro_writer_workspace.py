"""
Retro Writer Workspace Components
Detailed implementation of workspace, research, writing, and tools pages.
"""

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
import asyncio
import json
from datetime import datetime
from pathlib import Path

from retro_writer_app import RetroWriterTheme


class WorkspaceTab(QWidget):
    """Workspace navigation tab with book management."""
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Book management section
        book_group = QGroupBox("📚 Book Management")
        book_layout = QVBoxLayout(book_group)
        
        # Current book info
        self.current_book_label = QLabel("No book loaded")
        self.current_book_label.setFont(RetroWriterTheme.FONTS['subheading'])
        self.current_book_label.setStyleSheet("color: #8b4513; font-weight: bold;")
        book_layout.addWidget(self.current_book_label)
        
        # Book actions
        self.new_book_btn = QPushButton("📝 New Book")
        self.new_book_btn.clicked.connect(self.main_window.new_book)
        book_layout.addWidget(self.new_book_btn)
        
        self.open_book_btn = QPushButton("📂 Open Book")
        self.open_book_btn.clicked.connect(self.main_window.open_book)
        book_layout.addWidget(self.open_book_btn)
        
        self.save_book_btn = QPushButton("💾 Save Book")
        self.save_book_btn.clicked.connect(self.main_window.save_book)
        book_layout.addWidget(self.save_book_btn)
        
        layout.addWidget(book_group)
        
        # Chapter navigation
        chapter_group = QGroupBox("📖 Chapter Navigation")
        chapter_layout = QVBoxLayout(chapter_group)
        
        self.chapter_list = QListWidget()
        self.chapter_list.itemClicked.connect(self.on_chapter_selected)
        chapter_layout.addWidget(self.chapter_list)
        
        # Chapter actions
        chapter_actions_layout = QHBoxLayout()
        
        self.add_chapter_btn = QPushButton("➕ Add Chapter")
        self.add_chapter_btn.clicked.connect(self.add_chapter)
        chapter_actions_layout.addWidget(self.add_chapter_btn)
        
        self.delete_chapter_btn = QPushButton("🗑️ Delete")
        self.delete_chapter_btn.clicked.connect(self.delete_chapter)
        chapter_actions_layout.addWidget(self.delete_chapter_btn)
        
        chapter_layout.addLayout(chapter_actions_layout)
        layout.addWidget(chapter_group)
        
        # Document import
        import_group = QGroupBox("📄 Import Documents")
        import_layout = QVBoxLayout(import_group)
        
        self.import_btn = QPushButton("📁 Import Documents")
        self.import_btn.clicked.connect(self.main_window.import_documents)
        import_layout.addWidget(self.import_btn)
        
        self.imported_docs_list = QListWidget()
        import_layout.addWidget(self.imported_docs_list)
        
        layout.addWidget(import_group)
        
        # Add stretch to push everything to top
        layout.addStretch()
    
    def on_chapter_selected(self, item):
        """Handle chapter selection."""
        chapter_title = item.text()
        self.main_window.load_chapter(chapter_title)
    
    def add_chapter(self):
        """Add a new chapter."""
        title, ok = QInputDialog.getText(self, "New Chapter", "Chapter title:")
        if ok and title:
            self.chapter_list.addItem(title)
            self.main_window.add_chapter(title)
    
    def delete_chapter(self):
        """Delete selected chapter."""
        current_item = self.chapter_list.currentItem()
        if current_item:
            reply = QMessageBox.question(self, "Delete Chapter", 
                                       f"Delete chapter '{current_item.text()}'?",
                                       QMessageBox.StandardButton.Yes | 
                                       QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.chapter_list.takeItem(self.chapter_list.row(current_item))
                self.main_window.delete_chapter(current_item.text())


class ResearchTab(QWidget):
    """Research navigation tab with research management."""
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Research control
        research_group = QGroupBox("🔍 Research Control")
        research_layout = QVBoxLayout(research_group)
        
        self.start_research_btn = QPushButton("🚀 Start Research")
        self.start_research_btn.clicked.connect(self.start_research)
        research_layout.addWidget(self.start_research_btn)
        
        self.research_progress = QProgressBar()
        self.research_progress.setVisible(False)
        research_layout.addWidget(self.research_progress)
        
        layout.addWidget(research_group)
        
        # Research topics
        topics_group = QGroupBox("📋 Research Topics")
        topics_layout = QVBoxLayout(topics_group)
        
        self.topics_list = QListWidget()
        topics_layout.addWidget(self.topics_list)
        
        # Topic actions
        topic_actions_layout = QHBoxLayout()
        
        self.add_topic_btn = QPushButton("➕ Add Topic")
        self.add_topic_btn.clicked.connect(self.add_research_topic)
        topic_actions_layout.addWidget(self.add_topic_btn)
        
        self.remove_topic_btn = QPushButton("➖ Remove")
        self.remove_topic_btn.clicked.connect(self.remove_research_topic)
        topic_actions_layout.addWidget(self.remove_topic_btn)
        
        topics_layout.addLayout(topic_actions_layout)
        layout.addWidget(topics_group)
        
        # Research sources
        sources_group = QGroupBox("📚 Research Sources")
        sources_layout = QVBoxLayout(sources_group)
        
        self.sources_list = QListWidget()
        sources_layout.addWidget(self.sources_list)
        
        # Source actions
        source_actions_layout = QHBoxLayout()
        
        self.view_source_btn = QPushButton("👁️ View Source")
        self.view_source_btn.clicked.connect(self.view_source)
        source_actions_layout.addWidget(self.view_source_btn)
        
        self.manage_sources_btn = QPushButton("⚙️ Manage")
        self.manage_sources_btn.clicked.connect(self.manage_sources)
        source_actions_layout.addWidget(self.manage_sources_btn)
        
        sources_layout.addLayout(source_actions_layout)
        layout.addWidget(sources_group)
        
        # Memory management
        memory_group = QGroupBox("🧠 Memory Management")
        memory_layout = QVBoxLayout(memory_group)
        
        self.memory_stats_label = QLabel("Memory: 0 chunks")
        memory_layout.addWidget(self.memory_stats_label)
        
        self.view_memory_btn = QPushButton("🔍 View Memory")
        self.view_memory_btn.clicked.connect(self.view_memory)
        memory_layout.addWidget(self.view_memory_btn)
        
        self.clear_memory_btn = QPushButton("🗑️ Clear Memory")
        self.clear_memory_btn.clicked.connect(self.clear_memory)
        memory_layout.addWidget(self.clear_memory_btn)
        
        layout.addWidget(memory_group)
        
        layout.addStretch()
    
    def start_research(self):
        """Start research process."""
        self.research_progress.setVisible(True)
        self.research_progress.setValue(0)
        self.start_research_btn.setEnabled(False)
        
        # Start research in background
        self.main_window.start_research_async()
    
    def add_research_topic(self):
        """Add a research topic."""
        topic, ok = QInputDialog.getText(self, "Research Topic", "Enter research topic:")
        if ok and topic:
            self.topics_list.addItem(topic)
    
    def remove_research_topic(self):
        """Remove selected research topic."""
        current_item = self.topics_list.currentItem()
        if current_item:
            self.topics_list.takeItem(self.topics_list.row(current_item))
    
    def view_source(self):
        """View selected source."""
        current_item = self.sources_list.currentItem()
        if current_item:
            self.main_window.view_source(current_item.text())
    
    def manage_sources(self):
        """Manage research sources."""
        self.main_window.manage_sources()
    
    def view_memory(self):
        """View memory contents."""
        self.main_window.view_memory()
    
    def clear_memory(self):
        """Clear memory."""
        reply = QMessageBox.question(self, "Clear Memory", 
                                   "Clear all memory? This cannot be undone.",
                                   QMessageBox.StandardButton.Yes | 
                                   QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.main_window.clear_memory()


class WritingTab(QWidget):
    """Writing navigation tab with writing management."""
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Writing control
        writing_group = QGroupBox("✍️ Writing Control")
        writing_layout = QVBoxLayout(writing_group)
        
        self.generate_chapter_btn = QPushButton("📝 Generate Chapter")
        self.generate_chapter_btn.clicked.connect(self.generate_chapter)
        writing_layout.addWidget(self.generate_chapter_btn)
        
        self.writing_progress = QProgressBar()
        self.writing_progress.setVisible(False)
        writing_layout.addWidget(self.writing_progress)
        
        layout.addWidget(writing_group)
        
        # Writing style
        style_group = QGroupBox("🎨 Writing Style")
        style_layout = QVBoxLayout(style_group)
        
        self.style_combo = QComboBox()
        self.style_combo.addItems(["Academic", "Journalistic", "Narrative", "Technical", "Creative"])
        style_layout.addWidget(QLabel("Style:"))
        style_layout.addWidget(self.style_combo)
        
        self.tone_combo = QComboBox()
        self.tone_combo.addItems(["Formal", "Informal", "Conversational", "Authoritative", "Friendly"])
        style_layout.addWidget(QLabel("Tone:"))
        style_layout.addWidget(self.tone_combo)
        
        self.length_spin = QSpinBox()
        self.length_spin.setRange(500, 10000)
        self.length_spin.setValue(2000)
        self.length_spin.setSuffix(" words")
        style_layout.addWidget(QLabel("Target Length:"))
        style_layout.addWidget(self.length_spin)
        
        layout.addWidget(style_group)
        
        # Chapter management
        chapter_group = QGroupBox("📖 Chapter Management")
        chapter_layout = QVBoxLayout(chapter_group)
        
        self.current_chapter_label = QLabel("No chapter selected")
        chapter_layout.addWidget(self.current_chapter_label)
        
        chapter_actions_layout = QHBoxLayout()
        
        self.edit_chapter_btn = QPushButton("✏️ Edit Chapter")
        self.edit_chapter_btn.clicked.connect(self.edit_chapter)
        chapter_actions_layout.addWidget(self.edit_chapter_btn)
        
        self.review_chapter_btn = QPushButton("🔍 Review Chapter")
        self.review_chapter_btn.clicked.connect(self.review_chapter)
        chapter_actions_layout.addWidget(self.review_chapter_btn)
        
        chapter_layout.addLayout(chapter_actions_layout)
        layout.addWidget(chapter_group)
        
        # Writing statistics
        stats_group = QGroupBox("📊 Writing Statistics")
        stats_layout = QVBoxLayout(stats_group)
        
        self.word_count_label = QLabel("Words: 0")
        self.char_count_label = QLabel("Characters: 0")
        self.reading_time_label = QLabel("Reading time: 0 min")
        
        stats_layout.addWidget(self.word_count_label)
        stats_layout.addWidget(self.char_count_label)
        stats_layout.addWidget(self.reading_time_label)
        
        layout.addWidget(stats_group)
        
        layout.addStretch()
    
    def generate_chapter(self):
        """Generate a new chapter."""
        self.writing_progress.setVisible(True)
        self.writing_progress.setValue(0)
        self.generate_chapter_btn.setEnabled(False)
        
        # Start chapter generation in background
        self.main_window.generate_chapter_async()
    
    def edit_chapter(self):
        """Edit current chapter."""
        self.main_window.edit_chapter()
    
    def review_chapter(self):
        """Review current chapter."""
        self.main_window.review_chapter()


class ToolsTab(QWidget):
    """Tools navigation tab with system tools."""
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Agent status
        agents_group = QGroupBox("🤖 Agent Status")
        agents_layout = QVBoxLayout(agents_group)
        
        self.agent_status_list = QListWidget()
        agents_layout.addWidget(self.agent_status_list)
        
        self.refresh_agents_btn = QPushButton("🔄 Refresh Status")
        self.refresh_agents_btn.clicked.connect(self.refresh_agent_status)
        agents_layout.addWidget(self.refresh_agents_btn)
        
        layout.addWidget(agents_group)
        
        # System monitor
        system_group = QGroupBox("📊 System Monitor")
        system_layout = QVBoxLayout(system_group)
        
        self.cpu_label = QLabel("CPU: 0%")
        self.memory_label = QLabel("Memory: 0 MB")
        self.disk_label = QLabel("Disk: 0 MB")
        
        system_layout.addWidget(self.cpu_label)
        system_layout.addWidget(self.memory_label)
        system_layout.addWidget(self.disk_label)
        
        self.refresh_system_btn = QPushButton("🔄 Refresh System")
        self.refresh_system_btn.clicked.connect(self.refresh_system_status)
        system_layout.addWidget(self.refresh_system_btn)
        
        layout.addWidget(system_group)
        
        # Tool testing
        tools_group = QGroupBox("🛠️ Tool Testing")
        tools_layout = QVBoxLayout(tools_group)
        
        self.test_tools_btn = QPushButton("🧪 Test All Tools")
        self.test_tools_btn.clicked.connect(self.test_all_tools)
        tools_layout.addWidget(self.test_tools_btn)
        
        self.tool_results = QTextEdit()
        self.tool_results.setMaximumHeight(150)
        self.tool_results.setReadOnly(True)
        tools_layout.addWidget(self.tool_results)
        
        layout.addWidget(tools_group)
        
        # Export options
        export_group = QGroupBox("📤 Export Options")
        export_layout = QVBoxLayout(export_group)
        
        self.export_md_btn = QPushButton("📄 Export Markdown")
        self.export_md_btn.clicked.connect(self.export_markdown)
        export_layout.addWidget(self.export_md_btn)
        
        self.export_docx_btn = QPushButton("📝 Export DOCX")
        self.export_docx_btn.clicked.connect(self.export_docx)
        export_layout.addWidget(self.export_docx_btn)
        
        self.export_pdf_btn = QPushButton("📕 Export PDF")
        self.export_pdf_btn.clicked.connect(self.export_pdf)
        export_layout.addWidget(self.export_pdf_btn)
        
        layout.addWidget(export_group)
        
        layout.addStretch()
    
    def refresh_agent_status(self):
        """Refresh agent status."""
        self.main_window.refresh_agent_status()
    
    def refresh_system_status(self):
        """Refresh system status."""
        self.main_window.refresh_system_status()
    
    def test_all_tools(self):
        """Test all available tools."""
        self.main_window.test_all_tools()
    
    def export_markdown(self):
        """Export book as Markdown."""
        self.main_window.export_book_format("markdown")
    
    def export_docx(self):
        """Export book as DOCX."""
        self.main_window.export_book_format("docx")
    
    def export_pdf(self):
        """Export book as PDF."""
        self.main_window.export_book_format("pdf")


class SettingsTab(QWidget):
    """Settings navigation tab with configuration options."""
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # LLM settings
        llm_group = QGroupBox("🤖 LLM Settings")
        llm_layout = QFormLayout(llm_group)
        
        self.llm_provider_combo = QComboBox()
        self.llm_provider_combo.addItems(["OpenAI", "Ollama", "Local"])
        llm_layout.addRow("Provider:", self.llm_provider_combo)
        
        self.api_key_edit = QLineEdit()
        self.api_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        llm_layout.addRow("API Key:", self.api_key_edit)
        
        self.model_combo = QComboBox()
        self.model_combo.addItems(["gpt-4", "gpt-3.5-turbo", "llama2", "mistral"])
        llm_layout.addRow("Model:", self.model_combo)
        
        layout.addWidget(llm_group)
        
        # Memory settings
        memory_group = QGroupBox("🧠 Memory Settings")
        memory_layout = QFormLayout(memory_group)
        
        self.memory_provider_combo = QComboBox()
        self.memory_provider_combo.addItems(["ChromaDB", "Local", "Remote"])
        memory_layout.addRow("Provider:", self.memory_provider_combo)
        
        self.max_chunks_spin = QSpinBox()
        self.max_chunks_spin.setRange(100, 10000)
        self.max_chunks_spin.setValue(1000)
        memory_layout.addRow("Max Chunks:", self.max_chunks_spin)
        
        self.chunk_size_spin = QSpinBox()
        self.chunk_size_spin.setRange(100, 2000)
        self.chunk_size_spin.setValue(500)
        memory_layout.addRow("Chunk Size:", self.chunk_size_spin)
        
        layout.addWidget(memory_group)
        
        # Writing settings
        writing_group = QGroupBox("✍️ Writing Settings")
        writing_layout = QFormLayout(writing_group)
        
        self.default_style_combo = QComboBox()
        self.default_style_combo.addItems(["Academic", "Journalistic", "Narrative", "Technical", "Creative"])
        writing_layout.addRow("Default Style:", self.default_style_combo)
        
        self.default_tone_combo = QComboBox()
        self.default_tone_combo.addItems(["Formal", "Informal", "Conversational", "Authoritative", "Friendly"])
        writing_layout.addRow("Default Tone:", self.default_tone_combo)
        
        self.auto_save_check = QCheckBox("Auto-save")
        self.auto_save_check.setChecked(True)
        writing_layout.addRow(self.auto_save_check)
        
        layout.addWidget(writing_group)
        
        # Appearance settings
        appearance_group = QGroupBox("🎨 Appearance")
        appearance_layout = QFormLayout(appearance_group)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Retro Writer", "Classic", "Modern", "Dark"])
        appearance_layout.addRow("Theme:", self.theme_combo)
        
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 24)
        self.font_size_spin.setValue(12)
        appearance_layout.addRow("Font Size:", self.font_size_spin)
        
        self.show_line_numbers_check = QCheckBox("Show Line Numbers")
        self.show_line_numbers_check.setChecked(True)
        appearance_layout.addRow(self.show_line_numbers_check)
        
        layout.addWidget(appearance_group)
        
        # Action buttons
        actions_layout = QHBoxLayout()
        
        self.save_settings_btn = QPushButton("💾 Save Settings")
        self.save_settings_btn.clicked.connect(self.save_settings)
        actions_layout.addWidget(self.save_settings_btn)
        
        self.reset_settings_btn = QPushButton("🔄 Reset")
        self.reset_settings_btn.clicked.connect(self.reset_settings)
        actions_layout.addWidget(self.reset_settings_btn)
        
        layout.addLayout(actions_layout)
        
        layout.addStretch()
    
    def save_settings(self):
        """Save current settings."""
        self.main_window.save_settings()
    
    def reset_settings(self):
        """Reset settings to defaults."""
        reply = QMessageBox.question(self, "Reset Settings", 
                                   "Reset all settings to defaults?",
                                   QMessageBox.StandardButton.Yes | 
                                   QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.main_window.reset_settings()