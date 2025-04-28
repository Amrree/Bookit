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

def count_words(text):
    return len(re.findall(r'\b\w+\b', text))

def is_ollama_running():
    try:
        sock = socket.create_connection(("localhost", 11434), timeout=2)
        sock.close()
        return True
    except Exception:
        return False

def launch_ollama(model="sambegui/llama-3-70b-uncensored-lumi-tess-gradient:latest"):
    print("[INFO] Launching Ollama server...")
    subprocess.Popen(["ollama", "serve"])
    for _ in range(10):
        if is_ollama_running():
            print("[INFO] Ollama server is running.")
            break
        time.sleep(1)
    else:
        raise RuntimeError("Failed to launch Ollama server.")
    print(f"[INFO] Ensuring model '{model}' is available...")
    subprocess.run(["ollama", "pull", model], check=False)

def ollama_generate(prompt, model="sambegui/llama-3-70b-uncensored-lumi-tess-gradient:latest", timeout=180):
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

def enhance_single_chapter(chapter_file, model, prompt_path):
    if not os.path.exists(chapter_file):
        print(f"[ERROR] Chapter file does not exist: {chapter_file}")
        return
    with open(chapter_file, 'r', encoding='utf-8') as cf:
        chapter_text = cf.read().strip()
    word_count = count_words(chapter_text)
    target_range = max(2000, int(word_count * 2.2))
    # Try to extract chapter number from filename
    m = re.search(r'chapter(?:_|)(\d+)\.md', os.path.basename(chapter_file))
    chapter_num = m.group(1) if m else "?"
    if not os.path.exists(prompt_path):
        print(f"[ERROR] Prompt file not found: {prompt_path}")
        return
    with open(prompt_path, 'r', encoding='utf-8') as pf:
        story_prompt = pf.read().strip()
    prompt = build_enhancement_prompt(chapter_text, chapter_num, word_count, target_range, story_prompt)
    print(f"[INFO] Sending enhancement prompt to Ollama for chapter {chapter_num}...")
    enhanced = ollama_generate(prompt, model=model)
    # Split enhanced into main text and changes summary if present
    split_match = re.split(r'(?i)changes:|summary of changes:|---', enhanced)
    if len(split_match) >= 2:
        enhanced_chapter = split_match[0].strip()
        summary = split_match[1].strip()
    else:
        enhanced_chapter = enhanced.strip()
        summary = "[No summary returned by model.]"
    enhanced_path = chapter_file.replace('.md', '_enhanced.md')
    combined_path = chapter_file.replace('.md', '_combined.md')
    # Write enhanced file
    with open(enhanced_path, 'w', encoding='utf-8') as ef:
        ef.write(enhanced_chapter + "\n\nChanges:\n" + summary)
    # Write combined file
    with open(combined_path, 'w', encoding='utf-8') as cf:
        cf.write(f"# ORIGINAL CHAPTER\n\n{chapter_text}\n\n---\n\n# ENHANCED CHAPTER\n\n{enhanced_chapter}\n\n---\n\n# CHANGES\n\n{summary}\n")
    print(f"[INFO] Enhancement complete for {chapter_file}.")

def main():
    parser = argparse.ArgumentParser(description="Enhance a single chapter file using Ollama.")
    parser.add_argument('--chapter', required=True, help='Full path to the chapter markdown file to enhance')
    parser.add_argument('--prompt', required=True, help='Path to project prompt file (e.g., overview/manifesto_prompt.txt)')
    parser.add_argument('--model', required=False, default="sambegui/llama-3-70b-uncensored-lumi-tess-gradient:latest", help='Ollama model to use (default: sambegui/llama-3-70b-uncensored-lumi-tess-gradient:latest)')
    args = parser.parse_args()
    enhance_single_chapter(args.chapter, args.model, args.prompt)

if __name__ == "__main__":
    main()
