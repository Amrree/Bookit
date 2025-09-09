"""
GUI Module

Graphical user interface for the non-fiction book-writing system.
Provides a web-based interface using Streamlit.

Chosen libraries:
- Streamlit: Web-based GUI framework
- asyncio: Asynchronous operations
- logging: GUI activity logging

Adapted from: Streamlit documentation (https://docs.streamlit.io/)
Pattern: Multi-page web application with real-time updates
"""

import asyncio
import logging
import os
import sys
from pathlib import Path
from typing import Optional

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Import system modules
from document_ingestor import DocumentIngestor
from memory_manager import MemoryManager
from llm_client import LLMClient
from tool_manager import ToolManager
from agent_manager import AgentManager
from research_agent import ResearchAgent
from writer_agent import WriterAgent, WritingStyle
from editor_agent import EditorAgent, StyleGuide
from tool_agent import ToolAgent
from book_builder import BookBuilder

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Non-Fiction Book Writer",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .status-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .success-message {
        color: #28a745;
        font-weight: bold;
    }
    .error-message {
        color: #dc3545;
        font-weight: bold;
    }
    .warning-message {
        color: #ffc107;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


class GUIManager:
    """Manages the GUI application state and system initialization."""
    
    def __init__(self):
        self.system_initialized = False
        self.memory_manager = None
        self.llm_client = None
        self.tool_manager = None
        self.agent_manager = None
        self.research_agent = None
        self.writer_agent = None
        self.editor_agent = None
        self.tool_agent = None
        self.book_builder = None
    
    async def initialize_system(self):
        """Initialize the book-writing system."""
        try:
            # Get configuration from environment or session state
            openai_key = os.getenv('LLM_REMOTE_API_KEY') or st.session_state.get('openai_key')
            ollama_url = os.getenv('OLLAMA_LOCAL_URL', 'http://localhost:11434')
            embedding_key = os.getenv('EMBEDDING_API_KEY') or st.session_state.get('embedding_key')
            vector_db_path = os.getenv('VECTOR_DB_PATH', './memory_db')
            allow_unsafe = os.getenv('TOOL_MANAGER_ALLOW_UNSAFE', 'false').lower() == 'true'
            
            # Initialize memory manager
            self.memory_manager = MemoryManager(
                persist_directory=vector_db_path,
                use_remote_embeddings=bool(embedding_key),
                openai_api_key=embedding_key
            )
            
            # Initialize LLM client
            self.llm_client = LLMClient(
                primary_provider="openai" if openai_key else "ollama",
                openai_api_key=openai_key,
                ollama_url=ollama_url
            )
            
            # Initialize tool manager
            self.tool_manager = ToolManager(
                allow_unsafe=allow_unsafe,
                allow_restricted=True
            )
            
            # Initialize agent manager
            self.agent_manager = AgentManager()
            await self.agent_manager.start()
            
            # Initialize agents
            self.research_agent = ResearchAgent(
                agent_id="research_agent",
                memory_manager=self.memory_manager,
                llm_client=self.llm_client,
                tool_manager=self.tool_manager
            )
            
            self.writer_agent = WriterAgent(
                agent_id="writer_agent",
                memory_manager=self.memory_manager,
                llm_client=self.llm_client,
                research_agent=self.research_agent,
                writing_style=WritingStyle()
            )
            
            self.editor_agent = EditorAgent(
                agent_id="editor_agent",
                llm_client=self.llm_client,
                style_guide=StyleGuide()
            )
            
            self.tool_agent = ToolAgent(
                agent_id="tool_agent",
                tool_manager=self.tool_manager
            )
            
            # Register agents
            self.agent_manager.register_agent(
                self.research_agent, "research_agent", "research", 
                ["research", "web_search", "information_gathering"]
            )
            self.agent_manager.register_agent(
                self.writer_agent, "writer_agent", "writer",
                ["writing", "drafting", "content_generation"]
            )
            self.agent_manager.register_agent(
                self.editor_agent, "editor_agent", "editor",
                ["editing", "review", "quality_assurance"]
            )
            self.agent_manager.register_agent(
                self.tool_agent, "tool_agent", "tool",
                ["tool_execution", "automation"]
            )
            
            # Initialize book builder
            self.book_builder = BookBuilder(
                agent_manager=self.agent_manager,
                memory_manager=self.memory_manager,
                research_agent=self.research_agent,
                writer_agent=self.writer_agent,
                editor_agent=self.editor_agent,
                tool_agent=self.tool_agent
            )
            
            self.system_initialized = True
            return True
            
        except Exception as e:
            st.error(f"Failed to initialize system: {e}")
            return False


# Initialize GUI manager
if 'gui_manager' not in st.session_state:
    st.session_state.gui_manager = GUIManager()


def main():
    """Main GUI application."""
    st.markdown('<h1 class="main-header">📚 Non-Fiction Book Writer</h1>', unsafe_allow_html=True)
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page",
        ["Home", "Configuration", "Document Ingestion", "Research", "Book Management", "Tools", "System Status"]
    )
    
    # Initialize system if not already done
    if not st.session_state.gui_manager.system_initialized and page != "Configuration":
        st.warning("⚠️ System not initialized. Please configure the system first.")
        page = "Configuration"
    
    # Route to appropriate page
    if page == "Home":
        show_home_page()
    elif page == "Configuration":
        show_configuration_page()
    elif page == "Document Ingestion":
        show_ingestion_page()
    elif page == "Research":
        show_research_page()
    elif page == "Book Management":
        show_book_management_page()
    elif page == "Tools":
        show_tools_page()
    elif page == "System Status":
        show_status_page()


