# 01_folder_creator.py
import os
import argparse

def create_novel_folders(book_name=None, prompt=None, base_path=None):
    # If base_path is provided, use it directly (do NOT append book_name)
    if base_path:
        base_path = os.path.abspath(base_path)
    else:
        if not book_name:
            raise ValueError("book_name is required if base_path is not provided")
        base_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'drafts', book_name)
    folders = [
        "overview", "books", "notes", "characters", "scenes", "research",
        "drafts", "synopsis", "outline", "backmatter", "frontmatter"
    ]
    for folder in folders:
        os.makedirs(os.path.join(base_path, folder), exist_ok=True)
    drafts_path = os.path.join(base_path, "drafts")
    for i in range(1, 31):
        chapter_file = os.path.join(drafts_path, f"chapter{i}.md")
        with open(chapter_file, 'w', encoding='utf-8') as f:
            f.write(f"# Chapter {i}\n\n")
    structure_file = os.path.join(base_path, "folder_structure.txt")
    with open(structure_file, 'w', encoding='utf-8') as f:
        for folder in folders:
            f.write(f"{folder}\n")
    print(f"Created folder structure for {base_path}")
    print(f"Saved folder structure to {structure_file}")
    print(f"Created 30 chapter files in {drafts_path}")
    prompt_file = os.path.join(base_path, "overview", "manifesto_prompt.txt")
    prompt_text = prompt if prompt else "[Add your book prompt here!]"
    with open(prompt_file, 'w', encoding='utf-8') as f:
        f.write(prompt_text)
    print(f"Saved book prompt to {prompt_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a full book folder structure.")
    parser.add_argument('--book_name', required=False, help='Book name (used if base_path not provided)')
    parser.add_argument('--prompt', required=False, help='Prompt to save in overview/manifesto_prompt.txt')
    parser.add_argument('--base_path', required=False, help='Base path to create the book structure in (will append book_name if given)')
    args = parser.parse_args()
    if not args.base_path and not args.book_name:
        print("Book name is required if base_path is not provided. Exiting.")
    else:
        create_novel_folders(book_name=args.book_name, prompt=args.prompt, base_path=args.base_path)
