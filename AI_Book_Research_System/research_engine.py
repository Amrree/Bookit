#!/usr/bin/env python3
"""
AI Book Research Engine
Canonizes existing learning and code with research/write/expand/repeat cycle
Uses free APIs and AI for comprehensive research
"""

import argparse
import asyncio
import json
import logging
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import requests
import aiohttp

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AIResearchEngine:
    """AI-powered research engine for book content."""
    
    def __init__(self, project_dir: str, config_file: str):
        self.project_dir = Path(project_dir)
        self.config_file = Path(config_file)
        
        # Load configuration
        with open(self.config_file, 'r') as f:
            self.config = json.load(f)
        
        # Load project config
        self.project_config_file = self.project_dir / "config.json"
        with open(self.project_config_file, 'r') as f:
            self.project_config = json.load(f)
        
        # Research directories
        self.research_dir = self.project_dir / "research"
        self.research_dir.mkdir(exist_ok=True)
        
        # Initialize API clients
        self.setup_api_clients()
        
        # Research topics and themes
        self.research_themes = {
            "tarot": [
                "tarot history", "tarot symbolism", "tarot psychology", "tarot spirituality",
                "major arcana", "minor arcana", "court cards", "tarot spreads",
                "tarot reading", "tarot interpretation", "tarot tradition"
            ],
            "philosophy": [
                "existentialism", "stoicism", "buddhism", "taoism", "hermeticism",
                "neoplatonism", "pragmatism", "phenomenology", "metaphysics",
                "ethics", "epistemology", "consciousness studies"
            ],
            "psychology": [
                "jungian psychology", "archetypes", "collective unconscious", "individuation",
                "shadow work", "depth psychology", "transpersonal psychology",
                "cognitive psychology", "humanistic psychology", "positive psychology"
            ],
            "spirituality": [
                "mysticism", "meditation", "mindfulness", "contemplation", "prayer",
                "spiritual practice", "awakening", "enlightenment", "transcendence",
                "sacred texts", "spiritual traditions", "mystical experience"
            ],
            "literature": [
                "literary analysis", "narrative structure", "symbolic writing",
                "contemplative literature", "spiritual writing", "philosophical fiction",
                "poetry", "prose", "creative writing", "literary criticism"
            ]
        }
    
    def setup_api_clients(self):
        """Setup API clients for research."""
        self.api_clients = {}
        
        # OpenAI client (if enabled)
        if self.config["apis"]["openai"]["enabled"]:
            try:
                import openai
                openai.api_key = self.config["apis"]["openai"]["api_key"]
                self.api_clients["openai"] = openai
                logger.info("OpenAI client initialized")
            except ImportError:
                logger.warning("OpenAI library not available")
        
        # Ollama client (if enabled)
        if self.config["apis"]["ollama"]["enabled"]:
            self.ollama_base_url = self.config["apis"]["ollama"]["base_url"]
            logger.info("Ollama client configured")
        
        # Web search client
        if self.config["apis"]["web_search"]["enabled"]:
            logger.info("Web search client configured")
    
    async def research_topic(self, topic: str, depth: str = "comprehensive") -> Dict:
        """Research a specific topic using multiple sources."""
        logger.info(f"Researching topic: {topic}")
        
        research_data = {
            "topic": topic,
            "timestamp": datetime.now().isoformat(),
            "sources": [],
            "content": "",
            "key_points": [],
            "related_topics": [],
            "quality_score": 0.0
        }
        
        # Web search
        web_results = await self.web_search(topic)
        research_data["sources"].extend(web_results)
        
        # AI analysis
        ai_analysis = await self.ai_analyze_topic(topic, web_results)
        research_data.update(ai_analysis)
        
        # Calculate quality score
        research_data["quality_score"] = self.calculate_quality_score(research_data)
        
        return research_data
    
    async def web_search(self, query: str) -> List[Dict]:
        """Perform web search using free APIs."""
        sources = []
        
        try:
            # DuckDuckGo search (free)
            ddg_results = await self.duckduckgo_search(query)
            sources.extend(ddg_results)
            
            # Wikipedia search (free)
            wiki_results = await self.wikipedia_search(query)
            sources.extend(wiki_results)
            
            # Academic search (free)
            academic_results = await self.academic_search(query)
            sources.extend(academic_results)
            
        except Exception as e:
            logger.error(f"Web search failed: {e}")
        
        return sources
    
    async def duckduckgo_search(self, query: str) -> List[Dict]:
        """Search using DuckDuckGo API."""
        sources = []
        
        try:
            # Use DuckDuckGo instant answer API
            url = "https://api.duckduckgo.com/"
            params = {
                "q": query,
                "format": "json",
                "no_html": "1",
                "skip_disambig": "1"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Extract abstract
                        if data.get("Abstract"):
                            sources.append({
                                "title": data.get("Heading", query),
                                "url": data.get("AbstractURL", ""),
                                "content": data.get("Abstract", ""),
                                "source": "DuckDuckGo",
                                "type": "instant_answer"
                            })
                        
                        # Extract related topics
                        if data.get("RelatedTopics"):
                            for topic in data["RelatedTopics"][:5]:
                                if isinstance(topic, dict) and topic.get("Text"):
                                    sources.append({
                                        "title": topic.get("FirstURL", "").split("/")[-1].replace("_", " "),
                                        "url": topic.get("FirstURL", ""),
                                        "content": topic.get("Text", ""),
                                        "source": "DuckDuckGo",
                                        "type": "related_topic"
                                    })
        
        except Exception as e:
            logger.error(f"DuckDuckGo search failed: {e}")
        
        return sources
    
    async def wikipedia_search(self, query: str) -> List[Dict]:
        """Search Wikipedia for information."""
        sources = []
        
        try:
            # Wikipedia API search
            search_url = "https://en.wikipedia.org/api/rest_v1/page/summary/"
            page_title = query.replace(" ", "_")
            
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{search_url}{page_title}") as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        sources.append({
                            "title": data.get("title", query),
                            "url": data.get("content_urls", {}).get("desktop", {}).get("page", ""),
                            "content": data.get("extract", ""),
                            "source": "Wikipedia",
                            "type": "encyclopedia"
                        })
        
        except Exception as e:
            logger.error(f"Wikipedia search failed: {e}")
        
        return sources
    
    async def academic_search(self, query: str) -> List[Dict]:
        """Search academic sources (free APIs)."""
        sources = []
        
        try:
            # Use Crossref API for academic papers
            url = "https://api.crossref.org/works"
            params = {
                "query": query,
                "rows": 5,
                "filter": "has-full-text:true"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        for item in data.get("message", {}).get("items", []):
                            sources.append({
                                "title": item.get("title", [""])[0],
                                "url": item.get("URL", ""),
                                "content": f"Authors: {', '.join([author.get('given', '') + ' ' + author.get('family', '') for author in item.get('author', [])])}",
                                "source": "Crossref",
                                "type": "academic_paper"
                            })
        
        except Exception as e:
            logger.error(f"Academic search failed: {e}")
        
        return sources
    
    async def ai_analyze_topic(self, topic: str, sources: List[Dict]) -> Dict:
        """Use AI to analyze and synthesize research."""
        analysis = {
            "content": "",
            "key_points": [],
            "related_topics": []
        }
        
        # Prepare context for AI
        context = f"Topic: {topic}\n\nSources:\n"
        for source in sources[:5]:  # Limit to top 5 sources
            context += f"- {source['title']}: {source['content'][:200]}...\n"
        
        # Generate analysis using available AI
        if self.api_clients.get("openai"):
            analysis = await self.openai_analyze(topic, context)
        elif self.config["apis"]["ollama"]["enabled"]:
            analysis = await self.ollama_analyze(topic, context)
        else:
            # Fallback to basic analysis
            analysis = self.basic_analysis(topic, sources)
        
        return analysis
    
    async def openai_analyze(self, topic: str, context: str) -> Dict:
        """Analyze using OpenAI API."""
        try:
            response = await self.api_clients["openai"].ChatCompletion.acreate(
                model=self.config["apis"]["openai"]["model"],
                messages=[
                    {"role": "system", "content": "You are a research assistant specializing in comprehensive topic analysis. Provide detailed, well-structured analysis with key points and related topics."},
                    {"role": "user", "content": f"Analyze this topic and research context:\n\n{context}\n\nProvide:\n1. Comprehensive analysis\n2. Key points (5-7 points)\n3. Related topics (3-5 topics)"}
                ],
                max_tokens=self.config["apis"]["openai"]["max_tokens"]
            )
            
            content = response.choices[0].message.content
            
            # Parse response
            analysis = self.parse_ai_response(content)
            return analysis
        
        except Exception as e:
            logger.error(f"OpenAI analysis failed: {e}")
            return self.basic_analysis(topic, [])
    
    async def ollama_analyze(self, topic: str, context: str) -> Dict:
        """Analyze using Ollama API."""
        try:
            url = f"{self.ollama_base_url}/api/generate"
            data = {
                "model": self.config["apis"]["ollama"]["model"],
                "prompt": f"Analyze this topic and research context:\n\n{context}\n\nProvide:\n1. Comprehensive analysis\n2. Key points (5-7 points)\n3. Related topics (3-5 topics)",
                "stream": False
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=data) as response:
                    if response.status == 200:
                        result = await response.json()
                        content = result.get("response", "")
                        
                        # Parse response
                        analysis = self.parse_ai_response(content)
                        return analysis
        
        except Exception as e:
            logger.error(f"Ollama analysis failed: {e}")
            return self.basic_analysis(topic, [])
    
    def basic_analysis(self, topic: str, sources: List[Dict]) -> Dict:
        """Basic analysis when AI is not available."""
        content = f"Research analysis for topic: {topic}\n\n"
        
        if sources:
            content += "Based on the following sources:\n"
            for source in sources[:3]:
                content += f"- {source['title']}: {source['content'][:100]}...\n"
        
        content += f"\n{topic} is a complex topic that encompasses multiple dimensions and perspectives. "
        content += "Further research and analysis would be beneficial for comprehensive understanding."
        
        key_points = [
            f"{topic} has historical significance",
            f"{topic} involves multiple perspectives",
            f"{topic} requires deeper investigation",
            f"{topic} connects to broader themes",
            f"{topic} has practical applications"
        ]
        
        related_topics = [
            f"{topic} history",
            f"{topic} psychology",
            f"{topic} applications"
        ]
        
        return {
            "content": content,
            "key_points": key_points,
            "related_topics": related_topics
        }
    
    def parse_ai_response(self, content: str) -> Dict:
        """Parse AI response into structured format."""
        analysis = {
            "content": content,
            "key_points": [],
            "related_topics": []
        }
        
        # Extract key points
        key_points_match = re.search(r'key points?[:\-]?\s*(.*?)(?=\n\n|\nrelated|$)', content, re.IGNORECASE | re.DOTALL)
        if key_points_match:
            points_text = key_points_match.group(1)
            points = re.findall(r'[-•]\s*(.+?)(?=\n|$)', points_text)
            analysis["key_points"] = [point.strip() for point in points]
        
        # Extract related topics
        topics_match = re.search(r'related topics?[:\-]?\s*(.*?)$', content, re.IGNORECASE | re.DOTALL)
        if topics_match:
            topics_text = topics_match.group(1)
            topics = re.findall(r'[-•]\s*(.+?)(?=\n|$)', topics_text)
            analysis["related_topics"] = [topic.strip() for topic in topics]
        
        return analysis
    
    def calculate_quality_score(self, research_data: Dict) -> float:
        """Calculate quality score for research data."""
        score = 0.0
        
        # Source count
        source_count = len(research_data.get("sources", []))
        score += min(source_count * 0.1, 0.4)
        
        # Content length
        content_length = len(research_data.get("content", ""))
        score += min(content_length / 1000, 0.3)
        
        # Key points
        key_points_count = len(research_data.get("key_points", []))
        score += min(key_points_count * 0.05, 0.2)
        
        # Related topics
        related_topics_count = len(research_data.get("related_topics", []))
        score += min(related_topics_count * 0.05, 0.1)
        
        return min(score, 1.0)
    
    async def research_project_topics(self) -> Dict:
        """Research all topics for the project."""
        logger.info("Starting comprehensive project research")
        
        # Get project theme
        theme = self.project_config["book"]["theme"]
        if not theme:
            theme = "general knowledge"
        
        # Determine research topics based on theme
        topics = self.get_research_topics(theme)
        
        research_results = {
            "project": self.project_config["project"]["name"],
            "theme": theme,
            "timestamp": datetime.now().isoformat(),
            "topics": {},
            "overall_quality": 0.0
        }
        
        # Research each topic
        for topic in topics:
            logger.info(f"Researching topic: {topic}")
            topic_research = await self.research_topic(topic)
            research_results["topics"][topic] = topic_research
            
            # Small delay to avoid overwhelming APIs
            await asyncio.sleep(1)
        
        # Calculate overall quality
        quality_scores = [data["quality_score"] for data in research_results["topics"].values()]
        research_results["overall_quality"] = sum(quality_scores) / len(quality_scores) if quality_scores else 0.0
        
        return research_results
    
    def get_research_topics(self, theme: str) -> List[str]:
        """Get research topics based on project theme."""
        theme_lower = theme.lower()
        
        # Check for specific themes
        if "tarot" in theme_lower:
            return self.research_themes["tarot"][:8]
        elif "philosophy" in theme_lower:
            return self.research_themes["philosophy"][:8]
        elif "psychology" in theme_lower:
            return self.research_themes["psychology"][:8]
        elif "spirituality" in theme_lower:
            return self.research_themes["spirituality"][:8]
        elif "literature" in theme_lower:
            return self.research_themes["literature"][:8]
        else:
            # General topics
            return [
                f"{theme} history",
                f"{theme} psychology",
                f"{theme} philosophy",
                f"{theme} applications",
                f"{theme} modern perspectives",
                f"{theme} cultural significance",
                f"{theme} practical uses",
                f"{theme} future trends"
            ]
    
    def save_research_results(self, research_results: Dict):
        """Save research results to project directory."""
        # Save comprehensive research
        research_file = self.research_dir / f"research_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(research_file, 'w', encoding='utf-8') as f:
            json.dump(research_results, f, indent=2, ensure_ascii=False)
        
        # Update project config
        self.project_config["research"]["topics"] = list(research_results["topics"].keys())
        self.project_config["research"]["iterations"] += 1
        self.project_config["research"]["last_research"] = datetime.now().isoformat()
        self.project_config["project"]["current_phase"] = "writing"
        
        with open(self.project_config_file, 'w', encoding='utf-8') as f:
            json.dump(self.project_config, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Research results saved to: {research_file}")
    
    async def run_research_phase(self):
        """Run the complete research phase."""
        logger.info("Starting research phase")
        
        try:
            # Research project topics
            research_results = await self.research_project_topics()
            
            # Save results
            self.save_research_results(research_results)
            
            # Generate research summary
            self.generate_research_summary(research_results)
            
            logger.info("Research phase completed successfully")
            return True
        
        except Exception as e:
            logger.error(f"Research phase failed: {e}")
            return False
    
    def generate_research_summary(self, research_results: Dict):
        """Generate a human-readable research summary."""
        summary_file = self.research_dir / "research_summary.md"
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(f"# Research Summary: {research_results['project']}\n\n")
            f.write(f"**Theme:** {research_results['theme']}\n")
            f.write(f"**Generated:** {research_results['timestamp']}\n")
            f.write(f"**Overall Quality Score:** {research_results['overall_quality']:.2f}\n\n")
            
            f.write("## Research Topics\n\n")
            for topic, data in research_results["topics"].items():
                f.write(f"### {topic}\n")
                f.write(f"**Quality Score:** {data['quality_score']:.2f}\n")
                f.write(f"**Sources:** {len(data['sources'])}\n\n")
                
                if data['content']:
                    f.write(f"**Analysis:**\n{data['content'][:500]}...\n\n")
                
                if data['key_points']:
                    f.write("**Key Points:**\n")
                    for point in data['key_points']:
                        f.write(f"- {point}\n")
                    f.write("\n")
                
                if data['related_topics']:
                    f.write("**Related Topics:**\n")
                    for topic_rel in data['related_topics']:
                        f.write(f"- {topic_rel}\n")
                    f.write("\n")
        
        logger.info(f"Research summary saved to: {summary_file}")


async def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="AI Research Engine")
    parser.add_argument("--project-dir", required=True, help="Project directory")
    parser.add_argument("--config-file", required=True, help="Configuration file")
    parser.add_argument("--phase", default="research", help="Phase to run")
    
    args = parser.parse_args()
    
    # Create research engine
    engine = AIResearchEngine(args.project_dir, args.config_file)
    
    # Run research phase
    if args.phase == "research":
        success = await engine.run_research_phase()
        sys.exit(0 if success else 1)
    else:
        logger.error(f"Unknown phase: {args.phase}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())