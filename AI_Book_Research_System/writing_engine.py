#!/usr/bin/env python3
"""
AI Book Writing Engine
Canonizes existing learning and code with research/write/expand/repeat cycle
Uses AI to generate literary content based on research
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


class AIWritingEngine:
    """AI-powered writing engine for book content."""
    
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
        
        # Writing directories
        self.writing_dir = self.project_dir / "writing"
        self.writing_dir.mkdir(exist_ok=True)
        
        # Initialize API clients
        self.setup_api_clients()
        
        # Writing templates and styles
        self.writing_templates = {
            "literary": {
                "introduction": "The morning light filters through the window, casting long shadows across the wooden table where the {topic} lies before me. I have been sitting here for what feels like hours, though the clock on the wall suggests it has been only minutes. Time moves differently when we enter the realm of {theme}, when we allow ourselves to be drawn into the living mystery that {topic} represents.",
                "development": "As I sit with the {topic}, I am reminded of the countless ways in which {theme} has appeared in my own life—not just in formal study, but in moments of reflection, in dreams, in conversations with others, in the patterns I notice in the world around me.",
                "conclusion": "As I prepare to move on from the {topic}, I am aware that this exploration is not complete, nor could it ever be. The living {theme} continues to reveal its mysteries to us as we continue to grow and evolve."
            },
            "academic": {
                "introduction": "The study of {topic} represents a fundamental aspect of {theme} that has been explored across multiple disciplines and traditions. This chapter examines the historical, psychological, and cultural dimensions of {topic}.",
                "development": "Research in {theme} has shown that {topic} encompasses multiple layers of meaning and significance. The following analysis explores these dimensions in detail.",
                "conclusion": "The examination of {topic} reveals the complexity and depth of {theme}. Further research and exploration would be beneficial for comprehensive understanding."
            },
            "contemplative": {
                "introduction": "In the quiet moments of reflection, {topic} emerges as a gentle presence, inviting us to explore the deeper mysteries of {theme}. This is not a hurried examination, but a slow, deliberate journey into understanding.",
                "development": "The {topic} speaks to us in whispers, offering insights that emerge gradually, like the dawn breaking over a still landscape. Each moment of contemplation reveals new layers of meaning.",
                "conclusion": "As we conclude our exploration of {topic}, we carry with us the wisdom that has emerged through this contemplative journey. The {theme} continues to unfold before us, offering new insights and understanding."
            }
        }
    
    def setup_api_clients(self):
        """Setup API clients for writing."""
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
    
    def get_chapter_outline(self, theme: str, target_chapters: int) -> List[Dict]:
        """Generate chapter outline based on theme."""
        if "tarot" in theme.lower():
            return self.get_tarot_chapter_outline(target_chapters)
        elif "philosophy" in theme.lower():
            return self.get_philosophy_chapter_outline(target_chapters)
        elif "psychology" in theme.lower():
            return self.get_psychology_chapter_outline(target_chapters)
        elif "spirituality" in theme.lower():
            return self.get_spirituality_chapter_outline(target_chapters)
        else:
            return self.get_general_chapter_outline(theme, target_chapters)
    
    def get_tarot_chapter_outline(self, target_chapters: int) -> List[Dict]:
        """Generate tarot-specific chapter outline."""
        chapters = [
            {"number": 1, "title": "The Living Symbol", "focus": "Introduction to tarot as living system"},
            {"number": 2, "title": "The Fool's Journey", "focus": "Beginning the archetypal journey"},
            {"number": 3, "title": "The Magician's Power", "focus": "Conscious manifestation and will"},
            {"number": 4, "title": "The High Priestess's Wisdom", "focus": "Intuitive knowledge and mystery"},
            {"number": 5, "title": "The Empress's Creation", "focus": "Feminine power and nurturing"},
            {"number": 6, "title": "The Emperor's Authority", "focus": "Masculine power and structure"},
            {"number": 7, "title": "The Hierophant's Teaching", "focus": "Tradition and spiritual guidance"},
            {"number": 8, "title": "The Lovers' Choice", "focus": "Relationships and decision-making"},
            {"number": 9, "title": "The Chariot's Will", "focus": "Determination and overcoming obstacles"},
            {"number": 10, "title": "Strength's Courage", "focus": "Inner strength and compassion"},
            {"number": 11, "title": "The Hermit's Light", "focus": "Inner wisdom and introspection"},
            {"number": 12, "title": "Wheel of Fortune's Cycles", "focus": "Change and destiny"},
            {"number": 13, "title": "Justice's Balance", "focus": "Fairness and equilibrium"},
            {"number": 14, "title": "The Hanged Man's Surrender", "focus": "Sacrifice and new perspectives"},
            {"number": 15, "title": "Death's Transformation", "focus": "Endings and new beginnings"},
            {"number": 16, "title": "Temperance's Harmony", "focus": "Balance and moderation"},
            {"number": 17, "title": "The Devil's Shadow", "focus": "Limitations and illusions"},
            {"number": 18, "title": "The Tower's Awakening", "focus": "Sudden change and revelation"},
            {"number": 19, "title": "The Star's Hope", "focus": "Inspiration and guidance"},
            {"number": 20, "title": "The World's Completion", "focus": "Integration and wholeness"}
        ]
        
        return chapters[:target_chapters]
    
    def get_philosophy_chapter_outline(self, target_chapters: int) -> List[Dict]:
        """Generate philosophy-specific chapter outline."""
        chapters = [
            {"number": 1, "title": "The Question of Being", "focus": "Fundamental questions of existence"},
            {"number": 2, "title": "The Nature of Reality", "focus": "Metaphysical exploration"},
            {"number": 3, "title": "The Problem of Knowledge", "focus": "Epistemological inquiry"},
            {"number": 4, "title": "The Search for Meaning", "focus": "Existential questions"},
            {"number": 5, "title": "The Good Life", "focus": "Ethical philosophy"},
            {"number": 6, "title": "The Mind and Consciousness", "focus": "Philosophy of mind"},
            {"number": 7, "title": "The Beautiful and Sublime", "focus": "Aesthetics"},
            {"number": 8, "title": "The Social Contract", "focus": "Political philosophy"},
            {"number": 9, "title": "The Sacred and Profane", "focus": "Philosophy of religion"},
            {"number": 10, "title": "The Language of Thought", "focus": "Philosophy of language"},
            {"number": 11, "title": "The Scientific Method", "focus": "Philosophy of science"},
            {"number": 12, "title": "The Free Will Debate", "focus": "Determinism and freedom"},
            {"number": 13, "title": "The Nature of Time", "focus": "Philosophy of time"},
            {"number": 14, "title": "The Problem of Evil", "focus": "Theodicy"},
            {"number": 15, "title": "The Quest for Wisdom", "focus": "Philosophical practice"},
            {"number": 16, "title": "The Eastern Perspective", "focus": "Comparative philosophy"},
            {"number": 17, "title": "The Modern Dilemma", "focus": "Contemporary issues"},
            {"number": 18, "title": "The Future of Philosophy", "focus": "Emerging directions"},
            {"number": 19, "title": "The Integration of Knowledge", "focus": "Interdisciplinary approach"},
            {"number": 20, "title": "The Living Philosophy", "focus": "Philosophy as way of life"}
        ]
        
        return chapters[:target_chapters]
    
    def get_psychology_chapter_outline(self, target_chapters: int) -> List[Dict]:
        """Generate psychology-specific chapter outline."""
        chapters = [
            {"number": 1, "title": "The Conscious Mind", "focus": "Awareness and consciousness"},
            {"number": 2, "title": "The Unconscious Depths", "focus": "Unconscious processes"},
            {"number": 3, "title": "The Archetypal Patterns", "focus": "Jungian archetypes"},
            {"number": 4, "title": "The Shadow Self", "focus": "Shadow work and integration"},
            {"number": 5, "title": "The Journey of Individuation", "focus": "Personal development"},
            {"number": 6, "title": "The Collective Unconscious", "focus": "Shared psychological patterns"},
            {"number": 7, "title": "The Symbolic Language", "focus": "Symbols and meaning"},
            {"number": 8, "title": "The Dreams and Visions", "focus": "Dream psychology"},
            {"number": 9, "title": "The Anima and Animus", "focus": "Gender archetypes"},
            {"number": 10, "title": "The Wise Old Man", "focus": "Wisdom archetypes"},
            {"number": 11, "title": "The Great Mother", "focus": "Nurturing archetypes"},
            {"number": 12, "title": "The Hero's Journey", "focus": "Transformation patterns"},
            {"number": 13, "title": "The Transcendent Function", "focus": "Integration and wholeness"},
            {"number": 14, "title": "The Active Imagination", "focus": "Creative visualization"},
            {"number": 15, "title": "The Synchronicity Principle", "focus": "Meaningful coincidences"},
            {"number": 16, "title": "The Psychological Types", "focus": "Personality theory"},
            {"number": 17, "title": "The Therapeutic Process", "focus": "Healing and growth"},
            {"number": 18, "title": "The Spiritual Dimension", "focus": "Transpersonal psychology"},
            {"number": 19, "title": "The Modern Applications", "focus": "Contemporary psychology"},
            {"number": 20, "title": "The Future of Consciousness", "focus": "Evolution of awareness"}
        ]
        
        return chapters[:target_chapters]
    
    def get_spirituality_chapter_outline(self, target_chapters: int) -> List[Dict]:
        """Generate spirituality-specific chapter outline."""
        chapters = [
            {"number": 1, "title": "The Sacred Quest", "focus": "Spiritual seeking and longing"},
            {"number": 2, "title": "The Inner Light", "focus": "Divine spark within"},
            {"number": 3, "title": "The Path of Meditation", "focus": "Contemplative practice"},
            {"number": 4, "title": "The Voice of Silence", "focus": "Inner stillness"},
            {"number": 5, "title": "The Dance of Devotion", "focus": "Bhakti and love"},
            {"number": 6, "title": "The Wisdom of Surrender", "focus": "Letting go and trust"},
            {"number": 7, "title": "The Fire of Transformation", "focus": "Spiritual alchemy"},
            {"number": 8, "title": "The Waters of Purification", "focus": "Cleansing and renewal"},
            {"number": 9, "title": "The Breath of Life", "focus": "Prana and vital energy"},
            {"number": 10, "title": "The Sacred Geometry", "focus": "Divine patterns"},
            {"number": 11, "title": "The Mystical Union", "focus": "Oneness and unity"},
            {"number": 12, "title": "The Divine Play", "focus": "Lila and cosmic dance"},
            {"number": 13, "title": "The Eternal Now", "focus": "Present moment awareness"},
            {"number": 14, "title": "The Compassionate Heart", "focus": "Love and service"},
            {"number": 15, "title": "The Awakened Mind", "focus": "Enlightenment and realization"},
            {"number": 16, "title": "The Sacred Texts", "focus": "Spiritual literature"},
            {"number": 17, "title": "The Living Tradition", "focus": "Spiritual lineage"},
            {"number": 18, "title": "The Modern Mystic", "focus": "Contemporary spirituality"},
            {"number": 19, "title": "The Integration of Paths", "focus": "Universal spirituality"},
            {"number": 20, "title": "The Return to Source", "focus": "Homecoming and completion"}
        ]
        
        return chapters[:target_chapters]
    
    def get_general_chapter_outline(self, theme: str, target_chapters: int) -> List[Dict]:
        """Generate general chapter outline based on theme."""
        chapters = []
        
        for i in range(1, target_chapters + 1):
            chapters.append({
                "number": i,
                "title": f"{theme} - Chapter {i}",
                "focus": f"Exploration of {theme} from multiple perspectives"
            })
        
        return chapters
    
    async def write_chapter(self, chapter: Dict, research_data: Dict, theme: str) -> str:
        """Write a single chapter using AI."""
        logger.info(f"Writing chapter {chapter['number']}: {chapter['title']}")
        
        # Get writing style
        style = self.project_config["book"]["style"]
        target_words = self.project_config["book"]["target_words_per_chapter"]
        
        # Prepare context
        context = self.prepare_writing_context(chapter, research_data, theme)
        
        # Generate chapter content
        if self.api_clients.get("openai"):
            content = await self.openai_write_chapter(chapter, context, style, target_words)
        elif self.config["apis"]["ollama"]["enabled"]:
            content = await self.ollama_write_chapter(chapter, context, style, target_words)
        else:
            content = self.basic_write_chapter(chapter, context, style, target_words)
        
        return content
    
    def prepare_writing_context(self, chapter: Dict, research_data: Dict, theme: str) -> str:
        """Prepare context for writing."""
        context = f"Chapter: {chapter['title']}\n"
        context += f"Focus: {chapter['focus']}\n"
        context += f"Theme: {theme}\n\n"
        
        # Add relevant research
        if research_data and "topics" in research_data:
            context += "Research Context:\n"
            for topic, data in research_data["topics"].items():
                if topic.lower() in chapter["title"].lower() or topic.lower() in chapter["focus"].lower():
                    context += f"- {topic}: {data.get('content', '')[:200]}...\n"
        
        return context
    
    async def openai_write_chapter(self, chapter: Dict, context: str, style: str, target_words: int) -> str:
        """Write chapter using OpenAI API."""
        try:
            prompt = f"""Write a {target_words}-word chapter titled "{chapter['title']}" with the following context:

