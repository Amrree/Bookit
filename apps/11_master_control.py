import os
import argparse
import requests
import json
import re
from datetime import datetime

# 11_master_control.py

def get_chapter_files(chapters_dir):
    return [os.path.join(chapters_dir, f) for f in sorted(os.listdir(chapters_dir)) if f.startswith('chapter_') and f.endswith('.md')]

def get_all_md_files(project_path):
    md_files = []
    for root, dirs, files in os.walk(project_path):
        for f in files:
            if f.endswith('.md') and not f.endswith('_enhanced.md') and not f == 'changes.md':
                md_files.append(os.path.join(root, f))
    return sorted(md_files)

def count_words(text):
    return len(re.findall(r'\b\w+\b', text))

def read_context(project_path):
    context = {}
    for fname in ['outline/chapter_outline.json', 'notes/notes.md', 'characters/characters.md']:
        path = os.path.join(project_path, fname)
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                context[fname] = f.read()
    return context

def ollama_generate(prompt, model="sambegui/llama-3-70b-uncensored-lumi-tess-gradient:latest", timeout=900):
    url = "http://localhost:11434/api/generate"
    data = {"model": model, "prompt": prompt, "stream": True}
    result = ""
    with requests.post(url, json=data, timeout=timeout, stream=True) as response:
        response.raise_for_status()
        for line in response.iter_lines():
            if line:
                try:
                    chunk = json.loads(line.decode('utf-8'))
                    result += chunk.get('response', '')
                except Exception:
                    continue
    return result

def build_enhancement_prompt(context, previous_chapters, chapter_text, chapter_num, word_count, target_range):
    context_str = "\n\n".join([f"[{k}]\n{v.strip()}" for k, v in context.items()])
    prev_str = "\n\n".join(previous_chapters)
    prompt = f"""
You are a master novelist and editor. Your goal is to take the following chapter and, using the full context of the story so far, enhance it in every way:
- Add new details, dialogue, and foreshadowing where appropriate.
- Move or rewrite paragraphs for clarity, drama, and pacing.
- Deepen character arcs and relationships.
- Expand on themes and atmosphere.
- Never remove or condense any existing content—only add, clarify, or rephrase for improvement.
- The final result should be longer, richer, and more engaging than the original.
- Aim for a chapter length in the range of {target_range} words. If below, add new material to reach the target. If above, only add, never cut, and focus on immersion.
- You are allowed and encouraged to add adult (NSFW) material, but it must be tasteful, integral to the story, and never gratuitous or gross. All adult content must be legal and handled with narrative purpose and sensitivity.
- At the end, provide a short summary of the changes and enhancements you made.

Story context:
{context_str}

Story so far:
{prev_str}

Current chapter (word count: {word_count}):
{chapter_text}

Return only the enhanced chapter and your summary of changes.
"""
    return prompt

def determine_target_range(word_count):
    if word_count < 1500:
        return '2,000–5,000'
    elif word_count < 5000:
        return '2,000–5,000'
    elif word_count < 6000:
        return '6,000–10,000'
    else:
        return '6,000–10,000'

def enhance_chapters(project_path, model, overwrite=False, all_md=False):
    chapters_dir = os.path.join(project_path, "chapters")
    if all_md:
        chapter_files = get_all_md_files(project_path)
    else:
        chapter_files = get_chapter_files(chapters_dir)
    context = read_context(project_path)
    changes_log = []
    previous_chapters = []
    for idx, chapter_path in enumerate(chapter_files):
        with open(chapter_path, 'r', encoding='utf-8') as f:
            chapter_text = f.read().strip()
        word_count_before = count_words(chapter_text)
        target_range = determine_target_range(word_count_before)
        prompt = build_enhancement_prompt(
            context,
            previous_chapters,
            chapter_text,
            idx + 1,
            word_count_before,
            target_range
        )
        print(f"[INFO] Enhancing {os.path.basename(chapter_path)} (words: {word_count_before}, target: {target_range}) ...")
        enhanced_output = ollama_generate(prompt, model=model)
        split_match = re.split(r'(?i)summary of changes:?|enhancements:?|---', enhanced_output)
        if len(split_match) >= 2:
            enhanced_chapter = split_match[0].strip()
            summary = split_match[1].strip()
        else:
            enhanced_chapter = enhanced_output.strip()
            summary = "[No summary returned by model.]"
        word_count_after = count_words(enhanced_chapter)
        out_path = chapter_path if overwrite else chapter_path.replace('.md', '_enhanced.md')
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(enhanced_chapter)
        changes_log.append(f"# {os.path.basename(out_path)}\n- Word count before: {word_count_before} | after: {word_count_after}\n- {summary}\n\n---\n")
        if not all_md and chapter_path.startswith(chapters_dir):
            previous_chapters.append(enhanced_chapter)
    changes_path = os.path.join(project_path, "changes.md")
    with open(changes_path, 'a', encoding='utf-8') as f:
        f.write(f"\n## Enhancement pass on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        for entry in changes_log:
            f.write(entry)
    print(f"[INFO] Enhancement complete. Changes logged in {changes_path}")

def main():
    parser = argparse.ArgumentParser(description="Enhance and expand chapters with Ollama master editor (NSFW version).")
    parser.add_argument('--project', required=True, help="Path to the project folder.")
    parser.add_argument('--model', required=False, default="sambegui/llama-3-70b-uncensored-lumi-tess-gradient:latest")
    parser.add_argument('--overwrite', action='store_true', help="Overwrite original chapters.")
    parser.add_argument('--all-md', action='store_true', help="Process all .md files, not just chapters.")
    args = parser.parse_args()
    enhance_chapters(args.project, args.model, overwrite=args.overwrite, all_md=args.all_md)

if __name__ == "__main__":
    main()
