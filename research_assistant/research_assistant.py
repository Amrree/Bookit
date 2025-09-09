"""
Research Assistant Module

Provides AI-powered research capabilities including web search,
fact-checking, source verification, and citation management.

Features:
- Web search integration
- Academic paper analysis
- Fact-checking and verification
- Source citation management
- Research note organization
- Automated source validation
"""

import asyncio
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import logging

import pydantic
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class Source(pydantic.BaseModel):
    """Research source model."""
    source_id: str
    title: str
    url: str
    domain: str
    author: Optional[str] = None
    publication_date: Optional[datetime] = None
    content: str
    summary: str
    credibility_score: float = 0.0
    source_type: str = "web"  # web, academic, news, blog, etc.
    metadata: Dict[str, Any] = {}


class Citation(pydantic.BaseModel):
    """Citation model."""
    citation_id: str
    source_id: str
    text: str
    page_number: Optional[int] = None
    quote: Optional[str] = None
    citation_style: str = "apa"  # apa, mla, chicago, etc.
    created_at: datetime


class ResearchResult(pydantic.BaseModel):
    """Research result model."""
    query: str
    sources: List[Source]
    summary: str
    key_findings: List[str]
    credibility_score: float
    research_notes: List[str] = []
    created_at: datetime
    updated_at: datetime


