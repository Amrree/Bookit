import sys
import os
import json
import requests

def ollama_generate(prompt, model="llama3:70b"):
    url = "http://localhost:11434/api/generate"
    data = {"model": model, "prompt": prompt}
    with requests.post(url, json=data, timeout=60, stream=True) as response:
        response.raise_for_status()
        result = ""
        for line in response.iter_lines():
            if line:
                chunk = json.loads(line.decode('utf-8'))
                result += chunk.get("response", "")
        return result

def test_ollama():
    prompt = "Write a short story about a cat who learns to swim."
    print("[TEST] Sending prompt to Ollama:", prompt)
    result = ollama_generate(prompt)
    print("[TEST] Ollama response:\n", result[:500])
    assert "cat" in result.lower(), "Test failed: 'cat' not in Ollama response."
    print("[TEST] Test passed!")

if __name__ == "__main__":
    test_ollama()
