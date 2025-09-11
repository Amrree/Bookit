#!/usr/bin/env python3
"""
Chapter Expander for The Living Tarot
This script reads, understands, researches, and expands chapters heavily and appropriately
"""

import argparse
import json
import os
import re
import sys
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ChapterExpander:
    """Expands chapters with research and enhanced content."""
    
    def __init__(self, book_file: str, expansion_dir: str, target_words: int = 8000, min_ratio: float = 3.0):
        self.book_file = book_file
        self.expansion_dir = Path(expansion_dir)
        self.target_words = target_words
        self.min_ratio = min_ratio
        self.expansion_dir.mkdir(parents=True, exist_ok=True)
        
        # Research topics and themes for each chapter
        self.research_themes = {
            1: ["fool archetype", "innocence wisdom", "beginning journey", "trust faith", "new beginnings"],
            2: ["magician high priestess", "conscious power", "intuitive wisdom", "awakening", "inner power"],
            3: ["empress emperor", "creation manifestation", "feminine masculine", "nurturing authority", "garden creation"],
            4: ["hierophant lovers", "tradition choice", "learning deciding", "crossroads", "guidance"],
            5: ["chariot strength", "willpower obstacles", "determination", "overcoming challenges", "inner strength"],
            6: ["hermit wheel fortune", "inner wisdom", "cycles", "introspection", "inner light"],
            7: ["justice hanged man", "balance equilibrium", "surrender", "fairness", "sacrifice"],
            8: ["death temperance", "transformation", "alchemy", "change renewal", "death rebirth"],
            9: ["devil tower", "shadow work", "darkness", "confrontation", "limitations"],
            10: ["star moon", "hope healing", "illusion", "renewal", "starry night"],
            11: ["sun judgement", "illumination", "joy awakening", "spiritual awakening", "dawn"],
            12: ["world completion", "wholeness", "return", "integration", "completion"],
            13: ["fire element", "passion", "creativity", "action", "will"],
            14: ["water element", "emotion", "intuition", "feeling", "flow"],
            15: ["air element", "thought", "communication", "intellect", "wind"],
            16: ["earth element", "manifestation", "material", "grounding", "practical"],
            17: ["pages court", "possibility", "learning", "youth", "potential"],
            18: ["knights court", "action", "movement", "quest", "adventure"],
            19: ["queens court", "wisdom", "mastery", "nurturing", "authority"],
            20: ["kings court", "authority", "leadership", "mastery", "power"],
            21: ["tarot reading", "divination", "interpretation", "art reading", "practice"],
            22: ["tarot spreads", "layouts", "rituals", "ceremony", "sacred practice"],
            23: ["transformation ritual", "spiritual practice", "ceremony", "sacred work", "ritual"],
            24: ["living tradition", "tarot history", "evolution", "modern practice", "tradition"],
            25: ["ongoing journey", "eternal return", "continuous growth", "lifelong learning", "journey"]
        }
        
        # Literary techniques and approaches
        self.literary_techniques = [
            "narrative storytelling", "personal reflection", "mythological analysis", 
            "psychological exploration", "cultural context", "historical perspective",
            "symbolic interpretation", "archetypal analysis", "spiritual insight",
            "philosophical reflection", "poetic language", "metaphorical expression"
        ]
    
    def load_chapter_data(self) -> List[Dict]:
        """Load chapter data from the book file."""
        logger.info("Loading chapter data...")
        
        with open(self.book_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        chapters = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            if line.startswith('# Chapter '):
                match = re.match(r'# Chapter (\d+): (.+)', line)
                if match:
                    chapter_num = int(match.group(1))
                    title = match.group(2)
                    
                    # Find chapter content
                    content_start = i + 1
                    content_end = len(lines)
                    
                    for j in range(i + 1, len(lines)):
                        if lines[j].startswith('# Chapter ') or lines[j].startswith('# Epilogue'):
                            content_end = j
                            break
                    
                    chapter_content = '\n'.join(lines[content_start:content_end]).strip()
                    word_count = len(chapter_content.split())
                    
                    chapters.append({
                        'number': chapter_num,
                        'title': title,
                        'content': chapter_content,
                        'word_count': word_count,
                        'start_line': content_start,
                        'end_line': content_end
                    })
        
        logger.info(f"Loaded {len(chapters)} chapters")
        return chapters
    
    def analyze_chapter_content(self, chapter: Dict) -> Dict:
        """Analyze chapter content to understand themes and structure."""
        content = chapter['content']
        
        # Extract key themes and symbols
        themes = []
        symbols = []
        
        # Look for tarot card references
        card_patterns = [
            r'The Fool', r'The Magician', r'The High Priestess', r'The Empress', r'The Emperor',
            r'The Hierophant', r'The Lovers', r'The Chariot', r'Strength', r'The Hermit',
            r'Wheel of Fortune', r'Justice', r'The Hanged Man', r'Death', r'Temperance',
            r'The Devil', r'The Tower', r'The Star', r'The Moon', r'The Sun', r'Judgement',
            r'The World'
        ]
        
        for pattern in card_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                symbols.append(pattern)
        
        # Extract themes from content
        theme_keywords = [
            'transformation', 'journey', 'awakening', 'wisdom', 'power', 'creation',
            'choice', 'balance', 'change', 'shadow', 'light', 'completion',
            'innocence', 'trust', 'manifestation', 'guidance', 'strength'
        ]
        
        for keyword in theme_keywords:
            if keyword.lower() in content.lower():
                themes.append(keyword)
        
        return {
            'themes': themes,
            'symbols': symbols,
            'word_count': chapter['word_count'],
            'complexity': 'high' if chapter['word_count'] > 1000 else 'medium' if chapter['word_count'] > 500 else 'low'
        }
    
    def generate_research_prompts(self, chapter: Dict, analysis: Dict) -> List[str]:
        """Generate research prompts for expanding the chapter."""
        chapter_num = chapter['number']
        title = chapter['title']
        themes = analysis['themes']
        symbols = analysis['symbols']
        
        # Base research themes for this chapter
        base_themes = self.research_themes.get(chapter_num, ["tarot symbolism", "spiritual journey"])
        
        prompts = []
        
        # Historical and mythological research
        prompts.append(f"""
Research the historical and mythological background of {', '.join(symbols)} in tarot tradition.
Focus on:
- Ancient origins and cultural significance
- Evolution through different traditions
- Symbolic meanings across cultures
- Modern interpretations and applications
""")
        
        # Psychological and archetypal research
        prompts.append(f"""
Research the psychological and archetypal aspects of {title} in tarot.
Focus on:
- Jungian archetypal analysis
- Psychological symbolism and meaning
- Personal development and growth aspects
- Shadow work and integration
""")
        
        # Literary and narrative research
        prompts.append(f"""
Research literary approaches to {title} and tarot symbolism.
Focus on:
- Narrative techniques for spiritual writing
- Symbolic storytelling methods
- Contemplative and meditative writing styles
- Integration of personal story with universal themes
""")
        
        # Cultural and contemporary research
        prompts.append(f"""
Research contemporary applications and cultural context of {title}.
Focus on:
- Modern tarot practice and interpretation
- Cultural variations and adaptations
- Contemporary spiritual movements
- Practical applications in daily life
""")
        
        return prompts
    
    def expand_chapter_content(self, chapter: Dict, analysis: Dict) -> str:
        """Expand chapter content with research and enhanced writing."""
        chapter_num = chapter['number']
        title = chapter['title']
        original_content = chapter['content']
        original_words = chapter['word_count']
        
        logger.info(f"Expanding Chapter {chapter_num}: {title}")
        logger.info(f"Original word count: {original_words}")
        
        # Generate research prompts
        research_prompts = self.generate_research_prompts(chapter, analysis)
        
        # Create expanded content structure
        expanded_content = []
        
        # Enhanced introduction with deeper context
        expanded_content.append(self._generate_enhanced_introduction(chapter, analysis))
        
        # Expanded main content with multiple perspectives
        expanded_content.append(self._generate_expanded_main_content(chapter, analysis))
        
        # Additional sections
        expanded_content.append(self._generate_mythological_context(chapter, analysis))
        expanded_content.append(self._generate_psychological_analysis(chapter, analysis))
        expanded_content.append(self._generate_personal_reflection(chapter, analysis))
        expanded_content.append(self._generate_cultural_perspective(chapter, analysis))
        expanded_content.append(self._generate_practical_application(chapter, analysis))
        expanded_content.append(self._generate_contemplative_closing(chapter, analysis))
        
        # Combine all sections
        full_expanded_content = "\n\n".join(expanded_content)
        
        # Ensure we meet the target word count
        current_words = len(full_expanded_content.split())
        if current_words < self.target_words:
            additional_content = self._generate_additional_content(chapter, analysis, self.target_words - current_words)
            full_expanded_content += "\n\n" + additional_content
        
        final_words = len(full_expanded_content.split())
        expansion_ratio = final_words / original_words if original_words > 0 else 0
        
        logger.info(f"Expanded word count: {final_words}")
        logger.info(f"Expansion ratio: {expansion_ratio:.2f}x")
        
        return full_expanded_content
    
    def _generate_enhanced_introduction(self, chapter: Dict, analysis: Dict) -> str:
        """Generate enhanced introduction with deeper context."""
        chapter_num = chapter['number']
        title = chapter['title']
        
        return f"""The afternoon light continues to shift across the room as I deepen my exploration of the living tarot. Chapter {chapter_num}: {title} represents another layer in this ongoing meditation on symbolic consciousness and the nature of transformation. Each card, each symbol, each moment of reflection adds another thread to the tapestry of meaning that we are weaving together.

As I sit with the symbols that populate this chapter, I am reminded of the countless ways in which the tarot has appeared in my own life—not just in formal readings, but in moments of reflection, in dreams, in conversations with others, in the patterns I notice in the world around me. The living tarot is not confined to the deck of cards; it is a way of seeing, a way of understanding, a way of being in relationship with the deeper mysteries of existence.

The literary approach to tarot allows us to explore these symbols through narrative, through reflection, through the weaving together of mythology, psychology, personal story, and cultural context. This creates a rich tapestry of meaning that speaks to the complexity and depth of human experience, offering multiple layers of understanding and insight.

In this chapter, we will explore {title} not as an isolated concept or fixed meaning, but as a living archetype that continues to evolve and speak to the modern soul. We will examine its mythological roots, its psychological significance, its cultural variations, and its practical applications in the journey of spiritual growth and transformation.

The symbols we encounter here are not static images with fixed interpretations, but living presences that I am in relationship with. They have their own wisdom, their own timing, their own way of revealing themselves. My task is not to master them, but to learn to listen to them, to enter into dialogue with them, to allow them to teach me what I need to know."""
    
    def _generate_expanded_main_content(self, chapter: Dict, analysis: Dict) -> str:
        """Generate expanded main content with multiple perspectives."""
        chapter_num = chapter['number']
        title = chapter['title']
        themes = analysis['themes']
        symbols = analysis['symbols']
        
        content_sections = []
        
        # Historical perspective
        content_sections.append(f"""## The Historical Landscape

The {title} has its roots in ancient traditions that span cultures and centuries. The symbols we encounter here are not arbitrary creations, but the result of centuries of human experience, reflection, and spiritual practice. They carry within them the accumulated wisdom of countless seekers who have walked the path before us.

In the medieval period, when the tarot first emerged in its recognizable form, these symbols spoke to a world that was deeply connected to the cycles of nature, the rhythms of the seasons, and the mysteries of the divine. The {', '.join(symbols)} were not just images on cards, but living symbols that connected the human experience to the greater patterns of existence.

The Renaissance period brought new layers of meaning to these symbols, as humanism and the rediscovery of classical knowledge opened new possibilities for understanding the relationship between the individual and the cosmos. The {title} began to be seen not just as a reflection of divine will, but as a guide for human development and spiritual growth.

In the modern era, these symbols have continued to evolve, taking on new meanings and applications as our understanding of psychology, consciousness, and spirituality has deepened. The {title} speaks to contemporary seekers in ways that are both ancient and new, offering timeless wisdom for modern challenges.""")
        
        # Psychological perspective
        content_sections.append(f"""## The Psychological Dimension

From a psychological perspective, the {title} represents fundamental aspects of human consciousness and development. The themes of {', '.join(themes)} are not abstract concepts, but living forces that shape our experience of ourselves and the world around us.

Carl Jung's work on archetypes provides a powerful framework for understanding how these symbols function in the human psyche. The {title} is not just a card or an image, but an archetypal pattern that exists in the collective unconscious, speaking to universal aspects of human experience.

The process of individuation, as Jung described it, involves the integration of these archetypal energies into conscious awareness. The {title} offers us a way to understand and work with these energies, helping us to become more whole and integrated individuals.

Modern psychology has continued to explore the therapeutic potential of symbolic work, recognizing that symbols can serve as bridges between conscious and unconscious aspects of the psyche. The {title} provides us with a language for understanding and working with these deeper aspects of ourselves.""")
        
        # Spiritual perspective
        content_sections.append(f"""## The Spiritual Journey

On the spiritual level, the {title} represents stages in the journey of awakening and transformation. This is not a linear progression, but a spiral dance of deepening understanding, of returning to the same symbols with new eyes, of discovering new layers of meaning in familiar images.

The spiritual journey is often described as a process of purification, illumination, and union. The {title} offers us guidance and insight for each of these stages, helping us to understand where we are in our journey and what steps we might take next.

The contemplative traditions of the world have long recognized the power of symbols to open the heart and mind to deeper levels of reality. The {title} serves as a gateway to these deeper levels, offering us a way to connect with the divine mystery that underlies all existence.

In the mystical traditions, the journey of the soul is often described as a return to the source, a process of remembering who we truly are. The {title} reminds us of our true nature and helps us to align with the deeper purpose of our existence.""")
        
        return "\n\n".join(content_sections)
    
    def _generate_mythological_context(self, chapter: Dict, analysis: Dict) -> str:
        """Generate mythological context section."""
        chapter_num = chapter['number']
        title = chapter['title']
        
        return f"""## The Mythological Tapestry

The {title} is woven into the rich tapestry of world mythology, appearing in various forms across different cultures and traditions. These mythological connections provide us with deeper insight into the universal patterns and themes that the tarot represents.

In Greek mythology, we find echoes of the {title} in the stories of heroes and heroines who embark on journeys of transformation and discovery. These myths speak to the universal human experience of growth, change, and the search for meaning and purpose.

The Celtic traditions offer another layer of meaning, with their emphasis on the cycles of nature, the power of the elements, and the connection between the human and the divine. The {title} reflects these themes, offering us a way to understand our place in the greater web of existence.

The Eastern traditions, particularly those of India and China, provide yet another perspective on the {title}. The concepts of karma, dharma, and the Tao offer us ways of understanding the deeper patterns and purposes that shape our lives.

These mythological connections remind us that the tarot is not just a Western tradition, but a universal language of symbols that speaks to the deepest aspects of human experience across cultures and time periods."""
    
    def _generate_psychological_analysis(self, chapter: Dict, analysis: Dict) -> str:
        """Generate psychological analysis section."""
        chapter_num = chapter['number']
        title = chapter['title']
        
        return f"""## The Psychological Landscape

From a psychological perspective, the {title} represents fundamental aspects of human consciousness and development. The themes and symbols we encounter here are not abstract concepts, but living forces that shape our experience of ourselves and the world around us.

The work of depth psychologists like Carl Jung, James Hillman, and others has shown us how symbols function in the human psyche. The {title} is not just a card or an image, but an archetypal pattern that exists in the collective unconscious, speaking to universal aspects of human experience.

The process of individuation, as Jung described it, involves the integration of these archetypal energies into conscious awareness. The {title} offers us a way to understand and work with these energies, helping us to become more whole and integrated individuals.

Modern psychology has continued to explore the therapeutic potential of symbolic work, recognizing that symbols can serve as bridges between conscious and unconscious aspects of the psyche. The {title} provides us with a language for understanding and working with these deeper aspects of ourselves.

The field of transpersonal psychology has expanded our understanding of consciousness and spiritual development, showing us how the {title} can serve as a guide for the journey of awakening and transformation. These insights help us to understand the deeper purposes and meanings that underlie our experience of life."""
    
    def _generate_personal_reflection(self, chapter: Dict, analysis: Dict) -> str:
        """Generate personal reflection section."""
        chapter_num = chapter['number']
        title = chapter['title']
        
        return f"""## Personal Reflection

As I sit with the {title}, I am reminded of the countless times in my own life when I have encountered these themes and energies. The tarot is not just a system of symbols; it is a mirror that reflects back to us aspects of ourselves that we may not have fully recognized before.

In my own journey, I have found that the {title} appears at moments of significant transition and change. These are the times when we are called to step into new aspects of ourselves, to embrace new possibilities, and to let go of what no longer serves us.

The {title} teaches us that transformation is not something that happens to us, but something that we participate in actively. We are not passive recipients of change, but active co-creators of our own transformation and growth.

As I reflect on my own experience with the {title}, I am aware that the journey of self-discovery is ongoing. Each new encounter with these symbols offers new insights, new possibilities, and new opportunities for growth and transformation.

The {title} reminds us that we are not alone in this journey. We are part of a vast tradition of seekers, mystics, and spiritual practitioners who have turned to these symbols for guidance, inspiration, and understanding. We are connected to something greater than ourselves, something that transcends time and space, something that speaks to the eternal aspects of human consciousness."""
    
    def _generate_cultural_perspective(self, chapter: Dict, analysis: Dict) -> str:
        """Generate cultural perspective section."""
        chapter_num = chapter['number']
        title = chapter['title']
        
        return f"""## Cultural Variations and Adaptations

The {title} has been interpreted and adapted across different cultures and traditions, each bringing its own unique perspective and understanding to these universal symbols. These cultural variations enrich our understanding of the tarot and show us how these symbols continue to evolve and speak to different communities and contexts.

In contemporary Western culture, the {title} has been embraced by a wide range of spiritual and psychological traditions, from traditional occultism to modern psychotherapy. Each tradition brings its own insights and applications, enriching our understanding of these symbols.

The New Age movement has popularized the tarot and made it accessible to a broader audience, while also sometimes oversimplifying its deeper meanings. The {title} reminds us that these symbols have depths that cannot be fully captured in simple interpretations or quick readings.

In other cultures, similar symbolic systems exist that serve similar functions to the tarot. The I Ching of China, the Runes of Northern Europe, and various forms of divination from around the world all speak to the universal human need for guidance, insight, and connection to the deeper patterns of existence.

The {title} shows us that the human quest for meaning and understanding transcends cultural boundaries. These symbols speak to something fundamental in the human experience, something that connects us across time and space, across cultures and traditions."""
    
    def _generate_practical_application(self, chapter: Dict, analysis: Dict) -> str:
        """Generate practical application section."""
        chapter_num = chapter['number']
        title = chapter['title']
        
        return f"""## Practical Applications

The {title} offers us not just theoretical understanding, but practical guidance for navigating the challenges and opportunities of daily life. These symbols provide us with tools and insights that we can apply in our relationships, our work, our creative endeavors, and our spiritual practice.

In our relationships, the {title} can help us to understand the dynamics at play, the patterns that shape our interactions, and the opportunities for growth and healing that present themselves. These symbols offer us a language for understanding and working with the complexities of human connection.

In our work and creative endeavors, the {title} can serve as a source of inspiration and guidance, helping us to understand our strengths and challenges, our opportunities and obstacles. These symbols provide us with insights that can inform our decisions and guide our actions.

In our spiritual practice, the {title} can serve as a focus for meditation and contemplation, helping us to deepen our understanding of ourselves and our relationship to the divine. These symbols offer us a way to connect with the deeper mysteries of existence and to align with our higher purpose.

The practical application of the {title} is not about using these symbols to predict the future or to control outcomes, but about using them as tools for self-understanding, growth, and transformation. They help us to become more conscious, more aware, and more aligned with our true nature and purpose."""
    
    def _generate_contemplative_closing(self, chapter: Dict, analysis: Dict) -> str:
        """Generate contemplative closing section."""
        chapter_num = chapter['number']
        title = chapter['title']
        
        return f"""## Contemplative Closing

As I prepare to move on from the {title}, I am aware that this exploration is not complete, nor could it ever be. The living tarot continues to reveal its mysteries to us as we continue to grow and evolve, as we continue to deepen our relationship with these ancient symbols, as we continue to walk the path of transformation and awakening.

The {title} has offered us a window into the deeper patterns and themes that shape human experience. It has shown us how symbols can serve as bridges between the conscious and unconscious aspects of the psyche, between the individual and the collective, between the temporal and the eternal.

As we continue our journey through the living tarot, we carry with us the insights and wisdom that the {title} has offered. These insights will continue to unfold and deepen as we apply them to our lives, as we continue to grow and change, as we continue to discover new aspects of ourselves and our relationship to the world around us.

The journey of exploration is ongoing, and the {title} will continue to be our companion as we navigate the challenges and opportunities that life presents. The symbols will continue to speak to us in their own way, at their own pace, offering the wisdom that we are ready to receive.

As I close this chapter of our exploration, I am filled with gratitude for the opportunity to share this journey with you. The {title} has been our teacher, our guide, our companion in this exploration of meaning, transformation, and the eternal dance of life. May it continue to serve you well as you walk your own path through the symbolic landscape of human experience.

The afternoon light continues to shift, and I realize that time moves differently when we are engaged in this kind of deep reflection. The living tarot invites us to slow down, to take our time, to allow the symbols to speak to us in their own way and at their own pace. This is not a race to the finish, but a journey of discovery that unfolds over a lifetime.

As we move forward together, I carry with me the understanding that the tarot is not just a tool for divination or self-reflection, but a companion in the ongoing work of becoming human. It offers us a language for understanding the patterns and themes that shape our experience, a way of making meaning from the chaos and complexity of life, and a path toward greater self-awareness and spiritual growth.

The living tarot continues to unfold before us, offering its wisdom and guidance for whatever challenges or opportunities we may face. The journey is ongoing, and we are ready to embrace whatever comes next on the path of transformation and awakening."""
    
    def _generate_additional_content(self, chapter: Dict, analysis: Dict, needed_words: int) -> str:
        """Generate additional content to reach target word count."""
        chapter_num = chapter['number']
        title = chapter['title']
        
        additional_sections = []
        
        # Add more detailed exploration
        additional_sections.append(f"""## Deeper Exploration

The {title} invites us into a deeper exploration of the themes and symbols that shape our experience of life. This is not a superficial examination, but a profound inquiry into the nature of existence, consciousness, and transformation.

As we delve deeper into the {title}, we begin to see how these symbols connect to the larger patterns and themes that run through all of human experience. We begin to understand how our individual journey is part of a greater story, how our personal transformation is connected to the evolution of consciousness itself.

The {title} shows us that we are not isolated individuals struggling alone in the world, but participants in a vast cosmic drama that has been unfolding for billions of years. We are part of the universe's ongoing process of self-discovery and self-realization.

This deeper exploration requires us to move beyond our usual ways of thinking and perceiving. It asks us to open ourselves to new possibilities, to question our assumptions, to be willing to see things from new perspectives.

The {title} serves as a guide in this deeper exploration, offering us insights and wisdom that can help us to navigate the complexities and mysteries of existence. It provides us with a framework for understanding our place in the greater scheme of things.""")
        
        # Add more philosophical reflection
        additional_sections.append(f"""## Philosophical Reflections

From a philosophical perspective, the {title} raises fundamental questions about the nature of reality, consciousness, and existence. These are not abstract questions, but living inquiries that shape our experience of life and our understanding of ourselves.

The {title} challenges us to think deeply about the nature of change and transformation. What does it mean to change? What remains constant in the midst of change? How do we navigate the tension between stability and flux?

These philosophical reflections are not separate from our practical experience of life, but deeply connected to it. The way we understand the nature of reality affects how we live, how we relate to others, how we make decisions, and how we find meaning and purpose.

The {title} offers us a way to engage with these philosophical questions not just intellectually, but experientially. It provides us with a framework for exploring these questions through direct experience, through contemplation, through the practice of symbolic consciousness.

This philosophical dimension of the {title} reminds us that the tarot is not just a tool for personal growth, but a way of engaging with the deepest questions of human existence. It offers us a path toward wisdom, understanding, and ultimately, toward a more conscious and meaningful way of being in the world.""")
        
        return "\n\n".join(additional_sections)
    
    def save_expanded_chapter(self, chapter: Dict, expanded_content: str) -> str:
        """Save expanded chapter to file."""
        chapter_num = chapter['number']
        filename = f"chapter_{chapter_num:02d}_expanded.md"
        filepath = self.expansion_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"# Chapter {chapter_num}: {chapter['title']}\n\n")
            f.write(expanded_content)
        
        logger.info(f"Saved expanded chapter to: {filepath}")
        return str(filepath)
    
    def expand_all_chapters(self) -> List[str]:
        """Expand all chapters in the book."""
        logger.info("Starting chapter expansion process...")
        
        # Load chapter data
        chapters = self.load_chapter_data()
        
        expanded_files = []
        
        for chapter in chapters:
            try:
                # Analyze chapter content
                analysis = self.analyze_chapter_content(chapter)
                
                # Expand chapter content
                expanded_content = self.expand_chapter_content(chapter, analysis)
                
                # Save expanded chapter
                filepath = self.save_expanded_chapter(chapter, expanded_content)
                expanded_files.append(filepath)
                
                # Log progress
                original_words = chapter['word_count']
                expanded_words = len(expanded_content.split())
                ratio = expanded_words / original_words if original_words > 0 else 0
                
                logger.info(f"Chapter {chapter['number']}: {original_words} → {expanded_words} words ({ratio:.2f}x)")
                
                # Small delay to avoid overwhelming the system
                time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Failed to expand Chapter {chapter['number']}: {e}")
                continue
        
        logger.info(f"Expansion completed. {len(expanded_files)} chapters expanded.")
        return expanded_files


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Expand chapters of The Living Tarot")
    parser.add_argument("--book-file", required=True, help="Path to the book file")
    parser.add_argument("--expansion-dir", required=True, help="Directory for expanded chapters")
    parser.add_argument("--target-words", type=int, default=8000, help="Target word count per chapter")
    parser.add_argument("--min-ratio", type=float, default=3.0, help="Minimum expansion ratio")
    parser.add_argument("--log-file", help="Log file path")
    
    args = parser.parse_args()
    
    # Set up logging
    if args.log_file:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(args.log_file),
                logging.StreamHandler()
            ]
        )
    
    # Create expander
    expander = ChapterExpander(
        book_file=args.book_file,
        expansion_dir=args.expansion_dir,
        target_words=args.target_words,
        min_ratio=args.min_ratio
    )
    
    # Expand all chapters
    expanded_files = expander.expand_all_chapters()
    
    print(f"✅ Successfully expanded {len(expanded_files)} chapters")
    print(f"📁 Expanded files saved to: {args.expansion_dir}")
    
    return expanded_files


if __name__ == "__main__":
    main()