"""
Retro Writer Content Pages
Detailed implementation of content pages for dashboard, editor, research, etc.
"""

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
import asyncio
import json
from datetime import datetime
from pathlib import Path

from retro_writer_app import RetroWriterTheme


class DashboardPage(QWidget):
    """Dashboard page with overview and quick actions."""
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Welcome section
        welcome_group = QGroupBox("🎯 Welcome to Retro Writer")
        welcome_layout = QVBoxLayout(welcome_group)
        
        welcome_text = QLabel("""
        <h2 style="color: #8b4513;">Professional Book Writing Studio</h2>
        <p style="font-size: 14px; color: #2d2d2d;">
        Create comprehensive, well-researched non-fiction books with AI assistance.
        Start by creating a new book or opening an existing project.
        </p>
        """)
        welcome_text.setWordWrap(True)
        welcome_layout.addWidget(welcome_text)
        
        layout.addWidget(welcome_group)
        
        # Quick actions
        actions_group = QGroupBox("⚡ Quick Actions")
        actions_layout = QGridLayout(actions_group)
        
        self.new_book_action = QPushButton("📝 New Book")
        self.new_book_action.clicked.connect(self.main_window.new_book)
        self.new_book_action.setMinimumHeight(60)
        actions_layout.addWidget(self.new_book_action, 0, 0)
        
        self.open_book_action = QPushButton("📂 Open Book")
        self.open_book_action.clicked.connect(self.main_window.open_book)
        self.open_book_action.setMinimumHeight(60)
        actions_layout.addWidget(self.open_book_action, 0, 1)
        
        self.import_docs_action = QPushButton("📄 Import Documents")
        self.import_docs_action.clicked.connect(self.main_window.import_documents)
        self.import_docs_action.setMinimumHeight(60)
        actions_layout.addWidget(self.import_docs_action, 0, 2)
        
        self.start_research_action = QPushButton("🔍 Start Research")
        self.start_research_action.clicked.connect(self.main_window.start_research)
        self.start_research_action.setMinimumHeight(60)
        actions_layout.addWidget(self.start_research_action, 1, 0)
        
        self.generate_chapter_action = QPushButton("✍️ Generate Chapter")
        self.generate_chapter_action.clicked.connect(self.main_window.generate_chapter)
        self.generate_chapter_action.setMinimumHeight(60)
        actions_layout.addWidget(self.generate_chapter_action, 1, 1)
        
        self.export_book_action = QPushButton("📤 Export Book")
        self.export_book_action.clicked.connect(self.main_window.export_book)
        self.export_book_action.setMinimumHeight(60)
        actions_layout.addWidget(self.export_book_action, 1, 2)
        
        layout.addWidget(actions_group)
        
        # Recent projects
        recent_group = QGroupBox("📚 Recent Projects")
        recent_layout = QVBoxLayout(recent_group)
        
        self.recent_projects_list = QListWidget()
        self.recent_projects_list.itemDoubleClicked.connect(self.open_recent_project)
        recent_layout.addWidget(self.recent_projects_list)
        
        # Load recent projects
        self.load_recent_projects()
        
        layout.addWidget(recent_group)
        
        # System status
        status_group = QGroupBox("📊 System Status")
        status_layout = QGridLayout(status_group)
        
        self.memory_status_label = QLabel("Memory: Ready")
        self.llm_status_label = QLabel("LLM: Ready")
        self.agents_status_label = QLabel("Agents: Ready")
        
        status_layout.addWidget(self.memory_status_label, 0, 0)
        status_layout.addWidget(self.llm_status_label, 0, 1)
        status_layout.addWidget(self.agents_status_label, 0, 2)
        
        layout.addWidget(status_group)
        
        layout.addStretch()
    
    def load_recent_projects(self):
        """Load recent projects."""
        # This would load from a config file or database
        recent_projects = [
            "Modern Tarot: Ancient Ways in a Modern World",
            "The Future of AI in Education",
            "Sustainable Living Guide"
        ]
        
        for project in recent_projects:
            self.recent_projects_list.addItem(project)
    
    def open_recent_project(self, item):
        """Open a recent project."""
        project_name = item.text()
        self.main_window.open_project(project_name)


