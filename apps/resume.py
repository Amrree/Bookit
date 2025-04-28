import os

def get_last_filled_chapter(drafts_dir, min_length=50):
    """
    Returns the index (1-based) of the last chapter.md file that is considered 'filled'.
    min_length: minimum number of non-whitespace characters to consider a chapter filled.
    """
    last_filled = 0
    for i in range(1, 100):  # Support up to chapter99.md
        chapter_path = os.path.join(drafts_dir, f"chapter{i}.md")
        if not os.path.exists(chapter_path):
            break
        with open(chapter_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if len(content) >= min_length:
                last_filled = i
            else:
                break  # Stop at first empty or too-short chapter
    return last_filled

def get_next_chapter_to_generate(drafts_dir, min_length=50):
    last_filled = get_last_filled_chapter(drafts_dir, min_length)
    return last_filled + 1

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python resume.py <drafts_dir>")
        exit(1)
    drafts_dir = sys.argv[1]
    last = get_last_filled_chapter(drafts_dir)
    next_chap = get_next_chapter_to_generate(drafts_dir)
    print(f"Last filled chapter: {last}")
    print(f"Next chapter to generate: {next_chap}")
