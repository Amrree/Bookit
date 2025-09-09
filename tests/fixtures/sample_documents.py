"""
Sample documents for testing the book-writing system.
"""
from pathlib import Path
import tempfile
import shutil


class SampleDocuments:
    """Sample documents for testing."""
    
    @staticmethod
    def create_sample_pdf(temp_dir: Path) -> Path:
        """Create a sample PDF document."""
        pdf_content = """
        # Introduction to Machine Learning
        
        Machine learning is a subset of artificial intelligence that focuses on algorithms
        that can learn from data. This document covers the fundamentals of ML including
        supervised learning, unsupervised learning, and reinforcement learning.
        
        ## Supervised Learning
        
        Supervised learning uses labeled training data to learn a mapping from inputs
        to outputs. Common algorithms include linear regression, decision trees, and
        neural networks.
        
        ## Unsupervised Learning
        
        Unsupervised learning finds patterns in data without labeled examples.
        Clustering and dimensionality reduction are common techniques.
        
        ## Reinforcement Learning
        
        Reinforcement learning involves an agent learning to make decisions by
        interacting with an environment and receiving rewards or penalties.
        """
        
        pdf_file = temp_dir / "sample_ml.pdf"
        pdf_file.write_text(pdf_content)
        return pdf_file
    
    @staticmethod
    def create_sample_markdown(temp_dir: Path) -> Path:
        """Create a sample Markdown document."""
        markdown_content = """
        # The Future of Artificial Intelligence
        
        Artificial intelligence is rapidly evolving and will shape our future in
        profound ways. This article explores the current state of AI and its
        potential impact on society.
        
        ## Current Applications
        
        AI is already being used in healthcare, finance, transportation, and
        many other industries. The technology is becoming more accessible
        and powerful every day.
        
        ## Ethical Considerations
        
        As AI becomes more powerful, we must consider the ethical implications
        of its use. Issues include bias, privacy, and the potential for misuse.
        
        ## Future Prospects
        
        The future of AI holds great promise but also significant challenges.
        We must work to ensure that AI benefits all of humanity.
        """
        
        md_file = temp_dir / "sample_ai.md"
        md_file.write_text(markdown_content)
        return md_file
    
    @staticmethod
    def create_sample_txt(temp_dir: Path) -> Path:
        """Create a sample TXT document."""
        txt_content = """
        Data Science Fundamentals
        
        Data science combines statistics, programming, and domain expertise to
        extract insights from data. It involves data collection, cleaning,
        analysis, and visualization.
        
        Key Skills:
        - Programming (Python, R)
        - Statistics and Mathematics
        - Machine Learning
        - Data Visualization
        - Domain Knowledge
        
        Tools and Technologies:
        - Python libraries (pandas, numpy, scikit-learn)
        - R programming language
        - SQL databases
        - Cloud platforms (AWS, GCP, Azure)
        
        Career Paths:
        - Data Analyst
        - Data Scientist
        - Machine Learning Engineer
        - Data Engineer
        """
        
        txt_file = temp_dir / "sample_ds.txt"
        txt_file.write_text(txt_content)
        return txt_file
    
    @staticmethod
    def create_sample_docx(temp_dir: Path) -> Path:
        """Create a sample DOCX document."""
        # For testing purposes, we'll create a simple text file
        # In a real implementation, this would be a proper DOCX file
        docx_content = """
        # Business Intelligence and Analytics
        
        Business intelligence (BI) and analytics are essential for modern organizations
        to make data-driven decisions. This document covers the key concepts and
        practices in BI and analytics.
        
        ## Data Warehousing
        
        Data warehouses are centralized repositories that store integrated data
        from multiple sources. They are designed for query and analysis rather
        than transaction processing.
        
        ## ETL Processes
        
        Extract, Transform, Load (ETL) processes are used to move data from
        source systems to the data warehouse. This involves data cleaning,
        transformation, and loading.
        
        ## Reporting and Visualization
        
        BI tools provide reporting and visualization capabilities to help
        users understand and analyze data. Common tools include Tableau,
        Power BI, and QlikView.
        """
        
        docx_file = temp_dir / "sample_bi.docx"
        docx_file.write_text(docx_content)
        return docx_file
    
    @staticmethod
    def create_sample_epub(temp_dir: Path) -> Path:
        """Create a sample EPUB document."""
        # For testing purposes, we'll create a simple text file
        # In a real implementation, this would be a proper EPUB file
        epub_content = """
        # Cloud Computing Fundamentals
        
        Cloud computing is the delivery of computing services over the internet.
        This document covers the essential concepts and technologies in cloud computing.
        
        ## Service Models
        
        Cloud computing offers three main service models:
        - Infrastructure as a Service (IaaS)
        - Platform as a Service (PaaS)
        - Software as a Service (SaaS)
        
        ## Deployment Models
        
        There are four main deployment models:
        - Public Cloud
        - Private Cloud
        - Hybrid Cloud
        - Community Cloud
        
        ## Key Benefits
        
        Cloud computing offers several benefits including:
        - Cost savings
        - Scalability
        - Flexibility
        - Reliability
        - Security
        """
        
        epub_file = temp_dir / "sample_cloud.epub"
        epub_file.write_text(epub_content)
        return epub_file
    
    @staticmethod
    def create_all_sample_documents(temp_dir: Path) -> dict:
        """Create all sample documents."""
        return {
            "pdf": SampleDocuments.create_sample_pdf(temp_dir),
            "markdown": SampleDocuments.create_sample_markdown(temp_dir),
            "txt": SampleDocuments.create_sample_txt(temp_dir),
            "docx": SampleDocuments.create_sample_docx(temp_dir),
            "epub": SampleDocuments.create_sample_epub(temp_dir)
        }


