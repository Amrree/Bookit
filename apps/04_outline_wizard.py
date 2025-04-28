import os
import argparse
import re
import requests
import subprocess

# --- 04_outline_wizard.py ---
# --- OLLAMA MANAGEMENT HELPERS ---
def is_ollama_running():
    import socket
    try:
        sock = socket.create_connection(("localhost", 11434), timeout=2)
        sock.close()
        return True
    except Exception:
        return False

def launch_ollama(model="llama3:70b"):
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
# --- END OLLAMA MANAGEMENT HELPERS ---

def ollama_generate(prompt, model="llama3:70b"):
    if not is_ollama_running():
        launch_ollama(model)
    url = "http://localhost:11434/api/generate"
    data = {"model": model, "prompt": prompt}
    response = requests.post(url, json=data, timeout=60)
    response.raise_for_status()
    # Try to parse as JSON, fallback to plain string if not possible
    try:
        return response.json().get("response", "")
    except Exception:
        # Try to clean up Ollama output by extracting only the first JSON block, if present
        text = response.text
        # Remove markdown code block markers if present
        text = re.sub(r'^```[a-zA-Z]*', '', text, flags=re.MULTILINE)
        text = text.replace('```', '')
        # Try to find first JSON object or array
        match = re.search(r'(\{.*\}|\[.*\])', text, re.DOTALL)
        if match:
            return match.group(1)
        return text

def generate_outline(project_path, story_prompt, overview_path=None):
    # Ensure the outline is saved in the correct folder structure as made by folder_creator.py
    outline_dir = os.path.join(project_path, "outline")
    os.makedirs(outline_dir, exist_ok=True)
    outline_file = os.path.join(outline_dir, "outline.txt")
    overview_text = ''
    if overview_path and os.path.exists(overview_path):
        with open(overview_path, 'r', encoding='utf-8') as f:
            overview_text = f.read()
    prompt = f"Using the following novel overview (generated with the 'Three Hour Outline' method):\n{overview_text}\n\nNow generate a novel outline in 30 chapters for this story. List chapter titles and 2-3 sentence summaries. Save all generated content in the correct subfolders as defined by the BookBlitz folder structure."
    try:
        outline = ollama_generate(prompt)
    except Exception as e:
        print(f"[ERROR] Ollama failed: {e}")
        outline = "\n".join([f"Chapter {i+1}: ..." for i in range(30)])
    with open(outline_file, 'w', encoding='utf-8') as f:
        f.write(outline)
    print(f"Outline saved to {outline_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate novel outline using AI.")
    parser.add_argument('--project', required=True)
    parser.add_argument('--prompt', required=True)
    parser.add_argument('--overview', required=False, help='Path to overview.txt')
    args = parser.parse_args()
    overview_path = args.overview or os.path.join(args.project, 'overview', 'overview.txt')
    generate_outline(args.project, args.prompt, overview_path)