class ResearchAssistant:
    """
    AI-powered research assistant for book generation.
    
    Features:
    - Web search integration
    - Academic paper analysis
    - Fact-checking and verification
    - Source citation management
    - Research note organization
    """
    
    def __init__(self, research_dir: str = "./output/research"):
        """
        Initialize research assistant.
        
        Args:
            research_dir: Directory for storing research data
        """
        self.research_dir = Path(research_dir)
        self.sources_dir = self.research_dir / "sources"
        self.citations_dir = self.research_dir / "citations"
        self.notes_dir = self.research_dir / "notes"
        
        # Create directories
        for directory in [self.research_dir, self.sources_dir, self.citations_dir, self.notes_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        # Search engines configuration
        self.search_engines = {
            "google": self._search_google,
            "bing": self._search_bing,
            "duckduckgo": self._search_duckduckgo
        }
        
        logger.info(f"Research assistant initialized with directory: {self.research_dir}")
    
    async def research_topic(self, topic: str, depth: str = "medium", 
                           max_sources: int = 10) -> ResearchResult:
        """
        Research a topic comprehensively.
        
        Args:
            topic: Research topic
            depth: Research depth (shallow, medium, deep)
            max_sources: Maximum number of sources to collect
            
        Returns:
            Research result with sources and findings
        """
        logger.info(f"Starting research on topic: {topic}")
        
        # Determine search queries based on depth
        queries = self._generate_search_queries(topic, depth)
        
        # Collect sources from multiple search engines
        all_sources = []
        for query in queries:
            sources = await self._search_multiple_engines(query, max_sources // len(queries))
            all_sources.extend(sources)
        
        # Remove duplicates and rank by credibility
        unique_sources = self._deduplicate_sources(all_sources)
        ranked_sources = self._rank_sources_by_credibility(unique_sources)
        
        # Take top sources
        selected_sources = ranked_sources[:max_sources]
        
        # Generate summary and key findings
        summary = await self._generate_research_summary(selected_sources, topic)
        key_findings = await self._extract_key_findings(selected_sources, topic)
        
        # Calculate overall credibility score
        credibility_score = sum(source.credibility_score for source in selected_sources) / len(selected_sources) if selected_sources else 0.0
        
        # Create research result
        result = ResearchResult(
            query=topic,
            sources=selected_sources,
            summary=summary,
            key_findings=key_findings,
            credibility_score=credibility_score,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Save research result
        await self._save_research_result(result)
        
        logger.info(f"Research completed: {len(selected_sources)} sources, credibility: {credibility_score:.2f}")
        
        return result
    
    async def fact_check(self, claim: str, context: str = "") -> Dict[str, Any]:
        """
        Fact-check a specific claim.
        
        Args:
            claim: Claim to fact-check
            context: Additional context
            
        Returns:
            Fact-checking result
        """
        logger.info(f"Fact-checking claim: {claim}")
        
        # Search for evidence
        search_query = f'"{claim}" fact check verification'
        sources = await self._search_multiple_engines(search_query, 5)
        
        # Analyze sources for fact-checking
        fact_check_result = {
            "claim": claim,
            "context": context,
            "sources": sources,
            "verification_status": "unverified",  # verified, disputed, unverified
            "confidence_score": 0.0,
            "evidence": [],
            "contradictions": [],
            "recommendations": []
        }
        
        # Analyze each source
        for source in sources:
            if "fact" in source.content.lower() or "verify" in source.content.lower():
                fact_check_result["evidence"].append({
                    "source": source.title,
                    "url": source.url,
                    "content": source.content[:200] + "...",
                    "credibility": source.credibility_score
                })
        
        # Determine verification status
        if len(fact_check_result["evidence"]) >= 3:
            fact_check_result["verification_status"] = "verified"
            fact_check_result["confidence_score"] = 0.8
        elif len(fact_check_result["evidence"]) >= 1:
            fact_check_result["verification_status"] = "partially_verified"
            fact_check_result["confidence_score"] = 0.5
        else:
            fact_check_result["verification_status"] = "unverified"
            fact_check_result["confidence_score"] = 0.1
        
        return fact_check_result
    
    async def find_academic_sources(self, topic: str, max_sources: int = 5) -> List[Source]:
        """
        Find academic sources for a topic.
        
        Args:
            topic: Research topic
            max_sources: Maximum number of sources
            
        Returns:
            List of academic sources
        """
        logger.info(f"Finding academic sources for: {topic}")
        
        # Search for academic sources
        academic_queries = [
            f"{topic} site:scholar.google.com",
            f"{topic} site:arxiv.org",
            f"{topic} site:jstor.org",
            f"{topic} site:pubmed.ncbi.nlm.nih.gov",
            f"{topic} filetype:pdf"
        ]
        
        academic_sources = []
        for query in academic_queries:
            sources = await self._search_multiple_engines(query, max_sources // len(academic_queries))
            academic_sources.extend(sources)
        
        # Filter and rank academic sources
        academic_sources = [s for s in academic_sources if self._is_academic_source(s)]
        academic_sources = self._rank_sources_by_credibility(academic_sources)
        
        return academic_sources[:max_sources]
    
    def create_citation(self, source: Source, text: str, quote: Optional[str] = None,
                       citation_style: str = "apa") -> Citation:
        """
        Create a citation for a source.
        
        Args:
            source: Source to cite
            text: Text being cited
            quote: Direct quote (optional)
            citation_style: Citation style (apa, mla, chicago)
            
        Returns:
            Citation object
        """
        citation_id = f"cite_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        citation = Citation(
            citation_id=citation_id,
            source_id=source.source_id,
            text=text,
            quote=quote,
            citation_style=citation_style,
            created_at=datetime.now()
        )
        
        # Save citation
        self._save_citation(citation)
        
        return citation
    
    def generate_bibliography(self, sources: List[Source], style: str = "apa") -> str:
        """
        Generate bibliography from sources.
        
        Args:
            sources: List of sources
            style: Citation style
            
        Returns:
            Formatted bibliography
        """
        bibliography = []
        
        for source in sources:
            if style == "apa":
                bib_entry = self._format_apa_citation(source)
            elif style == "mla":
                bib_entry = self._format_mla_citation(source)
            elif style == "chicago":
                bib_entry = self._format_chicago_citation(source)
            else:
                bib_entry = self._format_apa_citation(source)
            
            bibliography.append(bib_entry)
        
        return "\n\n".join(bibliography)
    
    def _generate_search_queries(self, topic: str, depth: str) -> List[str]:
        """Generate search queries based on topic and depth."""
        base_queries = [topic]
        
        if depth == "shallow":
            return base_queries
        elif depth == "medium":
            return base_queries + [
                f"{topic} overview",
                f"{topic} guide",
                f"{topic} explanation"
            ]
        else:  # deep
            return base_queries + [
                f"{topic} overview",
                f"{topic} guide",
                f"{topic} explanation",
                f"{topic} research",
                f"{topic} analysis",
                f"{topic} study",
                f"{topic} report",
                f"{topic} statistics"
            ]
    
    async def _search_multiple_engines(self, query: str, max_results: int) -> List[Source]:
        """Search multiple engines and combine results."""
        all_sources = []
        
        for engine_name, search_func in self.search_engines.items():
            try:
                sources = await search_func(query, max_results // len(self.search_engines))
                all_sources.extend(sources)
            except Exception as e:
                logger.warning(f"Search engine {engine_name} failed: {e}")
                continue
        
        return all_sources
    
    async def _search_google(self, query: str, max_results: int) -> List[Source]:
        """Search Google (placeholder implementation)."""
        # This is a placeholder - in a real implementation, you would use Google Custom Search API
        logger.info(f"Searching Google for: {query}")
        return []
    
    async def _search_bing(self, query: str, max_results: int) -> List[Source]:
        """Search Bing (placeholder implementation)."""
        # This is a placeholder - in a real implementation, you would use Bing Search API
        logger.info(f"Searching Bing for: {query}")
        return []
    
    async def _search_duckduckgo(self, query: str, max_results: int) -> List[Source]:
        """Search DuckDuckGo (placeholder implementation)."""
        # This is a placeholder - in a real implementation, you would use DuckDuckGo API
        logger.info(f"Searching DuckDuckGo for: {query}")
        return []
    
    def _deduplicate_sources(self, sources: List[Source]) -> List[Source]:
        """Remove duplicate sources based on URL."""
        seen_urls = set()
        unique_sources = []
        
        for source in sources:
            if source.url not in seen_urls:
                seen_urls.add(source.url)
                unique_sources.append(source)
        
        return unique_sources
    
    def _rank_sources_by_credibility(self, sources: List[Source]) -> List[Source]:
        """Rank sources by credibility score."""
        return sorted(sources, key=lambda s: s.credibility_score, reverse=True)
    
    def _is_academic_source(self, source: Source) -> bool:
        """Check if source is academic."""
        academic_domains = [
            "scholar.google.com",
            "arxiv.org",
            "jstor.org",
            "pubmed.ncbi.nlm.nih.gov",
            "academia.edu",
            "researchgate.net"
        ]
        
        return any(domain in source.domain for domain in academic_domains)
    
    async def _generate_research_summary(self, sources: List[Source], topic: str) -> str:
        """Generate research summary from sources."""
        if not sources:
            return f"No sources found for topic: {topic}"
        
        # Extract key information from sources
        key_points = []
        for source in sources[:5]:  # Use top 5 sources
            key_points.append(f"- {source.title}: {source.summary}")
        
        summary = f"Research Summary for '{topic}':\n\n"
        summary += f"Found {len(sources)} sources with average credibility score of {sum(s.credibility_score for s in sources) / len(sources):.2f}.\n\n"
        summary += "Key findings:\n" + "\n".join(key_points)
        
        return summary
    
    async def _extract_key_findings(self, sources: List[Source], topic: str) -> List[str]:
        """Extract key findings from sources."""
        findings = []
        
        for source in sources[:3]:  # Use top 3 sources
            # Simple extraction - in a real implementation, you would use NLP
            sentences = source.content.split('.')
            for sentence in sentences:
                if topic.lower() in sentence.lower() and len(sentence) > 20:
                    findings.append(sentence.strip())
                    if len(findings) >= 5:
                        break
        
        return findings[:5]
    
    async def _save_research_result(self, result: ResearchResult):
        """Save research result to file."""
        result_path = self.research_dir / f"research_{result.query.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(result_path, 'w', encoding='utf-8') as f:
            json.dump(result.dict(), f, indent=2, default=str)
    
    def _save_citation(self, citation: Citation):
        """Save citation to file."""
        citation_path = self.citations_dir / f"{citation.citation_id}.json"
        
        with open(citation_path, 'w', encoding='utf-8') as f:
            json.dump(citation.dict(), f, indent=2, default=str)
    
    def _format_apa_citation(self, source: Source) -> str:
        """Format citation in APA style."""
        if source.author:
            return f"{source.author}. ({source.publication_date.year if source.publication_date else 'n.d.'}). {source.title}. Retrieved from {source.url}"
        else:
            return f"{source.title}. ({source.publication_date.year if source.publication_date else 'n.d.'}). Retrieved from {source.url}"
    
    def _format_mla_citation(self, source: Source) -> str:
        """Format citation in MLA style."""
        if source.author:
            return f'"{source.title}." {source.domain}, {source.publication_date.year if source.publication_date else "n.d."}, {source.url}.'
        else:
            return f'"{source.title}." {source.domain}, {source.publication_date.year if source.publication_date else "n.d."}, {source.url}.'
    
    def _format_chicago_citation(self, source: Source) -> str:
        """Format citation in Chicago style."""
        if source.author:
            return f"{source.author}. \"{source.title}.\" {source.domain}. {source.publication_date.strftime('%B %d, %Y') if source.publication_date else 'n.d.'}. {source.url}."
        else:
            return f"\"{source.title}.\" {source.domain}. {source.publication_date.strftime('%B %d, %Y') if source.publication_date else 'n.d.'}. {source.url}."
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get research assistant statistics."""
        return {
            "total_sources": len(list(self.sources_dir.glob("*.json"))),
            "total_citations": len(list(self.citations_dir.glob("*.json"))),
            "total_research_notes": len(list(self.notes_dir.glob("*.json"))),
            "research_directory": str(self.research_dir)
        }