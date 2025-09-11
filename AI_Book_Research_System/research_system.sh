#!/bin/bash

# AI Book Research System - Main CLI Interface
# Canonizes existing learning and code with research/write/expand/repeat cycle

set -e

# Configuration
SYSTEM_DIR="$(dirname "$0")"
PROJECTS_DIR="$SYSTEM_DIR/projects"
TEMPLATES_DIR="$SYSTEM_DIR/templates"
LOGS_DIR="$SYSTEM_DIR/logs"
CONFIG_FILE="$SYSTEM_DIR/config.json"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
    if [ -d "$LOGS_DIR" ]; then
        echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1" >> "$LOGS_DIR/system.log"
    fi
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    if [ -d "$LOGS_DIR" ]; then
        echo -e "${RED}[ERROR]${NC} $1" >> "$LOGS_DIR/system.log"
    fi
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
    if [ -d "$LOGS_DIR" ]; then
        echo -e "${GREEN}[SUCCESS]${NC} $1" >> "$LOGS_DIR/system.log"
    fi
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
    if [ -d "$LOGS_DIR" ]; then
        echo -e "${YELLOW}[WARNING]${NC} $1" >> "$LOGS_DIR/system.log"
    fi
}

info() {
    echo -e "${CYAN}[INFO]${NC} $1"
    if [ -d "$LOGS_DIR" ]; then
        echo -e "${CYAN}[INFO]${NC} $1" >> "$LOGS_DIR/system.log"
    fi
}