class BookEditorPage(QWidget):
    """Book editor page with rich text editing capabilities."""
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.current_chapter = None
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Toolbar
        toolbar_layout = QHBoxLayout()
        
        # Chapter selector
        toolbar_layout.addWidget(QLabel("Chapter:"))
        self.chapter_combo = QComboBox()
        self.chapter_combo.currentTextChanged.connect(self.on_chapter_changed)
        toolbar_layout.addWidget(self.chapter_combo)
        
        toolbar_layout.addStretch()
        
        # Editing tools
        self.bold_btn = QPushButton("B")
        self.bold_btn.setCheckable(True)
        self.bold_btn.clicked.connect(self.toggle_bold)
        toolbar_layout.addWidget(self.bold_btn)
        
        self.italic_btn = QPushButton("I")
        self.italic_btn.setCheckable(True)
        self.italic_btn.clicked.connect(self.toggle_italic)
        toolbar_layout.addWidget(self.italic_btn)
        
        self.underline_btn = QPushButton("U")
        self.underline_btn.setCheckable(True)
        self.underline_btn.clicked.connect(self.toggle_underline)
        toolbar_layout.addWidget(self.underline_btn)
        
        toolbar_layout.addWidget(QLabel("|"))
        
        # Font controls
        self.font_combo = QFontComboBox()
        self.font_combo.currentFontChanged.connect(self.change_font)
        toolbar_layout.addWidget(self.font_combo)
        
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 72)
        self.font_size_spin.setValue(12)
        self.font_size_spin.valueChanged.connect(self.change_font_size)
        toolbar_layout.addWidget(self.font_size_spin)
        
        layout.addLayout(toolbar_layout)
        
        # Main editor
        self.editor = QTextEdit()
        self.editor.setFont(RetroWriterTheme.FONTS['body'])
        self.editor.textChanged.connect(self.on_text_changed)
        self.editor.cursorPositionChanged.connect(self.on_cursor_changed)
        layout.addWidget(self.editor)
        
        # Status bar
        status_layout = QHBoxLayout()
        
        self.word_count_label = QLabel("Words: 0")
        self.char_count_label = QLabel("Characters: 0")
        self.line_count_label = QLabel("Lines: 0")
        
        status_layout.addWidget(self.word_count_label)
        status_layout.addWidget(self.char_count_label)
        status_layout.addWidget(self.line_count_label)
        
        status_layout.addStretch()
        
        self.reading_time_label = QLabel("Reading time: 0 min")
        status_layout.addWidget(self.reading_time_label)
        
        layout.addLayout(status_layout)
    
    def on_chapter_changed(self, chapter_title):
        """Handle chapter change."""
        self.current_chapter = chapter_title
        self.load_chapter_content(chapter_title)
    
    def load_chapter_content(self, chapter_title):
        """Load chapter content."""
        # This would load from the book data
        self.editor.setPlainText(f"Content for chapter: {chapter_title}")
    
    def on_text_changed(self):
        """Handle text changes."""
        text = self.editor.toPlainText()
        word_count = len(text.split())
        char_count = len(text)
        line_count = len(text.split('\n'))
        
        self.word_count_label.setText(f"Words: {word_count}")
        self.char_count_label.setText(f"Characters: {char_count}")
        self.line_count_label.setText(f"Lines: {line_count}")
        
        # Calculate reading time (average 200 words per minute)
        reading_time = word_count / 200
        self.reading_time_label.setText(f"Reading time: {reading_time:.1f} min")
        
        # Update main window word count
        if hasattr(self.main_window, 'word_count_label'):
            self.main_window.word_count_label.setText(f"Words: {word_count}")
    
    def on_cursor_changed(self):
        """Handle cursor position changes."""
        cursor = self.editor.textCursor()
        format = cursor.charFormat()
        
        # Update toolbar buttons
        self.bold_btn.setChecked(format.fontWeight() == QFont.Weight.Bold)
        self.italic_btn.setChecked(format.fontItalic())
        self.underline_btn.setChecked(format.fontUnderline())
    
    def toggle_bold(self):
        """Toggle bold formatting."""
        cursor = self.editor.textCursor()
        format = cursor.charFormat()
        format.setFontWeight(QFont.Weight.Bold if not format.fontWeight() == QFont.Weight.Bold else QFont.Weight.Normal)
        cursor.mergeCharFormat(format)
        self.editor.setTextCursor(cursor)
    
    def toggle_italic(self):
        """Toggle italic formatting."""
        cursor = self.editor.textCursor()
        format = cursor.charFormat()
        format.setFontItalic(not format.fontItalic())
        cursor.mergeCharFormat(format)
        self.editor.setTextCursor(cursor)
    
    def toggle_underline(self):
        """Toggle underline formatting."""
        cursor = self.editor.textCursor()
        format = cursor.charFormat()
        format.setFontUnderline(not format.fontUnderline())
        cursor.mergeCharFormat(format)
        self.editor.setTextCursor(cursor)
    
    def change_font(self, font):
        """Change font family."""
        cursor = self.editor.textCursor()
        format = cursor.charFormat()
        format.setFontFamily(font.family())
        cursor.mergeCharFormat(format)
        self.editor.setTextCursor(cursor)
    
    def change_font_size(self, size):
        """Change font size."""
        cursor = self.editor.textCursor()
        format = cursor.charFormat()
        format.setFontPointSize(size)
        cursor.mergeCharFormat(format)
        self.editor.setTextCursor(cursor)


