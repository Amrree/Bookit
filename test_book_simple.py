#!/usr/bin/env python3
"""
Simple Book Creation Test

Creates a complete book using mock LLM responses for testing the workflow.
"""

import asyncio
import json
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Mock LLM responses for testing
MOCK_RESPONSES = {
    "outline": {
        "introduction": {
            "title": "Introduction: The Ancient Art in Modern Times",
            "key_points": [
                "The resurgence of tarot in contemporary culture",
                "Bridging ancient wisdom with modern psychology",
                "What readers will discover in this journey"
            ],
            "word_count_target": 3000
        },
        "chapters": [
            {
                "chapter_number": 1,
                "title": "The Origins and Evolution of Tarot",
                "key_points": [
                    "Historical roots in 15th century Europe",
                    "Evolution from playing cards to divination tool",
                    "Cultural significance across different traditions"
                ],
                "word_count_target": 4000,
                "research_focus": "Historical development of tarot cards"
            },
            {
                "chapter_number": 2,
                "title": "Understanding the Major Arcana",
                "key_points": [
                    "The 22 cards of the Major Arcana",
                    "Symbolic meanings and interpretations",
                    "Life lessons and spiritual guidance"
                ],
                "word_count_target": 4000,
                "research_focus": "Major Arcana symbolism and meanings"
            },
            {
                "chapter_number": 3,
                "title": "The Minor Arcana: Suits and Numbers",
                "key_points": [
                    "Four suits: Cups, Wands, Swords, Pentacles",
                    "Numerical progression and meanings",
                    "Court cards and their personalities"
                ],
                "word_count_target": 4000,
                "research_focus": "Minor Arcana structure and interpretations"
            },
            {
                "chapter_number": 4,
                "title": "Modern Tarot Practices and Applications",
                "key_points": [
                    "Contemporary reading techniques",
                    "Integration with psychology and therapy",
                    "Digital tarot and online communities"
                ],
                "word_count_target": 4000,
                "research_focus": "Modern applications of tarot"
            },
            {
                "chapter_number": 5,
                "title": "Tarot and Personal Development",
                "key_points": [
                    "Self-reflection and introspection",
                    "Goal setting and decision making",
                    "Emotional intelligence and awareness"
                ],
                "word_count_target": 4000,
                "research_focus": "Personal growth through tarot"
            },
            {
                "chapter_number": 6,
                "title": "Ethics and Responsibility in Tarot Reading",
                "key_points": [
                    "Professional standards and boundaries",
                    "Ethical considerations in readings",
                    "Client care and confidentiality"
                ],
                "word_count_target": 4000,
                "research_focus": "Ethical practices in tarot"
            },
            {
                "chapter_number": 7,
                "title": "Building Your Tarot Practice",
                "key_points": [
                    "Choosing your first deck",
                    "Developing intuition and connection",
                    "Creating meaningful rituals and routines"
                ],
                "word_count_target": 4000,
                "research_focus": "Practical tarot practice development"
            },
            {
                "chapter_number": 8,
                "title": "The Future of Tarot in the Digital Age",
                "key_points": [
                    "Technology and traditional practices",
                    "Virtual readings and AI integration",
                    "Preserving authenticity in modern times"
                ],
                "word_count_target": 4000,
                "research_focus": "Future trends in tarot"
            }
        ],
        "conclusion": {
            "title": "Conclusion: Embracing Ancient Wisdom in Modern Life",
            "key_points": [
                "Key takeaways from the journey",
                "Integrating tarot into daily life",
                "The ongoing evolution of this ancient art"
            ],
            "word_count_target": 2000
        }
    }
}

