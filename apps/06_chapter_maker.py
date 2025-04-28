# 06_chapter_maker.py
import os
import argparse
import re

def extract_chapter_titles(outline_file):
    if not os.path.exists(outline_file):
        return [f"Chapter {i+1}" for i in range(30)]
    with open(outline_file, 'r', encoding='utf-8') as f:
        text = f.read()
    matches = re.findall(r'Chapter\s*(\d+)[\.:\-]?\s*(.*)', text, re.IGNORECASE)
    if matches and len(matches) >= 20:
        return [title.strip() if title else f"Chapter {num}" for num, title in matches[:30]]
    return [f"Chapter {i+1}" for i in range(30)]

def read_overview(overview_path):
    if not os.path.exists(overview_path):
        return ''
    with open(overview_path, 'r', encoding='utf-8') as f:
        return f.read()

def create_chapter_files(chapters_dir, chapter_titles, overview_text=None):
    os.makedirs(chapters_dir, exist_ok=True)
    for i, chapter_title in enumerate(chapter_titles):
        safe_title = chapter_title.replace(' ', '_').replace('/', '-').replace('\\', '-')[:50]
        filename = os.path.join(chapters_dir, f"chapter_{i+1:02d}_{safe_title}.md")
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"# {chapter_title}\n\n{overview_text or ''}\n")
    print(f"Created {len(chapter_titles)} chapter files in {chapters_dir}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create chapter files from outline and overview.")
    parser.add_argument('--project', required=True)
    parser.add_argument('--overview', required=False, help='Path to overview.txt')
    args = parser.parse_args()
    # Ensure outline is read from the correct folder structure
    outline_file = os.path.join(args.project, "outline", "outline.txt")
    chapters_dir = os.path.join(args.project, "chapters")
    overview_path = args.overview or os.path.join(args.project, 'overview', 'overview.txt')
    titles = extract_chapter_titles(outline_file)
    overview_text = read_overview(overview_path)
    create_chapter_files(chapters_dir, titles, overview_text)
