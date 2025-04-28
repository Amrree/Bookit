# 09_batch_fix.py
import os
import argparse
from chapter_creator import create_chapter_files, extract_chapter_titles

def batch_fix_chapters(base_dir):
    for project in os.listdir(base_dir):
        proj_path = os.path.join(base_dir, project)
        chapters_dir = os.path.join(proj_path, "chapters")
        outline_file = os.path.join(proj_path, "master_outline.txt")
        if os.path.isdir(chapters_dir):
            files = [f for f in os.listdir(chapters_dir) if f.endswith(".md")]
            if len(files) >= 30:
                print(f"[INFO] {project}/chapters already populated.")
                continue
            print(f"[BATCH] Populating {project}/chapters...")
            titles = extract_chapter_titles(outline_file)
            create_chapter_files(chapters_dir, titles)
            print(f"[BATCH] Populated {project}/chapters with {len(titles)} files.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Batch fix missing chapter files in all projects.")
    parser.add_argument('--base', default='.', help='Base directory to scan for projects')
    args = parser.parse_args()
    batch_fix_chapters(args.base)