def show_home_page():
    """Display the home page."""
    st.markdown("## Welcome to the Non-Fiction Book Writer")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Features")
        st.markdown("""
        - **Document Ingestion**: Upload and process PDF, DOCX, EPUB, and text files
        - **Research Agent**: Autonomous research using RAG and web search
        - **Writer Agent**: AI-powered content generation with style consistency
        - **Editor Agent**: Quality assurance and content review
        - **Book Builder**: Complete book generation workflow
        - **Multiple Export Formats**: Markdown, DOCX, and PDF
        """)
    
    with col2:
        st.markdown("### Quick Start")
        st.markdown("""
        1. **Configure** the system with your API keys
        2. **Ingest** your reference documents
        3. **Research** topics for your book
        4. **Create** a new book project
        5. **Generate** the book outline
        6. **Build** the complete book
        7. **Export** to your preferred format
        """)
    
    # System status overview
    if st.session_state.gui_manager.system_initialized:
        st.markdown("### System Status")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            memory_stats = st.session_state.gui_manager.memory_manager.get_stats()
            st.metric("Memory Chunks", memory_stats['total_chunks'])
        
        with col2:
            agent_stats = st.session_state.gui_manager.agent_manager.get_stats()
            st.metric("Active Agents", agent_stats['total_agents'])
        
        with col3:
            tool_stats = st.session_state.gui_manager.tool_manager.get_execution_stats()
            st.metric("Available Tools", tool_stats['available_tools'])


def show_configuration_page():
    """Display the configuration page."""
    st.markdown("## System Configuration")
    
    with st.form("config_form"):
        st.markdown("### API Configuration")
        
        openai_key = st.text_input(
            "OpenAI API Key",
            value=st.session_state.get('openai_key', ''),
            type="password",
            help="Required for remote LLM access"
        )
        
        ollama_url = st.text_input(
            "Ollama URL",
            value=st.session_state.get('ollama_url', 'http://localhost:11434'),
            help="Local Ollama server URL"
        )
        
        embedding_key = st.text_input(
            "Embedding API Key",
            value=st.session_state.get('embedding_key', ''),
            type="password",
            help="Optional: For remote embedding generation"
        )
        
        st.markdown("### System Configuration")
        
        vector_db_path = st.text_input(
            "Vector Database Path",
            value=st.session_state.get('vector_db_path', './memory_db'),
            help="Path to store the vector database"
        )
        
        allow_unsafe = st.checkbox(
            "Allow Unsafe Tools",
            value=st.session_state.get('allow_unsafe', False),
            help="Enable potentially dangerous tools (use with caution)"
        )
        
        submitted = st.form_submit_button("Initialize System")
        
        if submitted:
            # Store configuration in session state
            st.session_state.openai_key = openai_key
            st.session_state.ollama_url = ollama_url
            st.session_state.embedding_key = embedding_key
            st.session_state.vector_db_path = vector_db_path
            st.session_state.allow_unsafe = allow_unsafe
            
            # Initialize system
            with st.spinner("Initializing system..."):
                success = asyncio.run(st.session_state.gui_manager.initialize_system())
                
                if success:
                    st.success("✅ System initialized successfully!")
                    st.rerun()
                else:
                    st.error("❌ Failed to initialize system. Please check your configuration.")


