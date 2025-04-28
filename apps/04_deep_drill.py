# Renamed to 04_deep_drill.py for correct order and standalone update
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
                except Exception:
                    continue
    return result

def build_drill_prompt(chapter_text, chapter_path, word_count, story_prompt):
    prompt = (
        f"You are a master fiction editor. Given the following chapter from a novel, provide deep, actionable feedback and suggestions.\n"
        f"--- STORY PROMPT ---\n{story_prompt}\n\n--- CHAPTER ({chapter_path}) ---\n{chapter_text}\n\n--- WORD COUNT ---\n{word_count}\n\n"
        f"For this chapter, identify: (1) what works well, (2) what needs improvement, (3) opportunities for deeper emotion, suspense, or character development, (4) any plot holes or inconsistencies, (5) specific suggestions for rewriting or expanding scenes.\n"
        f"Provide your feedback in markdown format, organized by section."
    )
    return prompt

def build_enhancement_prompt(chapter_text, feedback, target_length=None):
    # If target_length is not set, aim for at least 2.2x the original word count or 2000 words
    word_count = len(chapter_text.split())
    if not target_length:
        target_length = max(2000, int(word_count * 2.2))
    prompt = f"""
You are a master fiction editor and enhancer. Your job is to take the following chapter and the detailed feedback, and rewrite it into a dramatically improved, richer, longer, and more creative version.
- Greatly expand the chapter, aiming for a word count of at least {target_length} words.
- Implement all actionable feedback and suggestions below.
- Invent new scenes, dialogue, subplots, and dramatic moments that deepen character arcs, relationships, and tension.
- Add vivid sensory detail, humor, and emotional depth.
- Carefully improve pacing, wordiness, narrative flow, emotion, suspense, character development, and fix any plot holes or inconsistencies.
- Do not pad with filler—make every addition meaningful.
- At the end, include a section titled 'Changes:' with a bullet-point summary of what you improved, added, or changed in this chapter.

--- FEEDBACK ---
{feedback}

--- ORIGINAL CHAPTER ---
{chapter_text}

[END OF CHAPTER]"""
    return prompt

def drill_chapter(chapter_path, story_prompt, model="llama3:70b"):
    with open(chapter_path, 'r', encoding='utf-8') as f:
        chapter_text = f.read()
    word_count = len(chapter_text.split())
    # Step 1: Critique/Analysis with llama3:70b
    critique_model = "llama3:70b"
    prompt = build_drill_prompt(chapter_text, chapter_path, word_count, story_prompt)
    print(f"[INFO] Sending deep drill prompt to Ollama for {chapter_path} using {critique_model}...")
    try:
        feedback = ollama_generate(prompt, model=critique_model)
    except Exception as e:
        print(f"[ERROR] Ollama failed: {e}")
        feedback = f"[ERROR] Ollama failed: {e}\nPrompt: {prompt}"
    feedback_path = chapter_path.replace('.md', '_deepdrill.md')
    with open(feedback_path, 'w', encoding='utf-8') as f:
        # 1. Copy the full current chapter text
        f.write("--- ORIGINAL CHAPTER TEXT ---\n\n")
        f.write(chapter_text)
        f.write("\n\n")
        # 2. Add the feedback (changes it wants to make)
        f.write("--- FEEDBACK AND SUGGESTIONS ---\n\n")
        f.write(feedback)
    print(f"[INFO] Deep drill feedback saved to {feedback_path}")

    # Step 2: Rewrite/Enhancement with sambegui/llama-3-70b-uncensored-lumi-tess-gradient:latest
    rewrite_model = "sambegui/llama-3-70b-uncensored-lumi-tess-gradient:latest"
    print(f"[INFO] Generating improved chapter using feedback with {rewrite_model}...")
    enhancement_prompt = build_enhancement_prompt(chapter_text, feedback)
    try:
        improved_chapter = ollama_generate(enhancement_prompt, model=rewrite_model)
    except Exception as e:
        print(f"[ERROR] Ollama failed to enhance chapter: {e}")
        improved_chapter = f"[ERROR] Ollama failed to enhance chapter: {e}\nPrompt: {enhancement_prompt}"
    improved_path = chapter_path.replace('.md', '_deepdrill_enhanced.md')
    with open(improved_path, 'w', encoding='utf-8') as f:
        f.write(improved_chapter)
    print(f"[INFO] Improved chapter saved to {improved_path}")

    # 3. Append the improved chapter to the bottom of the feedback file
    with open(feedback_path, 'a', encoding='utf-8') as f:
        f.write("\n\n--- IMPLEMENTED CHANGES (FULL REWRITE) ---\n\n")
        f.write(improved_chapter)
    print(f"[INFO] Implemented changes appended to {feedback_path}")

def main():
    parser = argparse.ArgumentParser(description="Deeply analyze a chapter using Ollama. Saves feedback in the same folder.")
    parser.add_argument('--chapter', required=False, help='Full path to the chapter markdown file to analyze')
    parser.add_argument('--prompt', required=False, help='Path to the main story prompt file (default: overview/manifesto_prompt.txt in the draft root)')
    parser.add_argument('--model', default='llama3:70b', help='Ollama model to use (default: llama3:70b)')
    args = parser.parse_args()

    chapter = args.chapter
    if not chapter:
        chapter = input("Which chapter file do you want to analyze? (Enter full path to .md file): ").strip()
    prompt_path = args.prompt
    if not prompt_path:
        print("Where is your story prompt file? (Press Enter to use the default: overview/manifesto_prompt.txt in the draft root)")
        user_input = input().strip()
        if user_input:
            prompt_path = user_input
        else:
            # Try to find the draft root by looking for 'drafts' in the path
            parts = os.path.abspath(chapter).split(os.sep)
            if 'drafts' in parts:
                idx = parts.index('drafts')
                draft_root = os.sep.join(parts[:idx+2])
                prompt_path = os.path.join(draft_root, 'overview', 'manifesto_prompt.txt')
            else:
                prompt_path = None
    model = args.model

    if not chapter:
        print("[ERROR] Chapter file is required.")
        exit(1)
    if not prompt_path or not os.path.exists(prompt_path):
        print(f"[WARN] Prompt file not found: {prompt_path}. Proceeding with empty story prompt.")
        story_prompt = ""
    else:
        with open(prompt_path, 'r', encoding='utf-8') as f:
            story_prompt = f.read()
    drill_chapter(chapter, story_prompt, model=model)

if __name__ == "__main__":
    main()