def create_mock_chapter_content(chapter_title, word_count_target):
    """Create mock chapter content."""
    return f"""
# {chapter_title}

## Introduction

This chapter explores the fascinating world of {chapter_title.lower()}, delving into both historical foundations and contemporary applications. The ancient art of tarot has found new relevance in our modern world, offering insights, guidance, and personal growth opportunities for people from all walks of life.

## Historical Context

The origins of tarot can be traced back to 15th century Europe, where these cards first appeared as playing cards. Over the centuries, they evolved into powerful tools for divination, self-reflection, and spiritual guidance. The rich symbolism embedded in each card speaks to universal human experiences and archetypal patterns that transcend cultural boundaries.

## Modern Applications

In today's fast-paced world, tarot has experienced a remarkable resurgence. People are turning to these ancient cards for guidance on career decisions, relationship challenges, personal growth, and spiritual development. The practice has evolved beyond traditional fortune-telling to become a valuable tool for introspection and self-awareness.

## Practical Insights

The beauty of tarot lies in its ability to provide multiple layers of meaning. Each card can be interpreted in various ways depending on the context, the question asked, and the individual's personal journey. This flexibility makes tarot a powerful tool for personal development and decision-making.

## Contemporary Perspectives

Modern practitioners are finding innovative ways to integrate tarot into their daily lives. From morning card draws for daily guidance to elaborate spreads for complex life decisions, tarot offers a framework for reflection and contemplation that is both ancient and timeless.

## Conclusion

{chapter_title} represents just one aspect of the rich tapestry that is the tarot tradition. As we continue to explore this ancient art in our modern context, we discover new layers of meaning and application that speak to the universal human experience.

---

*This chapter has been generated as part of "Modern Tarot: Ancient Ways in a Modern World" - a comprehensive exploration of tarot in contemporary society.*
"""

def create_mock_introduction():
    """Create mock introduction content."""
    return """
# Introduction: The Ancient Art in Modern Times

## Welcome to the Journey

In a world increasingly dominated by technology and rapid change, there exists an ancient practice that continues to offer profound insights and guidance: the art of tarot. This book, "Modern Tarot: Ancient Ways in a Modern World," invites you on a journey that bridges the wisdom of the past with the challenges and opportunities of the present.

## The Resurgence of Tarot

The 21st century has witnessed an extraordinary revival of interest in tarot. No longer confined to the fringes of society or dismissed as mere superstition, tarot has found its way into mainstream culture, therapy offices, corporate boardrooms, and personal development practices. This resurgence speaks to a deep human need for meaning, guidance, and connection in an increasingly complex world.

## What This Book Offers

This comprehensive guide explores tarot from multiple perspectives:

- **Historical Foundation**: Understanding the origins and evolution of tarot from 15th century playing cards to modern divination tools
- **Symbolic Language**: Decoding the rich symbolism of the Major and Minor Arcana
- **Practical Application**: Learning how to use tarot for personal growth, decision-making, and self-reflection
- **Modern Integration**: Discovering how tarot fits into contemporary life, psychology, and spirituality
- **Ethical Practice**: Understanding the responsibilities and ethics of tarot reading
- **Future Directions**: Exploring how technology and tradition can coexist

## A Bridge Between Worlds

Tarot serves as a unique bridge between ancient wisdom and modern understanding. The cards speak to universal human experiences—love, loss, growth, challenge, and transformation—while offering a framework for reflection that is both timeless and adaptable to contemporary life.

## How to Use This Book

Whether you are a complete beginner or someone with some experience in tarot, this book is designed to meet you where you are. Each chapter builds upon the previous one, creating a comprehensive foundation for understanding and practicing tarot in the modern world.

## The Journey Ahead

As you turn these pages, you'll discover that tarot is far more than fortune-telling or mystical divination. It's a tool for self-discovery, a language of symbols, and a pathway to deeper understanding of yourself and the world around you.

Welcome to the world of modern tarot—where ancient wisdom meets contemporary life, and where every card drawn is an invitation to explore, reflect, and grow.

---

*"The tarot is a mirror of the soul, reflecting not what will be, but what is, and what could be if we choose to see it clearly."*
"""

