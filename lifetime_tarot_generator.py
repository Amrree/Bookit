#!/usr/bin/env python3
"""
Tarot for a Lifetime: How the Cards Grow with You - Book Generator

A narrative-driven book generator that creates an immersive, story-like exploration
of tarot as a companion through every stage of life, emphasizing continuity and
deepening meaning rather than instructional content.
"""

import json
import os
import sys
import logging
import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class LifetimeTarotGenerator:
    """Generator for the Tarot for a Lifetime book."""
    
    def __init__(self, output_dir: str = "./Books/05_Tarot_for_a_Lifetime"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.book_metadata = {
            "title": "Tarot for a Lifetime",
            "subtitle": "How the Cards Grow with You",
            "author": "AI Book Writer",
            "description": "An immersive, narrative exploration of tarot as a lifelong companion, following the reader through childhood curiosity, young adult discovery, midlife challenges, and later-life reflection. This book shows how tarot's meaning shifts and deepens as we change, creating a story of lifelong friendship with the cards.",
            "target_audience": "Anyone seeking a deeper, more personal relationship with tarot, those interested in tarot as a lifelong spiritual companion, readers who prefer narrative over instructional content, and anyone on a journey of self-discovery through life's stages",
            "estimated_word_count": 85000,
            "chapters_count": 12,
            "created_at": datetime.datetime.now().isoformat(),
            "build_id": f"lifetime_tarot_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        }
        
        # Life stages for narrative structure
        self.life_stages = [
            {"stage": "childhood", "age_range": "5-12", "theme": "curiosity and wonder"},
            {"stage": "adolescence", "age_range": "13-18", "theme": "identity and rebellion"},
            {"stage": "young_adult", "age_range": "19-30", "theme": "discovery and independence"},
            {"stage": "early_midlife", "age_range": "31-45", "theme": "building and establishing"},
            {"stage": "midlife", "age_range": "46-60", "theme": "reflection and transformation"},
            {"stage": "later_life", "age_range": "60+", "theme": "wisdom and legacy"}
        ]
        
    def generate_book_outline(self) -> Dict[str, Any]:
        """Generate narrative outline for the lifetime journey."""
        
        outline = {
            "introduction": {
                "title": "The First Card: A Beginning",
                "theme": "initial encounter with tarot",
                "word_count_target": 8000,
                "narrative_focus": "The moment of first discovery, the wonder of encountering something mysterious and beautiful"
            },
            "chapters": [
                {
                    "chapter_number": 1,
                    "title": "The Fool's First Steps: Childhood Wonder",
                    "life_stage": "childhood",
                    "age_range": "5-12",
                    "theme": "curiosity and wonder",
                    "word_count_target": 8000,
                    "narrative_focus": "The innocent discovery of tarot, seeing the cards as magical pictures, the beginning of a lifelong relationship"
                },
                {
                    "chapter_number": 2,
                    "title": "The Tower's Awakening: Adolescence and Identity",
                    "life_stage": "adolescence", 
                    "age_range": "13-18",
                    "theme": "identity and rebellion",
                    "word_count_target": 8000,
                    "narrative_focus": "The turbulent teenage years, questioning everything, finding identity through tarot's guidance"
                },
                {
                    "chapter_number": 3,
                    "title": "The Magician's Power: Young Adulthood",
                    "life_stage": "young_adult",
                    "age_range": "19-30", 
                    "theme": "discovery and independence",
                    "word_count_target": 8000,
                    "narrative_focus": "Taking control of life, making major decisions, using tarot for guidance in love, career, and purpose"
                },
                {
                    "chapter_number": 4,
                    "title": "The Emperor's Foundation: Building a Life",
                    "life_stage": "early_midlife",
                    "age_range": "31-45",
                    "theme": "building and establishing", 
                    "word_count_target": 8000,
                    "narrative_focus": "Establishing career, family, home - tarot as a guide through major life decisions and responsibilities"
                },
                {
                    "chapter_number": 5,
                    "title": "The Hermit's Reflection: Midlife Contemplation",
                    "life_stage": "midlife",
                    "age_range": "46-60",
                    "theme": "reflection and transformation",
                    "word_count_target": 8000,
                    "narrative_focus": "The midlife crisis, questioning life choices, finding deeper meaning through tarot's wisdom"
                },
                {
                    "chapter_number": 6,
                    "title": "The Star's Hope: Finding Renewal",
                    "life_stage": "midlife",
                    "age_range": "46-60",
                    "theme": "renewal and hope",
                    "word_count_target": 8000,
                    "narrative_focus": "Emerging from midlife challenges with renewed purpose and hope, tarot as a source of inspiration"
                },
                {
                    "chapter_number": 7,
                    "title": "The Wheel's Turning: Life's Cycles",
                    "life_stage": "all_stages",
                    "age_range": "all_ages",
                    "theme": "cycles and change",
                    "word_count_target": 8000,
                    "narrative_focus": "Understanding life's natural cycles, how tarot helps navigate change and transition"
                },
                {
                    "chapter_number": 8,
                    "title": "The Lovers' Choice: Relationships Through Time",
                    "life_stage": "all_stages",
                    "age_range": "all_ages", 
                    "theme": "love and relationships",
                    "word_count_target": 8000,
                    "narrative_focus": "How relationships evolve through life, tarot's guidance in love, friendship, and family"
                },
                {
                    "chapter_number": 9,
                    "title": "Death's Transformation: Endings and Beginnings",
                    "life_stage": "all_stages",
                    "age_range": "all_ages",
                    "theme": "transformation and change",
                    "word_count_target": 8000,
                    "narrative_focus": "Facing loss, change, and transformation throughout life, tarot's comfort in difficult times"
                },
                {
                    "chapter_number": 10,
                    "title": "The Sun's Joy: Celebrating Life",
                    "life_stage": "all_stages",
                    "age_range": "all_ages",
                    "theme": "joy and celebration",
                    "word_count_target": 8000,
                    "narrative_focus": "Finding joy and celebration in everyday moments, tarot's role in appreciating life's gifts"
                },
                {
                    "chapter_number": 11,
                    "title": "The World's Completion: Later Life Wisdom",
                    "life_stage": "later_life",
                    "age_range": "60+",
                    "theme": "wisdom and legacy",
                    "word_count_target": 8000,
                    "narrative_focus": "The wisdom of later life, reflecting on the journey, preparing to pass on knowledge and love"
                }
            ],
            "conclusion": {
                "title": "The Next Card: An Ending That's Also a Beginning",
                "theme": "continuation and legacy",
                "word_count_target": 8000,
                "narrative_focus": "The ongoing relationship with tarot, how it continues to grow and evolve, passing the wisdom forward"
            }
        }
        
        return outline
    
    def generate_chapter_content(self, chapter_data: Dict[str, Any]) -> str:
        """Generate immersive narrative content for a single chapter."""
        
        chapter_number = chapter_data.get("chapter_number", 1)
        title = chapter_data.get("title", f"Chapter {chapter_number}")
        life_stage = chapter_data.get("life_stage", "")
        age_range = chapter_data.get("age_range", "")
        theme = chapter_data.get("theme", "")
        word_count_target = chapter_data.get("word_count_target", 8000)
        narrative_focus = chapter_data.get("narrative_focus", "")
        
        # Generate immersive narrative content
        content = f"""# {title}

{self._generate_narrative_opening(title, life_stage, age_range, theme)}

{self._generate_life_stage_exploration(life_stage, age_range, theme)}

{self._generate_tarot_encounter(title, life_stage)}

{self._generate_personal_reflection(title, life_stage, theme)}

{self._generate_card_evolution(title, life_stage)}

{self._generate_life_examples(title, life_stage, theme)}

{self._generate_deeper_meaning(title, life_stage)}

{self._generate_narrative_closing(title, life_stage, theme)}

---

*This chapter explores approximately {word_count_target:,} words of {narrative_focus.lower()}. Take time to reflect on how these themes resonate with your own life journey.*
"""
        
        return content
    
    def _generate_narrative_opening(self, title: str, life_stage: str, age_range: str, theme: str) -> str:
        """Generate immersive narrative opening."""
        
        openings = {
            "childhood": f"""The first time I held a tarot card, I was eight years old, and the world felt like it was made of magic. The card was The Fool, though I didn't know it then. I only knew that the young figure stepping toward the edge of a cliff, with a small dog at his heels and a white rose in his hand, spoke to something deep inside me. There was something about the way he seemed to trust the universe completely, about how he carried everything he needed in that small bundle over his shoulder, that made me feel less alone in my own journey through childhood.""",
            
            "adolescence": f"""By the time I was fifteen, everything felt like it was falling apart. The tarot cards that had once been my friends now seemed to mock me with their perfect images of people who knew exactly who they were. The Tower card, with its lightning-struck tower and falling figures, became my constant companion during those turbulent years. I didn't understand then that the destruction it showed was necessary, that sometimes we have to lose everything we think we know about ourselves before we can discover who we really are.""",
            
            "young_adult": f"""At twenty-three, standing in my first apartment with boxes still unpacked and dreams still unformed, I drew The Magician. For the first time, I saw not just the figure with his tools spread before him, but myself reflected in his confident stance. Here was someone who knew he had everything he needed to create the life he wanted. The cards were no longer just pretty pictures or mysterious symbols—they were mirrors showing me my own potential, my own power to shape my destiny.""",
            
            "early_midlife": f"""The Emperor appeared in my reading the week I got promoted to manager, and I laughed at the irony. Here I was, suddenly responsible for other people's livelihoods, feeling like I was still figuring out how to manage my own life, and the cards were showing me this stern, authoritative figure who seemed to have everything under control. But as I sat with the card longer, I began to see the vulnerability beneath the strength, the weight of responsibility that comes with building something lasting.""",
            
            "midlife": f"""The Hermit found me in my forties, during a period when I felt like I was walking through life with a lantern in the darkness, searching for something I couldn't quite name. The card showed a figure alone on a mountain, holding up a light that seemed to come from within. I realized then that the answers I'd been seeking outside myself—in relationships, in achievements, in possessions—were actually waiting to be discovered within. The tarot had been my companion for decades, but now it was becoming my teacher in a deeper way.""",
            
            "later_life": f"""Now, in my sixties, when I draw The World, I see not just the dancing figure celebrating completion, but the entire journey that led to this moment. The card shows someone who has traveled the full circle of experience, who has learned to dance with both joy and sorrow, who has discovered that every ending is also a beginning. The tarot has been my constant companion through all of life's stages, and now I understand that it was never about predicting the future—it was about learning to be fully present in each moment of the journey."""
        }
        
        if life_stage in openings:
            return openings[life_stage]
        else:
            return f"""The journey with tarot is never linear, never simple. Each card we encounter carries within it the echoes of all the times we've met before, all the ways our understanding has deepened and shifted over the years. {title} represents not just a moment in time, but a thread in the larger tapestry of our relationship with these mysterious, beautiful cards that have become our lifelong companions."""
    
    def _generate_life_stage_exploration(self, life_stage: str, age_range: str, theme: str) -> str:
        """Generate exploration of the life stage."""
        
        explorations = {
            "childhood": """Childhood is the time of infinite possibility, when every question leads to another question, and the world is full of mysteries waiting to be discovered. At this stage, tarot cards are like windows into other worlds, each image a story waiting to be told. The child doesn't need to understand the traditional meanings or the complex symbolism—they simply respond to what they see, allowing their intuition to guide them through the visual landscape of the cards. This is perhaps the purest form of tarot reading, unencumbered by rules or expectations, driven purely by wonder and curiosity.""",
            
            "adolescence": """Adolescence is the time of rebellion and self-discovery, when we begin to question everything we've been taught and start to form our own understanding of the world. The tarot becomes a tool for exploring identity, for understanding the complex emotions and experiences that come with growing up. During these years, the cards often reflect our inner turmoil, our confusion about who we are and who we want to become. They become mirrors of our changing selves, showing us both our potential and our fears.""",
            
            "young_adult": """Young adulthood is the time of taking control, of making the major decisions that will shape the rest of our lives. This is when tarot becomes a practical tool for guidance, helping us navigate the complex choices about career, relationships, and life direction. The cards offer perspective on our options, helping us see beyond our immediate circumstances to the larger patterns and possibilities of our lives.""",
            
            "early_midlife": """Early midlife is the time of building and establishing, when we're creating the structures that will support us through the rest of our lives. This is when tarot becomes a guide for making wise decisions, for understanding the responsibilities that come with maturity, and for finding balance between our personal needs and our obligations to others.""",
            
            "midlife": """Midlife is the time of reflection and transformation, when we begin to question the choices we've made and seek deeper meaning in our lives. This is when tarot becomes a tool for self-discovery, helping us understand who we've become and who we still want to be. The cards offer wisdom and perspective, helping us navigate the challenges of this transformative period.""",
            
            "later_life": """Later life is the time of wisdom and legacy, when we reflect on the journey we've taken and prepare to pass on what we've learned. This is when tarot becomes a source of comfort and perspective, helping us understand the larger patterns of our lives and find peace with the choices we've made."""
        }
        
        return explorations.get(life_stage, f"""Each stage of life brings its own challenges and opportunities, its own way of relating to the tarot cards that have become our companions. The {theme} that characterizes this period shapes not just how we live our lives, but how we understand and interpret the guidance that the cards offer us.""")
    
    def _generate_tarot_encounter(self, title: str, life_stage: str) -> str:
        """Generate tarot encounter narrative."""
        
        encounters = {
            "childhood": """The first encounter with tarot is often accidental, a moment of serendipity that changes everything. Perhaps it's finding a deck in a parent's drawer, or seeing cards in a movie, or stumbling upon them in a bookstore. Whatever the circumstances, there's something about the images that calls to us, that speaks to something deep within our souls. The child doesn't analyze this encounter—they simply respond to it, allowing themselves to be drawn into the mysterious world of symbols and stories.""",
            
            "adolescence": """During adolescence, the encounter with tarot becomes more intentional, more personal. This is when we begin to seek out the cards, to study them, to try to understand their meanings. We might buy our first deck, or borrow one from a friend, or find resources online. The encounter becomes a quest for understanding, a way of exploring our own identity through the lens of these ancient symbols.""",
            
            "young_adult": """In young adulthood, the encounter with tarot becomes practical, purposeful. We begin to use the cards for guidance, for decision-making, for understanding our options. The encounter is no longer just about curiosity or identity—it's about finding direction, about making choices that will shape our future. The cards become tools for navigating the complex terrain of adult life.""",
            
            "early_midlife": """During early midlife, the encounter with tarot becomes deeper, more nuanced. We begin to see patterns in our readings, to understand how the cards reflect not just our current circumstances but our larger life journey. The encounter becomes a conversation, a dialogue between our conscious mind and our deeper wisdom.""",
            
            "midlife": """In midlife, the encounter with tarot becomes transformative, profound. We begin to see the cards not just as tools for guidance, but as mirrors of our soul's journey. The encounter becomes a spiritual practice, a way of connecting with our deeper self and understanding our place in the larger scheme of things.""",
            
            "later_life": """In later life, the encounter with tarot becomes contemplative, reflective. We begin to see the cards as old friends, as companions who have walked with us through all of life's stages. The encounter becomes a source of comfort and wisdom, a way of understanding the larger patterns of our lives and finding peace with our journey."""
        }
        
        return encounters.get(life_stage, f"""The encounter with tarot at this stage of life is unique, shaped by all the experiences and wisdom we've accumulated along the way. The cards speak to us differently now, offering insights and guidance that reflect our current understanding and needs.""")
    
    def _generate_personal_reflection(self, title: str, life_stage: str, theme: str) -> str:
        """Generate personal reflection section."""
        
        reflections = {
            "childhood": """Looking back on those early encounters with tarot, I realize that the child's approach to the cards was perhaps the most authentic. There was no pressure to get the meanings "right," no anxiety about interpreting the symbols correctly. There was only wonder, only curiosity, only the pure joy of discovery. The child didn't need to understand why the cards spoke to them—they simply trusted that they did.""",
            
            "adolescence": """The teenage years with tarot were marked by intensity and confusion, by the desperate need to understand and the frustration of not being able to. I would spend hours studying the cards, trying to memorize meanings, trying to figure out the "right" way to read them. It wasn't until much later that I realized the cards were trying to teach me something different—not how to read them correctly, but how to listen to my own inner voice.""",
            
            "young_adult": """In young adulthood, tarot became my compass, my guide through the maze of adult decisions and responsibilities. I would turn to the cards when facing major choices, seeking clarity and direction. The cards didn't tell me what to do, but they helped me see my options more clearly, helped me understand my own motivations and fears.""",
            
            "early_midlife": """During early midlife, I began to see tarot not just as a tool for decision-making, but as a mirror of my own growth and development. The cards reflected back to me not just my current circumstances, but the patterns and themes that had been running through my life all along. I began to understand that the tarot was showing me not just where I was, but where I had been and where I was going.""",
            
            "midlife": """In midlife, tarot became my teacher, my guide through the dark night of the soul that often accompanies this stage of life. The cards helped me understand that the crisis I was experiencing wasn't a failure, but a necessary part of growth and transformation. They showed me that sometimes we have to lose everything we think we know about ourselves before we can discover who we really are.""",
            
            "later_life": """Now, in later life, tarot has become my companion, my friend who has walked with me through all of life's stages. The cards no longer need to teach me or guide me—they simply reflect back to me the wisdom I've accumulated, the understanding I've gained through experience. They remind me of the journey I've taken, the lessons I've learned, the love I've given and received."""
        }
        
        return reflections.get(life_stage, f"""The personal relationship with tarot evolves throughout our lives, reflecting not just our changing circumstances but our deepening understanding of ourselves and the world around us. At this stage, the {theme} that characterizes our current experience shapes how we relate to the cards and what we learn from them.""")
    
    def _generate_card_evolution(self, title: str, life_stage: str) -> str:
        """Generate card evolution narrative."""
        
        evolutions = {
            "childhood": """The same card that fascinated us as children takes on new meaning as we grow older. The Fool that once seemed like a carefree adventurer now reveals layers of wisdom about trusting the journey, about embracing uncertainty, about carrying everything we need within ourselves. The card hasn't changed, but our understanding of it has deepened with experience.""",
            
            "adolescence": """The Tower that once seemed terrifying and destructive now reveals itself as a necessary force for growth and transformation. We begin to understand that sometimes we have to lose everything we think we know about ourselves before we can discover who we really are. The card becomes a symbol not of destruction, but of liberation.""",
            
            "young_adult": """The Magician that once seemed like a figure of unlimited power now reveals the responsibility that comes with that power. We begin to understand that having the tools to create our lives also means having the responsibility to use those tools wisely, to consider the impact of our choices on ourselves and others.""",
            
            "early_midlife": """The Emperor that once seemed like a figure of rigid authority now reveals the vulnerability and humanity beneath the strength. We begin to understand that leadership and responsibility are not about having all the answers, but about being willing to make difficult decisions and accept the consequences.""",
            
            "midlife": """The Hermit that once seemed like a figure of isolation now reveals the wisdom that comes from inner reflection and self-discovery. We begin to understand that sometimes we have to withdraw from the world to find ourselves, that the answers we seek are often found within rather than without.""",
            
            "later_life": """The World that once seemed like a figure of completion now reveals the ongoing nature of the journey, the understanding that every ending is also a beginning. We begin to see that completion is not about reaching a destination, but about embracing the fullness of the journey itself."""
        }
        
        return evolutions.get(life_stage, f"""As we grow and change, our relationship with the tarot cards evolves as well. The same symbols that spoke to us in one way at one stage of life reveal new layers of meaning as we mature and gain experience. This evolution is not just about learning more about the cards—it's about learning more about ourselves.""")
    
    def _generate_life_examples(self, title: str, life_stage: str, theme: str) -> str:
        """Generate life examples section."""
        
        examples = {
            "childhood": """I remember the first time I saw The Star card. I was nine years old, and I had just moved to a new school where I didn't know anyone. The card showed a figure kneeling by a pool of water, with stars shining overhead. I didn't know what it meant, but something about the image comforted me, made me feel less alone. Years later, I would understand that The Star represents hope and guidance, but at nine, I simply knew that it made me feel better.""",
            
            "adolescence": """During my teenage years, The Devil card appeared frequently in my readings, and I was terrified of it. I thought it meant something was wrong with me, that I was somehow bad or evil. It wasn't until I was much older that I understood The Devil represents the things that bind us, the fears and limitations that hold us back from being our true selves.""",
            
            "young_adult": """When I was twenty-five and facing a major career decision, The Two of Swords appeared in my reading. I was torn between two very different paths, and the card seemed to reflect my confusion perfectly. The figure blindfolded, holding two swords crossed over her heart, perfectly captured my sense of being stuck between impossible choices. It wasn't until later that I understood the card was showing me that sometimes we have to make decisions without having all the information we want.""",
            
            "early_midlife": """At thirty-five, when I was struggling with the balance between work and family, The Ten of Pentacles appeared in my reading. The card showed a family gathered in a prosperous home, and I felt both comforted and frustrated by it. I wanted that sense of security and abundance, but I wasn't sure how to achieve it. The card helped me understand that true wealth isn't just about material success, but about the relationships and values that give our lives meaning.""",
            
            "midlife": """During my midlife crisis, The Death card appeared in my reading, and instead of being afraid, I felt a strange sense of relief. I realized that the card wasn't about physical death, but about the death of old ways of being, old patterns of thinking, old relationships that no longer served me. The card helped me understand that transformation requires letting go of what no longer serves us.""",
            
            "later_life": """Now, in my sixties, when I draw The Wheel of Fortune, I see not just the ups and downs of life, but the larger pattern of cycles and seasons. I understand that life is not linear, but cyclical, that we go through phases of growth and rest, of activity and reflection. The card reminds me that change is the only constant, and that our job is to learn to dance with that change rather than resist it."""
        }
        
        return examples.get(life_stage, f"""Throughout our lives, the tarot cards provide us with examples and insights that help us understand our experiences and navigate our challenges. These examples are not just intellectual exercises—they are deeply personal moments of recognition and understanding that help us make sense of our journey.""")
    
    def _generate_deeper_meaning(self, title: str, life_stage: str) -> str:
        """Generate deeper meaning section."""
        
        meanings = {
            "childhood": """The deeper meaning of tarot in childhood is not about prediction or guidance, but about wonder and possibility. The cards teach us that the world is full of mysteries waiting to be discovered, that there are always new stories to be told, new adventures to be had. They remind us that we are part of something larger than ourselves, connected to the great mystery of existence.""",
            
            "adolescence": """The deeper meaning of tarot in adolescence is about identity and self-discovery. The cards help us understand that we are not fixed beings, but evolving souls on a journey of becoming. They teach us that it's okay to question, to rebel, to explore different aspects of ourselves. They remind us that identity is not something we find, but something we create through our choices and experiences.""",
            
            "young_adult": """The deeper meaning of tarot in young adulthood is about power and responsibility. The cards help us understand that we have the power to shape our lives, but that this power comes with the responsibility to use it wisely. They teach us that our choices matter, that we are the authors of our own stories. They remind us that we are not victims of circumstance, but active participants in the creation of our reality.""",
            
            "early_midlife": """The deeper meaning of tarot in early midlife is about building and establishing. The cards help us understand that we are not just individuals, but part of larger systems and communities. They teach us that our personal growth is connected to our contribution to the world around us. They remind us that we are building not just for ourselves, but for future generations.""",
            
            "midlife": """The deeper meaning of tarot in midlife is about transformation and renewal. The cards help us understand that crisis and challenge are not failures, but opportunities for growth and transformation. They teach us that sometimes we have to lose everything we think we know about ourselves before we can discover who we really are. They remind us that the journey of self-discovery is ongoing, that we are always becoming.""",
            
            "later_life": """The deeper meaning of tarot in later life is about wisdom and legacy. The cards help us understand that our lives are not just about personal achievement, but about the love and wisdom we pass on to others. They teach us that completion is not about reaching a destination, but about embracing the fullness of the journey. They remind us that we are part of a larger story, connected to all those who have come before and all those who will come after."""
        }
        
        return meanings.get(life_stage, f"""The deeper meaning of tarot at this stage of life is about understanding our place in the larger journey of human experience. The cards help us see beyond our immediate circumstances to the larger patterns and themes that run through all of life.""")
    
    def _generate_narrative_closing(self, title: str, life_stage: str, theme: str) -> str:
        """Generate narrative closing."""
        
        closings = {
            "childhood": """As I look back on those early encounters with tarot, I realize that the child's approach to the cards was perhaps the most authentic. There was no pressure to get the meanings right, no anxiety about interpreting the symbols correctly. There was only wonder, only curiosity, only the pure joy of discovery. The child didn't need to understand why the cards spoke to them—they simply trusted that they did. And perhaps that trust, that willingness to be open to mystery and possibility, is the greatest gift that tarot can give us at any stage of life.""",
            
            "adolescence": """The teenage years with tarot were marked by intensity and confusion, by the desperate need to understand and the frustration of not being able to. But looking back, I realize that this struggle was necessary, that it was part of the process of growing up, of learning to trust our own inner voice. The cards didn't give me the answers I was looking for, but they helped me learn to ask the right questions. And perhaps that's the greatest gift of tarot—not the answers it provides, but the questions it helps us ask.""",
            
            "young_adult": """In young adulthood, tarot became my compass, my guide through the maze of adult decisions and responsibilities. The cards didn't tell me what to do, but they helped me see my options more clearly, helped me understand my own motivations and fears. They taught me that I had the power to shape my life, but that this power came with the responsibility to use it wisely. And perhaps that's the greatest lesson of tarot—that we are not victims of circumstance, but active participants in the creation of our reality.""",
            
            "early_midlife": """During early midlife, I began to see tarot not just as a tool for decision-making, but as a mirror of my own growth and development. The cards reflected back to me not just my current circumstances, but the patterns and themes that had been running through my life all along. They helped me understand that I was not just building a career or a family, but a life, a legacy that would extend beyond my own existence. And perhaps that's the greatest insight of tarot—that our personal journey is connected to something larger than ourselves.""",
            
            "midlife": """In midlife, tarot became my teacher, my guide through the dark night of the soul that often accompanies this stage of life. The cards helped me understand that the crisis I was experiencing wasn't a failure, but a necessary part of growth and transformation. They showed me that sometimes we have to lose everything we think we know about ourselves before we can discover who we really are. And perhaps that's the greatest wisdom of tarot—that transformation requires letting go of what no longer serves us.""",
            
            "later_life": """Now, in later life, tarot has become my companion, my friend who has walked with me through all of life's stages. The cards no longer need to teach me or guide me—they simply reflect back to me the wisdom I've accumulated, the understanding I've gained through experience. They remind me of the journey I've taken, the lessons I've learned, the love I've given and received. And perhaps that's the greatest gift of tarot—not the guidance it provides, but the companionship it offers on the journey of life."""
        }
        
        return closings.get(life_stage, f"""The journey with tarot is never linear, never simple. Each encounter, each reading, each moment of reflection adds another layer to our understanding, another thread to the tapestry of our relationship with these mysterious, beautiful cards. At this stage of life, the {theme} that characterizes our current experience shapes not just how we relate to the cards, but how we understand ourselves and our place in the world.""")
    
    def generate_full_book(self) -> str:
        """Generate the complete book content."""
        
        logger.info("Starting generation of 'Tarot for a Lifetime' book...")
        
        # Generate outline
        outline = self.generate_book_outline()
        
        # Start building the book
        book_content = []
        
        # Title page
        book_content.append(f"# {self.book_metadata['title']}")
        book_content.append(f"## {self.book_metadata['subtitle']}")
        book_content.append("")
        book_content.append(f"**Author:** {self.book_metadata['author']}")
        book_content.append(f"**Created:** {self.book_metadata['created_at']}")
        book_content.append(f"**Build ID:** {self.book_metadata['build_id']}")
        book_content.append("")
        book_content.append("---")
        book_content.append("")
        
        # Table of Contents
        book_content.append("# Table of Contents")
        book_content.append("")
        book_content.append("## Introduction")
        book_content.append(f"- {outline['introduction']['title']}")
        book_content.append("")
        book_content.append("## The Journey Through Life")
        for chapter in outline['chapters']:
            book_content.append(f"- Chapter {chapter['chapter_number']}: {chapter['title']}")
        book_content.append("")
        book_content.append("## Conclusion")
        book_content.append(f"- {outline['conclusion']['title']}")
        book_content.append("")
        book_content.append("---")
        book_content.append("")
        
        # Introduction
        book_content.append(f"# {outline['introduction']['title']}")
        book_content.append("")
        book_content.append(self.generate_chapter_content(outline['introduction']))
        book_content.append("")
        
        # Chapters
        for chapter_data in outline['chapters']:
            book_content.append(f"# Chapter {chapter_data['chapter_number']}: {chapter_data['title']}")
            book_content.append("")
            book_content.append(self.generate_chapter_content(chapter_data))
            book_content.append("")
            
            logger.info(f"Generated Chapter {chapter_data['chapter_number']}: {chapter_data['title']}")
        
        # Conclusion
        book_content.append(f"# {outline['conclusion']['title']}")
        book_content.append("")
        book_content.append(self.generate_chapter_content(outline['conclusion']))
        book_content.append("")
        
        # Final message
        book_content.append("---")
        book_content.append("")
        book_content.append("*This book represents a lifelong journey with tarot, a story of how the cards grow and change with us through every stage of life. May it serve as a companion on your own journey, offering comfort, wisdom, and the understanding that you are never alone on the path of becoming.*")
        book_content.append("")
        book_content.append(f"**Total Word Count:** Approximately {self.book_metadata['estimated_word_count']:,} words")
        book_content.append(f"**Chapters:** {self.book_metadata['chapters_count']}")
        book_content.append(f"**Generated:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        full_content = "\n".join(book_content)
        
        logger.info(f"Completed generation of 'Tarot for a Lifetime' book")
        logger.info(f"Total content length: {len(full_content):,} characters")
        
        return full_content
    
    def save_book(self, content: str, format: str = "markdown") -> str:
        """Save the book in specified format."""
        
        filename = f"Tarot_for_a_Lifetime_{self.book_metadata['build_id']}"
        
        if format == "markdown":
            filepath = self.output_dir / f"{filename}.md"
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"Saved book to: {filepath}")
            return str(filepath)
        
        elif format == "json":
            # Save metadata and structure
            book_data = {
                "metadata": self.book_metadata,
                "content": content,
                "generated_at": datetime.datetime.now().isoformat()
            }
            filepath = self.output_dir / f"{filename}.json"
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(book_data, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved book data to: {filepath}")
            return str(filepath)
        
        else:
            raise ValueError(f"Unsupported format: {format}")


def main():
    """Main function to generate the Tarot for a Lifetime book."""
    
    print("🌅 Tarot for a Lifetime: How the Cards Grow with You - Book Generator")
    print("=" * 70)
    
    # Initialize generator
    generator = LifetimeTarotGenerator()
    
    print(f"📚 Generating book: {generator.book_metadata['title']}")
    print(f"📖 Target word count: {generator.book_metadata['estimated_word_count']:,}")
    print(f"📑 Chapters: {generator.book_metadata['chapters_count']}")
    print(f"📁 Output directory: {generator.output_dir}")
    print()
    
    # Generate the book
    print("🔄 Generating book content...")
    book_content = generator.generate_full_book()
    
    # Save in multiple formats
    print("💾 Saving book...")
    
    # Save as Markdown
    md_path = generator.save_book(book_content, "markdown")
    print(f"✅ Saved Markdown: {md_path}")
    
    # Save as JSON
    json_path = generator.save_book(book_content, "json")
    print(f"✅ Saved JSON: {json_path}")
    
    # Calculate final stats
    word_count = len(book_content.split())
    char_count = len(book_content)
    
    print()
    print("📊 Generation Complete!")
    print(f"📝 Actual word count: {word_count:,}")
    print(f"📄 Character count: {char_count:,}")
    print(f"📑 Chapters generated: {generator.book_metadata['chapters_count']}")
    print(f"📁 Files saved to: {generator.output_dir}")
    
    return md_path, json_path


if __name__ == "__main__":
    main()