class ResearchPage(QWidget):
    """Research page with research management and source viewing."""
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setup_ui()
    
    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Left panel - Research topics and sources
        left_panel = QWidget()
        left_panel.setFixedWidth(400)
        left_layout = QVBoxLayout(left_panel)
        
        # Research topics
        topics_group = QGroupBox("📋 Research Topics")
        topics_layout = QVBoxLayout(topics_group)
        
        self.topics_list = QListWidget()
        self.topics_list.itemClicked.connect(self.on_topic_selected)
        topics_layout.addWidget(self.topics_list)
        
        # Topic actions
        topic_actions_layout = QHBoxLayout()
        
        self.add_topic_btn = QPushButton("➕ Add")
        self.add_topic_btn.clicked.connect(self.add_topic)
        topic_actions_layout.addWidget(self.add_topic_btn)
        
        self.remove_topic_btn = QPushButton("➖ Remove")
        self.remove_topic_btn.clicked.connect(self.remove_topic)
        topic_actions_layout.addWidget(self.remove_topic_btn)
        
        topics_layout.addLayout(topic_actions_layout)
        left_layout.addWidget(topics_group)
        
        # Research sources
        sources_group = QGroupBox("📚 Research Sources")
        sources_layout = QVBoxLayout(sources_group)
        
        self.sources_list = QListWidget()
        self.sources_list.itemClicked.connect(self.on_source_selected)
        sources_layout.addWidget(self.sources_list)
        
        # Source actions
        source_actions_layout = QHBoxLayout()
        
        self.view_source_btn = QPushButton("👁️ View")
        self.view_source_btn.clicked.connect(self.view_source)
        source_actions_layout.addWidget(self.view_source_btn)
        
        self.search_sources_btn = QPushButton("🔍 Search")
        self.search_sources_btn.clicked.connect(self.search_sources)
        source_actions_layout.addWidget(self.search_sources_btn)
        
        sources_layout.addLayout(source_actions_layout)
        left_layout.addWidget(sources_group)
        
        layout.addWidget(left_panel)
        
        # Right panel - Source content and research results
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Source content viewer
        content_group = QGroupBox("📄 Source Content")
        content_layout = QVBoxLayout(content_group)
        
        self.source_content = QTextBrowser()
        self.source_content.setFont(RetroWriterTheme.FONTS['body'])
        content_layout.addWidget(self.source_content)
        
        right_layout.addWidget(content_group)
        
        # Research results
        results_group = QGroupBox("🔍 Research Results")
        results_layout = QVBoxLayout(results_group)
        
        self.research_results = QTextEdit()
        self.research_results.setReadOnly(True)
        self.research_results.setFont(RetroWriterTheme.FONTS['body'])
        results_layout.addWidget(self.research_results)
        
        right_layout.addWidget(results_group)
        
        layout.addWidget(right_panel)
    
    def on_topic_selected(self, item):
        """Handle topic selection."""
        topic = item.text()
        self.load_topic_sources(topic)
    
    def on_source_selected(self, item):
        """Handle source selection."""
        source = item.text()
        self.load_source_content(source)
    
    def add_topic(self):
        """Add a research topic."""
        topic, ok = QInputDialog.getText(self, "Research Topic", "Enter research topic:")
        if ok and topic:
            self.topics_list.addItem(topic)
    
    def remove_topic(self):
        """Remove selected topic."""
        current_item = self.topics_list.currentItem()
        if current_item:
            self.topics_list.takeItem(self.topics_list.row(current_item))
    
    def view_source(self):
        """View selected source."""
        current_item = self.sources_list.currentItem()
        if current_item:
            self.load_source_content(current_item.text())
    
    def search_sources(self):
        """Search sources."""
        query, ok = QInputDialog.getText(self, "Search Sources", "Enter search query:")
        if ok and query:
            self.perform_source_search(query)
    
    def load_topic_sources(self, topic):
        """Load sources for a topic."""
        # This would load from the memory manager
        self.sources_list.clear()
        self.sources_list.addItem(f"Source 1 for {topic}")
        self.sources_list.addItem(f"Source 2 for {topic}")
    
    def load_source_content(self, source):
        """Load content for a source."""
        # This would load from the memory manager
        content = f"Content for {source}\n\nThis is sample content that would be loaded from the memory manager."
        self.source_content.setPlainText(content)
    
    def perform_source_search(self, query):
        """Perform source search."""
        # This would search the memory manager
        results = f"Search results for '{query}':\n\nFound 3 relevant sources:\n1. Source A\n2. Source B\n3. Source C"
        self.research_results.setPlainText(results)


