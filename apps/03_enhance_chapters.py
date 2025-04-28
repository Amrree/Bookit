import os
import argparse
import requests
import json
import re
from datetime import datetime
import traceback
import socket
import subprocess
import time

# 03_enhance_chapters.py

def get_chapter_files(chapters_dir):
    # Only match files like chapter1.md (or chapter_XX.md), NOT files with _enhanced or _combined
    all_files = sorted(os.listdir(chapters_dir))
    print(f"[DEBUG] All files in chapters_dir: {all_files}")
    chapter_pattern = re.compile(r'^chapter(\d+)\.md$|^chapter_(\d{2})\.md$')
    matched_files = [f for f in all_files if chapter_pattern.match(f)]
    # Numeric sort for chapter files
    def chapter_num(filename):
        m = re.search(r'chapter(?:_|)(\d+)\.md', filename)
        return int(m.group(1)) if m else float('inf')
    matched_files.sort(key=chapter_num)
    print(f"[DEBUG] Files matching chapter pattern: {matched_files}")
    full_paths = [os.path.join(chapters_dir, f) for f in matched_files]
    print(f"[DEBUG] Full paths of chapter files to process: {full_paths}")
    return full_paths

def count_words(text):
    return len(re.findall(r'\b\w+\b', text))

# --- OLLAMA HEALTH CHECKS (from 02_architects_outline.py) ---
def is_ollama_running():
    import socket
    try:
        sock = socket.create_connection(("localhost", 11434), timeout=2)
        sock.close()
        return True
    except Exception:
        return False

def launch_ollama(model="sambegui/llama-3-70b-uncensored-lumi-tess-gradient:latest"):
    print("[INFO] Launching Ollama server...")
    subprocess.Popen(["ollama", "serve"])
    import time
    for _ in range(10):
        if is_ollama_running():
            print("[INFO] Ollama server is running.")
            break
        time.sleep(1)
    else:
        raise RuntimeError("Failed to launch Ollama server.")
    print(f"[INFO] Ensuring model '{model}' is available...")
    subprocess.run(["ollama", "pull", model], check=False)

# --- PATCHED OLLAMA GENERATE ---
def ollama_generate(prompt, model="sambegui/llama-3-70b-uncensored-lumi-tess-gradient:latest", timeout=180):
    import requests
    if not is_ollama_running():
        launch_ollama(model)
    url = "http://localhost:11434/api/generate"
    headers = {"Content-Type": "application/json"}
    data = {
        "model": model,
        "prompt": prompt,
        "stream": True,
    }
    try:
        with requests.post(url, headers=headers, json=data, stream=True, timeout=timeout) as response:
            response.raise_for_status()
            result = ""
            for line in response.iter_lines():
                if line:
                    try:
                        chunk = line.decode('utf-8')
                        if chunk.startswith('{'):
                            chunk_json = json.loads(chunk)
                            result += chunk_json.get('response', '')
                    except Exception as e:
                        print(f"[DEBUG] Failed to parse Ollama chunk: {e}")
            print(f"[DEBUG] Ollama response received (len={len(result)})")
            return result
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Ollama request failed: {e}")
        return "[OLLAMA ERROR]: Could not connect to Ollama or request timed out."
    except Exception as e:
        print(f"[ERROR] Unexpected error in ollama_generate: {e}")
        return "[OLLAMA ERROR]: Unexpected error occurred."

def build_enhancement_prompt(chapter_text, chapter_num, word_count, target_range, story_prompt):
    prompt = f"""
You are a master novelist and story architect. Your task is to take the following chapter and, using the story context, transform it into a dramatically longer, richer, and more creative version.
- Greatly expand the chapter, aiming for a word count of at least {target_range}.
- Invent new scenes, dialogue, subplots, and dramatic moments that deepen character arcs, relationships, and tension.
- Add vivid sensory detail, humor, and emotional depth.
- Ensure the result is immersive, modern, and highly engaging for the target audience.
- Do not pad with filler—make every addition meaningful.
- Carefully implement improvements in pacing, wordiness, narrative flow, emotion, suspense, character development, and fix any plot holes or inconsistencies.
- At the end, include a section titled 'Changes:' with a bullet-point summary of what you improved, added, or changed in this chapter.

Story Premise: {story_prompt}

Original Chapter (#{chapter_num}, {word_count} words):
"""
    prompt += chapter_text + "\n\n[END OF CHAPTER]"
    return prompt

def is_chapter_completed(enhanced_path, combined_path):
    # Check both files exist and are non-empty
    return (
        os.path.exists(enhanced_path) and os.path.getsize(enhanced_path) > 0 and
        os.path.exists(combined_path) and os.path.getsize(combined_path) > 0
    )

