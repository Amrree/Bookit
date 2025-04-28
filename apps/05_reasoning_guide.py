import os
import argparse
import requests

# 05_reasoning_guide.py

def reasoning_generate(prompt, model="hf.co/reedmayhew/claude-3.7-sonnet-reasoning-gemma3-12B:latest"):
    # NOTE: This is a placeholder for the actual API call to the reasoning model.
    # If you have a local or remote endpoint for this model, update the URL and payload accordingly.
    url = "http://localhost:11435/api/generate"  # Example: adjust as needed
    data = {"model": model, "prompt": prompt}
    response = requests.post(url, json=data, timeout=120)
    response.raise_for_status()
    return response.json().get("response", "")

def get_folder_structure(project_path):
    structure_file = os.path.join(project_path, "folder_structure.txt")
    if not os.path.exists(structure_file):
        # Fallback to hardcoded structure if missing
        return [
            "overview", "chapters", "notes", "characters", "scenes", "research",
            "drafts", "synopsis", "outline", "backmatter", "frontmatter"
        ]
    with open(structure_file, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]

def generate_reasoning_content(project_path, outline_path, overview_path, output_file):
    with open(outline_path, 'r', encoding='utf-8') as f:
        outline = f.read()
    with open(overview_path, 'r', encoding='utf-8') as f:
        overview = f.read()
    folders = get_folder_structure(project_path)
    prompt = (
        f"You are a world-class story reasoning AI. Given the following novel overview, detailed outline, and project folder structure, "
        f"expand on the story's structure, logic, and narrative flow. For each chapter, provide reasoning about character motivations, "
        f"plot logic, possible twists, and how each part connects to the overarching themes. Also suggest what content should go in each folder.\n\n"
        f"--- FOLDER STRUCTURE ---\n{', '.join(folders)}\n\n--- OVERVIEW ---\n{overview}\n\n--- OUTLINE ---\n{outline}\n\n"
        f"Write your reasoning in a way that will help a human author plan and execute the novel at a high level, and guide the filling of all project folders."
    )
    try:
        reasoning_content = reasoning_generate(prompt)
    except Exception as e:
        print(f"[ERROR] Reasoning AI failed: {e}")
        reasoning_content = f"[PLACEHOLDER]\nPrompt: {prompt}"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(reasoning_content)
    print(f"Reasoning content saved to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate detailed reasoning content from outline and overview.")
    parser.add_argument('--project', required=True)
    parser.add_argument('--reasoning_output', default="reasoning_content.md", help='Filename for reasoning content')
    parser.add_argument('--overview', required=False, help='Path to overview.txt')
    parser.add_argument('--outline', required=False, help='Path to master_outline.txt')
    args = parser.parse_args()
    overview_path = args.overview or os.path.join(args.project, 'overview', 'overview.txt')
    outline_path = args.outline or os.path.join(args.project, 'master_outline.txt')
    output_file = os.path.join(args.project, args.reasoning_output)
    generate_reasoning_content(args.project, outline_path, overview_path, output_file)