class TestDataGenerator:
    """Generate test data for various scenarios."""
    
    @staticmethod
    def generate_large_document(temp_dir: Path, size_mb: float = 1.0) -> Path:
        """Generate a large document for stress testing."""
        # Generate content to reach approximately the target size
        content = "This is a test document for stress testing. " * 1000
        target_size = int(size_mb * 1024 * 1024)  # Convert MB to bytes
        current_size = len(content.encode('utf-8'))
        
        # Repeat content to reach target size
        repetitions = max(1, target_size // current_size)
        large_content = content * repetitions
        
        large_file = temp_dir / f"large_document_{size_mb}mb.txt"
        large_file.write_text(large_content)
        return large_file
    
    @staticmethod
    def generate_multilingual_document(temp_dir: Path) -> Path:
        """Generate a multilingual document for testing."""
        multilingual_content = """
        # Multilingual Document
        
        English: This is a test document with multiple languages.
        Spanish: Este es un documento de prueba con múltiples idiomas.
        French: Ceci est un document de test avec plusieurs langues.
        German: Dies ist ein Testdokument mit mehreren Sprachen.
        Chinese: 这是一个包含多种语言的测试文档。
        Japanese: これは複数の言語を含むテスト文書です。
        Arabic: هذا مستند اختبار يحتوي على لغات متعددة.
        Russian: Это тестовый документ с несколькими языками.
        """
        
        multilingual_file = temp_dir / "multilingual_document.txt"
        multilingual_file.write_text(multilingual_content)
        return multilingual_file
    
    @staticmethod
    def generate_structured_document(temp_dir: Path) -> Path:
        """Generate a structured document with specific formatting."""
        structured_content = """
        # Structured Document
        
        ## Section 1: Introduction
        This is the introduction section with proper formatting.
        
        ### Subsection 1.1: Overview
        This is a subsection with detailed information.
        
        ### Subsection 1.2: Objectives
        The objectives of this document are:
        1. To provide comprehensive information
        2. To demonstrate proper structure
        3. To test parsing capabilities
        
        ## Section 2: Methodology
        This section describes the methodology used.
        
        ### Subsection 2.1: Data Collection
        Data collection methods include:
        - Surveys
        - Interviews
        - Observations
        - Document analysis
        
        ### Subsection 2.2: Analysis
        Analysis techniques include:
        - Statistical analysis
        - Qualitative analysis
        - Comparative analysis
        
        ## Section 3: Results
        This section presents the results.
        
        ### Subsection 3.1: Quantitative Results
        The quantitative results show significant findings.
        
        ### Subsection 3.2: Qualitative Results
        The qualitative results provide additional insights.
        
        ## Section 4: Conclusion
        This section concludes the document.
        
        ### Subsection 4.1: Summary
        A summary of the key findings.
        
        ### Subsection 4.2: Recommendations
        Recommendations for future work.
        """
        
        structured_file = temp_dir / "structured_document.txt"
        structured_file.write_text(structured_content)
        return structured_file
    
    @staticmethod
    def generate_corrupted_document(temp_dir: Path) -> Path:
        """Generate a corrupted document for error testing."""
        corrupted_content = """
        # Corrupted Document
        
        This document contains some corrupted content.
        
        ## Section 1: Normal Content
        This section contains normal, readable content.
        
        ## Section 2: Corrupted Content
        This section contains some corrupted characters: 
        
        ## Section 3: Mixed Content
        This section has both normal and corrupted content:  normal text 
        
        ## Section 4: Encoding Issues
        This section has encoding issues: â€œquoted textâ€
        """
        
        corrupted_file = temp_dir / "corrupted_document.txt"
        corrupted_file.write_text(corrupted_content)
        return corrupted_file