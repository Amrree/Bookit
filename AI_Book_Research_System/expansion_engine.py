#!/usr/bin/env python3
"""
AI Book Expansion Engine
Canonizes existing learning and code with research/write/expand/repeat cycle
Uses AI to expand and enhance written content
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


class AIExpansionEngine:
    """AI-powered expansion engine for book content."""
    
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
        
        # Expansion directories
        self.expansion_dir = self.project_dir / "expansion"
        self.expansion_dir.mkdir(exist_ok=True)
        
        # Initialize API clients
        self.setup_api_clients()
        
        # Expansion perspectives and techniques
        self.expansion_perspectives = {
            "historical": {
                "description": "Historical context and evolution",
                "prompts": [
                    "What is the historical background of this topic?",
                    "How has this concept evolved over time?",
                    "What historical figures or events are relevant?",
                    "How do historical traditions inform this topic?"
                ]
            },
            "psychological": {
                "description": "Psychological and archetypal analysis",
                "prompts": [
                    "What psychological patterns are at work here?",
                    "How do archetypes relate to this topic?",
                    "What does depth psychology reveal?",
                    "How does this affect human consciousness?"
                ]
            },
            "cultural": {
                "description": "Cultural variations and contemporary relevance",
                "prompts": [
                    "How do different cultures approach this topic?",
                    "What are the contemporary applications?",
                    "How does this relate to modern society?",
                    "What cultural variations exist?"
                ]
            },
            "practical": {
                "description": "Practical applications and real-world guidance",
                "prompts": [
                    "How can this be applied in daily life?",
                    "What practical tools or techniques are relevant?",
                    "How does this help with personal growth?",
                    "What actionable insights can be derived?"
                ]
            },
            "philosophical": {
                "description": "Philosophical implications and deeper meaning",
                "prompts": [
                    "What are the philosophical implications?",
                    "How does this relate to fundamental questions?",
                    "What deeper meanings can be found?",
                    "How does this connect to universal themes?"
                ]
            },
            "spiritual": {
                "description": "Spiritual dimensions and mystical aspects",
                "prompts": [
                    "What are the spiritual dimensions of this topic?",
                    "How does this relate to mystical experience?",
                    "What spiritual practices are relevant?",
                    "How does this connect to divine consciousness?"
                ]
            }
        }
    
    def setup_api_clients(self):
        """Setup API clients for expansion."""
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
    
    def load_chapter_content(self, chapter_file: str) -> str:
        """Load chapter content from file."""
        try:
            with open(chapter_file, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Failed to load chapter content: {e}")
            return ""
    
    def analyze_chapter_content(self, content: str) -> Dict:
        """Analyze chapter content for expansion opportunities."""
        analysis = {
            "word_count": len(content.split()),
            "sections": [],
            "themes": [],
            "expansion_opportunities": [],
            "complexity": "medium"
        }
        
        # Extract sections
        sections = re.findall(r'^#+\s+(.+)$', content, re.MULTILINE)
        analysis["sections"] = sections
        
        # Extract themes (simple keyword extraction)
        theme_keywords = [
            "transformation", "journey", "awakening", "wisdom", "power", "creation",
            "choice", "balance", "change", "shadow", "light", "completion",
            "innocence", "trust", "manifestation", "guidance", "strength"
        ]
        
        content_lower = content.lower()
        for keyword in theme_keywords:
            if keyword in content_lower:
                analysis["themes"].append(keyword)
        
        # Determine complexity
        if analysis["word_count"] < 1000:
            analysis["complexity"] = "low"
        elif analysis["word_count"] > 3000:
            analysis["complexity"] = "high"
        
        # Identify expansion opportunities
        if analysis["word_count"] < 2000:
            analysis["expansion_opportunities"].append("needs_more_content")
        
        if len(analysis["sections"]) < 3:
            analysis["expansion_opportunities"].append("needs_more_sections")
        
        if len(analysis["themes"]) < 3:
            analysis["expansion_opportunities"].append("needs_more_themes")
        
        return analysis
    
    async def expand_chapter(self, chapter: Dict, research_data: Dict) -> str:
        """Expand a single chapter using AI."""
        logger.info(f"Expanding chapter {chapter['number']}: {chapter['title']}")
        
        # Load original content
        original_content = self.load_chapter_content(chapter["file"])
        if not original_content:
            logger.error(f"No content found for chapter {chapter['number']}")
            return ""
        
        # Analyze content
        analysis = self.analyze_chapter_content(original_content)
        
        # Get expansion perspectives
        perspectives = self.config["expansion"]["perspectives"]
        target_expansion_ratio = self.config["expansion"]["target_expansion_ratio"]
        
        # Generate expanded content
        expanded_content = original_content
        
        # Add expansion sections for each perspective
        for perspective in perspectives:
            if perspective in self.expansion_perspectives:
                perspective_content = await self.expand_with_perspective(
                    chapter, original_content, perspective, research_data
                )
                if perspective_content:
                    expanded_content += f"\n\n## {perspective.title()} Perspective\n\n{perspective_content}"
        
        # Ensure target expansion ratio
        current_words = len(expanded_content.split())
        original_words = analysis["word_count"]
        current_ratio = current_words / original_words if original_words > 0 else 0
        
        if current_ratio < target_expansion_ratio:
            additional_content = await self.generate_additional_content(
                chapter, original_content, target_expansion_ratio - current_ratio, research_data
            )
            expanded_content += f"\n\n## Additional Exploration\n\n{additional_content}"
        
        return expanded_content
    
    async def expand_with_perspective(self, chapter: Dict, original_content: str, perspective: str, research_data: Dict) -> str:
        """Expand chapter with a specific perspective."""
        perspective_info = self.expansion_perspectives[perspective]
        
        # Prepare context
        context = f"Chapter: {chapter['title']}\n"
        context += f"Original Content: {original_content[:500]}...\n"
        context += f"Perspective: {perspective_info['description']}\n"
        
        # Add relevant research
        if research_data and "topics" in research_data:
            context += "\nResearch Context:\n"
            for topic, data in research_data["topics"].items():
                if topic.lower() in chapter["title"].lower():
                    context += f"- {topic}: {data.get('content', '')[:200]}...\n"
        
        # Generate perspective content
        if self.api_clients.get("openai"):
            content = await self.openai_expand_perspective(perspective, context, perspective_info)
        elif self.config["apis"]["ollama"]["enabled"]:
            content = await self.ollama_expand_perspective(perspective, context, perspective_info)
        else:
            content = self.basic_expand_perspective(perspective, context, perspective_info)
        
        return content
    
    async def openai_expand_perspective(self, perspective: str, context: str, perspective_info: Dict) -> str:
        """Expand with perspective using OpenAI API."""
        try:
            prompt = f"""Expand the following content from a {perspective} perspective:

{context}

Perspective Description: {perspective_info['description']}

Requirements:
- Write 500-800 words
- Focus on the {perspective} perspective
- Integrate research insights naturally
- Maintain literary quality
- Provide deep, thoughtful analysis
- Include specific examples and insights

Structure:
1. Introduction to the perspective
2. Main analysis and insights
3. Specific examples and applications
4. Contemplative conclusion"""

            response = await self.api_clients["openai"].ChatCompletion.acreate(
                model=self.config["apis"]["openai"]["model"],
                messages=[
                    {"role": "system", "content": f"You are a skilled writer specializing in {perspective} analysis. Create deep, insightful content that explores topics from this specific perspective."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.config["apis"]["openai"]["max_tokens"]
            )
            
            content = response.choices[0].message.content
            return content
        
        except Exception as e:
            logger.error(f"OpenAI perspective expansion failed: {e}")
            return self.basic_expand_perspective(perspective, context, perspective_info)
    
    async def ollama_expand_perspective(self, perspective: str, context: str, perspective_info: Dict) -> str:
        """Expand with perspective using Ollama API."""
        try:
            prompt = f"""Expand the following content from a {perspective} perspective:

{context}

Perspective Description: {perspective_info['description']}

Requirements:
- Write 500-800 words
- Focus on the {perspective} perspective
- Integrate research insights naturally
- Maintain literary quality
- Provide deep, thoughtful analysis
- Include specific examples and insights"""

            url = f"{self.ollama_base_url}/api/generate"
            data = {
                "model": self.config["apis"]["ollama"]["model"],
                "prompt": prompt,
                "stream": False
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=data) as response:
                    if response.status == 200:
                        result = await response.json()
                        content = result.get("response", "")
                        return content
        
        except Exception as e:
            logger.error(f"Ollama perspective expansion failed: {e}")
            return self.basic_expand_perspective(perspective, context, perspective_info)
    
    def basic_expand_perspective(self, perspective: str, context: str, perspective_info: Dict) -> str:
        """Basic perspective expansion when AI is not available."""
        content = f"From a {perspective} perspective, this topic reveals additional layers of meaning and significance. "
        content += f"{perspective_info['description']} offers unique insights that deepen our understanding of the subject matter.\n\n"
        
        # Add some basic content based on perspective
        if perspective == "historical":
            content += "Historically, this concept has evolved through various periods and traditions. "
            content += "Understanding its historical development provides context for contemporary applications and interpretations.\n\n"
        elif perspective == "psychological":
            content += "Psychologically, this topic touches on fundamental aspects of human consciousness and development. "
            content += "The psychological dimensions reveal patterns and processes that shape our experience and understanding.\n\n"
        elif perspective == "cultural":
            content += "Culturally, this concept manifests differently across various traditions and communities. "
            content += "Cultural variations enrich our understanding and offer diverse approaches to the same fundamental themes.\n\n"
        elif perspective == "practical":
            content += "Practically, this topic offers tools and techniques for personal growth and development. "
            content += "The practical applications provide concrete ways to integrate these insights into daily life.\n\n"
        elif perspective == "philosophical":
            content += "Philosophically, this topic raises fundamental questions about existence, meaning, and purpose. "
            content += "The philosophical implications connect to broader themes of human inquiry and understanding.\n\n"
        elif perspective == "spiritual":
            content += "Spiritually, this concept connects to deeper dimensions of consciousness and divine experience. "
            content += "The spiritual aspects offer pathways for transcendence and mystical understanding.\n\n"
        
        content += f"The {perspective} perspective thus adds valuable depth and breadth to our exploration of this topic, "
        content += "offering insights that complement and enhance the original content."
        
        return content
    
    async def generate_additional_content(self, chapter: Dict, original_content: str, needed_ratio: float, research_data: Dict) -> str:
        """Generate additional content to reach target expansion ratio."""
        logger.info(f"Generating additional content for chapter {chapter['number']}")
        
        # Calculate needed words
        original_words = len(original_content.split())
        needed_words = int(original_words * needed_ratio)
        
        # Prepare context
        context = f"Chapter: {chapter['title']}\n"
        context += f"Original Content: {original_content[:500]}...\n"
        context += f"Additional Words Needed: {needed_words}\n"
        
        # Generate additional content
        if self.api_clients.get("openai"):
            content = await self.openai_generate_additional(context, needed_words)
        elif self.config["apis"]["ollama"]["enabled"]:
            content = await self.ollama_generate_additional(context, needed_words)
        else:
            content = self.basic_generate_additional(chapter, needed_words)
        
        return content
    
    async def openai_generate_additional(self, context: str, needed_words: int) -> str:
        """Generate additional content using OpenAI API."""
        try:
            prompt = f"""Generate additional content for the following chapter:

{context}

Requirements:
- Write approximately {needed_words} words
- Expand on themes and concepts from the original content
- Add new insights and perspectives
- Maintain literary quality and flow
- Include contemplative and reflective elements
- Provide deeper exploration of the topic

Structure:
1. Extended exploration of key themes
2. Additional perspectives and insights
3. Contemplative reflection
4. Integration with broader themes"""

            response = await self.api_clients["openai"].ChatCompletion.acreate(
                model=self.config["apis"]["openai"]["model"],
                messages=[
                    {"role": "system", "content": "You are a skilled writer who creates additional content that seamlessly extends and enhances existing material. Focus on depth, insight, and literary quality."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.config["apis"]["openai"]["max_tokens"]
            )
            
            content = response.choices[0].message.content
            return content
        
        except Exception as e:
            logger.error(f"OpenAI additional content generation failed: {e}")
            return self.basic_generate_additional(None, needed_words)
    
    async def ollama_generate_additional(self, context: str, needed_words: int) -> str:
        """Generate additional content using Ollama API."""
        try:
            prompt = f"""Generate additional content for the following chapter:

{context}

Requirements:
- Write approximately {needed_words} words
- Expand on themes and concepts from the original content
- Add new insights and perspectives
- Maintain literary quality and flow
- Include contemplative and reflective elements"""

            url = f"{self.ollama_base_url}/api/generate"
            data = {
                "model": self.config["apis"]["ollama"]["model"],
                "prompt": prompt,
                "stream": False
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=data) as response:
                    if response.status == 200:
                        result = await response.json()
                        content = result.get("response", "")
                        return content
        
        except Exception as e:
            logger.error(f"Ollama additional content generation failed: {e}")
            return self.basic_generate_additional(None, needed_words)
    
    def basic_generate_additional(self, chapter: Dict, needed_words: int) -> str:
        """Basic additional content generation when AI is not available."""
        content = "This topic continues to unfold in new and unexpected ways, revealing additional layers of meaning and significance. "
        content += "As we deepen our exploration, we discover connections and insights that were not immediately apparent in our initial examination.\n\n"
        
        content += "The journey of understanding is ongoing, and each moment of reflection brings new clarity and wisdom. "
        content += "The complexity and depth of this subject matter invites continued exploration and contemplation.\n\n"
        
        content += "In the broader context of human experience, this topic connects to fundamental questions and themes that have occupied "
        content += "thinkers and seekers throughout history. The insights gained from this exploration contribute to our overall understanding "
        content += "of the human condition and our place in the greater mystery of existence.\n\n"
        
        content += "As we continue to explore and reflect, we remain open to new possibilities and perspectives. "
        content += "The living nature of this topic ensures that our understanding will continue to evolve and deepen over time."
        
        return content
    
    def save_expanded_chapter(self, chapter: Dict, expanded_content: str):
        """Save expanded chapter to file."""
        chapter_file = self.expansion_dir / f"chapter_{chapter['number']:02d}_expanded_{chapter['title'].replace(' ', '_').lower()}.md"
        
        with open(chapter_file, 'w', encoding='utf-8') as f:
            f.write(expanded_content)
        
        logger.info(f"Expanded chapter saved to: {chapter_file}")
        return str(chapter_file)
    
    async def run_expansion_phase(self):
        """Run the complete expansion phase."""
        logger.info("Starting expansion phase")
        
        try:
            # Load research data
            research_files = list(self.project_dir.glob("research/research_*.json"))
            if not research_files:
                logger.error("No research data found")
                return False
            
            # Get latest research file
            latest_research = max(research_files, key=lambda x: x.stat().st_mtime)
            with open(latest_research, 'r', encoding='utf-8') as f:
                research_data = json.load(f)
            
            # Get written chapters
            chapters = self.project_config["writing"]["chapters"]
            if not chapters:
                logger.error("No written chapters found")
                return False
            
            # Expand each chapter
            expanded_chapters = []
            total_original_words = 0
            total_expanded_words = 0
            
            for chapter_info in chapters:
                chapter = {
                    "number": chapter_info["number"],
                    "title": chapter_info["title"],
                    "file": chapter_info["file"]
                }
                
                expanded_content = await self.expand_chapter(chapter, research_data)
                if expanded_content:
                    expanded_file = self.save_expanded_chapter(chapter, expanded_content)
                    
                    original_words = chapter_info["word_count"]
                    expanded_words = len(expanded_content.split())
                    expansion_ratio = expanded_words / original_words if original_words > 0 else 0
                    
                    total_original_words += original_words
                    total_expanded_words += expanded_words
                    
                    expanded_chapters.append({
                        "number": chapter["number"],
                        "title": chapter["title"],
                        "original_file": chapter["file"],
                        "expanded_file": expanded_file,
                        "original_words": original_words,
                        "expanded_words": expanded_words,
                        "expansion_ratio": expansion_ratio
                    })
                    
                    logger.info(f"Chapter {chapter['number']} expanded: {original_words} → {expanded_words} words ({expansion_ratio:.2f}x)")
                    
                    # Small delay to avoid overwhelming APIs
                    await asyncio.sleep(1)
            
            # Calculate overall expansion ratio
            overall_expansion_ratio = total_expanded_words / total_original_words if total_original_words > 0 else 0
            
            # Update project config
            self.project_config["expansion"]["expanded_chapters"] = expanded_chapters
            self.project_config["expansion"]["expansion_ratio"] = overall_expansion_ratio
            self.project_config["expansion"]["last_expansion"] = datetime.now().isoformat()
            self.project_config["project"]["current_phase"] = "completed"
            
            with open(self.project_config_file, 'w', encoding='utf-8') as f:
                json.dump(self.project_config, f, indent=2, ensure_ascii=False)
            
            # Generate expansion summary
            self.generate_expansion_summary(expanded_chapters, overall_expansion_ratio)
            
            logger.info("Expansion phase completed successfully")
            return True
        
        except Exception as e:
            logger.error(f"Expansion phase failed: {e}")
            return False
    
    def generate_expansion_summary(self, chapters: List[Dict], overall_ratio: float):
        """Generate an expansion summary."""
        summary_file = self.expansion_dir / "expansion_summary.md"
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(f"# Expansion Summary: {self.project_config['project']['name']}\n\n")
            f.write(f"**Generated:** {datetime.now().isoformat()}\n")
            f.write(f"**Overall Expansion Ratio:** {overall_ratio:.2f}x\n")
            f.write(f"**Chapters Expanded:** {len(chapters)}\n\n")
            
            f.write("## Chapter Details\n\n")
            for chapter in chapters:
                f.write(f"### Chapter {chapter['number']}: {chapter['title']}\n")
                f.write(f"**Original Words:** {chapter['original_words']:,}\n")
                f.write(f"**Expanded Words:** {chapter['expanded_words']:,}\n")
                f.write(f"**Expansion Ratio:** {chapter['expansion_ratio']:.2f}x\n")
                f.write(f"**Expanded File:** {chapter['expanded_file']}\n\n")
        
        logger.info(f"Expansion summary saved to: {summary_file}")


async def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="AI Expansion Engine")
    parser.add_argument("--project-dir", required=True, help="Project directory")
    parser.add_argument("--config-file", required=True, help="Configuration file")
    parser.add_argument("--phase", default="expansion", help="Phase to run")
    
    args = parser.parse_args()
    
    # Create expansion engine
    engine = AIExpansionEngine(args.project_dir, args.config_file)
    
    # Run expansion phase
    if args.phase == "expansion":
        success = await engine.run_expansion_phase()
        sys.exit(0 if success else 1)
    else:
        logger.error(f"Unknown phase: {args.phase}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())