def create_mock_conclusion():
    """Create mock conclusion content."""
    return """
# Conclusion: Embracing Ancient Wisdom in Modern Life

## The Journey Completed

As we reach the end of our exploration of "Modern Tarot: Ancient Ways in a Modern World," we find ourselves at a unique intersection of past and present, tradition and innovation, ancient wisdom and contemporary understanding. The journey through these pages has revealed tarot not as a relic of the past, but as a living, breathing practice that continues to evolve and adapt to our changing world.

## Key Discoveries

Throughout this book, we've uncovered several fundamental truths about tarot in the modern world:

### 1. Timeless Relevance
The symbols and archetypes found in tarot speak to universal human experiences that transcend time and culture. The challenges, joys, and transformations depicted in the cards are as relevant today as they were centuries ago.

### 2. Modern Applications
Tarot has found new life in contemporary settings, from therapy offices to corporate training rooms, from personal development workshops to digital platforms. Its versatility makes it a valuable tool for anyone seeking guidance and self-understanding.

### 3. Personal Growth Tool
Beyond divination, tarot serves as a powerful instrument for self-reflection, decision-making, and personal development. It encourages us to pause, reflect, and consider our choices from multiple perspectives.

### 4. Ethical Responsibility
As tarot gains mainstream acceptance, practitioners bear the responsibility to approach their work with integrity, compassion, and ethical awareness. The power of tarot comes with the duty to use it wisely.

## Integration into Daily Life

The true value of tarot lies not in occasional readings, but in its integration into daily life. Whether through morning card draws, journaling with tarot, or using cards for decision-making, tarot can become a regular practice that supports ongoing growth and awareness.

## The Future of Tarot

As we look ahead, tarot faces both opportunities and challenges. Technology offers new ways to engage with the cards, while also raising questions about authenticity and connection. The key lies in finding balance—embracing innovation while preserving the essential human elements that make tarot meaningful.

## A Call to Action

The ancient art of tarot invites us to become active participants in our own growth and understanding. It challenges us to look beyond surface appearances and explore the deeper currents of our lives. In a world that often values speed and efficiency over reflection and depth, tarot offers a counterbalance—a space for contemplation, insight, and wisdom.

## Final Thoughts

"Modern Tarot: Ancient Ways in a Modern World" has been more than a book—it's been an invitation to explore, learn, and grow. The cards are ready to speak to you, to guide you, and to support you on your journey. The question is: are you ready to listen?

The ancient wisdom of tarot is not locked in the past; it's alive and evolving, waiting to be discovered by each new generation. As you continue your own journey with tarot, remember that you are not just learning about an ancient practice—you are becoming part of its ongoing story.

May your path with tarot be filled with insight, growth, and wisdom. The cards are in your hands now. What will they reveal?

---

*"In the end, we are all students of life, and tarot is simply one of the most beautiful and profound textbooks ever created."*
"""

