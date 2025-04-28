# 10_combine_chapters.py
import os
import argparse

def write_all_chapters_to_single_file(project_path):
    chapters_dir = os.path.join(project_path, "chapters")
    chapter_files = [os.path.join(chapters_dir, f) for f in sorted(os.listdir(chapters_dir)) if f.endswith(".md")]
    all_text = []
    for chapter_file in chapter_files:
        with open(chapter_file, 'r', encoding='utf-8') as f:
            chapter_content = f.read().strip()
            all_text.append(chapter_content)
    all_md_path = os.path.join(project_path, "all.md")
    with open(all_md_path, 'w', encoding='utf-8') as f:
        f.write("\n\n---\n\n".join(all_text))
    print(f"[INFO] Wrote all chapters to {all_md_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Combine all chapter .md files into a single all.md file.")
    parser.add_argument('--project', required=True)
    args = parser.parse_args()
    write_all_chapters_to_single_file(args.project)
