import os
import argparse
import subprocess
import requests
import json
import re

# --- 02_architects_outline.py ---
def is_ollama_running():
    import socket
    try:
        sock = socket.create_connection(("localhost", 11434), timeout=2)
        sock.close()
        return True
    except Exception:
        return False

def launch_ollama(model="llama3:70b"):
    # Start Ollama server if not running
    print("[INFO] Launching Ollama server...")
    # Launch ollama serve in the background
    subprocess.Popen(["ollama", "serve"])  # Assumes ollama is in PATH
    import time
    for _ in range(10):  # Wait up to 10 seconds
        if is_ollama_running():
            print("[INFO] Ollama server is running.")
            break
        time.sleep(1)
    else:
        raise RuntimeError("Failed to launch Ollama server.")
    # Optionally pull or ensure model is available
    print(f"[INFO] Ensuring model '{model}' is available...")
    subprocess.run(["ollama", "pull", model], check=False)

# --- END OLLAMA MANAGEMENT HELPERS ---

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

def extract_json_array(text):
    # Find the first and last square brackets (assumes the largest array is the outline)
    matches = list(re.finditer(r'\[', text))
    if not matches:
        return None
    start = matches[0].start()
    end = text.rfind(']')
    json_str = text[start:end+1]
    # Remove trailing commas before closing braces/brackets
    json_str = re.sub(r',\s*([}\]])', r'\1', json_str)
    return json_str

def generate_outline_keywords(draft_path, story_prompt, model="llama3:70b"):
    prompt = (
        f"You are a professional story architect. Given the following story premise, generate a 30-chapter outline for a novel. "
        f"For each chapter, provide:\n- Chapter number\n- Title\n- 3-5 keywords\n- A 1-2 sentence plot direction or summary.\n"
        f"Output in JSON array format, where each item is an object with keys: 'chapter', 'title', 'keywords', 'plot_direction'.\n\n"
        f"Story premise: {story_prompt}"
    )
    print("[INFO] Generating 30-chapter outline with keywords and plot directions...")
    result = ollama_generate(prompt, model=model)
    json_str = extract_json_array(result)
    try:
        outline = json.loads(json_str)
    except Exception as e:
        print(f"[ERROR] Failed to parse outline JSON: {e}")
        # Optionally save the raw output for manual inspection
        outline_path = os.path.join(draft_path, "outline", "chapter_outline_raw.txt")
        os.makedirs(os.path.dirname(outline_path), exist_ok=True)
        with open(outline_path, 'w', encoding='utf-8') as f:
            f.write(result)
        outline = []
    outline_path = os.path.join(draft_path, "outline", "chapter_outline.json")
    os.makedirs(os.path.dirname(outline_path), exist_ok=True)
    with open(outline_path, 'w', encoding='utf-8') as f:
        json.dump(outline, f, indent=2)
    print(f"[INFO] Outline with keywords saved to {outline_path}")
    return outline

def fill_md_files(draft_path, story_prompt, model="llama3:70b"):
    # Generate or load outline with keywords and plot directions
    outline_path = os.path.join(draft_path, "outline", "chapter_outline.json")
    if os.path.exists(outline_path):
        with open(outline_path, 'r', encoding='utf-8') as f:
            outline = json.load(f)
    else:
        outline = generate_outline_keywords(draft_path, story_prompt, model)

    # Gather chapter file paths in order
    chapters_dir = os.path.join(draft_path, "chapters")
    chapter_files = [os.path.join(chapters_dir, f) for f in sorted(os.listdir(chapters_dir)) if f.endswith(".md")]
    previous_chapter = ""
    for idx, chapter_file in enumerate(chapter_files, 1):
        # Check if file exists and is non-empty with real content
        needs_generation = True
        if os.path.exists(chapter_file):
            with open(chapter_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                # Consider file 'empty' if it's very short or just a title
                if len(content) > 50 and not re.match(r'^#\s*Chapter\s*\d+\s*$', content, re.IGNORECASE):
                    print(f"[SKIP] {chapter_file} already contains substantial content. Skipping.")
                    previous_chapter = content[:1000]
                    needs_generation = False
        if not needs_generation:
            continue
        # Get outline info for this chapter if available
        if outline and idx-1 < len(outline):
            chapter_info = outline[idx-1]
            title = chapter_info.get('title', f'Chapter {idx}')
            keywords = ', '.join(chapter_info.get('keywords', []))
            plot_direction = chapter_info.get('plot_direction', '')
        else:
            title = f'Chapter {idx}'
            keywords = ''
            plot_direction = ''
        prompt = (
            f"You are writing a novel. Here is the story premise: {story_prompt}\n"
            f"Chapter {idx} title: {title}\n"
            f"Keywords: {keywords}\n"
            f"Plot direction: {plot_direction}\n"
            f"Write the full prose for Chapter {idx} of the novel. "
            f"The story must be coherent, follow from the previous chapter, and make sense as part of a continuous narrative. "
            f"Do not summarize—write the actual chapter prose.\n"
            f"Previous chapter summary/content (if any):\n{previous_chapter}\n"
        )
        print(f"[INFO] Generating chapter {idx} in {chapter_file}...")
        try:
            content = ollama_generate(prompt, model=model)
        except Exception as e:
            content = f"[ERROR] Ollama failed: {e}\nPrompt: {prompt}"
        with open(chapter_file, 'w', encoding='utf-8') as f:
            f.write(content)
        previous_chapter = content[:1000]  # Optionally limit summary length for context
        print(f"[INFO] Wrote content to {chapter_file}")
    # Fill other .md files (notes, characters, etc.)
    for root, dirs, files in os.walk(draft_path):
        for file in files:
            if file.endswith(".md") and not root.endswith("chapters"):
                file_path = os.path.join(root, file)
                prompt = f"Generate the content for '{file}' in the context of a novel about: {story_prompt}"
                print(f"[INFO] Filling {file_path} with Ollama-generated content...")
                try:
                    content = ollama_generate(prompt, model=model)
                except Exception as e:
                    content = f"[ERROR] Ollama failed: {e}\nPrompt: {prompt}"
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"[INFO] Wrote content to {file_path}")

def write_all_chapters_to_single_file(draft_path):
    chapters_dir = os.path.join(draft_path, "chapters")
    chapter_files = [os.path.join(chapters_dir, f) for f in sorted(os.listdir(chapters_dir)) if f.endswith(".md")]
    all_text = []
    for chapter_file in chapter_files:
        with open(chapter_file, 'r', encoding='utf-8') as f:
            chapter_content = f.read().strip()
            all_text.append(chapter_content)
    all_md_path = os.path.join(draft_path, "all.md")
    with open(all_md_path, 'w', encoding='utf-8') as f:
        f.write("\n\n---\n\n".join(all_text))
    print(f"[INFO] Wrote all chapters to {all_md_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fill all .md files in the draft folder with Ollama-generated content.")
    parser.add_argument('--draft', required=True, help='Full path to the draft folder (e.g. BookDrop/drafts/Fear)')
    parser.add_argument('--prompt', required=True)
    parser.add_argument('--model', required=False, default="llama3:70b")
    args = parser.parse_args()
    fill_md_files(args.draft, args.prompt, model=args.model)
    write_all_chapters_to_single_file(args.draft)
