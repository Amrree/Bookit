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

def generate_outline_keywords(project_path, story_prompt, model="llama3:70b"):
    prompt = (
        f"You are a professional story architect. Given the following story premise, generate a 30-chapter outline for a novel. "
        f"For each chapter, provide:\n- Chapter number\n- Title\n- 3-5 keywords\n- A 1-2 sentence plot direction or summary.\n"
        f"Output in JSON array format, where each item is an object with keys: 'chapter', 'title', 'keywords', 'plot_direction'.\n\n"
        f"Story premise: {story_prompt}"
    )
    print("[INFO] Generating 30-chapter outline with keywords and plot directions...")
    result = ollama_generate(prompt, model=model)
    # Try to extract JSON from result
    try:
        json_start = result.index('[')
        json_data = result[json_start:]
        outline = json.loads(json_data)
    except Exception as e:
        print(f"[ERROR] Failed to parse outline JSON: {e}")
        outline = []
    outline_path = os.path.join(project_path, "outline", "chapter_outline.json")
    os.makedirs(os.path.dirname(outline_path), exist_ok=True)
    with open(outline_path, 'w', encoding='utf-8') as f:
        json.dump(outline, f, indent=2)
    print(f"[INFO] Outline with keywords saved to {outline_path}")
    return outline_path

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a 30-chapter outline with keywords and plot directions.")
    parser.add_argument('--project', required=True)
    parser.add_argument('--prompt', required=True)
    parser.add_argument('--model', required=False, default="llama3:70b")
    args = parser.parse_args()
    generate_outline_keywords(args.project, args.prompt, model=args.model)