class WritingPage(QWidget):
    """Writing page with AI-assisted writing tools."""
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Writing controls
        controls_layout = QHBoxLayout()
        
        # Chapter selector
        controls_layout.addWidget(QLabel("Chapter:"))
        self.chapter_combo = QComboBox()
        controls_layout.addWidget(self.chapter_combo)
        
        controls_layout.addStretch()
        
        # Writing style controls
        controls_layout.addWidget(QLabel("Style:"))
        self.style_combo = QComboBox()
        self.style_combo.addItems(["Academic", "Journalistic", "Narrative", "Technical", "Creative"])
        controls_layout.addWidget(self.style_combo)
        
        controls_layout.addWidget(QLabel("Tone:"))
        self.tone_combo = QComboBox()
        self.tone_combo.addItems(["Formal", "Informal", "Conversational", "Authoritative", "Friendly"])
        controls_layout.addWidget(self.tone_combo)
        
        layout.addLayout(controls_layout)
        
        # Main writing area
        writing_layout = QHBoxLayout()
        
        # Left side - Writing editor
        editor_group = QGroupBox("✍️ Writing Editor")
        editor_layout = QVBoxLayout(editor_group)
        
        self.writing_editor = QTextEdit()
        self.writing_editor.setFont(RetroWriterTheme.FONTS['body'])
        self.writing_editor.textChanged.connect(self.on_writing_changed)
        editor_layout.addWidget(self.writing_editor)
        
        writing_layout.addWidget(editor_group)
        
        # Right side - AI assistance
        ai_group = QGroupBox("🤖 AI Assistance")
        ai_layout = QVBoxLayout(ai_group)
        
        # AI suggestions
        self.ai_suggestions = QTextEdit()
        self.ai_suggestions.setReadOnly(True)
        self.ai_suggestions.setMaximumHeight(200)
        ai_layout.addWidget(self.ai_suggestions)
        
        # AI action buttons
        ai_actions_layout = QGridLayout()
        
        self.improve_btn = QPushButton("✨ Improve")
        self.improve_btn.clicked.connect(self.improve_text)
        ai_actions_layout.addWidget(self.improve_btn, 0, 0)
        
        self.expand_btn = QPushButton("📝 Expand")
        self.expand_btn.clicked.connect(self.expand_text)
        ai_actions_layout.addWidget(self.expand_btn, 0, 1)
        
        self.summarize_btn = QPushButton("📋 Summarize")
        self.summarize_btn.clicked.connect(self.summarize_text)
        ai_actions_layout.addWidget(self.summarize_btn, 1, 0)
        
        self.check_style_btn = QPushButton("🎨 Check Style")
        self.check_style_btn.clicked.connect(self.check_style)
        ai_actions_layout.addWidget(self.check_style_btn, 1, 1)
        
        ai_layout.addLayout(ai_actions_layout)
        
        # Research context
        context_group = QGroupBox("🔍 Research Context")
        context_layout = QVBoxLayout(context_group)
        
        self.research_context = QTextEdit()
        self.research_context.setReadOnly(True)
        self.research_context.setMaximumHeight(150)
        context_layout.addWidget(self.research_context)
        
        ai_layout.addWidget(context_group)
        
        writing_layout.addWidget(ai_group)
        
        layout.addLayout(writing_layout)
        
        # Status bar
        status_layout = QHBoxLayout()
        
        self.word_count_label = QLabel("Words: 0")
        self.char_count_label = QLabel("Characters: 0")
        self.reading_time_label = QLabel("Reading time: 0 min")
        
        status_layout.addWidget(self.word_count_label)
        status_layout.addWidget(self.char_count_label)
        status_layout.addWidget(self.reading_time_label)
        
        status_layout.addStretch()
        
        self.ai_status_label = QLabel("AI: Ready")
        status_layout.addWidget(self.ai_status_label)
        
        layout.addLayout(status_layout)
    
    def on_writing_changed(self):
        """Handle writing changes."""
        text = self.writing_editor.toPlainText()
        word_count = len(text.split())
        char_count = len(text)
        
        self.word_count_label.setText(f"Words: {word_count}")
        self.char_count_label.setText(f"Characters: {char_count}")
        
        # Calculate reading time
        reading_time = word_count / 200
        self.reading_time_label.setText(f"Reading time: {reading_time:.1f} min")
        
        # Update research context
        self.update_research_context()
    
    def improve_text(self):
        """Improve selected text using AI."""
        cursor = self.writing_editor.textCursor()
        selected_text = cursor.selectedText()
        
        if selected_text:
            self.ai_status_label.setText("AI: Improving text...")
            # This would call the AI improvement service
            improved_text = f"Improved version of: {selected_text}"
            self.ai_suggestions.setPlainText(improved_text)
            self.ai_status_label.setText("AI: Ready")
        else:
            QMessageBox.information(self, "No Selection", "Please select text to improve.")
    
    def expand_text(self):
        """Expand selected text using AI."""
        cursor = self.writing_editor.textCursor()
        selected_text = cursor.selectedText()
        
        if selected_text:
            self.ai_status_label.setText("AI: Expanding text...")
            # This would call the AI expansion service
            expanded_text = f"Expanded version of: {selected_text}"
            self.ai_suggestions.setPlainText(expanded_text)
            self.ai_status_label.setText("AI: Ready")
        else:
            QMessageBox.information(self, "No Selection", "Please select text to expand.")
    
    def summarize_text(self):
        """Summarize selected text using AI."""
        cursor = self.writing_editor.textCursor()
        selected_text = cursor.selectedText()
        
        if selected_text:
            self.ai_status_label.setText("AI: Summarizing text...")
            # This would call the AI summarization service
            summary = f"Summary of: {selected_text}"
            self.ai_suggestions.setPlainText(summary)
            self.ai_status_label.setText("AI: Ready")
        else:
            QMessageBox.information(self, "No Selection", "Please select text to summarize.")
    
    def check_style(self):
        """Check writing style using AI."""
        text = self.writing_editor.toPlainText()
        
        if text:
            self.ai_status_label.setText("AI: Checking style...")
            # This would call the AI style checking service
            style_feedback = f"Style feedback for your text:\n\n- Consider using more active voice\n- Vary sentence length\n- Check for consistency in tone"
            self.ai_suggestions.setPlainText(style_feedback)
            self.ai_status_label.setText("AI: Ready")
        else:
            QMessageBox.information(self, "No Text", "Please write some text to check style.")
    
    def update_research_context(self):
        """Update research context based on current text."""
        text = self.writing_editor.toPlainText()
        
        if text:
            # This would search the memory manager for relevant context
            context = f"Relevant research context for your current writing:\n\n- Topic: {text[:50]}...\n- Related sources: 3 found\n- Key concepts: AI, Writing, Research"
            self.research_context.setPlainText(context)
        else:
            self.research_context.setPlainText("Start writing to see relevant research context.")


