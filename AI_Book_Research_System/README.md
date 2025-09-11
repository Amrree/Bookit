# AI Book Research System

## 🚀 Overview

The AI Book Research System is a comprehensive CLI tool that canonizes existing learning and code with a **research/write/expand/repeat** cycle. It uses AI and free APIs to create full-length books through automated research, writing, and expansion processes.

## 🎯 Key Features

### 🔄 Research/Write/Expand/Repeat Cycle
- **Research Phase:** Comprehensive topic research using free APIs
- **Writing Phase:** AI-powered content generation with literary quality
- **Expansion Phase:** Multi-perspective content expansion and enhancement
- **Repeat Cycle:** Iterative improvement and refinement

### 🤖 AI Integration
- **OpenAI API:** GPT models for high-quality content generation
- **Ollama:** Local LLM support for privacy and cost control
- **Free APIs:** DuckDuckGo, Wikipedia, Crossref for research
- **Fallback Systems:** Basic content generation when AI unavailable

### 📚 Comprehensive Book Creation
- **Multiple Themes:** Tarot, Philosophy, Psychology, Spirituality, Literature
- **Literary Quality:** Contemplative, academic, and narrative styles
- **Multi-Format Export:** DOCX, PDF, MD, TXT, HTML
- **Professional Structure:** Prologue, chapters, epilogue, bibliography

## 🛠️ System Architecture

### Core Components

#### 1. **Research Engine** (`research_engine.py`)
- **Web Search:** DuckDuckGo, Wikipedia, academic sources
- **AI Analysis:** Topic synthesis and insight generation
- **Quality Scoring:** Research validation and assessment
- **Source Management:** Comprehensive source tracking

#### 2. **Writing Engine** (`writing_engine.py`)
- **Chapter Outlines:** Theme-specific chapter structures
- **AI Writing:** Literary content generation
- **Style Templates:** Multiple writing styles and approaches
- **Content Integration:** Research-informed writing

#### 3. **Expansion Engine** (`expansion_engine.py`)
- **Multi-Perspective:** Historical, psychological, cultural, practical
- **AI Enhancement:** Deep content expansion
- **Quality Control:** Expansion ratio monitoring
- **Content Analysis:** Chapter complexity assessment

#### 4. **Export Engine** (`export_engine.py`)
- **Multi-Format:** DOCX, PDF, MD, TXT, HTML export
- **Professional Layout:** Structured book formatting
- **Metadata Management:** Comprehensive book information
- **Quality Assurance:** Export validation and reporting

### CLI Interface (`research_system.sh`)
- **Project Management:** Create, manage, and track projects
- **Phase Control:** Run individual phases or complete cycles
- **Status Monitoring:** Real-time progress tracking
- **Configuration:** Flexible system configuration

## 📋 Installation & Setup

### Prerequisites
```bash
# Python dependencies
pip install requests aiohttp

# Optional: For enhanced export features
pip install python-docx reportlab

# Optional: For OpenAI integration
pip install openai
```

### System Initialization
```bash
# Initialize the system
./research_system.sh init

# Check configuration
./research_system.sh config
```

## 🚀 Usage Guide

### Basic Workflow

#### 1. **Create a Project**
```bash
./research_system.sh create "Mystical Philosophy"
```

#### 2. **Run Complete Cycle**
```bash
./research_system.sh cycle "Mystical Philosophy"
```

#### 3. **Export Results**
```bash
./research_system.sh export "Mystical Philosophy"
```

### Individual Phase Control

#### Research Phase
```bash
./research_system.sh research "Mystical Philosophy"
```

#### Writing Phase
```bash
./research_system.sh write "Mystical Philosophy"
```

#### Expansion Phase
```bash
./research_system.sh expand "Mystical Philosophy"
```

### Project Management

#### List Projects
```bash
./research_system.sh list
```

#### Check Status
```bash
./research_system.sh status "Mystical Philosophy"
```

## ⚙️ Configuration

### System Configuration (`config.json`)
```json
{
    "system": {
        "name": "AI Book Research System",
        "version": "1.0.0"
    },
    "apis": {
        "openai": {
            "enabled": false,
            "api_key": "",
            "model": "gpt-3.5-turbo"
        },
        "ollama": {
            "enabled": true,
            "model": "llama2",
            "base_url": "http://localhost:11434"
        },
        "web_search": {
            "enabled": true,
            "provider": "duckduckgo"
        }
    },
    "research": {
        "max_iterations": 5,
        "min_sources": 3,
        "quality_threshold": 0.8
    },
    "writing": {
        "target_words_per_chapter": 3000,
        "expansion_ratio": 3.0,
        "literary_style": "contemplative"
    },
    "expansion": {
        "target_expansion_ratio": 4.0,
        "research_depth": "comprehensive",
        "perspectives": ["historical", "psychological", "cultural", "practical"]
    }
}
```

### Project Configuration
Each project has its own configuration file with:
- **Book Metadata:** Title, author, theme, target audience
- **Research Data:** Topics, sources, quality scores
- **Writing Progress:** Chapters, word counts, completion status
- **Expansion Results:** Expanded chapters, ratios, enhancement data