def show_ingestion_page():
    """Display the document ingestion page."""
    st.markdown("## Document Ingestion")
    
    tab1, tab2 = st.tabs(["Single Document", "Directory"])
    
    with tab1:
        st.markdown("### Upload Single Document")
        
        uploaded_file = st.file_uploader(
            "Choose a file",
            type=['pdf', 'docx', 'epub', 'txt', 'md'],
            help="Supported formats: PDF, DOCX, EPUB, TXT, MD"
        )
        
        if uploaded_file is not None:
            if st.button("Ingest Document"):
                with st.spinner("Ingesting document..."):
                    try:
                        # Save uploaded file temporarily
                        temp_path = f"/tmp/{uploaded_file.name}"
                        with open(temp_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        
                        # Ingest document
                        ingestor = DocumentIngestor()
                        metadata, chunks = asyncio.run(ingestor.ingest_document(temp_path))
                        
                        # Store in memory
                        chunk_ids = asyncio.run(
                            st.session_state.gui_manager.memory_manager.store_document_chunks(
                                metadata, chunks, "gui_user"
                            )
                        )
                        
                        st.success(f"✅ Ingested {uploaded_file.name}")
                        st.info(f"Chunks: {len(chunks)}, Words: {sum(c.word_count for c in chunks)}")
                        
                        # Clean up temp file
                        os.remove(temp_path)
                        
                    except Exception as e:
                        st.error(f"❌ Failed to ingest document: {e}")
    
    with tab2:
        st.markdown("### Ingest Directory")
        
        directory_path = st.text_input(
            "Directory Path",
            help="Path to directory containing documents"
        )
        
        if st.button("Ingest Directory") and directory_path:
            with st.spinner("Ingesting directory..."):
                try:
                    ingestor = DocumentIngestor()
                    results = asyncio.run(ingestor.ingest_directory(directory_path))
                    
                    total_chunks = 0
                    total_words = 0
                    
                    for metadata, chunks in results:
                        chunk_ids = asyncio.run(
                            st.session_state.gui_manager.memory_manager.store_document_chunks(
                                metadata, chunks, "gui_user"
                            )
                        )
                        total_chunks += len(chunks)
                        total_words += sum(c.word_count for c in chunks)
                    
                    st.success(f"✅ Ingested {len(results)} documents")
                    st.info(f"Total chunks: {total_chunks}, Total words: {total_words}")
                    
                except Exception as e:
                    st.error(f"❌ Failed to ingest directory: {e}")


def show_research_page():
    """Display the research page."""
    st.markdown("## Research Management")
    
    tab1, tab2 = st.tabs(["Start Research", "Research Status"])
    
    with tab1:
        st.markdown("### Start New Research")
        
        with st.form("research_form"):
            topic = st.text_input("Research Topic", help="What do you want to research?")
            description = st.text_area("Description", help="Detailed description of the research")
            keywords = st.text_input("Keywords", help="Comma-separated keywords")
            priority = st.slider("Priority", 1, 10, 5, help="Research priority (1-10)")
            
            submitted = st.form_submit_button("Start Research")
            
            if submitted and topic:
                with st.spinner("Starting research..."):
                    try:
                        topic_id = asyncio.run(
                            st.session_state.gui_manager.research_agent.start_research(
                                topic_title=topic,
                                description=description or f"Research on {topic}",
                                keywords=keywords.split(',') if keywords else [],
                                priority=priority
                            )
                        )
                        
                        st.success(f"✅ Started research: {topic}")
                        st.info(f"Topic ID: {topic_id}")
                        
                    except Exception as e:
                        st.error(f"❌ Failed to start research: {e}")
    
    with tab2:
        st.markdown("### Research Status")
        
        # Get active research topics
        try:
            topics = asyncio.run(st.session_state.gui_manager.research_agent.get_active_topics())
            
            if topics:
                for topic in topics:
                    with st.expander(f"{topic.title} ({topic.status})"):
                        st.write(f"**Description:** {topic.description}")
                        st.write(f"**Keywords:** {', '.join(topic.keywords)}")
                        st.write(f"**Priority:** {topic.priority}")
                        st.write(f"**Created:** {topic.created_at}")
                        
                        if topic.status == "completed":
                            # Show research summary
                            summary = asyncio.run(
                                st.session_state.gui_manager.research_agent.get_research_summary(topic.topic_id)
                            )
                            if summary:
                                st.write("**Summary:**")
                                st.write(summary.overview)
                                
                                if summary.key_findings:
                                    st.write("**Key Findings:**")
                                    for finding in summary.key_findings:
                                        st.write(f"- {finding}")
            else:
                st.info("No active research topics")
                
        except Exception as e:
            st.error(f"❌ Failed to get research status: {e}")


def show_book_management_page():
    """Display the book management page."""
    st.markdown("## Book Management")
    
    tab1, tab2, tab3 = st.tabs(["Create Book", "Book Status", "Export Book"])
    
    with tab1:
        st.markdown("### Create New Book")
        
        with st.form("book_form"):
            title = st.text_input("Book Title")
            author = st.text_input("Author")
            description = st.text_area("Description")
            audience = st.selectbox("Target Audience", ["general", "academic", "technical", "beginner", "expert"])
            word_count = st.number_input("Estimated Word Count", min_value=1000, value=50000, step=1000)
            
            submitted = st.form_submit_button("Create Book")
            
            if submitted and title and author:
                with st.spinner("Creating book..."):
                    try:
                        book_id = asyncio.run(
                            st.session_state.gui_manager.book_builder.create_book(
                                title=title,
                                author=author,
                                description=description,
                                target_audience=audience,
                                estimated_word_count=word_count
                            )
                        )
                        
                        st.success(f"✅ Created book: {title}")
                        st.info(f"Book ID: {book_id}")
                        
                    except Exception as e:
                        st.error(f"❌ Failed to create book: {e}")
    
    with tab2:
        st.markdown("### Book Status")
        
        # Get book status
        try:
            # This would need to be implemented to get all books
            st.info("Book status monitoring will be implemented here")
            
        except Exception as e:
            st.error(f"❌ Failed to get book status: {e}")
    
    with tab3:
        st.markdown("### Export Book")
        
        book_id = st.text_input("Book ID", help="Enter the book ID to export")
        export_format = st.selectbox("Export Format", ["markdown", "docx", "pdf"])
        include_bibliography = st.checkbox("Include Bibliography", value=True)
        
        if st.button("Export Book") and book_id:
            with st.spinner("Exporting book..."):
                try:
                    output_path = asyncio.run(
                        st.session_state.gui_manager.book_builder.export_book(
                            book_id=book_id,
                            format=export_format,
                            include_bibliography=include_bibliography
                        )
                    )
                    
                    st.success(f"✅ Book exported successfully!")
                    st.info(f"Output: {output_path}")
                    
                except Exception as e:
                    st.error(f"❌ Failed to export book: {e}")


def show_tools_page():
    """Display the tools page."""
    st.markdown("## Tool Management")
    
    tab1, tab2 = st.tabs(["Available Tools", "Execute Tool"])
    
    with tab1:
        st.markdown("### Available Tools")
        
        try:
            tools = asyncio.run(st.session_state.gui_manager.tool_agent.get_available_tools())
            
            if tools:
                for tool in tools:
                    with st.expander(f"{tool.tool_name} ({tool.category})"):
                        st.write(f"**Description:** {tool.description}")
                        st.write(f"**Parameters:** {tool.parameters}")
                        
                        if tool.examples:
                            st.write("**Examples:**")
                            for example in tool.examples:
                                st.write(f"- {example['description']}")
                                st.code(f"Parameters: {example['parameters']}")
            else:
                st.info("No tools available")
                
        except Exception as e:
            st.error(f"❌ Failed to get tools: {e}")
    
    with tab2:
        st.markdown("### Execute Tool")
        
        tool_name = st.selectbox(
            "Select Tool",
            options=[tool.tool_name for tool in asyncio.run(st.session_state.gui_manager.tool_agent.get_available_tools())]
        )
        
        if tool_name:
            st.write(f"Executing: {tool_name}")
            # Tool execution interface would be implemented here


def show_status_page():
    """Display the system status page."""
    st.markdown("## System Status")
    
    if not st.session_state.gui_manager.system_initialized:
        st.error("❌ System not initialized")
        return
    
    # System overview
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        memory_stats = st.session_state.gui_manager.memory_manager.get_stats()
        st.metric("Memory Chunks", memory_stats['total_chunks'])
    
    with col2:
        agent_stats = st.session_state.gui_manager.agent_manager.get_stats()
        st.metric("Total Agents", agent_stats['total_agents'])
    
    with col3:
        tool_stats = st.session_state.gui_manager.tool_manager.get_execution_stats()
        st.metric("Available Tools", tool_stats['available_tools'])
    
    with col4:
        st.metric("Running Tasks", agent_stats['running_tasks'])
    
    # Detailed status
    st.markdown("### Detailed Status")
    
    # Agent status
    st.markdown("#### Agent Status")
    agent_df = pd.DataFrame([
        {"Agent": "Research", "Status": "Active", "Tasks": 0},
        {"Agent": "Writer", "Status": "Active", "Tasks": 0},
        {"Agent": "Editor", "Status": "Active", "Tasks": 0},
        {"Agent": "Tool", "Status": "Active", "Tasks": 0}
    ])
    st.dataframe(agent_df, use_container_width=True)
    
    # Tool execution stats
    st.markdown("#### Tool Execution Statistics")
    try:
        tool_stats = asyncio.run(st.session_state.gui_manager.tool_agent.get_execution_stats())
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Total Executions", tool_stats['total_executions'])
            st.metric("Success Rate", f"{tool_stats['success_rate']:.1%}")
        
        with col2:
            st.metric("Failed Executions", tool_stats['failed_executions'])
            st.metric("Avg Execution Time", f"{tool_stats['average_execution_time']:.2f}s")
        
    except Exception as e:
        st.error(f"❌ Failed to get tool stats: {e}")


if __name__ == "__main__":
    main()