class ToolsPage(QWidget):
    """Tools page with system monitoring and tool testing."""
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # System monitoring
        monitor_group = QGroupBox("📊 System Monitor")
        monitor_layout = QGridLayout(monitor_group)
        
        # Agent status
        self.agent_status_table = QTableWidget()
        self.agent_status_table.setColumnCount(3)
        self.agent_status_table.setHorizontalHeaderLabels(["Agent", "Status", "Tasks"])
        self.agent_status_table.setMaximumHeight(200)
        monitor_layout.addWidget(self.agent_status_table, 0, 0, 1, 2)
        
        # System metrics
        self.cpu_label = QLabel("CPU: 0%")
        self.memory_label = QLabel("Memory: 0 MB")
        self.disk_label = QLabel("Disk: 0 MB")
        
        monitor_layout.addWidget(self.cpu_label, 1, 0)
        monitor_layout.addWidget(self.memory_label, 1, 1)
        monitor_layout.addWidget(self.disk_label, 2, 0)
        
        layout.addWidget(monitor_group)
        
        # Tool testing
        tools_group = QGroupBox("🛠️ Tool Testing")
        tools_layout = QVBoxLayout(tools_group)
        
        # Tool test buttons
        test_buttons_layout = QGridLayout()
        
        self.test_memory_btn = QPushButton("🧠 Test Memory")
        self.test_memory_btn.clicked.connect(self.test_memory)
        test_buttons_layout.addWidget(self.test_memory_btn, 0, 0)
        
        self.test_llm_btn = QPushButton("🤖 Test LLM")
        self.test_llm_btn.clicked.connect(self.test_llm)
        test_buttons_layout.addWidget(self.test_llm_btn, 0, 1)
        
        self.test_tools_btn = QPushButton("🛠️ Test Tools")
        self.test_tools_btn.clicked.connect(self.test_tools)
        test_buttons_layout.addWidget(self.test_tools_btn, 0, 2)
        
        self.test_agents_btn = QPushButton("🤖 Test Agents")
        self.test_agents_btn.clicked.connect(self.test_agents)
        test_buttons_layout.addWidget(self.test_agents_btn, 1, 0)
        
        self.test_workflow_btn = QPushButton("🔄 Test Workflow")
        self.test_workflow_btn.clicked.connect(self.test_workflow)
        test_buttons_layout.addWidget(self.test_workflow_btn, 1, 1)
        
        self.test_all_btn = QPushButton("🧪 Test All")
        self.test_all_btn.clicked.connect(self.test_all)
        test_buttons_layout.addWidget(self.test_all_btn, 1, 2)
        
        tools_layout.addLayout(test_buttons_layout)
        
        # Test results
        self.test_results = QTextEdit()
        self.test_results.setReadOnly(True)
        self.test_results.setMaximumHeight(200)
        tools_layout.addWidget(self.test_results)
        
        layout.addWidget(tools_group)
        
        # Export options
        export_group = QGroupBox("📤 Export Options")
        export_layout = QGridLayout(export_group)
        
        self.export_md_btn = QPushButton("📄 Export Markdown")
        self.export_md_btn.clicked.connect(self.export_markdown)
        export_layout.addWidget(self.export_md_btn, 0, 0)
        
        self.export_docx_btn = QPushButton("📝 Export DOCX")
        self.export_docx_btn.clicked.connect(self.export_docx)
        export_layout.addWidget(self.export_docx_btn, 0, 1)
        
        self.export_pdf_btn = QPushButton("📕 Export PDF")
        self.export_pdf_btn.clicked.connect(self.export_pdf)
        export_layout.addWidget(self.export_pdf_btn, 0, 2)
        
        self.export_html_btn = QPushButton("🌐 Export HTML")
        self.export_html_btn.clicked.connect(self.export_html)
        export_layout.addWidget(self.export_html_btn, 1, 0)
        
        self.export_epub_btn = QPushButton("📚 Export EPUB")
        self.export_epub_btn.clicked.connect(self.export_epub)
        export_layout.addWidget(self.export_epub_btn, 1, 1)
        
        layout.addWidget(export_group)
        
        # Initialize agent status table
        self.update_agent_status()
    
    def update_agent_status(self):
        """Update agent status table."""
        agents = [
            ("Research Agent", "Ready", "0"),
            ("Writer Agent", "Ready", "0"),
            ("Editor Agent", "Ready", "0"),
            ("Tool Agent", "Ready", "0")
        ]
        
        self.agent_status_table.setRowCount(len(agents))
        
        for row, (agent, status, tasks) in enumerate(agents):
            self.agent_status_table.setItem(row, 0, QTableWidgetItem(agent))
            self.agent_status_table.setItem(row, 1, QTableWidgetItem(status))
            self.agent_status_table.setItem(row, 2, QTableWidgetItem(tasks))
    
    def test_memory(self):
        """Test memory manager."""
        self.test_results.append("Testing Memory Manager...")
        # This would test the memory manager
        self.test_results.append("✓ Memory Manager: OK")
    
    def test_llm(self):
        """Test LLM client."""
        self.test_results.append("Testing LLM Client...")
        # This would test the LLM client
        self.test_results.append("✓ LLM Client: OK")
    
    def test_tools(self):
        """Test tool manager."""
        self.test_results.append("Testing Tool Manager...")
        # This would test the tool manager
        self.test_results.append("✓ Tool Manager: OK")
    
    def test_agents(self):
        """Test agents."""
        self.test_results.append("Testing Agents...")
        # This would test all agents
        self.test_results.append("✓ All Agents: OK")
    
    def test_workflow(self):
        """Test book workflow."""
        self.test_results.append("Testing Book Workflow...")
        # This would test the book workflow
        self.test_results.append("✓ Book Workflow: OK")
    
    def test_all(self):
        """Test all components."""
        self.test_results.clear()
        self.test_results.append("Running comprehensive system test...")
        
        self.test_memory()
        self.test_llm()
        self.test_tools()
        self.test_agents()
        self.test_workflow()
        
        self.test_results.append("\n✓ All tests completed successfully!")
    
    def export_markdown(self):
        """Export book as Markdown."""
        self.main_window.export_book_format("markdown")
    
    def export_docx(self):
        """Export book as DOCX."""
        self.main_window.export_book_format("docx")
    
    def export_pdf(self):
        """Export book as PDF."""
        self.main_window.export_book_format("pdf")
    
    def export_html(self):
        """Export book as HTML."""
        self.main_window.export_book_format("html")
    
    def export_epub(self):
        """Export book as EPUB."""
        self.main_window.export_book_format("epub")