async def create_mock_book():
    """Create a complete mock book."""
    
    print("🚀 Creating Mock Book: 'Modern Tarot: Ancient Ways in a Modern World'")
    print("=" * 70)
    
    # Create output directory
    output_dir = Path("output/mock_tarot_book")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Book metadata
    book_title = "Modern Tarot: Ancient Ways in a Modern World"
    author = "AI Book Writer"
    build_id = "mock_tarot_2024"
    
    # Create the full manuscript
    manuscript_parts = []
    
    # Title page
    manuscript_parts.append(f"# {book_title}")
    manuscript_parts.append(f"**Author:** {author}")
    manuscript_parts.append(f"**Build ID:** {build_id}")
    manuscript_parts.append(f"**Created:** 2024-09-09")
    manuscript_parts.append("")
    manuscript_parts.append("---")
    manuscript_parts.append("")
    
    # Introduction
    manuscript_parts.append(create_mock_introduction())
    manuscript_parts.append("")
    
    # Chapters
    outline = MOCK_RESPONSES["outline"]
    for chapter in outline["chapters"]:
        content = create_mock_chapter_content(chapter["title"], chapter["word_count_target"])
        manuscript_parts.append(content)
        manuscript_parts.append("")
    
    # Conclusion
    manuscript_parts.append(create_mock_conclusion())
    manuscript_parts.append("")
    
    # Bibliography
    manuscript_parts.append("# Bibliography")
    manuscript_parts.append("")
    manuscript_parts.append("This book draws from a rich tradition of tarot scholarship and practice. Key sources include:")
    manuscript_parts.append("")
    manuscript_parts.append("- Historical texts on tarot origins and development")
    manuscript_parts.append("- Contemporary research on tarot in psychology and therapy")
    manuscript_parts.append("- Modern practitioners' insights and experiences")
    manuscript_parts.append("- Academic studies on symbolism and archetypal psychology")
    manuscript_parts.append("- Digital resources and online tarot communities")
    manuscript_parts.append("")
    manuscript_parts.append("*Note: This is a demonstration book created for testing purposes.*")
    
    # Combine all parts
    full_manuscript = "\n".join(manuscript_parts)
    
    # Save in multiple formats
    print("📝 Saving book in multiple formats...")
    
    # Markdown
    md_path = output_dir / f"{book_title.replace(' ', '_')}.md"
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(full_manuscript)
    print(f"✅ Markdown saved: {md_path}")
    
    # Create build log
    build_log = {
        "book_metadata": {
            "title": book_title,
            "theme": "Tarot, Divination, Spirituality, Modern Applications",
            "author": author,
            "build_id": build_id,
            "created_at": "2024-09-09T08:30:00Z",
            "total_word_count": len(full_manuscript.split()),
            "chapter_count": len(outline["chapters"]) + 2,  # +2 for intro and conclusion
            "status": "completed"
        },
        "chapters_produced": [
            {
                "chapter_number": 0,
                "title": "Introduction: The Ancient Art in Modern Times",
                "word_count": 800,
                "status": "completed"
            }
        ] + [
            {
                "chapter_number": chapter["chapter_number"],
                "title": chapter["title"],
                "word_count": 1200,
                "status": "completed"
            }
            for chapter in outline["chapters"]
        ] + [
            {
                "chapter_number": 999,
                "title": "Conclusion: Embracing Ancient Wisdom in Modern Life",
                "word_count": 600,
                "status": "completed"
            }
        ],
        "quality_metrics": {
            "total_references": 5,
            "average_chapter_length": 1200,
            "completion_rate": 1.0
        }
    }
    
    # Save build log
    log_path = output_dir / "build_log.json"
    with open(log_path, 'w', encoding='utf-8') as f:
        json.dump(build_log, f, indent=2)
    print(f"✅ Build log saved: {log_path}")
    
    # Display summary
    print("\n" + "=" * 70)
    print("✅ MOCK BOOK CREATION COMPLETED!")
    print("=" * 70)
    print(f"📖 Title: {book_title}")
    print(f"👤 Author: {author}")
    print(f"📝 Word count: {len(full_manuscript.split()):,}")
    print(f"📚 Chapters: {len(outline['chapters']) + 2}")
    print(f"🆔 Build ID: {build_id}")
    print(f"📁 Output: {output_dir}")
    print(f"📄 Files created:")
    print(f"   - {md_path.name}")
    print(f"   - {log_path.name}")
    
    print("\n📋 Chapter Breakdown:")
    print("  ✅ Introduction: The Ancient Art in Modern Times (800 words)")
    for chapter in outline["chapters"]:
        print(f"  ✅ Chapter {chapter['chapter_number']}: {chapter['title']} (1,200 words)")
    print("  ✅ Conclusion: Embracing Ancient Wisdom in Modern Life (600 words)")
    
    print(f"\n🎉 Total: {len(full_manuscript.split()):,} words across {len(outline['chapters']) + 2} sections")
    print("\nThe mock book demonstrates the complete workflow and output format!")
    
    return build_log

if __name__ == "__main__":
    asyncio.run(create_mock_book())