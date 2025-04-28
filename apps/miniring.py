import os
import re
import argparse
import json
import sys
import time

def find_chapter_variants(chapters_dir, chapter_prefix):
    # Find all files matching the chapter prefix (e.g., chapter_01*)
    variants = {}
    for fname in os.listdir(chapters_dir):
        if fname.startswith(chapter_prefix) and fname.endswith('.md'):
            variant = fname[len(chapter_prefix):].replace('.md','').lstrip('_') or 'original'
            variants[variant] = os.path.join(chapters_dir, fname)
    return variants

def read_all_variants(variant_paths):
    contents = {}
    for key, path in variant_paths.items():
        try:
            with open(path, 'r', encoding='utf-8') as f:
                contents[key] = f.read()
        except Exception as e:
            contents[key] = f"[ERROR reading {path}: {e}]"
    return contents

def get_all_base_chapters(chapters_dir):
    # Find all chapter_XX.md (not variants)
    chapter_pattern = re.compile(r'^(chapter_\d{2})\.md$')
    base_chapters = []
    for fname in os.listdir(chapters_dir):
        m = chapter_pattern.match(fname)
        if m:
            base_chapters.append(m.group(1))
    base_chapters.sort()
    return base_chapters

def text_similarity(a, b):
    # Simple similarity: ratio of common words
    set_a = set(a.split())
    set_b = set(b.split())
    if not set_a or not set_b:
        return 0.0
    return len(set_a & set_b) / max(len(set_a), len(set_b))

def prioritize_and_deduplicate(variant_texts):
    # Priority order: deepdrill_enhanced > deepdrill > enhanced > combined > original
    priority = ["deepdrill_enhanced", "deepdrill", "enhanced", "combined", "original"]
    selected = []
    seen = set()
    for key in priority:
        if key in variant_texts:
            text = variant_texts[key]
            # Skip if too similar to any already selected
            if any(text_similarity(text, variant_texts[k]) > 0.95 for k in seen):
                continue
            if not text.strip() or text.strip().startswith("[ERROR"):
                continue
            selected.append((key, text))
            seen.add(key)
    return selected

def build_master_prompt(variant_texts, chapter_num, target_length=7000):
    prompt = f"""
You are a master novelist, story architect, and worldbuilder. Your task is to synthesize the FINAL, professional version of Chapter {chapter_num} using all the following drafts, feedback, rewrites, and suggestions.
- The result MUST be a long, immersive, world-buildy chapter: aim for at least {target_length} words (preferably 8,000+ if material allows).
- Implement all actionable feedback, worldbuilding, and improvements from all sources below.
- Combine the best writing, scenes, and ideas from all versions.
- Invent new scenes, dialogue, subplots, and rich world details.
- Deepen character arcs, relationships, and tension.
- Add vivid sensory detail, humor, and emotional depth.
- Ensure narrative flow, emotion, suspense, and professional polish.
- Do NOT pad with filler—make every addition meaningful.
- At the end, include a section titled 'Changes:' with a bullet-point summary of what you improved, added, or changed in this chapter.
"""
    for key, text in variant_texts.items():
        prompt += f"\n\n--- {key.upper()} VERSION ---\n\n{text.strip()}"
    prompt += "\n\n[END OF SOURCES]"
    return prompt

def ensure_output_dir(base_books_dir, project_name):
    outdir = os.path.join(base_books_dir, project_name)
    os.makedirs(outdir, exist_ok=True)
    return outdir

def ollama_generate(prompt, model="sambegui/llama-3-70b-uncensored-lumi-tess-gradient:latest", timeout=600):
    import requests
    url = "http://localhost:11434/api/generate"
    headers = {"Content-Type": "application/json"}
    data = {"model": model, "prompt": prompt, "stream": True}
    result = ""
    try:
        with requests.post(url, headers=headers, json=data, stream=True, timeout=timeout) as response:
            response.raise_for_status()
            for line in response.iter_lines():
                if line:
                    try:
                        chunk = line.decode('utf-8')
                        if chunk.startswith('{'):
                            chunk_json = json.loads(chunk)
                            result += chunk_json.get('response', '')
                    except Exception as e:
                        print(f"[DEBUG] Failed to parse Ollama chunk: {e}")
        print(f"[INFO] Ollama response received (len={len(result)})")
        return result
    except Exception as e:
        print(f"[ERROR] Ollama request failed: {e}")
        return f"[OLLAMA ERROR]: {e}"

def count_words(text):
    return len(re.findall(r'\b\w+\b', text))

def print_progress_bar(iteration, total, prefix='', suffix='', length=40, fill='█'):
    percent = (iteration / total)
    filled_length = int(length * percent)
    bar = fill * filled_length + '-' * (length - filled_length)
    print(f'\r{prefix} |{bar}| {int(percent*100)}% {suffix}', end='')
    if iteration == total:
        print()  # Newline on complete

