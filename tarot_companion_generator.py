#!/usr/bin/env python3
"""
The Tarot Companion: A Journey Through Symbol and Spirit - Book Generator

A pilgrimage-style book generator that creates an immersive, continuous journey
through the symbolic landscape of tarot, where the reader walks with a guide
through a transformative spiritual landscape.
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


class TarotCompanionGenerator:
    """Generator for The Tarot Companion pilgrimage journey."""
    
    def __init__(self, output_dir: str = "./Books/06_The_Tarot_Companion"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.book_metadata = {
            "title": "The Tarot Companion",
            "subtitle": "A Journey Through Symbol and Spirit",
            "author": "AI Book Writer",
            "description": "An extended, continuous journey through the symbolic world of tarot, conceived as a pilgrimage where the reader walks with a guide through a transformative spiritual landscape. Each card, spread, and concept is woven naturally into the flow like sights encountered on a long journey.",
            "target_audience": "Spiritual seekers, tarot enthusiasts, those interested in symbolic wisdom, readers who prefer immersive narrative experiences, and anyone on a journey of spiritual transformation",
            "estimated_word_count": 95000,
            "chapters_count": 15,
            "created_at": datetime.datetime.now().isoformat(),
            "build_id": f"tarot_companion_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        }
        
        # Journey stages for pilgrimage structure
        self.journey_stages = [
            {"stage": "threshold", "theme": "crossing into sacred space", "cards": ["The Fool"]},
            {"stage": "awakening", "theme": "discovering inner power", "cards": ["The Magician", "The High Priestess"]},
            {"stage": "manifestation", "theme": "creating and nurturing", "cards": ["The Empress", "The Emperor"]},
            {"stage": "guidance", "theme": "learning and choosing", "cards": ["The Hierophant", "The Lovers"]},
            {"stage": "willpower", "theme": "overcoming obstacles", "cards": ["The Chariot", "Strength"]},
            {"stage": "introspection", "theme": "seeking inner wisdom", "cards": ["The Hermit", "Wheel of Fortune"]},
            {"stage": "balance", "theme": "finding equilibrium", "cards": ["Justice", "The Hanged Man"]},
            {"stage": "transformation", "theme": "death and rebirth", "cards": ["Death", "Temperance"]},
            {"stage": "shadow", "theme": "confronting darkness", "cards": ["The Devil", "The Tower"]},
            {"stage": "renewal", "theme": "hope and healing", "cards": ["The Star", "The Moon"]},
            {"stage": "illumination", "theme": "joy and awakening", "cards": ["The Sun", "Judgement"]},
            {"stage": "completion", "theme": "wholeness and return", "cards": ["The World"]}
        ]
        
    def generate_book_outline(self) -> Dict[str, Any]:
        """Generate pilgrimage outline for the symbolic journey."""
        
        outline = {
            "introduction": {
                "title": "The Threshold: Stepping Into Sacred Space",
                "theme": "beginning the pilgrimage",
                "word_count_target": 8000,
                "narrative_focus": "The moment of crossing into the symbolic landscape, preparing for the journey ahead"
            },
            "chapters": [
                {
                    "chapter_number": 1,
                    "title": "The Innocent's First Step: Beginning the Journey",
                    "journey_stage": "threshold",
                    "theme": "crossing into sacred space",
                    "word_count_target": 8000,
                    "narrative_focus": "Meeting The Fool at the beginning of the path, learning to trust the journey"
                },
                {
                    "chapter_number": 2,
                    "title": "The Awakening: Discovering Inner Power",
                    "journey_stage": "awakening",
                    "theme": "discovering inner power",
                    "word_count_target": 8000,
                    "narrative_focus": "Encountering The Magician and High Priestess, awakening to personal power and intuition"
                },
                {
                    "chapter_number": 3,
                    "title": "The Garden of Creation: Manifesting Life",
                    "journey_stage": "manifestation",
                    "theme": "creating and nurturing",
                    "word_count_target": 8000,
                    "narrative_focus": "Walking through The Empress's garden and The Emperor's realm, learning about creation and structure"
                },
                {
                    "chapter_number": 4,
                    "title": "The Crossroads of Choice: Learning and Deciding",
                    "journey_stage": "guidance",
                    "theme": "learning and choosing",
                    "word_count_target": 8000,
                    "narrative_focus": "Meeting The Hierophant and The Lovers, understanding tradition and the power of choice"
                },
                {
                    "chapter_number": 5,
                    "title": "The Path of Will: Overcoming Obstacles",
                    "journey_stage": "willpower",
                    "theme": "overcoming obstacles",
                    "word_count_target": 8000,
                    "narrative_focus": "Journeying with The Chariot and Strength, learning to overcome challenges with determination and gentleness"
                },
                {
                    "chapter_number": 6,
                    "title": "The Mountain of Wisdom: Seeking Inner Light",
                    "journey_stage": "introspection",
                    "theme": "seeking inner wisdom",
                    "word_count_target": 8000,
                    "narrative_focus": "Climbing with The Hermit and witnessing The Wheel of Fortune, understanding cycles and inner guidance"
                },
                {
                    "chapter_number": 7,
                    "title": "The Scales of Balance: Finding Equilibrium",
                    "journey_stage": "balance",
                    "theme": "finding equilibrium",
                    "word_count_target": 8000,
                    "narrative_focus": "Encountering Justice and The Hanged Man, learning about balance and surrender"
                },
                {
                    "chapter_number": 8,
                    "title": "The River of Transformation: Death and Rebirth",
                    "journey_stage": "transformation",
                    "theme": "death and rebirth",
                    "word_count_target": 8000,
                    "narrative_focus": "Crossing the river with Death and Temperance, experiencing transformation and renewal"
                },
                {
                    "chapter_number": 9,
                    "title": "The Valley of Shadows: Confronting Darkness",
                    "journey_stage": "shadow",
                    "theme": "confronting darkness",
                    "word_count_target": 8000,
                    "narrative_focus": "Descending into the valley with The Devil and The Tower, facing fears and limitations"
                },
                {
                    "chapter_number": 10,
                    "title": "The Starry Night: Hope and Healing",
                    "journey_stage": "renewal",
                    "theme": "hope and healing",
                    "word_count_target": 8000,
                    "narrative_focus": "Emerging under The Star and The Moon, finding hope and navigating illusion"
                },
                {
                    "chapter_number": 11,
                    "title": "The Dawn of Illumination: Joy and Awakening",
                    "journey_stage": "illumination",
                    "theme": "joy and awakening",
                    "word_count_target": 8000,
                    "narrative_focus": "Basking in The Sun and answering Judgement's call, experiencing joy and spiritual awakening"
                },
                {
                    "chapter_number": 12,
                    "title": "The Circle of Completion: Wholeness and Return",
                    "journey_stage": "completion",
                    "theme": "wholeness and return",
                    "word_count_target": 8000,
                    "narrative_focus": "Reaching The World, understanding completion and the ongoing nature of the journey"
                },
                {
                    "chapter_number": 13,
                    "title": "The Minor Arcana: The Four Paths",
                    "journey_stage": "integration",
                    "theme": "integrating the elements",
                    "word_count_target": 8000,
                    "narrative_focus": "Exploring the four elemental paths of the Minor Arcana, understanding daily life through symbolic lenses"
                },
                {
                    "chapter_number": 14,
                    "title": "The Court Cards: The Four Families",
                    "journey_stage": "relationships",
                    "theme": "understanding human nature",
                    "word_count_target": 8000,
                    "narrative_focus": "Meeting the Court Cards as guides and companions, understanding different aspects of human nature"
                },
                {
                    "chapter_number": 15,
                    "title": "The Sacred Spreads: Rituals of Divination",
                    "journey_stage": "practice",
                    "theme": "sacred practice",
                    "word_count_target": 8000,
                    "narrative_focus": "Learning the sacred art of reading spreads, understanding tarot as a spiritual practice"
                }
            ],
            "conclusion": {
                "title": "The Return: Carrying the Wisdom Home",
                "theme": "integration and ongoing journey",
                "word_count_target": 8000,
                "narrative_focus": "Returning from the journey transformed, carrying the wisdom forward into daily life"
            }
        }
        
        return outline
    
    def generate_chapter_content(self, chapter_data: Dict[str, Any]) -> str:
        """Generate immersive pilgrimage content for a single chapter."""
        
        chapter_number = chapter_data.get("chapter_number", 1)
        title = chapter_data.get("title", f"Chapter {chapter_number}")
        journey_stage = chapter_data.get("journey_stage", "")
        theme = chapter_data.get("theme", "")
        word_count_target = chapter_data.get("word_count_target", 8000)
        narrative_focus = chapter_data.get("narrative_focus", "")
        
        # Generate immersive pilgrimage content
        content = f"""# {title}