## 📊 Supported Themes

### 1. **Tarot**
- **Chapters:** 20 chapters covering Major Arcana journey
- **Focus:** Symbolic consciousness, archetypal patterns, spiritual transformation
- **Style:** Contemplative narrative with mystical depth

### 2. **Philosophy**
- **Chapters:** 20 chapters covering fundamental philosophical questions
- **Focus:** Metaphysics, epistemology, ethics, consciousness studies
- **Style:** Academic analysis with contemplative reflection

### 3. **Psychology**
- **Chapters:** 20 chapters covering depth psychology and consciousness
- **Focus:** Jungian archetypes, individuation, shadow work, transpersonal psychology
- **Style:** Psychological analysis with practical applications

### 4. **Spirituality**
- **Chapters:** 20 chapters covering mystical and contemplative traditions
- **Focus:** Meditation, mysticism, spiritual practice, divine consciousness
- **Style:** Contemplative prose with spiritual depth

### 5. **Literature**
- **Chapters:** 20 chapters covering literary analysis and creative writing
- **Focus:** Symbolic writing, narrative structure, contemplative literature
- **Style:** Literary analysis with creative insights

### 6. **Custom Themes**
- **Flexible:** System adapts to any theme or topic
- **Research:** Automatic topic generation and research
- **Writing:** Adaptive chapter outlines and content generation

## 🔍 Research Capabilities

### Free API Integration
- **DuckDuckGo:** Instant answers and related topics
- **Wikipedia:** Comprehensive encyclopedic information
- **Crossref:** Academic papers and research
- **Extensible:** Easy addition of new research sources

### AI-Powered Analysis
- **Topic Synthesis:** Research integration and insight generation
- **Quality Assessment:** Research validation and scoring
- **Source Evaluation:** Relevance and reliability assessment
- **Context Building:** Research-informed content creation

### Research Quality Control
- **Source Diversity:** Multiple perspectives and sources
- **Quality Thresholds:** Minimum quality requirements
- **Iteration Limits:** Controlled research depth
- **Validation:** Research quality scoring and assessment

## ✍️ Writing Capabilities

### AI-Powered Generation
- **OpenAI Integration:** GPT models for high-quality content
- **Ollama Support:** Local LLM for privacy and control
- **Style Adaptation:** Multiple writing styles and approaches
- **Research Integration:** Evidence-based content creation

### Literary Quality
- **Contemplative Style:** Deep, reflective prose
- **Academic Rigor:** Scholarly analysis and insight
- **Narrative Flow:** Engaging storytelling and structure
- **Personal Reflection:** Individual experience integration

### Content Structure
- **Chapter Outlines:** Theme-specific organization
- **Logical Flow:** Coherent progression and development
- **Integration:** Seamless research incorporation
- **Quality Control:** Writing validation and enhancement

## 🔄 Expansion Capabilities

### Multi-Perspective Analysis
- **Historical:** Evolution and cultural context
- **Psychological:** Archetypal and consciousness analysis
- **Cultural:** Contemporary relevance and variations
- **Practical:** Real-world applications and tools
- **Philosophical:** Deeper meaning and implications
- **Spiritual:** Mystical and transcendent dimensions

### AI Enhancement
- **Deep Analysis:** Comprehensive topic exploration
- **Perspective Integration:** Multiple viewpoint synthesis
- **Quality Expansion:** Meaningful content enhancement
- **Ratio Control:** Targeted expansion goals

### Content Analysis
- **Complexity Assessment:** Chapter depth evaluation
- **Expansion Opportunities:** Enhancement identification
- **Quality Metrics:** Content quality measurement
- **Improvement Tracking:** Progress monitoring

## 📤 Export Capabilities

### Multiple Formats
- **Markdown (.md):** Original format with full formatting
- **HTML (.html):** Web-ready with styling and navigation
- **Plain Text (.txt):** Universal compatibility format
- **DOCX (.docx):** Microsoft Word compatible
- **PDF (.pdf):** Professional document format

### Professional Structure
- **Title Page:** Book metadata and information
- **Table of Contents:** Complete chapter listing
- **Prologue:** Engaging introduction and context
- **Chapters:** Full content with proper formatting
- **Epilogue:** Contemplative conclusion and integration
- **Bibliography:** Comprehensive reference list

### Quality Assurance
- **Format Validation:** Export quality checking
- **Metadata Management:** Complete book information
- **Structure Verification:** Content organization validation
- **Export Reporting:** Comprehensive export statistics

## 📈 Performance Metrics

### Research Phase
- **Source Count:** 3-10 sources per topic
- **Quality Score:** 0.0-1.0 research quality rating
- **Coverage:** Comprehensive topic exploration
- **Validation:** Research quality assessment

### Writing Phase
- **Word Count:** 2,000-4,000 words per chapter
- **Quality:** Literary and academic standards
- **Integration:** Research-informed content
- **Structure:** Professional organization

### Expansion Phase
- **Expansion Ratio:** 3.0-5.0x content enhancement
- **Perspectives:** 4-6 different viewpoints
- **Depth:** Comprehensive analysis
- **Quality:** Enhanced literary value