def enhance_chapters(project_path, model, prompt_path):
    chapters_dir = os.path.join(project_path, "drafts")
    chapter_files = get_chapter_files(chapters_dir)
    total_chapters = len(chapter_files)
    print(f"[INFO] Detected {total_chapters} chapters to process.")
    with open(prompt_path, 'r', encoding='utf-8') as pf:
        story_prompt = pf.read().strip()
    processed = 0
    skipped = 0
    failed = 0
    retried = 0
    for idx, chapter_file in enumerate(chapter_files, 1):
        print(f"\n[INFO] === Processing chapter {idx} of {total_chapters}: {os.path.basename(chapter_file)} ===")
        enhanced_path = chapter_file.replace('.md', '_enhanced.md')
        combined_path = chapter_file.replace('.md', '_combined.md')
        if is_chapter_completed(enhanced_path, combined_path):
            print(f"[SKIP] {chapter_file} already has robust enhanced and combined files.")
            skipped += 1
            continue
        def try_enhance():
            try:
                with open(chapter_file, 'r', encoding='utf-8') as cf:
                    chapter_text = cf.read().strip()
                word_count = count_words(chapter_text)
                target_range = max(2000, int(word_count * 2.2))
                prompt = build_enhancement_prompt(chapter_text, idx, word_count, target_range, story_prompt)
                print(f"[INFO] Sending enhancement prompt to Ollama for chapter {idx}...")
                enhanced = ollama_generate(prompt, model=model)
                # Split enhanced into main text and changes summary if present
                split_match = re.split(r'(?i)changes:|summary of changes:|---', enhanced)
                if len(split_match) >= 2:
                    enhanced_chapter = split_match[0].strip()
                    summary = split_match[1].strip()
                else:
                    enhanced_chapter = enhanced.strip()
                    summary = "[No summary returned by model.]"
                # Write enhanced file
                if not os.path.exists(enhanced_path) or os.path.getsize(enhanced_path) == 0:
                    print(f"[DEBUG] Writing enhanced chapter to {enhanced_path}")
                    with open(enhanced_path, 'w', encoding='utf-8') as ef:
                        ef.write(enhanced_chapter + "\n\nChanges:\n" + summary)
                else:
                    print(f"[SKIP] Enhanced file already exists: {enhanced_path}")
                # Write combined file
                if not os.path.exists(combined_path) or os.path.getsize(combined_path) == 0:
                    print(f"[DEBUG] Writing combined chapter to {combined_path}")
                    with open(combined_path, 'w', encoding='utf-8') as cf:
                        cf.write(f"# ORIGINAL CHAPTER\n\n{chapter_text}\n\n---\n\n# ENHANCED CHAPTER\n\n{enhanced_chapter}\n\n---\n\n# CHANGES\n\n{summary}\n")
                else:
                    print(f"[SKIP] Combined file already exists: {combined_path}")
                print(f"[INFO] Enhancement process checked for {chapter_file}")
                return True
            except Exception as e:
                print(f"[ERROR] Enhancement attempt failed for {chapter_file}: {e}\n{traceback.format_exc()}")
                return False
        # First attempt
        success = try_enhance()
        if not success:
            print(f"[RETRY] Retrying enhancement for {chapter_file}...")
            retried += 1
            success = try_enhance()
        if success:
            processed += 1
        else:
            failed += 1
    print("\n[SUMMARY]")
    print(f"Chapters processed: {processed}")
    print(f"Chapters skipped (already enhanced): {skipped}")
    print(f"Chapters retried: {retried}")
    print(f"Chapters failed: {failed}")
    if processed + skipped + failed != total_chapters:
        print(f"[WARNING] Only {processed + skipped + failed} out of {total_chapters} chapters were attempted! Check logs for interruptions.")
    else:
        print("[INFO] All chapters checked.")
    if failed > 0:
        print("[GUIDE] Some chapters failed. Review errors above and re-run the script to retry failed chapters.")
    print("[INFO] Enhancement script complete. You may now review the enhanced files.")

def main():
    parser = argparse.ArgumentParser(description="Enhance all chapters in a draft folder using Ollama.")
    parser.add_argument('--draft', required=False, help='Full path to the draft folder (e.g. BookDrop/drafts/Fear)')
    parser.add_argument('--prompt', required=False, help='Path to project prompt file (e.g., overview/manifesto_prompt.txt)')
    parser.add_argument('--model', required=False, default="sambegui/llama-3-70b-uncensored-lumi-tess-gradient:latest", help='Ollama model to use (default: sambegui/llama-3-70b-uncensored-lumi-tess-gradient:latest)')
    args = parser.parse_args()

    draft = args.draft or input("Where is your draft folder located? (e.g. BookDrop/drafts/Fear): ").strip()
    print("Where is your writing prompt file? (Press Enter to use the default: overview/manifesto_prompt.txt)")
    prompt_path = args.prompt
    if not prompt_path:
        user_input = input().strip()
        if user_input:
            prompt_path = user_input
        else:
            prompt_path = os.path.join(draft, 'overview', 'manifesto_prompt.txt')
    model = args.model

    if not draft or not prompt_path:
        print("[ERROR] Both draft folder and prompt file are required.")
        exit(1)
    if not os.path.exists(prompt_path):
        print(f"[ERROR] Prompt file not found: {prompt_path}")
        exit(1)

    enhance_chapters(draft, model, prompt_path)

if __name__ == "__main__":
    main()