# Initialize system
init_system() {
    log "Initializing AI Book Research System..."
    
    # Create directories
    mkdir -p "$PROJECTS_DIR"
    mkdir -p "$TEMPLATES_DIR"
    mkdir -p "$LOGS_DIR"
    
    # Create default config if not exists
    if [ ! -f "$CONFIG_FILE" ]; then
        cat > "$CONFIG_FILE" << EOF
{
    "system": {
        "name": "AI Book Research System",
        "version": "1.0.0",
        "description": "Research/Write/Expand/Repeat cycle for book creation"
    },
    "apis": {
        "openai": {
            "enabled": false,
            "api_key": "",
            "model": "gpt-3.5-turbo",
            "max_tokens": 4000
        },
        "ollama": {
            "enabled": true,
            "model": "llama2",
            "base_url": "http://localhost:11434"
        },
        "web_search": {
            "enabled": true,
            "provider": "duckduckgo",
            "max_results": 10
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
EOF
        success "Created default configuration file"
    fi
    
    # Check Python dependencies
    if ! python3 -c "import requests, json, asyncio, aiohttp" 2>/dev/null; then
        warning "Some Python dependencies may be missing. Install with: pip install requests aiohttp"
    fi
    
    success "System initialized successfully"
}

# Display help
show_help() {
    echo -e "${PURPLE}AI Book Research System${NC}"
    echo -e "${BLUE}Research/Write/Expand/Repeat Cycle for Book Creation${NC}"
    echo ""
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  init                    Initialize the system"
    echo "  create <project_name>    Create a new book project"
    echo "  research <project>       Research topics for a project"
    echo "  write <project>          Write content for a project"
    echo "  expand <project>         Expand existing content"
    echo "  cycle <project>          Run full research/write/expand cycle"
    echo "  status <project>         Show project status"
    echo "  list                    List all projects"
    echo "  config                  Show/edit configuration"
    echo "  export <project>         Export project in multiple formats"
    echo "  help                    Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 init"
    echo "  $0 create 'Mystical Philosophy'"
    echo "  $0 cycle 'Mystical Philosophy'"
    echo "  $0 export 'Mystical Philosophy'"
    echo ""
    echo "For more information, see the documentation in the system directory."
}

# Create new project
create_project() {
    local project_name="$1"
    
    if [ -z "$project_name" ]; then
        error "Project name is required"
        return 1
    fi
    
    # Sanitize project name
    project_name=$(echo "$project_name" | tr ' ' '_' | tr -cd '[:alnum:]_')
    local project_dir="$PROJECTS_DIR/$project_name"
    
    if [ -d "$project_dir" ]; then
        error "Project '$project_name' already exists"
        return 1
    fi
    
    log "Creating project: $project_name"
    
    # Create project structure
    mkdir -p "$project_dir"
    mkdir -p "$project_dir/research"
    mkdir -p "$project_dir/writing"
    mkdir -p "$project_dir/expansion"
    mkdir -p "$project_dir/exports"
    mkdir -p "$project_dir/logs"
    
    # Create project config
    cat > "$project_dir/config.json" << EOF
{
    "project": {
        "name": "$project_name",
        "created": "$(date -Iseconds)",
        "status": "created",
        "current_phase": "research"
    },
    "book": {
        "title": "",
        "subtitle": "",
        "author": "AI Research System",
        "target_chapters": 20,
        "target_words_per_chapter": 3000,
        "total_target_words": 60000,
        "theme": "",
        "audience": "",
        "style": "literary"
    },
    "research": {
        "topics": [],
        "sources": [],
        "iterations": 0,
        "last_research": null
    },
    "writing": {
        "chapters": [],
        "total_words": 0,
        "last_writing": null
    },
    "expansion": {
        "expanded_chapters": [],
        "expansion_ratio": 0,
        "last_expansion": null
    }
}
EOF
    
    # Create project README
    cat > "$project_dir/README.md" << EOF
# $project_name

## Project Overview
- **Created:** $(date)
- **Status:** Created
- **Current Phase:** Research

## Project Structure
- \`research/\` - Research data and sources
- \`writing/\` - Written content and chapters
- \`expansion/\` - Expanded content
- \`exports/\` - Exported formats
- \`logs/\` - Project logs

## Usage
Use the main system CLI to work with this project:
\`\`\`bash
./research_system.sh cycle "$project_name"
\`\`\`
EOF
    
    success "Project '$project_name' created successfully"
    info "Project directory: $project_dir"
}

# Run research phase
research_project() {
    local project_name="$1"
    
    if [ -z "$project_name" ]; then
        error "Project name is required"
        return 1
    fi
    
    local project_dir="$PROJECTS_DIR/$project_name"
    
    if [ ! -d "$project_dir" ]; then
        error "Project '$project_name' not found"
        return 1
    fi
    
    log "Starting research phase for project: $project_name"
    
    # Run Python research script
    python3 "$SYSTEM_DIR/research_engine.py" \
        --project-dir "$project_dir" \
        --config-file "$CONFIG_FILE" \
        --phase research
    
    if [ $? -eq 0 ]; then
        success "Research phase completed for $project_name"
    else
        error "Research phase failed for $project_name"
        return 1
    fi
}

# Run writing phase
write_project() {
    local project_name="$1"
    
    if [ -z "$project_name" ]; then
        error "Project name is required"
        return 1
    fi
    
    local project_dir="$PROJECTS_DIR/$project_name"
    
    if [ ! -d "$project_dir" ]; then
        error "Project '$project_name' not found"
        return 1
    fi
    
    log "Starting writing phase for project: $project_name"
    
    # Run Python writing script
    python3 "$SYSTEM_DIR/writing_engine.py" \
        --project-dir "$project_dir" \
        --config-file "$CONFIG_FILE" \
        --phase writing
    
    if [ $? -eq 0 ]; then
        success "Writing phase completed for $project_name"
    else
        error "Writing phase failed for $project_name"
        return 1
    fi
}

# Run expansion phase
expand_project() {
    local project_name="$1"
    
    if [ -z "$project_name" ]; then
        error "Project name is required"
        return 1
    fi
    
    local project_dir="$PROJECTS_DIR/$project_name"
    
    if [ ! -d "$project_dir" ]; then
        error "Project '$project_name' not found"
        return 1
    fi
    
    log "Starting expansion phase for project: $project_name"
    
    # Run Python expansion script
    python3 "$SYSTEM_DIR/expansion_engine.py" \
        --project-dir "$project_dir" \
        --config-file "$CONFIG_FILE" \
        --phase expansion
    
    if [ $? -eq 0 ]; then
        success "Expansion phase completed for $project_name"
    else
        error "Expansion phase failed for $project_name"
        return 1
    fi
}

# Run full cycle
cycle_project() {
    local project_name="$1"
    
    if [ -z "$project_name" ]; then
        error "Project name is required"
        return 1
    fi
    
    log "Starting full cycle for project: $project_name"
    
    # Run research phase
    info "Phase 1: Research"
    research_project "$project_name"
    if [ $? -ne 0 ]; then
        error "Research phase failed, stopping cycle"
        return 1
    fi
    
    # Run writing phase
    info "Phase 2: Writing"
    write_project "$project_name"
    if [ $? -ne 0 ]; then
        error "Writing phase failed, stopping cycle"
        return 1
    fi
    
    # Run expansion phase
    info "Phase 3: Expansion"
    expand_project "$project_name"
    if [ $? -ne 0 ]; then
        error "Expansion phase failed, stopping cycle"
        return 1
    fi
    
    success "Full cycle completed for $project_name"
}

# Show project status
show_status() {
    local project_name="$1"
    
    if [ -z "$project_name" ]; then
        error "Project name is required"
        return 1
    fi
    
    local project_dir="$PROJECTS_DIR/$project_name"
    
    if [ ! -d "$project_dir" ]; then
        error "Project '$project_name' not found"
        return 1
    fi
    
    # Load project config
    if [ -f "$project_dir/config.json" ]; then
        echo -e "${PURPLE}Project Status: $project_name${NC}"
        echo ""
        python3 -c "
import json
with open('$project_dir/config.json', 'r') as f:
    config = json.load(f)
    
print(f'📚 Title: {config[\"book\"][\"title\"] or \"Not set\"}')
print(f'📝 Author: {config[\"book\"][\"author\"]}')
print(f'📑 Target Chapters: {config[\"book\"][\"target_chapters\"]}')
print(f'📊 Target Words: {config[\"book\"][\"total_target_words\"]:,}')
print(f'🎯 Current Phase: {config[\"project\"][\"current_phase\"]}')
print(f'📅 Created: {config[\"project\"][\"created\"]}')
print(f'🔄 Research Iterations: {config[\"research\"][\"iterations\"]}')
print(f'📝 Chapters Written: {len(config[\"writing\"][\"chapters\"])}')
print(f'📈 Total Words: {config[\"writing\"][\"total_words\"]:,}')
print(f'🔍 Expanded Chapters: {len(config[\"expansion\"][\"expanded_chapters\"])}')
print(f'📊 Expansion Ratio: {config[\"expansion\"][\"expansion_ratio\"]:.2f}x')
"
    else
        error "Project config not found"
        return 1
    fi
}

# List all projects
list_projects() {
    echo -e "${PURPLE}Available Projects:${NC}"
    echo ""
    
    if [ ! -d "$PROJECTS_DIR" ] || [ -z "$(ls -A "$PROJECTS_DIR" 2>/dev/null)" ]; then
        info "No projects found"
        return 0
    fi
    
    for project_dir in "$PROJECTS_DIR"/*; do
        if [ -d "$project_dir" ]; then
            project_name=$(basename "$project_dir")
            if [ -f "$project_dir/config.json" ]; then
                python3 -c "
import json
try:
    with open('$project_dir/config.json', 'r') as f:
        config = json.load(f)
    print(f'📚 {project_name}')
    print(f'   Status: {config[\"project\"][\"status\"]}')
    print(f'   Phase: {config[\"project\"][\"current_phase\"]}')
    print(f'   Words: {config[\"writing\"][\"total_words\"]:,}')
    print(f'   Chapters: {len(config[\"writing\"][\"chapters\"])}')
    print('')
except:
    print(f'📚 {project_name} (config error)')
    print('')
"
            else
                echo "📚 $project_name (no config)"
            fi
        fi
    done
}

# Show/edit configuration
show_config() {
    echo -e "${PURPLE}System Configuration:${NC}"
    echo ""
    
    if [ -f "$CONFIG_FILE" ]; then
        python3 -c "
import json
with open('$CONFIG_FILE', 'r') as f:
    config = json.load(f)
    
print(f'System: {config[\"system\"][\"name\"]} v{config[\"system\"][\"version\"]}')
print(f'Description: {config[\"system\"][\"description\"]}')
print('')
print('APIs:')
print(f'  OpenAI: {\"Enabled\" if config[\"apis\"][\"openai\"][\"enabled\"] else \"Disabled\"}')
print(f'  Ollama: {\"Enabled\" if config[\"apis\"][\"ollama\"][\"enabled\"] else \"Disabled\"}')
print(f'  Web Search: {\"Enabled\" if config[\"apis\"][\"web_search\"][\"enabled\"] else \"Disabled\"}')
print('')
print('Research:')
print(f'  Max Iterations: {config[\"research\"][\"max_iterations\"]}')
print(f'  Min Sources: {config[\"research\"][\"min_sources\"]}')
print(f'  Quality Threshold: {config[\"research\"][\"quality_threshold\"]}')
print('')
print('Writing:')
print(f'  Target Words/Chapter: {config[\"writing\"][\"target_words_per_chapter\"]}')
print(f'  Expansion Ratio: {config[\"writing\"][\"expansion_ratio\"]}')
print(f'  Literary Style: {config[\"writing\"][\"literary_style\"]}')
print('')
print('Expansion:')
print(f'  Target Expansion Ratio: {config[\"expansion\"][\"target_expansion_ratio\"]}')
print(f'  Research Depth: {config[\"expansion\"][\"research_depth\"]}')
print(f'  Perspectives: {', '.join(config[\"expansion\"][\"perspectives\"])}')
"
    else
        error "Configuration file not found"
        return 1
    fi
}

# Export project
export_project() {
    local project_name="$1"
    
    if [ -z "$project_name" ]; then
        error "Project name is required"
        return 1
    fi
    
    local project_dir="$PROJECTS_DIR/$project_name"
    
    if [ ! -d "$project_dir" ]; then
        error "Project '$project_name' not found"
        return 1
    fi
    
    log "Exporting project: $project_name"
    
    # Run Python export script
    python3 "$SYSTEM_DIR/export_engine.py" \
        --project-dir "$project_dir" \
        --config-file "$CONFIG_FILE" \
        --output-dir "$project_dir/exports"
    
    if [ $? -eq 0 ]; then
        success "Export completed for $project_name"
        info "Exports available in: $project_dir/exports"
    else
        error "Export failed for $project_name"
        return 1
    fi
}

# Main command dispatcher
main() {
    # Initialize system if needed
    if [ ! -d "$SYSTEM_DIR" ]; then
        init_system
    fi
    
    case "$1" in
        "init")
            init_system
            ;;
        "create")
            create_project "$2"
            ;;
        "research")
            research_project "$2"
            ;;
        "write")
            write_project "$2"
            ;;
        "expand")
            expand_project "$2"
            ;;
        "cycle")
            cycle_project "$2"
            ;;
        "status")
            show_status "$2"
            ;;
        "list")
            list_projects
            ;;
        "config")
            show_config
            ;;
        "export")
            export_project "$2"
            ;;
        "help"|"--help"|"-h"|"")
            show_help
            ;;
        *)
            error "Unknown command: $1"
            show_help
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"