{context}

Style: {style}
Focus: {chapter['focus']}

Requirements:
- Write in a {style} style
- Include personal reflection and contemplation
- Weave in research insights naturally
- Create a flowing narrative
- End with contemplative closing
- Aim for approximately {target_words} words

Structure:
1. Engaging introduction
2. Main content with multiple perspectives
3. Personal reflection
4. Contemplative closing"""

            response = await self.api_clients["openai"].ChatCompletion.acreate(
                model=self.config["apis"]["openai"]["model"],
                messages=[
                    {"role": "system", "content": f"You are a skilled writer specializing in {style} prose. Create engaging, contemplative content that flows naturally and incorporates research insights seamlessly."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.config["apis"]["openai"]["max_tokens"]
            )
            
            content = response.choices[0].message.content
            return content
        
        except Exception as e:
            logger.error(f"OpenAI writing failed: {e}")
            return self.basic_write_chapter(chapter, context, style, target_words)
    
    async def ollama_write_chapter(self, chapter: Dict, context: str, style: str, target_words: int) -> str:
        """Write chapter using Ollama API."""
        try:
            prompt = f"""Write a {target_words}-word chapter titled "{chapter['title']}" with the following context:

{context}

Style: {style}
Focus: {chapter['focus']}

Requirements:
- Write in a {style} style
- Include personal reflection and contemplation
- Weave in research insights naturally
- Create a flowing narrative
- End with contemplative closing
- Aim for approximately {target_words} words"""

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
            logger.error(f"Ollama writing failed: {e}")
            return self.basic_write_chapter(chapter, context, style, target_words)
    
    def basic_write_chapter(self, chapter: Dict, context: str, style: str, target_words: int) -> str:
        """Basic chapter writing when AI is not available."""
        template = self.writing_templates.get(style, self.writing_templates["literary"])
        
        content = f"# {chapter['title']}\n\n"
        
        # Introduction
        intro = template["introduction"].format(
            topic=chapter["title"],
            theme=self.project_config["book"]["theme"]
        )
        content += intro + "\n\n"
        
        # Main content
        main_content = template["development"].format(
            topic=chapter["title"],
            theme=self.project_config["book"]["theme"]
        )
        content += main_content + "\n\n"
        
        # Add some basic content
        content += f"The {chapter['title']} represents a fundamental aspect of {self.project_config['book']['theme']} that deserves careful exploration. "
        content += f"This chapter examines the various dimensions and perspectives related to {chapter['focus']}. "
        content += f"Through contemplation and reflection, we can gain deeper insights into the nature and significance of this topic.\n\n"
        
        content += f"As we explore {chapter['title']}, we encounter multiple layers of meaning and understanding. "
        content += f"Each perspective offers unique insights that contribute to our overall comprehension of {self.project_config['book']['theme']}. "
        content += f"The journey of understanding is ongoing, and each moment of reflection brings new clarity and wisdom.\n\n"
        
        # Conclusion
        conclusion = template["conclusion"].format(
            topic=chapter["title"],
            theme=self.project_config["book"]["theme"]
        )
        content += conclusion + "\n\n"
        
        return content
    
    def save_chapter(self, chapter: Dict, content: str):
        """Save chapter to file."""
        chapter_file = self.writing_dir / f"chapter_{chapter['number']:02d}_{chapter['title'].replace(' ', '_').lower()}.md"
        
        with open(chapter_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"Chapter saved to: {chapter_file}")
        return str(chapter_file)
    
    async def run_writing_phase(self):
        """Run the complete writing phase."""
        logger.info("Starting writing phase")
        
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
            
            # Generate chapter outline
            theme = self.project_config["book"]["theme"]
            target_chapters = self.project_config["book"]["target_chapters"]
            chapters = self.get_chapter_outline(theme, target_chapters)
            
            # Write each chapter
            written_chapters = []
            total_words = 0
            
            for chapter in chapters:
                content = await self.write_chapter(chapter, research_data, theme)
                chapter_file = self.save_chapter(chapter, content)
                
                word_count = len(content.split())
                total_words += word_count
                
                written_chapters.append({
                    "number": chapter["number"],
                    "title": chapter["title"],
                    "file": chapter_file,
                    "word_count": word_count
                })
                
                logger.info(f"Chapter {chapter['number']} written: {word_count} words")
                
                # Small delay to avoid overwhelming APIs
                await asyncio.sleep(1)
            
            # Update project config
            self.project_config["writing"]["chapters"] = written_chapters
            self.project_config["writing"]["total_words"] = total_words
            self.project_config["writing"]["last_writing"] = datetime.now().isoformat()
            self.project_config["project"]["current_phase"] = "expansion"
            
            with open(self.project_config_file, 'w', encoding='utf-8') as f:
                json.dump(self.project_config, f, indent=2, ensure_ascii=False)
            
            # Generate writing summary
            self.generate_writing_summary(written_chapters, total_words)
            
            logger.info("Writing phase completed successfully")
            return True
        
        except Exception as e:
            logger.error(f"Writing phase failed: {e}")
            return False
    
    def generate_writing_summary(self, chapters: List[Dict], total_words: int):
        """Generate a writing summary."""
        summary_file = self.writing_dir / "writing_summary.md"
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(f"# Writing Summary: {self.project_config['project']['name']}\n\n")
            f.write(f"**Generated:** {datetime.now().isoformat()}\n")
            f.write(f"**Total Words:** {total_words:,}\n")
            f.write(f"**Chapters:** {len(chapters)}\n")
            f.write(f"**Average Words per Chapter:** {total_words // len(chapters) if chapters else 0}\n\n")
            
            f.write("## Chapters\n\n")
            for chapter in chapters:
                f.write(f"### Chapter {chapter['number']}: {chapter['title']}\n")
                f.write(f"**Words:** {chapter['word_count']}\n")
                f.write(f"**File:** {chapter['file']}\n\n")
        
        logger.info(f"Writing summary saved to: {summary_file}")


async def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="AI Writing Engine")
    parser.add_argument("--project-dir", required=True, help="Project directory")
    parser.add_argument("--config-file", required=True, help="Configuration file")
    parser.add_argument("--phase", default="writing", help="Phase to run")
    
    args = parser.parse_args()
    
    # Create writing engine
    engine = AIWritingEngine(args.project_dir, args.config_file)
    
    # Run writing phase
    if args.phase == "writing":
        success = await engine.run_writing_phase()
        sys.exit(0 if success else 1)
    else:
        logger.error(f"Unknown phase: {args.phase}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())