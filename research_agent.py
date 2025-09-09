"""
Research Agent Module

Performs autonomous research and generates structured summaries.
Uses RAG and web search to gather information for book writing.

Chosen libraries:
- asyncio: Asynchronous research operations
- pydantic: Data validation and type safety
- logging: Research activity logging

Adapted from: maowrag-unlimited-ai-agent (https://github.com/buithanhdam/maowrag-unlimited-ai-agent)
Pattern: Advanced RAG techniques with web search integration
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

import pydantic

logger = logging.getLogger(__name__)


class ResearchTopic(pydantic.BaseModel):
    """Model for research topics."""
    topic_id: str
    title: str
    description: str
    keywords: List[str] = []
    priority: int = 1
    status: str = "pending"  # pending, in_progress, completed, failed
    created_at: datetime
    completed_at: Optional[datetime] = None


class ResearchResult(pydantic.BaseModel):
    """Model for research results."""
    result_id: str
    topic_id: str
    source_type: str  # web, document, memory
    source_url: Optional[str] = None
    source_title: str
    content: str
    relevance_score: float
    confidence_score: float
    summary: str
    key_points: List[str] = []
    citations: List[str] = []
    created_at: datetime


class ResearchSummary(pydantic.BaseModel):
    """Model for research summaries."""
    summary_id: str
    topic_id: str
    title: str
    overview: str
    key_findings: List[str] = []
    sources: List[Dict[str, str]] = []
    recommendations: List[str] = []
    gaps: List[str] = []
    created_at: datetime


class ResearchAgent:
    """
    Autonomous research agent for gathering information.
    
    Responsibilities:
    - Conduct research on specified topics
    - Use RAG to retrieve relevant information from memory
    - Perform web searches for additional information
    - Generate structured summaries and insights
    - Identify knowledge gaps and research needs
    """
    
    def __init__(
        self,
        agent_id: str,
        memory_manager: Any,
        llm_client: Any,
        tool_manager: Any,
        max_web_results: int = 10,
        max_memory_results: int = 20
    ):
        """
        Initialize the research agent.
        
        Args:
            agent_id: Unique agent identifier
            memory_manager: Memory manager for RAG operations
            llm_client: LLM client for text generation
            tool_manager: Tool manager for web search and other tools
            max_web_results: Maximum web search results to process
            max_memory_results: Maximum memory retrieval results
        """
        self.agent_id = agent_id
        self.memory_manager = memory_manager
        self.llm_client = llm_client
        self.tool_manager = tool_manager
        self.max_web_results = max_web_results
        self.max_memory_results = max_memory_results
        
        # Research state
        self.active_topics: Dict[str, ResearchTopic] = {}
        self.research_results: Dict[str, List[ResearchResult]] = {}
        self.research_summaries: Dict[str, ResearchSummary] = {}
        
        logger.info(f"Research agent {agent_id} initialized")
    
    async def start_research(
        self,
        topic_title: str,
        description: str,
        keywords: List[str] = None,
        priority: int = 1
    ) -> str:
        """
        Start research on a new topic.
        
        Args:
            topic_title: Title of the research topic
            description: Description of what to research
            keywords: Keywords for the research
            priority: Research priority (1-10)
            
        Returns:
            Topic ID
        """
        topic_id = f"topic_{self.agent_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        topic = ResearchTopic(
            topic_id=topic_id,
            title=topic_title,
            description=description,
            keywords=keywords or [],
            priority=priority,
            created_at=datetime.now()
        )
        
        self.active_topics[topic_id] = topic
        
        # Start research process
        asyncio.create_task(self._conduct_research(topic_id))
        
        logger.info(f"Started research on topic: {topic_title}")
        return topic_id
    
    async def _conduct_research(self, topic_id: str):
        """Conduct research on a topic."""
        topic = self.active_topics.get(topic_id)
        if not topic:
            return
        
        try:
            topic.status = "in_progress"
            
            # Step 1: Memory-based research using RAG
            memory_results = await self._research_from_memory(topic)
            
            # Step 2: Web-based research
            web_results = await self._research_from_web(topic)
            
            # Step 3: Process and analyze results
            all_results = memory_results + web_results
            processed_results = await self._process_research_results(topic, all_results)
            
            # Step 4: Generate summary
            summary = await self._generate_research_summary(topic, processed_results)
            
            # Store results
            self.research_results[topic_id] = processed_results
            self.research_summaries[topic_id] = summary
            
            # Update topic status
            topic.status = "completed"
            topic.completed_at = datetime.now()
            
            logger.info(f"Completed research on topic: {topic.title}")
            
        except Exception as e:
            topic.status = "failed"
            logger.error(f"Research failed for topic {topic_id}: {e}")
    
    async def _research_from_memory(self, topic: ResearchTopic) -> List[ResearchResult]:
        """Research using memory/RAG."""
        results = []
        
        try:
            # Create search query
            query = f"{topic.title} {topic.description} {' '.join(topic.keywords)}"
            
            # Retrieve relevant chunks
            retrieval_results = await self.memory_manager.retrieve_relevant_chunks(
                query=query,
                top_k=self.max_memory_results
            )
            
            # Process each result
            for i, result in enumerate(retrieval_results):
                research_result = ResearchResult(
                    result_id=f"memory_{topic.topic_id}_{i}",
                    topic_id=topic.topic_id,
                    source_type="memory",
                    source_title=result.metadata.get("original_filename", "Unknown"),
                    content=result.content,
                    relevance_score=result.score,
                    confidence_score=result.score * 0.9,  # Slightly lower confidence for memory
                    summary=await self._summarize_content(result.content),
                    key_points=await self._extract_key_points(result.content),
                    citations=[result.chunk_id],
                    created_at=datetime.now()
                )
                results.append(research_result)
            
            logger.info(f"Retrieved {len(results)} results from memory for topic: {topic.title}")
            
        except Exception as e:
            logger.error(f"Memory research failed for topic {topic.topic_id}: {e}")
        
        return results
    
    async def _research_from_web(self, topic: ResearchTopic) -> List[ResearchResult]:
        """Research using web search."""
        results = []
        
        try:
            # Create search queries
            queries = [
                f"{topic.title} {topic.description}",
                f"{' '.join(topic.keywords)}",
                f"{topic.title} research findings"
            ]
            
            for query in queries:
                # Use web search tool
                search_request = {
                    "tool_name": "web_search",
                    "args": {"query": query},
                    "request_id": f"search_{topic.topic_id}_{datetime.now().strftime('%H%M%S')}",
                    "agent_id": self.agent_id
                }
                
                response = await self.tool_manager.execute_tool(search_request)
                
                if response.status == "success" and response.output:
                    search_data = response.output
                    
                    # Process search results
                    for i, result in enumerate(search_data.get("results", [])[:self.max_web_results]):
                        research_result = ResearchResult(
                            result_id=f"web_{topic.topic_id}_{i}",
                            topic_id=topic.topic_id,
                            source_type="web",
                            source_url=result.get("url", ""),
                            source_title=result.get("title", "Unknown"),
                            content=result.get("snippet", ""),
                            relevance_score=0.8,  # Default relevance for web results
                            confidence_score=0.7,  # Lower confidence for web results
                            summary=await self._summarize_content(result.get("snippet", "")),
                            key_points=await self._extract_key_points(result.get("snippet", "")),
                            citations=[result.get("url", "")],
                            created_at=datetime.now()
                        )
                        results.append(research_result)
            
            logger.info(f"Retrieved {len(results)} results from web for topic: {topic.title}")
            
        except Exception as e:
            logger.error(f"Web research failed for topic {topic.topic_id}: {e}")
        
        return results
    
    async def _process_research_results(
        self,
        topic: ResearchTopic,
        results: List[ResearchResult]
    ) -> List[ResearchResult]:
        """Process and analyze research results."""
        if not results:
            return results
        
        # Sort by relevance and confidence
        results.sort(key=lambda x: (x.relevance_score + x.confidence_score) / 2, reverse=True)
        
        # Remove duplicates based on content similarity
        unique_results = []
        seen_content = set()
        
        for result in results:
            content_hash = hash(result.content[:100])  # Use first 100 chars as fingerprint
            if content_hash not in seen_content:
                unique_results.append(result)
                seen_content.add(content_hash)
        
        # Limit results
        processed_results = unique_results[:self.max_web_results + self.max_memory_results]
        
        logger.info(f"Processed {len(processed_results)} unique results for topic: {topic.title}")
        return processed_results
    
    async def _generate_research_summary(
        self,
        topic: ResearchTopic,
        results: List[ResearchResult]
    ) -> ResearchSummary:
        """Generate a comprehensive research summary."""
        if not results:
            return ResearchSummary(
                summary_id=f"summary_{topic.topic_id}",
                topic_id=topic.topic_id,
                title=topic.title,
                overview="No research results found.",
                created_at=datetime.now()
            )
        
        # Prepare content for LLM
        content_parts = [f"Research Topic: {topic.title}\nDescription: {topic.description}\n\n"]
        
        for i, result in enumerate(results[:10]):  # Limit to top 10 results
            content_parts.append(f"Source {i+1}: {result.source_title}\n{result.content}\n")
        
        research_content = "\n".join(content_parts)
        
        # Generate summary using LLM
        prompt = f"""
        Based on the following research results, create a comprehensive summary for the topic: {topic.title}
        
        Research Content:
        {research_content}
        
        Please provide:
        1. A clear overview of the findings
        2. Key findings and insights
        3. Source recommendations
        4. Research gaps or areas needing more investigation
        5. Recommendations for further research
        
        Format your response as a structured summary.
        """
        
        try:
            response = await self.llm_client.generate(
                prompt=prompt,
                max_tokens=1500,
                temperature=0.3
            )
            
            # Parse the response (simplified parsing)
            summary_text = response.content
            
            # Extract key components (simplified extraction)
            key_findings = await self._extract_key_findings(summary_text)
            recommendations = await self._extract_recommendations(summary_text)
            gaps = await self._identify_gaps(summary_text)
            
            # Prepare sources
            sources = []
            for result in results[:5]:  # Top 5 sources
                sources.append({
                    "title": result.source_title,
                    "url": result.source_url or "",
                    "type": result.source_type,
                    "relevance": result.relevance_score
                })
            
            summary = ResearchSummary(
                summary_id=f"summary_{topic.topic_id}",
                topic_id=topic.topic_id,
                title=topic.title,
                overview=summary_text,
                key_findings=key_findings,
                sources=sources,
                recommendations=recommendations,
                gaps=gaps,
                created_at=datetime.now()
            )
            
            # Store in memory for future reference
            await self.memory_manager.add_agent_notes(
                content=summary_text,
                agent_id=self.agent_id,
                tags=[topic.title, "research_summary"],
                provenance_notes=f"Research summary for topic: {topic.title}"
            )
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to generate research summary: {e}")
            return ResearchSummary(
                summary_id=f"summary_{topic.topic_id}",
                topic_id=topic.topic_id,
                title=topic.title,
                overview="Failed to generate summary due to LLM error.",
                created_at=datetime.now()
            )
    
    async def _summarize_content(self, content: str) -> str:
        """Generate a brief summary of content."""
        if len(content) < 100:
            return content
        
        try:
            prompt = f"Summarize the following content in 2-3 sentences:\n\n{content[:500]}"
            response = await self.llm_client.generate(
                prompt=prompt,
                max_tokens=100,
                temperature=0.3
            )
            return response.content
        except Exception as e:
            logger.warning(f"Failed to summarize content: {e}")
            return content[:200] + "..."
    
    async def _extract_key_points(self, content: str) -> List[str]:
        """Extract key points from content."""
        try:
            prompt = f"Extract 3-5 key points from the following content:\n\n{content[:500]}"
            response = await self.llm_client.generate(
                prompt=prompt,
                max_tokens=200,
                temperature=0.3
            )
            
            # Simple parsing of key points
            points = []
            for line in response.content.split('\n'):
                line = line.strip()
                if line and (line.startswith('-') or line.startswith('•') or line.startswith('*')):
                    points.append(line[1:].strip())
                elif line and line[0].isdigit():
                    points.append(line)
            
            return points[:5]  # Limit to 5 points
        except Exception as e:
            logger.warning(f"Failed to extract key points: {e}")
            return []
    
    async def _extract_key_findings(self, summary_text: str) -> List[str]:
        """Extract key findings from summary text."""
        try:
            prompt = f"Extract the key findings from this research summary:\n\n{summary_text}"
            response = await self.llm_client.generate(
                prompt=prompt,
                max_tokens=300,
                temperature=0.3
            )
            
            findings = []
            for line in response.content.split('\n'):
                line = line.strip()
                if line and (line.startswith('-') or line.startswith('•') or line.startswith('*')):
                    findings.append(line[1:].strip())
            
            return findings[:10]  # Limit to 10 findings
        except Exception as e:
            logger.warning(f"Failed to extract key findings: {e}")
            return []
    
    async def _extract_recommendations(self, summary_text: str) -> List[str]:
        """Extract recommendations from summary text."""
        try:
            prompt = f"Extract recommendations from this research summary:\n\n{summary_text}"
            response = await self.llm_client.generate(
                prompt=prompt,
                max_tokens=200,
                temperature=0.3
            )
            
            recommendations = []
            for line in response.content.split('\n'):
                line = line.strip()
                if line and (line.startswith('-') or line.startswith('•') or line.startswith('*')):
                    recommendations.append(line[1:].strip())
            
            return recommendations[:5]  # Limit to 5 recommendations
        except Exception as e:
            logger.warning(f"Failed to extract recommendations: {e}")
            return []
    
    async def _identify_gaps(self, summary_text: str) -> List[str]:
        """Identify research gaps from summary text."""
        try:
            prompt = f"Identify research gaps or areas needing more investigation from this summary:\n\n{summary_text}"
            response = await self.llm_client.generate(
                prompt=prompt,
                max_tokens=200,
                temperature=0.3
            )
            
            gaps = []
            for line in response.content.split('\n'):
                line = line.strip()
                if line and (line.startswith('-') or line.startswith('•') or line.startswith('*')):
                    gaps.append(line[1:].strip())
            
            return gaps[:5]  # Limit to 5 gaps
        except Exception as e:
            logger.warning(f"Failed to identify gaps: {e}")
            return []
    
    async def get_research_summary(self, topic_id: str) -> Optional[ResearchSummary]:
        """Get research summary for a topic."""
        return self.research_summaries.get(topic_id)
    
    async def get_research_results(self, topic_id: str) -> List[ResearchResult]:
        """Get research results for a topic."""
        return self.research_results.get(topic_id, [])
    
    async def get_active_topics(self) -> List[ResearchTopic]:
        """Get all active research topics."""
        return list(self.active_topics.values())
    
    async def execute_task(self, task_type: str, payload: Dict[str, Any]) -> Any:
        """Execute a research task."""
        if task_type == "start_research":
            return await self.start_research(
                topic_title=payload.get("title", ""),
                description=payload.get("description", ""),
                keywords=payload.get("keywords", []),
                priority=payload.get("priority", 1)
            )
        elif task_type == "get_summary":
            topic_id = payload.get("topic_id")
            return await self.get_research_summary(topic_id)
        elif task_type == "get_results":
            topic_id = payload.get("topic_id")
            return await self.get_research_results(topic_id)
        else:
            raise ValueError(f"Unknown task type: {task_type}")