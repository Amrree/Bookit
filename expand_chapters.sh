#!/bin/bash

# Chapter Expansion Script for The Living Tarot
# This script orchestrates the expansion of chapters using AI research and writing

set -e

# Configuration
BOOK_DIR="./Books/07_The_Living_Tarot"
EXPANSION_DIR="./Books/07_The_Living_Tarot/expanded"
LOG_FILE="./expansion_log.txt"
TARGET_WORD_COUNT=8000  # Target words per chapter
MIN_EXPANSION_RATIO=3.0  # Minimum 3x expansion

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

# Check if Python script exists
if [ ! -f "./chapter_expander.py" ]; then
    error "chapter_expander.py not found. Please ensure it exists."
    exit 1
fi

# Create expansion directory
mkdir -p "$EXPANSION_DIR"

# Find the main book file
BOOK_FILE=$(find "$BOOK_DIR" -name "The_Living_Tarot_*.md" -type f | head -1)

if [ -z "$BOOK_FILE" ]; then
    error "No Living Tarot book file found in $BOOK_DIR"
    exit 1
fi

log "Found book file: $BOOK_FILE"

# Extract chapter information
log "Extracting chapter information..."
python3 -c "
import re
import sys

def extract_chapters(book_file):
    with open(book_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all chapters
    chapters = []
    lines = content.split('\n')
    
    for i, line in enumerate(lines):
        if line.startswith('# Chapter '):
            # Extract chapter number and title
            match = re.match(r'# Chapter (\d+): (.+)', line)
            if match:
                chapter_num = int(match.group(1))
                title = match.group(2)
                
                # Find chapter content (until next chapter or end)
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
    
    return chapters

chapters = extract_chapters('$BOOK_FILE')
print(f'Found {len(chapters)} chapters')

# Save chapter data for processing
import json
with open('$EXPANSION_DIR/chapter_data.json', 'w', encoding='utf-8') as f:
    json.dump(chapters, f, indent=2, ensure_ascii=False)

# Print summary
for ch in chapters:
    print(f'Chapter {ch[\"number\"]}: {ch[\"title\"]} ({ch[\"word_count\"]} words)')
"

if [ $? -ne 0 ]; then
    error "Failed to extract chapter information"
    exit 1
fi

success "Chapter information extracted successfully"

# Process each chapter for expansion
log "Starting chapter expansion process..."

python3 chapter_expander.py \
    --book-file "$BOOK_FILE" \
    --expansion-dir "$EXPANSION_DIR" \
    --target-words "$TARGET_WORD_COUNT" \
    --min-ratio "$MIN_EXPANSION_RATIO" \
    --log-file "$LOG_FILE"

if [ $? -ne 0 ]; then
    error "Chapter expansion failed"
    exit 1
fi

success "Chapter expansion completed successfully"

# Generate expansion report
log "Generating expansion report..."
python3 -c "
import json
import os
from datetime import datetime

# Load original and expanded data
with open('$EXPANSION_DIR/chapter_data.json', 'r', encoding='utf-8') as f:
    original_chapters = json.load(f)

expanded_files = []
for i in range(1, 26):  # 25 chapters
    expanded_file = f'$EXPANSION_DIR/chapter_{i:02d}_expanded.md'
    if os.path.exists(expanded_file):
        with open(expanded_file, 'r', encoding='utf-8') as f:
            content = f.read()
            word_count = len(content.split())
            expanded_files.append({
                'chapter': i,
                'word_count': word_count,
                'file': expanded_file
            })

# Generate report
report = f'''# Chapter Expansion Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary
- Original chapters: {len(original_chapters)}
- Expanded chapters: {len(expanded_files)}
- Target word count per chapter: $TARGET_WORD_COUNT
- Minimum expansion ratio: $MIN_EXPANSION_RATIO

## Chapter Details
'''

total_original_words = 0
total_expanded_words = 0

for orig in original_chapters:
    expanded = next((e for e in expanded_files if e['chapter'] == orig['number']), None)
    if expanded:
        ratio = expanded['word_count'] / orig['word_count'] if orig['word_count'] > 0 else 0
        total_original_words += orig['word_count']
        total_expanded_words += expanded['word_count']
        
        report += f'''
### Chapter {orig['number']}: {orig['title']}
- Original: {orig['word_count']} words
- Expanded: {expanded['word_count']} words
- Expansion ratio: {ratio:.2f}x
- Status: {'✅ Expanded' if ratio >= $MIN_EXPANSION_RATIO else '⚠️ Needs more expansion'}
'''

report += f'''
## Overall Statistics
- Total original words: {total_original_words:,}
- Total expanded words: {total_expanded_words:,}
- Overall expansion ratio: {total_expanded_words / total_original_words if total_original_words > 0 else 0:.2f}x
- Average words per expanded chapter: {total_expanded_words / len(expanded_files) if expanded_files else 0:.0f}
'''

with open('$EXPANSION_DIR/expansion_report.md', 'w', encoding='utf-8') as f:
    f.write(report)

print('Expansion report generated: $EXPANSION_DIR/expansion_report.md')
"

success "Expansion report generated"

# Create combined expanded book
log "Creating combined expanded book..."
python3 -c "
import json
import os
from datetime import datetime

# Load original book structure
with open('$BOOK_FILE', 'r', encoding='utf-8') as f:
    original_content = f.read()

# Replace each chapter with expanded version
expanded_content = original_content

for i in range(1, 26):  # 25 chapters
    expanded_file = f'$EXPANSION_DIR/chapter_{i:02d}_expanded.md'
    if os.path.exists(expanded_file):
        with open(expanded_file, 'r', encoding='utf-8') as f:
            expanded_chapter = f.read()
        
        # Find and replace the chapter content
        import re
        pattern = rf'(# Chapter {i}: .+?)(?=# Chapter {i+1}:|# Epilogue:|$)'
        match = re.search(pattern, expanded_content, re.DOTALL)
        if match:
            expanded_content = expanded_content.replace(match.group(1), expanded_chapter)

# Update metadata
expanded_content = expanded_content.replace(
    '**Generated:** September 11, 2025',
    f'**Generated:** September 11, 2025\n**Expanded:** {datetime.now().strftime(\"%Y-%m-%d %H:%M:%S\")}'
)

expanded_content = expanded_content.replace(
    '**Total Word Count:** Approximately 120,000 words',
    f'**Total Word Count:** Approximately {len(expanded_content.split()):,} words (Expanded)'
)

# Save expanded book
expanded_book_file = '$EXPANSION_DIR/The_Living_Tarot_Expanded.md'
with open(expanded_book_file, 'w', encoding='utf-8') as f:
    f.write(expanded_content)

print(f'Expanded book created: {expanded_book_file}')
print(f'Total words: {len(expanded_content.split()):,}')
"

success "Combined expanded book created"

log "Chapter expansion process completed successfully!"
log "Check the expansion report for detailed statistics: $EXPANSION_DIR/expansion_report.md"
log "Expanded book available at: $EXPANSION_DIR/The_Living_Tarot_Expanded.md"

echo -e "${GREEN}🎉 Chapter expansion completed successfully!${NC}"
echo -e "${BLUE}📊 Check the expansion report for detailed statistics${NC}"
echo -e "${BLUE}📚 Expanded book available in: $EXPANSION_DIR${NC}"