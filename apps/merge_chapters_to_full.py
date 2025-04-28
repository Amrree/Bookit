import os
import re

def get_chapter_files(chapters_dir):
    chapter_pattern = re.compile(r'^chapter_\d{2}\.md$')
    all_files = sorted(os.listdir(chapters_dir))
    matched_files = [f for f in all_files if chapter_pattern.match(f)]
    # Sort numerically by chapter number
    matched_files.sort(key=lambda x: int(re.findall(r'\d+', x)[0]))
    full_paths = [os.path.join(chapters_dir, f) for f in matched_files]
    return full_paths

def merge_chapters(chapters_dir, output_file="full.md"):
    chapter_files = get_chapter_files(chapters_dir)
    with open(os.path.join(chapters_dir, output_file), 'w', encoding='utf-8') as out_f:
        for idx, chapter_path in enumerate(chapter_files, 1):
            with open(chapter_path, 'r', encoding='utf-8') as ch_f:
                chapter_text = ch_f.read().strip()
            out_f.write(f"\n\n# Chapter {idx}\n\n")
            out_f.write(chapter_text)
    print(f"[INFO] Combined {len(chapter_files)} chapters into {output_file}")

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Combine all chapter.md files into a single full.md file.")
    parser.add_argument('--chapters_dir', required=True, help='Path to the chapters directory')
    parser.add_argument('--output', required=False, default="full.md", help="Output filename (default: full.md)")
    args = parser.parse_args()
    merge_chapters(args.chapters_dir, args.output)

if __name__ == "__main__":
    main()