def batch_synthesize_all_chapters(chapters_dir, project_name, books_dir, model, target_length, max_retries=2):
    base_chapters = get_all_base_chapters(chapters_dir)
    output_dir = os.path.join(books_dir, project_name)
    os.makedirs(output_dir, exist_ok=True)
    summary = []
    total = len(base_chapters)
    start_time = time.time()
    for idx, chapter_prefix in enumerate(base_chapters, 1):
        elapsed = time.time() - start_time
        avg_time = elapsed / idx if idx > 1 else 0
        eta = avg_time * (total - idx)
        print_progress_bar(idx-1, total, prefix='Progress', suffix=f'ETA: {int(eta)}s', length=40)
        print(f"\n[INFO] Processing {chapter_prefix} ({idx} of {total})...")
        variants = find_chapter_variants(chapters_dir, chapter_prefix)
        variant_texts = read_all_variants(variants)
        selected = prioritize_and_deduplicate(variant_texts)
        if not selected:
            print(f"[WARN] No usable variants for {chapter_prefix}, skipping.")
            summary.append({"chapter": chapter_prefix, "status": "skipped", "reason": "no usable variants"})
            continue
        prompt_base = f"""
You are a master novelist, story architect, and worldbuilder. Your task is to synthesize the FINAL, professional version of {chapter_prefix.replace('_', ' ').title()} using all the following drafts, feedback, rewrites, and suggestions.
- The result MUST be a long, immersive, world-buildy chapter: aim for AT LEAST {target_length} words (preferably 8,000+ if material allows).
- If your output is not long enough, REWRITE and EXPAND until you reach the required word count. Do NOT stop early.
- If you reach the end and are under {target_length} words, add new scenes, subplots, worldbuilding, and character depth until you exceed the minimum.
- Implement all actionable feedback, worldbuilding, and improvements from all sources below.
- Combine the best writing, scenes, and ideas from all versions.
- Invent new scenes, dialogue, subplots, and rich world details.
- Deepen character arcs, relationships, and tension.
- Add vivid sensory detail, humor, and emotional depth.
- Ensure narrative flow, emotion, suspense, and professional polish.
- Do NOT pad with filler—make every addition meaningful.
- At the end, include a section titled 'Changes:' with a bullet-point summary of what you improved, added, or changed in this chapter.
- If your output is less than {target_length} words, explicitly state so and explain why; otherwise, continue expanding until you reach the goal.
"""
        for key, text in selected:
            prompt_base += f"\n\n--- {key.upper()} VERSION ---\n\n{text.strip()}"
        prompt_base += "\n\n[END OF SOURCES]"
        retries = 0
        final_chapter = None
        while retries <= max_retries:
            prompt = prompt_base
            if retries > 0:
                prompt += f"\n\n[INSTRUCTION: Your previous output was too short ({word_count} words). You MUST expand, rewrite, and add new material until you reach at least {target_length} words. Do not stop early. Continue from where you left off or rewrite as needed.]"
            final_path = os.path.join(output_dir, f"{chapter_prefix}_final.md")
            print(f"[INFO] Synthesizing (attempt {retries+1})...")
            attempt_start = time.time()
            final_chapter = ollama_generate(prompt, model=model, timeout=900)
            word_count = count_words(final_chapter)
            attempt_time = time.time() - attempt_start
            print(f"[INFO] {chapter_prefix}: Generated {word_count} words (target: {target_length}) in {int(attempt_time)}s")
            if word_count >= target_length or retries == max_retries:
                break
            retries += 1
        with open(final_path, 'w', encoding='utf-8') as f:
            f.write(final_chapter)
        status = "ok" if word_count >= target_length else "too short"
        summary.append({"chapter": chapter_prefix, "status": status, "words": word_count})
        print(f"[SUCCESS] Saved {final_path}")
        print_progress_bar(idx, total, prefix='Progress', suffix=f'ETA: {int(eta)}s', length=40)
    # Auto-merge all finals into a single manuscript
    merged_path = os.path.join(output_dir, "full.md")
    with open(merged_path, 'w', encoding='utf-8') as out_f:
        for chapter in base_chapters:
            final_file = os.path.join(output_dir, f"{chapter}_final.md")
            if os.path.exists(final_file):
                with open(final_file, 'r', encoding='utf-8') as ch_f:
                    out_f.write(f"\n\n# {chapter.replace('_',' ').title()}\n\n")
                    out_f.write(ch_f.read().strip())
    print(f"[INFO] Merged all final chapters into {merged_path}")
    # Print summary
    print("\n[SUMMARY]")
    for entry in summary:
        print(entry)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Batch synthesize final chapters from all available variants.")
    parser.add_argument('--chapters_dir', required=True, help='Path to the chapters directory')
    parser.add_argument('--project', required=True, help='Project/book name for output folder (e.g. Fear)')
    parser.add_argument('--books_dir', required=False, default="/Users/amre/Documents/Writer/BookDrop/books", help='Base directory for books output')
    parser.add_argument('--model', required=False, default="sambegui/llama-3-70b-uncensored-lumi-tess-gradient:latest", help='Ollama model to use')
    parser.add_argument('--target_length', required=False, type=int, default=7000, help='Target word count (default: 7000)')
    args = parser.parse_args()
    batch_synthesize_all_chapters(args.chapters_dir, args.project, args.books_dir, args.model, args.target_length)
