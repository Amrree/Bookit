import os
import re
import argparse
import json

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

def main():
    parser = argparse.ArgumentParser(description="Synthesize the final, professional chapter from all available variants.")
    parser.add_argument('--chapters_dir', required=True, help='Path to the chapters directory')
    parser.add_argument('--chapter', required=True, help='Chapter prefix, e.g. chapter_01')
    parser.add_argument('--project', required=True, help='Project/book name for output folder (e.g. Fear)')
    parser.add_argument('--books_dir', required=False, default="/Users/amre/Documents/Writer/BookDrop/books", help='Base directory for books output')
    parser.add_argument('--model', required=False, default="sambegui/llama-3-70b-uncensored-lumi-tess-gradient:latest", help='Ollama model to use')
    parser.add_argument('--target_length', required=False, type=int, default=7000, help='Target word count (default: 7000)')
    args = parser.parse_args()

    print(f"[INFO] Gathering chapter variants for {args.chapter} in {args.chapters_dir}...")
    variant_paths = find_chapter_variants(args.chapters_dir, args.chapter)
    if not variant_paths:
        print(f"[ERROR] No files found for prefix {args.chapter} in {args.chapters_dir}")
        return
    variant_texts = read_all_variants(variant_paths)
    prompt = build_master_prompt(variant_texts, args.chapter, target_length=args.target_length)
    outdir = ensure_output_dir(args.books_dir, args.project)
    output_path = os.path.join(outdir, f"{args.chapter}_final.md")
    print(f"[INFO] Sending synthesis prompt to Ollama (target {args.target_length} words)...")
    final_chapter = ollama_generate(prompt, model=args.model)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(final_chapter)
    print(f"[SUCCESS] Final chapter saved to {output_path}")

if __name__ == "__main__":
    main()
