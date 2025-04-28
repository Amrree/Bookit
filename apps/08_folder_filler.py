import os
import argparse
import requests
import json

# 08_folder_filler.py

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

def fill_folder(project_path, overview_text, folder, file, prompt_template, model="llama3:70b"):
    folder_path = os.path.join(project_path, folder)
    os.makedirs(folder_path, exist_ok=True)
    file_path = os.path.join(folder_path, file)
    prompt = prompt_template.format(overview=overview_text)
    try:
        content = ollama_generate(prompt, model=model)
    except Exception as e:
        print(f"[ERROR] Ollama failed for {file_path}: {e}")
        content = f"[PLACEHOLDER]\nPrompt: {prompt}"
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Filled {file_path}")

def fill_all(project_path, overview_path, model="llama3:70b"):
    with open(overview_path, 'r', encoding='utf-8') as f:
        overview_text = f.read()
    # Define what to fill and with what prompt
    targets = [
        ("notes", "notes.md", "Based on this overview, generate brainstorming notes, research ideas, and worldbuilding seeds for the novel.\n\n{overview}"),
        ("characters", "characters.md", "Based on this overview, generate a list of main characters, each with a short bio and their arc.\n\n{overview}"),
        ("scenes", "scenes.md", "Based on this overview, propose a list of key scenes or set pieces that should appear in the novel.\n\n{overview}"),
        ("research", "research.md", "Based on this overview, list topics the author should research to write this novel authentically.\n\n{overview}"),
        ("drafts", "draft_1.md", "Start the first draft of the novel, using this overview as your guide.\n\n{overview}"),
        ("synopsis", "synopsis.md", "Write a back-of-book synopsis for the novel based on this overview.\n\n{overview}"),
        ("outline", "outline.md", "Create a detailed outline, including chapter-by-chapter bullet points, based on this overview.\n\n{overview}"),
        ("backmatter", "backmatter.md", "Suggest possible backmatter content (author bio, acknowledgments, reading group guide, etc.) for this novel.\n\n{overview}"),
        ("frontmatter", "frontmatter.md", "Suggest possible frontmatter content (dedication, copyright, epigraph, etc.) for this novel.\n\n{overview}"),
    ]
    for folder, file, prompt in targets:
        fill_folder(project_path, overview_text, folder, file, prompt, model=model)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fill all project folders with AI-generated content based on the overview.")
    parser.add_argument('--project', required=True)
    parser.add_argument('--overview', required=True)
    parser.add_argument('--model', required=False, default="llama3:70b")
    args = parser.parse_args()
    fill_all(args.project, args.overview, model=args.model)