### Export Phase
- **Formats:** 5 different output formats
- **Structure:** Professional book layout
- **Metadata:** Complete book information
- **Quality:** Publication-ready output

## 🔧 Advanced Features

### Iterative Improvement
- **Cycle Repetition:** Multiple research/write/expand cycles
- **Quality Enhancement:** Continuous improvement
- **Learning Integration:** System learning from previous cycles
- **Adaptive Optimization:** Performance-based adjustments

### Customization
- **Theme Adaptation:** Flexible topic support
- **Style Selection:** Multiple writing approaches
- **API Configuration:** Flexible AI and research sources
- **Output Customization:** Configurable export options

### Integration
- **Existing Code:** Canonizes previous book generation systems
- **API Compatibility:** Works with existing AI services
- **Format Support:** Compatible with existing tools
- **Extensibility:** Easy addition of new features

## 📚 Example Projects

### 1. **"The Living Tarot"**
- **Theme:** Tarot as living symbol system
- **Chapters:** 25 literary chapters
- **Word Count:** 78,934 words (expanded)
- **Style:** Contemplative narrative
- **Focus:** Symbolic consciousness and transformation

### 2. **"Mystical Philosophy"**
- **Theme:** Philosophy and mysticism integration
- **Chapters:** 20 philosophical chapters
- **Word Count:** 60,000+ words
- **Style:** Academic with contemplative elements
- **Focus:** Metaphysics and consciousness studies

### 3. **"Depth Psychology"**
- **Theme:** Jungian psychology and archetypes
- **Chapters:** 20 psychological chapters
- **Word Count:** 60,000+ words
- **Style:** Psychological analysis with practical applications
- **Focus:** Individuation and shadow work

## 🚀 Getting Started

### Quick Start
```bash
# 1. Initialize system
./research_system.sh init

# 2. Create project
./research_system.sh create "My Book Project"

# 3. Run complete cycle
./research_system.sh cycle "My Book Project"

# 4. Export results
./research_system.sh export "My Book Project"
```

### Configuration Setup
```bash
# Edit system configuration
nano AI_Book_Research_System/config.json

# Set up OpenAI API (optional)
export OPENAI_API_KEY="your-api-key"

# Configure Ollama (optional)
ollama serve
```

### Project Management
```bash
# List all projects
./research_system.sh list

# Check project status
./research_system.sh status "My Book Project"

# Run individual phases
./research_system.sh research "My Book Project"
./research_system.sh write "My Book Project"
./research_system.sh expand "My Book Project"
```

## 🔍 Troubleshooting

### Common Issues

#### 1. **API Connection Problems**
```bash
# Check API configuration
./research_system.sh config

# Test Ollama connection
curl http://localhost:11434/api/tags

# Verify OpenAI API key
python3 -c "import openai; print('OpenAI available')"
```

#### 2. **Missing Dependencies**
```bash
# Install required packages
pip install requests aiohttp

# Install optional packages
pip install python-docx reportlab openai
```

#### 3. **Permission Issues**
```bash
# Make script executable
chmod +x research_system.sh

# Check directory permissions
ls -la AI_Book_Research_System/
```

### Performance Optimization

#### 1. **API Rate Limiting**
- Configure appropriate delays between requests
- Use local Ollama for high-volume operations
- Implement request queuing and throttling

#### 2. **Memory Management**
- Process chapters individually to avoid memory issues
- Clear temporary files between phases
- Monitor system resources during operation

#### 3. **Quality Control**
- Set appropriate quality thresholds
- Monitor expansion ratios and content quality
- Implement validation checks at each phase

## 📄 License & Usage

This system is designed for educational and research purposes. It canonizes existing learning and code from previous book generation systems while adding comprehensive AI-powered research, writing, and expansion capabilities.

### Usage Rights
- **Educational Use:** Free for educational and research purposes
- **Commercial Use:** Check individual API terms and conditions
- **Attribution:** Credit the system and its components
- **Modification:** Open source, modify as needed

### API Considerations
- **OpenAI:** Requires API key and usage fees
- **Ollama:** Free local LLM option
- **Free APIs:** DuckDuckGo, Wikipedia, Crossref (no API keys required)
- **Rate Limits:** Respect API rate limits and terms of service

## 🤝 Contributing

### Development
- **Code Structure:** Modular design for easy extension
- **API Integration:** Simple addition of new research sources
- **Theme Support:** Easy addition of new book themes
- **Export Formats:** Simple addition of new output formats

### Enhancement
- **New Research Sources:** Add additional free APIs
- **Writing Styles:** Add new literary approaches
- **Expansion Perspectives:** Add new analytical viewpoints
- **Export Formats:** Add new output options

### Testing
- **Unit Tests:** Individual component testing
- **Integration Tests:** End-to-end workflow testing
- **Quality Tests:** Content quality validation
- **Performance Tests:** System performance monitoring

---

*The AI Book Research System represents a comprehensive approach to automated book creation, combining the power of AI with free research APIs to create high-quality, full-length books through an iterative research/write/expand/repeat cycle.*