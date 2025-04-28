import os
import argparse
import traceback
from 04_deep_drill import drill_chapter

def get_chapter_files(chapters_dir):
    import re
    all_files = sorted(os.listdir(chapters_dir))
    chapter_pattern = re.compile(r'^chapter_\d{2}\.md$')
    matched_files = [f for f in all_files if chapter_pattern.match(f)]
    full_paths = [os.path.join(chapters_dir, f) for f in matched_files]
    return full_paths

def book_drill(draft_dir, story_prompt, model="llama3:70b"):
    chapters_dir = os.path.join(draft_dir, "chapters")
    chapter_files = get_chapter_files(chapters_dir)
    print(f"[INFO] Found {len(chapter_files)} chapters to deep drill.")
    for idx, chapter_path in enumerate(chapter_files, 1):
        print(f"\n[INFO] === Deep drilling chapter {idx} of {len(chapter_files)}: {os.path.basename(chapter_path)} ===")
        try:
            drill_chapter(chapter_path, story_prompt, model=model)
        except Exception as e:
            print(f"[ERROR] Failed to deep drill {chapter_path}: {e}\n{traceback.format_exc()}")

def main():
    parser = argparse.ArgumentParser(description="Deep drill all chapters in a draft folder using AI.")
    parser.add_argument('--draft', required=True, help='Full path to the draft folder (e.g. BookDrop/drafts/Fear)')
    parser.add_argument('--prompt', required=False, help='Path to project prompt file (e.g., overview/manifesto_prompt.txt)')
    parser.add_argument('--model', required=False, default="llama3:70b", help='Ollama model to use')
    args = parser.parse_args()
    # Default prompt path if not provided
    if args.prompt:
        prompt_path = args.prompt
    else:
        prompt_path = os.path.join(args.draft, 'overview', 'manifesto_prompt.txt')
    if not os.path.exists(prompt_path):
        print(f"[ERROR] Prompt file not found: {prompt_path}")
        return
    with open(prompt_path, 'r', encoding='utf-8') as pf:
        story_prompt = pf.read().strip()
    book_drill(args.draft, story_prompt, model=args.model)

if __name__ == "__main__":
    main()