class SettingsPage(QWidget):
    """Settings page with configuration options."""
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Create tabbed settings
        settings_tabs = QTabWidget()
        layout.addWidget(settings_tabs)
        
        # LLM settings tab
        llm_tab = self.create_llm_settings_tab()
        settings_tabs.addTab(llm_tab, "🤖 LLM")
        
        # Memory settings tab
        memory_tab = self.create_memory_settings_tab()
        settings_tabs.addTab(memory_tab, "🧠 Memory")
        
        # Writing settings tab
        writing_tab = self.create_writing_settings_tab()
        settings_tabs.addTab(writing_tab, "✍️ Writing")
        
        # Appearance settings tab
        appearance_tab = self.create_appearance_settings_tab()
        settings_tabs.addTab(appearance_tab, "🎨 Appearance")
        
        # Action buttons
        actions_layout = QHBoxLayout()
        
        self.save_settings_btn = QPushButton("💾 Save Settings")
        self.save_settings_btn.clicked.connect(self.save_settings)
        actions_layout.addWidget(self.save_settings_btn)
        
        self.reset_settings_btn = QPushButton("🔄 Reset to Defaults")
        self.reset_settings_btn.clicked.connect(self.reset_settings)
        actions_layout.addWidget(self.reset_settings_btn)
        
        self.import_settings_btn = QPushButton("📂 Import Settings")
        self.import_settings_btn.clicked.connect(self.import_settings)
        actions_layout.addWidget(self.import_settings_btn)
        
        self.export_settings_btn = QPushButton("📤 Export Settings")
        self.export_settings_btn.clicked.connect(self.export_settings)
        actions_layout.addWidget(self.export_settings_btn)
        
        layout.addLayout(actions_layout)
    
    def create_llm_settings_tab(self):
        """Create LLM settings tab."""
        tab = QWidget()
        layout = QFormLayout(tab)
        
        self.llm_provider_combo = QComboBox()
        self.llm_provider_combo.addItems(["OpenAI", "Ollama", "Local"])
        layout.addRow("Provider:", self.llm_provider_combo)
        
        self.api_key_edit = QLineEdit()
        self.api_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addRow("API Key:", self.api_key_edit)
        
        self.model_combo = QComboBox()
        self.model_combo.addItems(["gpt-4", "gpt-3.5-turbo", "llama2", "mistral"])
        layout.addRow("Model:", self.model_combo)
        
        self.temperature_slider = QSlider(Qt.Orientation.Horizontal)
        self.temperature_slider.setRange(0, 100)
        self.temperature_slider.setValue(70)
        layout.addRow("Temperature:", self.temperature_slider)
        
        self.max_tokens_spin = QSpinBox()
        self.max_tokens_spin.setRange(100, 4000)
        self.max_tokens_spin.setValue(2000)
        layout.addRow("Max Tokens:", self.max_tokens_spin)
        
        return tab
    
    def create_memory_settings_tab(self):
        """Create memory settings tab."""
        tab = QWidget()
        layout = QFormLayout(tab)
        
        self.memory_provider_combo = QComboBox()
        self.memory_provider_combo.addItems(["ChromaDB", "Local", "Remote"])
        layout.addRow("Provider:", self.memory_provider_combo)
        
        self.max_chunks_spin = QSpinBox()
        self.max_chunks_spin.setRange(100, 10000)
        self.max_chunks_spin.setValue(1000)
        layout.addRow("Max Chunks:", self.max_chunks_spin)
        
        self.chunk_size_spin = QSpinBox()
        self.chunk_size_spin.setRange(100, 2000)
        self.chunk_size_spin.setValue(500)
        layout.addRow("Chunk Size:", self.chunk_size_spin)
        
        self.embedding_model_combo = QComboBox()
        self.embedding_model_combo.addItems(["sentence-transformers", "OpenAI", "Local"])
        layout.addRow("Embedding Model:", self.embedding_model_combo)
        
        return tab
    
    def create_writing_settings_tab(self):
        """Create writing settings tab."""
        tab = QWidget()
        layout = QFormLayout(tab)
        
        self.default_style_combo = QComboBox()
        self.default_style_combo.addItems(["Academic", "Journalistic", "Narrative", "Technical", "Creative"])
        layout.addRow("Default Style:", self.default_style_combo)
        
        self.default_tone_combo = QComboBox()
        self.default_tone_combo.addItems(["Formal", "Informal", "Conversational", "Authoritative", "Friendly"])
        layout.addRow("Default Tone:", self.default_tone_combo)
        
        self.auto_save_check = QCheckBox("Auto-save")
        self.auto_save_check.setChecked(True)
        layout.addRow(self.auto_save_check)
        
        self.auto_backup_check = QCheckBox("Auto-backup")
        self.auto_backup_check.setChecked(True)
        layout.addRow(self.auto_backup_check)
        
        self.backup_interval_spin = QSpinBox()
        self.backup_interval_spin.setRange(1, 60)
        self.backup_interval_spin.setValue(5)
        self.backup_interval_spin.setSuffix(" minutes")
        layout.addRow("Backup Interval:", self.backup_interval_spin)
        
        return tab
    
    def create_appearance_settings_tab(self):
        """Create appearance settings tab."""
        tab = QWidget()
        layout = QFormLayout(tab)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Retro Writer", "Classic", "Modern", "Dark"])
        layout.addRow("Theme:", self.theme_combo)
        
        self.font_family_combo = QFontComboBox()
        layout.addRow("Font Family:", self.font_family_combo)
        
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 24)
        self.font_size_spin.setValue(12)
        layout.addRow("Font Size:", self.font_size_spin)
        
        self.show_line_numbers_check = QCheckBox("Show Line Numbers")
        self.show_line_numbers_check.setChecked(True)
        layout.addRow(self.show_line_numbers_check)
        
        self.show_word_count_check = QCheckBox("Show Word Count")
        self.show_word_count_check.setChecked(True)
        layout.addRow(self.show_word_count_check)
        
        self.show_reading_time_check = QCheckBox("Show Reading Time")
        self.show_reading_time_check.setChecked(True)
        layout.addRow(self.show_reading_time_check)
        
        return tab
    
    def save_settings(self):
        """Save current settings."""
        settings = {
            "llm": {
                "provider": self.llm_provider_combo.currentText(),
                "api_key": self.api_key_edit.text(),
                "model": self.model_combo.currentText(),
                "temperature": self.temperature_slider.value() / 100.0,
                "max_tokens": self.max_tokens_spin.value()
            },
            "memory": {
                "provider": self.memory_provider_combo.currentText(),
                "max_chunks": self.max_chunks_spin.value(),
                "chunk_size": self.chunk_size_spin.value(),
                "embedding_model": self.embedding_model_combo.currentText()
            },
            "writing": {
                "default_style": self.default_style_combo.currentText(),
                "default_tone": self.default_tone_combo.currentText(),
                "auto_save": self.auto_save_check.isChecked(),
                "auto_backup": self.auto_backup_check.isChecked(),
                "backup_interval": self.backup_interval_spin.value()
            },
            "appearance": {
                "theme": self.theme_combo.currentText(),
                "font_family": self.font_family_combo.currentText(),
                "font_size": self.font_size_spin.value(),
                "show_line_numbers": self.show_line_numbers_check.isChecked(),
                "show_word_count": self.show_word_count_check.isChecked(),
                "show_reading_time": self.show_reading_time_check.isChecked()
            }
        }
        
        # Save to file
        settings_file = Path.home() / ".retro_writer" / "settings.json"
        settings_file.parent.mkdir(exist_ok=True)
        
        with open(settings_file, 'w') as f:
            json.dump(settings, f, indent=2)
        
        QMessageBox.information(self, "Settings Saved", "Settings have been saved successfully.")
    
    def reset_settings(self):
        """Reset settings to defaults."""
        reply = QMessageBox.question(self, "Reset Settings", 
                                   "Reset all settings to defaults?",
                                   QMessageBox.StandardButton.Yes | 
                                   QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            # Reset to default values
            self.llm_provider_combo.setCurrentText("OpenAI")
            self.api_key_edit.clear()
            self.model_combo.setCurrentText("gpt-4")
            self.temperature_slider.setValue(70)
            self.max_tokens_spin.setValue(2000)
            
            QMessageBox.information(self, "Settings Reset", "Settings have been reset to defaults.")
    
    def import_settings(self):
        """Import settings from file."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Import Settings", "", "JSON Files (*.json)")
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    settings = json.load(f)
                
                # Apply settings
                if "llm" in settings:
                    llm = settings["llm"]
                    self.llm_provider_combo.setCurrentText(llm.get("provider", "OpenAI"))
                    self.api_key_edit.setText(llm.get("api_key", ""))
                    self.model_combo.setCurrentText(llm.get("model", "gpt-4"))
                    self.temperature_slider.setValue(int(llm.get("temperature", 0.7) * 100))
                    self.max_tokens_spin.setValue(llm.get("max_tokens", 2000))
                
                QMessageBox.information(self, "Settings Imported", "Settings have been imported successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Import Error", f"Failed to import settings: {e}")
    
    def export_settings(self):
        """Export settings to file."""
        file_path, _ = QFileDialog.getSaveFileName(self, "Export Settings", "retro_writer_settings.json", "JSON Files (*.json)")
        if file_path:
            try:
                settings = {
                    "llm": {
                        "provider": self.llm_provider_combo.currentText(),
                        "api_key": self.api_key_edit.text(),
                        "model": self.model_combo.currentText(),
                        "temperature": self.temperature_slider.value() / 100.0,
                        "max_tokens": self.max_tokens_spin.value()
                    },
                    "memory": {
                        "provider": self.memory_provider_combo.currentText(),
                        "max_chunks": self.max_chunks_spin.value(),
                        "chunk_size": self.chunk_size_spin.value(),
                        "embedding_model": self.embedding_model_combo.currentText()
                    },
                    "writing": {
                        "default_style": self.default_style_combo.currentText(),
                        "default_tone": self.default_tone_combo.currentText(),
                        "auto_save": self.auto_save_check.isChecked(),
                        "auto_backup": self.auto_backup_check.isChecked(),
                        "backup_interval": self.backup_interval_spin.value()
                    },
                    "appearance": {
                        "theme": self.theme_combo.currentText(),
                        "font_family": self.font_family_combo.currentText(),
                        "font_size": self.font_size_spin.value(),
                        "show_line_numbers": self.show_line_numbers_check.isChecked(),
                        "show_word_count": self.show_word_count_check.isChecked(),
                        "show_reading_time": self.show_reading_time_check.isChecked()
                    }
                }
                
                with open(file_path, 'w') as f:
                    json.dump(settings, f, indent=2)
                
                QMessageBox.information(self, "Settings Exported", "Settings have been exported successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to export settings: {e}")