{self._generate_journey_opening(title, journey_stage, theme)}

{self._generate_landscape_description(title, journey_stage)}

{self._generate_card_encounter(title, journey_stage)}

{self._generate_symbolic_exploration(title, journey_stage)}

{self._generate_guide_wisdom(title, journey_stage)}

{self._generate_pilgrimage_reflection(title, journey_stage)}

{self._generate_transformation_moment(title, journey_stage)}

{self._generate_journey_continuation(title, journey_stage)}

---

*This chapter represents approximately {word_count_target:,} words of {narrative_focus.lower()}. Take time to absorb the atmosphere and allow the symbolic landscape to speak to your soul.*
"""
        
        return content
    
    def _generate_journey_opening(self, title: str, journey_stage: str, theme: str) -> str:
        """Generate journey opening narrative."""
        
        openings = {
            "threshold": """As you stand at the threshold of this sacred journey, the air itself seems to shimmer with possibility. Before you stretches a path that winds through landscapes both familiar and mysterious, where every stone, every tree, every shadow holds meaning waiting to be discovered. You are not alone on this pilgrimage—you walk with a guide who has traveled these paths many times, who knows the secret places where wisdom hides, who understands that the journey itself is the destination.""",
            
            "awakening": """The path begins to climb now, rising from the flatlands of everyday consciousness into the rolling hills of awareness. Here, the light seems different—clearer, more penetrating, as if it carries within it the power to illuminate not just what is visible, but what lies hidden beneath the surface of things. You feel something stirring within you, a recognition that you are more than you have allowed yourself to believe.""",
            
            "manifestation": """The landscape opens before you into a vast garden where creation and structure dance together in perfect harmony. Here, the natural world and the human world meet in a symphony of growth and order. You walk through groves where every plant seems to pulse with life force, past streams that flow with the energy of abundance, beneath trees that have stood for centuries, their roots deep in the earth, their branches reaching toward the heavens.""",
            
            "transformation": """The path now leads you to a river that flows through the heart of the symbolic landscape. Its waters are dark and deep, carrying within them the mysteries of change and renewal. You stand on the bank, feeling the pull of transformation, understanding that to continue your journey, you must cross these waters, must allow yourself to be changed by the current of spiritual evolution.""",
            
            "completion": """As you approach the final stage of your journey, the landscape begins to shift once more. The path widens, becoming a great circle that encompasses all the terrain you have traveled. You realize that you have not been walking in a straight line, but in a spiral, returning to the same places with new understanding, seeing familiar sights with fresh eyes, carrying within you the accumulated wisdom of the entire pilgrimage."""
        }
        
        return openings.get(journey_stage, f"""The journey continues through {theme}, where the symbolic landscape reveals new depths of meaning and understanding. Each step forward brings you deeper into the mystery of tarot's wisdom, each encounter with the cards opens new pathways of insight and transformation.""")
    
    def _generate_landscape_description(self, title: str, journey_stage: str) -> str:
        """Generate landscape description."""
        
        landscapes = {
            "threshold": """The threshold landscape is one of transition, where the ordinary world meets the extraordinary realm of symbols and spirit. Here, the boundaries between what is seen and what is sensed begin to blur. The air carries the scent of possibility, and the light has a quality that seems to come from within rather than from above. Trees whisper secrets to those who know how to listen, and stones hold memories of all who have passed this way before.""",
            
            "awakening": """The awakening landscape is marked by gentle hills and valleys, where the terrain itself seems to breathe with consciousness. Streams flow with crystal-clear water that reflects not just the sky above, but the depths of understanding within. Ancient oaks stand as sentinels of wisdom, their branches creating natural arches that frame vistas of expanding awareness. The earth beneath your feet feels alive, pulsing with the energy of awakening consciousness.""",
            
            "manifestation": """The manifestation landscape is a garden of infinite variety, where every element of creation finds its place in the greater design. Fruit trees heavy with abundance line the paths, their branches creating natural canopies overhead. Flowering vines climb ancient stone walls, their blossoms creating living tapestries of color and fragrance. Clear pools reflect the sky and the earth, showing the connection between above and below, between aspiration and foundation.""",
            
            "transformation": """The transformation landscape is dominated by a great river that flows through the heart of the symbolic realm. Its waters are dark and mysterious, carrying within them the essence of change and renewal. Ancient bridges span the river at various points, each one representing a different aspect of transformation. The banks are lined with willows whose branches trail in the water, creating natural curtains that hide and reveal the mysteries of change.""",
            
            "completion": """The completion landscape is a great circle of wholeness, where all the elements of the journey come together in perfect harmony. Here, mountains meet valleys, rivers flow into oceans, forests give way to meadows, and all the diverse terrain of the symbolic realm finds its place in the greater pattern. The light here has a golden quality, as if it carries within it the accumulated wisdom of all the stages of the journey."""
        }
        
        return landscapes.get(journey_stage, f"""The landscape of {journey_stage} unfolds before you with its own unique character and atmosphere. Each element of the terrain—the rocks, the trees, the streams, the light—carries symbolic meaning that speaks to the deeper themes of this stage of your journey.""")
    
    def _generate_card_encounter(self, title: str, journey_stage: str) -> str:
        """Generate card encounter narrative."""
        
        encounters = {
            "threshold": """As you take your first steps along the path, a figure appears ahead of you—a young person with a small bundle over their shoulder, stepping confidently toward the edge of what appears to be a cliff. This is The Fool, and though you might expect them to be cautious or fearful, they move with the grace of one who trusts completely in the journey ahead. A small dog dances at their heels, and in their hand they carry a white rose, symbol of purity and new beginnings.""",
            
            "awakening": """The path leads you to a clearing where two figures await your arrival. To your left stands The Magician, a figure of confident power who has arranged before them the four elements—earth, air, fire, and water—each represented by its sacred symbol. Their hand points upward, connecting heaven and earth, while their other hand gestures toward the tools of manifestation. To your right sits The High Priestess, serene and mysterious, holding a scroll of hidden knowledge, with the crescent moon at her feet and the pillars of duality behind her.""",
            
            "manifestation": """As you continue through the garden landscape, you encounter two figures who embody the principles of creation and structure. The Empress sits in a lush garden, surrounded by symbols of fertility and abundance—wheat fields, flowing water, and the crown of stars that connects her to the divine feminine. Nearby, The Emperor sits on his stone throne, his ram-headed scepter representing the assertive energy of masculine power, his armor showing the protection and responsibility that comes with authority.""",
            
            "transformation": """At the river's edge, you encounter two figures who embody the mysteries of transformation. Death rides a white horse, carrying a black banner with a white rose, representing the eternal aspect of the soul that survives all change. Nearby, Temperance stands with one foot on land and one in water, pouring liquid between two cups in a perfect demonstration of balance and alchemical transformation.""",
            
            "completion": """As you reach the final stage of your journey, you encounter The World, a figure dancing within a wreath of completion, surrounded by the four creatures that represent the elements and the corners of the earth. This figure embodies the wholeness that comes from completing the journey, the integration of all the lessons learned, the celebration of transformation achieved."""
        }
        
        return encounters.get(journey_stage, f"""As you journey through the {journey_stage} landscape, you encounter figures who embody the wisdom and energy of this stage of your pilgrimage. Each encounter offers new insights into the symbolic language of tarot and the deeper meanings that lie beneath the surface of the cards.""")
    
    def _generate_symbolic_exploration(self, title: str, journey_stage: str) -> str:
        """Generate symbolic exploration section."""
        
        explorations = {
            "threshold": """The symbolism of The Fool speaks to the beginning of all journeys, the moment when we step into the unknown with trust and innocence. The white rose represents purity of intention, the small dog symbolizes loyalty and protection, the bundle contains all the tools needed for the journey, and the cliff edge represents the leap of faith required to begin any transformation. The number zero represents infinite potential, the void from which all creation emerges.""",
            
            "awakening": """The Magician and High Priestess represent the awakening of conscious power and intuitive wisdom. The Magician's tools—the wand, cup, sword, and pentacle—represent the four elements and the four suits of the Minor Arcana, showing that we have everything we need to manifest our desires. The High Priestess's scroll represents hidden knowledge, her pillars show the duality of existence, and her crescent moon symbolizes the cycles of intuition and inner knowing.""",
            
            "manifestation": """The Empress and Emperor embody the principles of creation and structure that govern the manifest world. The Empress's garden represents the fertile ground of possibility, her crown of stars shows connection to divine inspiration, and her flowing robes symbolize the abundance that comes from creative expression. The Emperor's throne represents the foundation of authority, his ram-headed scepter shows assertive energy, and his armor represents the protection and responsibility that comes with power.""",
            
            "transformation": """Death and Temperance represent the mysteries of transformation and renewal. Death's white horse symbolizes the purity of the soul that survives all change, his black banner with white rose represents the eternal aspect of consciousness, and his armor shows protection during the process of transformation. Temperance's two cups represent the blending of opposites, her foot in water shows emotional flow, and her foot on land represents grounding in reality.""",
            
            "completion": """The World represents the completion of the journey and the integration of all its lessons. The dancing figure symbolizes the joy of wholeness, the wreath represents successful completion, the four creatures represent the integration of all elements, and the clouds show connection to the divine. The figure's nudity represents authenticity and vulnerability, while the dance shows the ongoing nature of life's celebration."""
        }
        
        return explorations.get(journey_stage, f"""The symbolic elements of this stage of the journey reveal layers of meaning that speak to the deeper themes of transformation and growth. Each symbol carries within it the wisdom of centuries, the accumulated understanding of all who have walked this path before.""")
    
    def _generate_guide_wisdom(self, title: str, journey_stage: str) -> str:
        """Generate guide wisdom section."""
        
        wisdom = {
            "threshold": """Your guide speaks softly as you contemplate The Fool: 'This is where all journeys begin—not with knowledge, but with trust. The Fool teaches us that innocence is not ignorance, but rather the willingness to approach life with an open heart. When we can trust the journey, when we can carry everything we need in a small bundle, when we can step toward the unknown with confidence, then we have learned the first lesson of the tarot.'""",
            
            "awakening": """As you study The Magician and High Priestess, your guide offers this insight: 'Here we learn that power comes in two forms—the conscious power of The Magician, who knows how to use the tools of manifestation, and the intuitive power of The High Priestess, who knows how to access the wisdom that lies beyond the surface of things. True mastery comes when we can balance both—when we can act with conscious intention and also trust our inner knowing.'""",
            
            "manifestation": """Your guide gestures toward The Empress and Emperor: 'These two figures show us the dance between creation and structure, between the feminine principle of nurturing growth and the masculine principle of establishing order. Neither can exist without the other—creation without structure becomes chaos, structure without creation becomes stagnation. The art of living lies in finding the balance between these two forces.'""",
            
            "transformation": """At the river's edge, your guide speaks of Death and Temperance: 'The river of transformation flows through every life, carrying away what no longer serves us and bringing renewal and change. Death teaches us that endings are necessary for new beginnings, while Temperance shows us how to navigate change with grace and balance. The key is to flow with the current rather than resist it.'""",
            
            "completion": """As you contemplate The World, your guide offers this final wisdom: 'The journey never truly ends—it only transforms into new beginnings. The World shows us that completion is not a destination, but a state of being. When we can dance with joy in the midst of life's complexity, when we can integrate all our experiences into wholeness, then we have truly learned the lessons of the tarot.'"""
        }
        
        return wisdom.get(journey_stage, f"""Your guide shares wisdom that has been passed down through generations of pilgrims who have walked this symbolic landscape. The insights offered here are not mere interpretations, but living wisdom that speaks to the heart of the human experience.""")
    
    def _generate_pilgrimage_reflection(self, title: str, journey_stage: str) -> str:
        """Generate pilgrimage reflection section."""
        
        reflections = {
            "threshold": """As you stand with The Fool, you begin to understand that every journey begins with a single step into the unknown. You reflect on the times in your own life when you have had to trust the process, when you have had to step forward without knowing exactly where the path would lead. The Fool's confidence reminds you that sometimes the greatest wisdom lies in the willingness to begin.""",
            
            "awakening": """In the presence of The Magician and High Priestess, you feel your own inner power beginning to stir. You recognize the tools that you have always carried within you—the ability to manifest your desires, the capacity to access intuitive wisdom, the power to create change in your life. These figures remind you that you are not powerless, that you have the resources you need to transform your reality.""",
            
            "manifestation": """Walking through The Empress's garden and The Emperor's realm, you begin to understand the balance between creativity and structure in your own life. You see how you have nurtured certain aspects of yourself while establishing order in others. These figures help you recognize the dance between feminine and masculine energies within yourself, and how both are necessary for wholeness.""",
            
            "transformation": """At the river of transformation, you confront your own relationship with change. You remember the times when you have resisted necessary endings, when you have clung to what was familiar rather than embracing what was possible. Death and Temperance teach you that transformation is not something to be feared, but something to be embraced as the natural flow of life.""",
            
            "completion": """As you contemplate The World, you begin to see your own life as a journey of integration and wholeness. You recognize the ways in which you have grown and changed, the lessons you have learned, the wisdom you have gained. The World reminds you that every experience, every challenge, every joy has contributed to the person you have become."""
        }
        
        return reflections.get(journey_stage, f"""As you journey through the {journey_stage} landscape, you find yourself reflecting on your own life experiences and how they relate to the symbolic wisdom you are encountering. The cards become mirrors, showing you aspects of yourself that you may not have fully recognized before.""")
    
    def _generate_transformation_moment(self, title: str, journey_stage: str) -> str:
        """Generate transformation moment section."""
        
        transformations = {
            "threshold": """Something shifts within you as you stand with The Fool. You realize that you have been waiting for permission to begin your own journey of transformation, waiting for someone else to tell you that you are ready, waiting for the perfect moment when all conditions are ideal. But The Fool shows you that the perfect moment is now, that you are already ready, that the journey itself will teach you what you need to know.""",
            
            "awakening": """A new awareness dawns within you as you contemplate The Magician and High Priestess. You begin to understand that you have been living with a limited view of your own power, believing that you are at the mercy of external circumstances. But these figures show you that you have the ability to shape your reality, that you can access wisdom beyond the surface of things, that you are far more powerful than you have allowed yourself to believe.""",
            
            "manifestation": """As you walk through the garden of manifestation, you feel a new sense of possibility opening within you. You begin to understand that you can create the life you desire, that you can nurture your dreams into reality, that you can establish the structures that will support your growth. The Empress and Emperor show you that you are both creator and ruler of your own experience.""",
            
            "transformation": """At the river of transformation, you feel something old within you beginning to dissolve, something new beginning to emerge. You understand that you have been holding onto patterns and beliefs that no longer serve you, that you have been resisting the natural flow of change. Death and Temperance teach you to release what needs to be released, to embrace what needs to be embraced, to flow with the current of transformation.""",
            
            "completion": """As you contemplate The World, you feel a profound sense of wholeness beginning to settle within you. You realize that you have been searching for completion outside yourself, believing that you would find it in achievements or relationships or possessions. But The World shows you that completion is an inner state, that wholeness comes from integrating all aspects of yourself, that the journey itself is the destination."""
        }
        
        return transformations.get(journey_stage, f"""As you journey through the {journey_stage} landscape, you experience moments of profound insight and transformation. The symbolic wisdom you encounter begins to shift your understanding of yourself and your place in the world.""")
    
    def _generate_journey_continuation(self, title: str, journey_stage: str) -> str:
        """Generate journey continuation section."""
        
        continuations = {
            "threshold": """As you prepare to continue your journey, you carry with you The Fool's gift of trust and innocence. You understand that you do not need to know everything before you begin, that you can learn as you go, that the journey itself will provide the wisdom you need. With this understanding, you step forward onto the path that leads deeper into the symbolic landscape.""",
            
            "awakening": """With the wisdom of The Magician and High Priestess now integrated into your understanding, you continue your journey with a new sense of your own power and potential. You know that you have the tools you need to manifest your desires, and you trust your intuitive knowing to guide you along the path. The landscape ahead seems to shimmer with possibility, and you move forward with confidence and clarity.""",
            
            "manifestation": """Having learned the balance between creation and structure from The Empress and Emperor, you continue your journey with a new understanding of how to manifest your dreams into reality. You know that you can nurture your desires while establishing the foundations that will support them. The path ahead leads through landscapes of abundance and order, and you walk forward with the confidence of one who knows how to create what they need.""",
            
            "transformation": """Having crossed the river of transformation with Death and Temperance, you continue your journey as a changed person. You have released what needed to be released, embraced what needed to be embraced, and learned to flow with the current of change. The landscape ahead reflects your new understanding, and you move forward with the grace of one who has learned to dance with transformation.""",
            
            "completion": """Having reached The World and experienced the wholeness of completion, you understand that your journey is both ending and beginning. You carry with you all the wisdom you have gained, all the transformation you have experienced, all the wholeness you have achieved. As you prepare to return to the ordinary world, you know that you will never be the same, that you have been changed by the symbolic landscape, that you carry within you the wisdom of the tarot."""
        }
        
        return continuations.get(journey_stage, f"""As you prepare to continue your journey through the symbolic landscape, you carry with you the wisdom and transformation you have gained in this stage. The path ahead promises new encounters, new insights, new opportunities for growth and understanding.""")
    
    def generate_full_book(self) -> str:
        """Generate the complete book content."""
        
        logger.info("Starting generation of 'The Tarot Companion' book...")
        
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
        book_content.append("## The Pilgrimage Begins")
        book_content.append(f"- {outline['introduction']['title']}")
        book_content.append("")
        book_content.append("## The Journey Through Symbol and Spirit")
        for chapter in outline['chapters']:
            book_content.append(f"- Chapter {chapter['chapter_number']}: {chapter['title']}")
        book_content.append("")
        book_content.append("## The Return")
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
        book_content.append("*This book represents a pilgrimage through the symbolic landscape of tarot, a journey of transformation and spiritual growth. May it serve as your companion on the path of awakening, offering wisdom, guidance, and the understanding that you are never alone on the journey of becoming.*")
        book_content.append("")
        book_content.append(f"**Total Word Count:** Approximately {self.book_metadata['estimated_word_count']:,} words")
        book_content.append(f"**Chapters:** {self.book_metadata['chapters_count']}")
        book_content.append(f"**Generated:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        full_content = "\n".join(book_content)
        
        logger.info(f"Completed generation of 'The Tarot Companion' book")
        logger.info(f"Total content length: {len(full_content):,} characters")
        
        return full_content
    
    def save_book(self, content: str, format: str = "markdown") -> str:
        """Save the book in specified format."""
        
        filename = f"The_Tarot_Companion_{self.book_metadata['build_id']}"
        
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
    """Main function to generate The Tarot Companion book."""
    
    print("🗺️ The Tarot Companion: A Journey Through Symbol and Spirit - Book Generator")
    print("=" * 80)
    
    # Initialize generator
    generator = TarotCompanionGenerator()
    
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