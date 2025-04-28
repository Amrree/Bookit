# 07_deep_drill.py
import os
import argparse
import requests
import json

def is_ollama_running():
    import socket
    try:
        sock = socket.create_connection(("localhost", 11434), timeout=2)
        sock.close()
        return True
    except Exception:
        return False

def launch_ollama(model="llama3:70b"):
    import subprocess
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

def ollama_generate(prompt, model="llama3:70b"):
    if not is_ollama_running():
        launch_ollama(model)
    url = "http://localhost:11434/api/generate"
    data = {"model": model, "prompt": prompt}
    with requests.post(url, json=data, timeout=120, stream=True) as response:
        response.raise_for_status()
        result = ""
        for line in response.iter_lines():
            if line:
                try:
                    chunk = json.loads(line.decode('utf-8'))
                    result += chunk.get("response", "")
                except Exception as e:
                    print(f"[DEBUG] Failed to parse Ollama chunk: {e}")
        return result

def build_drill_prompt(chapter_text, chapter_path, word_count, target_range, story_prompt):
    prompt = f"""
You are a master novelist, developmental editor, and literary analyst. Your mission is to perform a deep, synergistic enhancement of a single chapter, making it world-class, immersive, and maximally meaningful for the intended audience.

Before you begin writing, you must thoroughly analyze the chapter. Your analysis must include:
- A breakdown of the chapter’s tone, style, and narrative voice, with specific examples.
- Identification of the main character arcs and their emotional journeys in this chapter.
- Examination of world-building details and how they contribute to setting, atmosphere, and plot.
- Pinpointing of all major themes present, both explicit and implicit.
- A critical look at the pacing, structure, and flow of the chapter, noting any slow or rushed sections.
- Identification of any logical inconsistencies, plot holes, or missed opportunities for drama, tension, or character development.
- Noting any areas where dialogue, description, or internal monologue could be improved or expanded.
- Suggestions for new scenes, subplots, or character moments that would meaningfully deepen the story.

After your analysis, you must:
- Synergistically enhance the chapter: expand, improve, and deepen it so that every addition works in harmony with the original material. The goal is not just to increase length, but to elevate quality, narrative depth, and emotional impact.
- Add new scenes, dialogue, subplots, and character development that fit naturally with the story and enhance its depth and engagement.
- Deepen world-building, emotional resonance, and thematic complexity.
- Make the writing more vivid, immersive, and modern, suitable for a discerning contemporary audience.
- Ensure every addition is purposeful, cohesive, and improves the story as a whole.
- At the end, include a section titled 'Changes:' with a bullet-point summary of what you improved, added, or changed in this chapter.

Story Premise: {story_prompt}

Original Chapter ({os.path.basename(chapter_path)}, {word_count} words):
"""
    prompt += chapter_text + "\n\n[END OF CHAPTER]"
    return prompt

def drill_chapter(chapter_path, story_prompt, model="llama3-gradient:latest"):
    with open(chapter_path, 'r', encoding='utf-8') as f:
        chapter_text = f.read().strip()
    word_count = len(chapter_text.split())
    target_range = max(2000, int(word_count * 2.2))
    prompt = build_drill_prompt(chapter_text, chapter_path, word_count, target_range, story_prompt)
    print(f"[INFO] Enhancing {chapter_path} with model {model}...")
    enhanced = ollama_generate(prompt, model=model)
    base, ext = os.path.splitext(chapter_path)
    enhanced_path = f"{base}(drilled){ext}"
    with open(enhanced_path, 'w', encoding='utf-8') as f:
        f.write(enhanced)
    print(f"[INFO] Wrote enhanced chapter to {enhanced_path}")

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Deeply enhance a single chapter using Ollama.")
    parser.add_argument('--chapter', required=True, help='Path to the chapter markdown file to enhance.')
    parser.add_argument('--prompt', required=False, help='Path to the main story prompt file (optional, will use context if not provided).')
    parser.add_argument('--model', default='llama3-gradient:latest', help='Ollama model to use (default: llama3-gradient:latest).')
    args = parser.parse_args()

    # Try to auto-detect a prompt file in the same directory or parent directories
    story_prompt = ''
    if args.prompt:
        try:
            with open(args.prompt, 'r', encoding='utf-8') as pf:
                story_prompt = pf.read().strip()
        except Exception as e:
            print(f"[WARN] Could not read prompt file '{args.prompt}': {e}")
    else:
        # Look for a prompt file nearby
        search_dirs = [os.path.dirname(args.chapter)]
        parent = os.path.dirname(args.chapter)
        for _ in range(3):  # Search up to 3 parent directories
            parent = os.path.dirname(parent)
            search_dirs.append(parent)
        found = False
        for d in search_dirs:
            for name in ["story_prompt.txt", "prompt.txt", "overview.txt", "manifesto_prompt.txt"]:
                candidate = os.path.join(d, name)
                if os.path.exists(candidate):
                    try:
                        with open(candidate, 'r', encoding='utf-8') as pf:
                            story_prompt = pf.read().strip()
                        print(f"[INFO] Using prompt file: {candidate}")
                        found = True
                        break
                    except Exception as e:
                        print(f"[WARN] Could not read found prompt file '{candidate}': {e}")
            if found:
                break
        if not found:
            print("[WARN] No prompt file found. Proceeding with empty story prompt.")
    drill_chapter(args.chapter, story_prompt, model=args.model)

if __name__ == "__main__":
    main()
