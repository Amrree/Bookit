import os
import tkinter as tk
from tkinter import scrolledtext, messagebox, simpledialog, filedialog, ttk
import threading
import json
import re
import time
import subprocess
import requests
import tkinter.font as tkfont

# --- Folder creation logic (from 01_folder_creator.py) ---
def create_novel_folders(book_name, prompt=None):
    base_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'drafts', book_name)
    folders = [
        "overview", "books", "notes", "characters", "scenes", "research",
        "drafts", "synopsis", "outline", "backmatter", "frontmatter"
    ]
    for folder in folders:
        os.makedirs(os.path.join(base_path, folder), exist_ok=True)
    drafts_path = os.path.join(base_path, "drafts")
    for i in range(1, 31):
        chapter_file = os.path.join(drafts_path, f"chapter{i}.md")
        with open(chapter_file, 'w', encoding='utf-8') as f:
            f.write(f"# Chapter {i}\n\n")
    structure_file = os.path.join(base_path, "folder_structure.txt")
    with open(structure_file, 'w', encoding='utf-8') as f:
        for folder in folders:
            f.write(f"{folder}\n")
    prompt_file = os.path.join(base_path, "overview", "manifesto_prompt.txt")
    prompt_text = prompt if prompt else "[Add your book prompt here!]"
    with open(prompt_file, 'w', encoding='utf-8') as f:
        f.write(prompt_text)
    return base_path

# --- Ollama/AI logic (from 02_architects_outline_safe.py) ---
def is_ollama_running():
    import socket
    try:
        sock = socket.create_connection(("localhost", 11434), timeout=2)
        sock.close()
        return True
    except Exception:
        return False

def launch_ollama(model="llama3:70b"):
    subprocess.Popen(["ollama", "serve"])
    for _ in range(10):
        if is_ollama_running():
            break
        time.sleep(1)
    else:
        raise RuntimeError("Failed to launch Ollama server.")
    subprocess.run(["ollama", "pull", model], check=False)

def ollama_generate(prompt, model="llama3:70b", retries=3, delay=5):
    for attempt in range(1, retries+1):
        try:
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
                            pass
                return result
        except Exception as e:
            if attempt < retries:
                time.sleep(delay)
            else:
                raise

def extract_json_array(text):
    matches = list(re.finditer(r'\[', text))
    if not matches:
        return None
    start = matches[0].start()
    end = text.rfind(']')
    json_str = text[start:end+1]
    json_str = re.sub(r',\s*([}\]])', r'\1', json_str)
    return json_str

def generate_outline_keywords(draft_path, story_prompt, model="llama3:70b"):
    prompt = (
        f"You are a professional story architect. Given the following story premise, generate a 30-chapter outline for a novel. "
        f"For each chapter, provide:\n- Chapter number\n- Title\n- 3-5 keywords\n- A 1-2 sentence plot direction or summary.\n"
        f"Output in JSON array format, where each item is an object with keys: 'chapter', 'title', 'keywords', 'plot_direction'.\n\n"
        f"Story premise: {story_prompt}"
    )
    try:
        result = ollama_generate(prompt, model=model)
        json_str = extract_json_array(result)
        outline = json.loads(json_str)
    except Exception as e:
        outline_path = os.path.join(draft_path, "outline", "chapter_outline_raw.txt")
        os.makedirs(os.path.dirname(outline_path), exist_ok=True)
        with open(outline_path, 'w', encoding='utf-8') as f:
            f.write(result)
        outline = []
    outline_path = os.path.join(draft_path, "outline", "chapter_outline.json")
    os.makedirs(os.path.dirname(outline_path), exist_ok=True)
    with open(outline_path, 'w', encoding='utf-8') as f:
        json.dump(outline, f, indent=2)
    return outline

def fill_md_files(draft_path, story_prompt, model="llama3:70b", retries=3, status_callback=None):
    outline_path = os.path.join(draft_path, "outline", "chapter_outline.json")
    if os.path.exists(outline_path):
        with open(outline_path, 'r', encoding='utf-8') as f:
            outline = json.load(f)
    else:
        outline = generate_outline_keywords(draft_path, story_prompt, model)
    chapters_dir = os.path.join(draft_path, "drafts")
    # Numeric sort for chapter files
    def chapter_num(filename):
        m = re.search(r'chapter(\d+)\\.md', filename)
        return int(m.group(1)) if m else float('inf')
    chapter_files = [f for f in os.listdir(chapters_dir) if f.startswith('chapter') and f.endswith('.md')]
    chapter_files.sort(key=chapter_num)
    chapter_files = [os.path.join(chapters_dir, f) for f in chapter_files]
    previous_chapter = ""
    for idx, chapter_file in enumerate(chapter_files, 1):
        needs_generation = True
        if os.path.exists(chapter_file):
            with open(chapter_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if len(content) > 50 and not re.match(r'^#\s*Chapter\s*\d+\s*$', content, re.IGNORECASE):
                    previous_chapter = content[:1000]
                    needs_generation = False
        if not needs_generation:
            continue
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
        if status_callback:
            status_callback(f"Generating chapter {idx}...")
        try:
            content = ollama_generate(prompt, model=model, retries=retries)
            with open(chapter_file, 'w', encoding='utf-8') as f:
                f.write(content)
            previous_chapter = content[:1000]
            if status_callback:
                status_callback(f"Wrote content to {chapter_file}")
        except Exception as e:
            if status_callback:
                status_callback(f"Failed to generate {chapter_file}: {e}")
    # Fill other .md files (notes, characters, etc.)
    for root, dirs, files in os.walk(draft_path):
        for file in files:
            if file.endswith(".md") and not root.endswith("drafts"):
                file_path = os.path.join(root, file)
                prompt = f"Generate the content for '{file}' in the context of a novel about: {story_prompt}"
                if status_callback:
                    status_callback(f"Filling {file_path} with Ollama-generated content...")
                try:
                    content = ollama_generate(prompt, model=model, retries=retries)
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    if status_callback:
                        status_callback(f"Wrote content to {file_path}")
                except Exception as e:
                    if status_callback:
                        status_callback(f"Failed to generate {file_path}: {e}")

# --- Utility for recent folders/projects ---
RECENT_FOLDERS_PATH = os.path.expanduser('~/.bookstart_recent_folders.json')

def load_recent_folders():
    if os.path.exists(RECENT_FOLDERS_PATH):
        with open(RECENT_FOLDERS_PATH, 'r') as f:
            return json.load(f)
    return []

def save_recent_folder(folder_path):
    folders = load_recent_folders()
    if folder_path in folders:
        folders.remove(folder_path)
    folders.insert(0, folder_path)
    folders = folders[:10]
    with open(RECENT_FOLDERS_PATH, 'w') as f:
        json.dump(folders, f)

# --- Markdown formatting helper ---
def apply_markdown_tags(text_widget, content):
    text_widget.tag_remove('bold', '1.0', 'end')
    text_widget.tag_remove('italic', '1.0', 'end')
    for match in re.finditer(r'\*\*(.+?)\*\*', content):
        start = f"1.0+{match.start()}c"
        end = f"1.0+{match.end()}c"
        text_widget.tag_add('bold', start, end)
    for match in re.finditer(r'\*(.+?)\*', content):
        start = f"1.0+{match.start()}c"
        end = f"1.0+{match.end()}c"
        text_widget.tag_add('italic', start, end)

# --- Export chat and logs to Markdown ---
def export_conversation_and_log(conversation, folder_path, terminal_log):
    notes_dir = os.path.join(folder_path, 'notes')
    os.makedirs(notes_dir, exist_ok=True)
    export_path = os.path.join(notes_dir, f"bookstart_chat_{time.strftime('%Y%m%d_%H%M%S')}.md")
    with open(export_path, 'w', encoding='utf-8') as f:
        f.write(f"# BookStart Session Export\n\n")
        f.write(f"## Project Folder\n{folder_path}\n\n")
        f.write(f"## Conversation\n{conversation}\n\n")
        f.write(f"## Terminal Log\n{terminal_log}\n")
    return export_path

# --- GUI ---
class BookstartApp:
    def __init__(self, root):
        self.root = root
        root.title("BookStart")
        root.configure(bg="#161821")
        root.geometry("900x750")
        root.minsize(800, 600)
        root.resizable(True, True)

        # Fonts
        title_font = tkfont.Font(family="Helvetica Neue", size=26, weight="bold")
        label_font = tkfont.Font(family="Helvetica Neue", size=14, weight="bold")
        entry_font = tkfont.Font(family="Fira Mono", size=14)
        button_font = tkfont.Font(family="Helvetica Neue", size=13, weight="bold")
        status_font = tkfont.Font(family="Fira Mono", size=12)
        terminal_font = tkfont.Font(family="Fira Mono", size=12)

        # Configure grid for resizing
        root.grid_rowconfigure(4, weight=1)
        root.grid_columnconfigure(0, weight=1)

        # Title
        title_label = tk.Label(root, text="BookStart", font=title_font, fg="#e0e0e0", bg="#161821")
        title_label.grid(row=0, column=0, columnspan=2, pady=(28, 16), sticky="ew")

        # Folder Frame
        folder_frame = tk.Frame(root, bg="#161821")
        folder_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=40, pady=(0, 10))
        folder_frame.grid_columnconfigure(1, weight=1)
        tk.Label(folder_frame, text="Project Folder", font=label_font, fg="#e0e0e0", bg="#161821").grid(row=0, column=0, sticky='w')
        folder_row = tk.Frame(folder_frame, bg="#161821")
        folder_row.grid(row=1, column=0, columnspan=2, sticky='ew', pady=(4, 0))
        folder_row.grid_columnconfigure(0, weight=1)
        self.folder_var = tk.StringVar()
        self.folder_entry = tk.Entry(folder_row, font=entry_font, textvariable=self.folder_var, relief='flat', bg="#232946", fg="#e0e0e0", insertbackground="#e0e0e0", highlightthickness=2, highlightbackground="#394867", highlightcolor="#3da9fc")
        self.folder_entry.grid(row=0, column=0, sticky='ew', ipady=6)
        browse_btn = tk.Button(folder_row, text="Browse", font=button_font, command=self.browse_folder, bg="#394867", fg="#e0e0e0", activebackground="#3da9fc", activeforeground="#fff", relief='flat', padx=18, pady=6, borderwidth=0, highlightthickness=0)
        browse_btn.grid(row=0, column=1, padx=(10,0))
        create_btn = tk.Button(folder_row, text="New", font=button_font, command=self.create_new_folder, bg="#394867", fg="#e0e0e0", activebackground="#3da9fc", activeforeground="#fff", relief='flat', padx=18, pady=6, borderwidth=0, highlightthickness=0)
        create_btn.grid(row=0, column=2, padx=(10,0))
        open_btn = tk.Button(folder_row, text="Open", font=button_font, command=self.open_in_finder, bg="#394867", fg="#e0e0e0", activebackground="#3da9fc", activeforeground="#fff", relief='flat', padx=18, pady=6, borderwidth=0, highlightthickness=0)
        open_btn.grid(row=0, column=3, padx=(10,0))

        # User Idea / Raw Text
        idea_frame = tk.Frame(root, bg="#161821")
        idea_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=40, pady=(0, 10))
        tk.Label(idea_frame, text="Your Idea / Raw Text", font=label_font, fg="#e0e0e0", bg="#161821").pack(anchor='w')
        self.idea_text = tk.Text(idea_frame, font=entry_font, height=5, relief='flat', bg="#232946", fg="#e0e0e0", insertbackground="#e0e0e0", highlightthickness=2, highlightbackground="#394867", highlightcolor="#3da9fc", wrap='word')
        self.idea_text.pack(fill='both', expand=True, pady=(4,0), ipady=6)

        # Generate Prompt/Premise Button
        gen_btn_frame = tk.Frame(root, bg="#161821")
        gen_btn_frame.grid(row=3, column=0, columnspan=2, sticky="ew", padx=40, pady=(0, 10))
        self.gen_prompt_btn = tk.Button(gen_btn_frame, text="Generate Prompt/Premise from Above", font=button_font, bg="#3da9fc", fg="#161821", activebackground="#232946", activeforeground="#fff", relief='flat', padx=24, pady=10, borderwidth=0, highlightthickness=0, command=self.generate_prompt_from_idea)
        self.gen_prompt_btn.pack(anchor='w', pady=(0, 0))

        # Prompt Area (acts as chat/conversation with AI)
        prompt_frame = tk.Frame(root, bg="#161821")
        prompt_frame.grid(row=4, column=0, columnspan=2, sticky="nsew", padx=40, pady=(0, 10))
        tk.Label(prompt_frame, text="Prompt / Conversation", font=label_font, fg="#e0e0e0", bg="#161821").pack(anchor='w')
        self.prompt_text = tk.Text(prompt_frame, font=entry_font, height=10, relief='flat', bg="#232946", fg="#e0e0e0", insertbackground="#e0e0e0", highlightthickness=2, highlightbackground="#394867", highlightcolor="#3da9fc", wrap='word')
        self.prompt_text.pack(fill='both', expand=True, pady=(4,0), ipady=6)
        self.prompt_text.bind('<Control-Return>', self.send_to_ollama)
        self.prompt_text.bind('<Command-Return>', self.send_to_ollama)  # For Mac

        # Action Button (optional, can be enabled as needed)
        self.start_btn = tk.Button(root, text="Create & Generate", font=button_font, bg="#3da9fc", fg="#161821", activebackground="#232946", activeforeground="#fff", relief='flat', padx=24, pady=10, borderwidth=0, highlightthickness=0, command=self.start_process)
        self.start_btn.grid(row=5, column=0, columnspan=2, pady=(8, 0))

        # Ollama Service Status Bar
        self.status_var = tk.StringVar()
        self.status_var.set("Checking Ollama status...")
        status_bar = tk.Label(root, textvariable=self.status_var, font=status_font, fg="#e0e0e0", bg="#232946", anchor='w', padx=12, pady=4)
        status_bar.grid(row=6, column=0, columnspan=2, sticky="ew", pady=(0, 0))

        # Terminal/Log Output Area
        terminal_frame = tk.Frame(root, bg="#161821")
        terminal_frame.grid(row=7, column=0, columnspan=2, sticky="nsew", padx=0, pady=(6, 0))
        self.terminal_box = tk.Text(terminal_frame, font=terminal_font, height=7, relief='flat', bg="#11131a", fg="#e0e0e0", insertbackground="#e0e0e0", state='disabled', wrap='word')
        self.terminal_box.pack(fill='both', expand=True)

        # For resizing
        root.grid_rowconfigure(4, weight=2)
        root.grid_rowconfigure(7, weight=1)

        self.check_ollama_status()

    def log_terminal(self, msg):
        self.terminal_box.config(state='normal')
        self.terminal_box.insert('end', msg + '\n')
        self.terminal_box.see('end')
        self.terminal_box.config(state='disabled')

    def browse_folder(self):
        folder_selected = filedialog.askdirectory(title="Select Project Folder")
        if folder_selected:
            self.folder_var.set(folder_selected)
            self.status_var.set(f"Selected folder: {folder_selected}")
            self.log_terminal(f"[INFO] Selected folder: {folder_selected}")

    def create_new_folder(self):
        parent = filedialog.askdirectory(title="Select Parent Directory for New Folder")
        if not parent:
            self.status_var.set("Folder creation cancelled.")
            self.log_terminal("[INFO] Folder creation cancelled.")
            return
        new_name = simpledialog.askstring("New Folder", "Enter new folder name:")
        if new_name:
            new_path = os.path.join(parent, new_name)
            try:
                os.makedirs(new_path, exist_ok=True)
                self.folder_var.set(new_path)
                self.status_var.set(f"Created new folder: {new_path}")
                self.log_terminal(f"[INFO] Created new folder: {new_path}")
            except Exception as e:
                self.status_var.set(f"Could not create folder: {e}")
                self.log_terminal(f"[ERROR] Could not create folder: {e}")
        else:
            self.status_var.set("No folder name provided.")
            self.log_terminal("[INFO] No folder name provided.")

    def open_in_finder(self):
        folder = self.folder_var.get().strip()
        if not folder or not os.path.isdir(folder):
            self.status_var.set("Please select a valid folder to open.")
            self.log_terminal("[ERROR] Please select a valid folder to open.")
            return
        try:
            subprocess.Popen(["open", folder])
            self.status_var.set(f"Opened folder in Finder: {folder}")
            self.log_terminal(f"[INFO] Opened folder in Finder: {folder}")
        except Exception as e:
            self.status_var.set(f"Could not open folder: {e}")
            self.log_terminal(f"[ERROR] Could not open folder: {e}")

    def check_ollama_status(self):
        try:
            if is_ollama_running():
                self.status_var.set("Ollama service: Available ")
                self.log_terminal("[CHECKPOINT] Ollama service: Available ")
            else:
                self.status_var.set("Ollama service: Not running (click to retry)")
                self.log_terminal("[CHECKPOINT] Ollama service: Not running ")
        except Exception:
            self.status_var.set("Ollama service: Error (click to retry)")
            self.log_terminal("[ERROR] Ollama service: Error ")

    def generate_prompt_from_idea(self):
        idea = self.idea_text.get('1.0', 'end').strip()
        if not idea:
            self.status_var.set("Please enter your idea above.")
            self.log_terminal("[INFO] No idea text entered for prompt generation.")
            return
        self.status_var.set("Generating prompt with Ollama...")
        self.log_terminal("[CHECKPOINT] Generating prompt with Ollama...")
        self.root.after(100, lambda: self._generate_prompt_thread(idea))

    def _generate_prompt_thread(self, idea):
        import threading
        def run():
            try:
                self.log_terminal(f"[PROMPT] Sending idea to Ollama: {idea}")
                prompt = ollama_generate(f"Turn this idea into a book premise or prompt: {idea}")
                self.prompt_text.delete('1.0', 'end')
                self.prompt_text.insert('1.0', prompt)
                self.status_var.set("Prompt generated with Ollama ")
                self.log_terminal(f"[RESPONSE] Prompt generated: {prompt}")
            except Exception as e:
                self.status_var.set(f"Ollama error: {e}")
                self.log_terminal(f"[ERROR] Ollama error: {e}")
        threading.Thread(target=run, daemon=True).start()

    def send_to_ollama(self, event=None):
        user_input = self.prompt_text.get('1.0', 'end').strip()
        if not user_input:
            self.status_var.set("Please enter text to send to Ollama.")
            self.log_terminal("[INFO] No text to send to Ollama.")
            return "break"
        self.status_var.set("Ollama: Generating response...")
        self.log_terminal(f"[PROMPT] Sending to Ollama: {user_input}")
        self.prompt_text.insert('end', "\n[AI is thinking...]")
        self.prompt_text.see('end')
        self.prompt_text.update()
        self.root.after(100, lambda: self._ollama_chat_thread(user_input))
        return "break"

    def _ollama_chat_thread(self, user_input):
        import threading
        def run():
            try:
                response = ollama_generate(user_input)
                # Remove the thinking message and append AI response
                content = self.prompt_text.get('1.0', 'end').replace("[AI is thinking...]\n", "")
                self.prompt_text.delete('1.0', 'end')
                self.prompt_text.insert('1.0', content)
                self.prompt_text.insert('end', f"\n[AI]: {response}\n")
                self.prompt_text.see('end')
                self.status_var.set("Ollama: Response received ")
                self.log_terminal(f"[RESPONSE] Ollama: {response}")
            except Exception as e:
                self.status_var.set(f"Ollama error: {e}")
                self.log_terminal(f"[ERROR] Ollama error: {e}")
        threading.Thread(target=run, daemon=True).start()

    def start_process(self):
        folder = self.folder_var.get().strip()
        prompt = self.prompt_text.get('1.0', 'end').strip()
        if not folder:
            self.status_var.set("Project folder is required.")
            self.log_terminal("[ERROR] Project folder is required.")
            return
        self.start_btn.config(state='disabled')
        self.status_var.set("Creating book structure...")
        self.log_terminal("[CHECKPOINT] Creating book structure...")
        threading.Thread(target=self.run_all, args=(folder, prompt)).start()

    def run_all(self, folder, prompt):
        try:
            if not os.path.exists(folder):
                os.makedirs(folder, exist_ok=True)
                self.status_var.set(f"Created folder: {folder}")
                self.log_terminal(f"[CHECKPOINT] Created folder: {folder}")
            self.status_var.set(f"Creating book structure in '{folder}'...")
            self.log_terminal(f"[CHECKPOINT] Creating book structure in '{folder}'...")
            base_path = create_novel_folders_from_path(folder, prompt)
            self.status_var.set("Folders created. Starting AI generation...")
            self.log_terminal("[CHECKPOINT] Folders created. Starting AI generation...")
            fill_md_files(base_path, prompt, status_callback=self.log_terminal)
            self.status_var.set("[SUCCESS] All done!")
            self.log_terminal("[SUCCESS] All done!")
        except Exception as e:
            self.status_var.set(f"[ERROR] {e}")
            self.log_terminal(f"[ERROR] {e}")
        finally:
            self.start_btn.config(state='normal')

    def send_to_ollama(self, event=None):
        user_input = self.prompt_text.get('1.0', 'end').strip()
        if not user_input:
            self.status_var.set("Please enter text to send to Ollama.")
            self.log_terminal("[INFO] No text to send to Ollama.")
            return "break"
        self.status_var.set("Ollama: Generating response...")
        self.log_terminal(f"[PROMPT] Sending to Ollama: {user_input}")
        self.prompt_text.insert('end', "\n[AI is thinking...]")
        self.prompt_text.see('end')
        self.prompt_text.update()
        self.root.after(100, lambda: self._ollama_chat_thread(user_input))
        return "break"

    def _ollama_chat_thread(self, user_input):
        import threading
        def run():
            try:
                response = ollama_generate(user_input)
                # Remove the thinking message and append AI response
                content = self.prompt_text.get('1.0', 'end').replace("[AI is thinking...]\n", "")
                self.prompt_text.delete('1.0', 'end')
                self.prompt_text.insert('1.0', content)
                self.prompt_text.insert('end', f"\n[AI]: {response}\n")
                self.prompt_text.see('end')
                self.status_var.set("Ollama: Response received ")
                self.log_terminal(f"[RESPONSE] Ollama: {response}")
            except Exception as e:
                self.status_var.set(f"Ollama error: {e}")
                self.log_terminal(f"[ERROR] Ollama error: {e}")
        threading.Thread(target=run, daemon=True).start()

    def start_process(self):
        folder = self.folder_var.get().strip()
        prompt = self.prompt_text.get('1.0', 'end').strip()
        if not folder:
            self.status_var.set("Project folder is required.")
            self.log_terminal("[ERROR] Project folder is required.")
            return
        self.start_btn.config(state='disabled')
        self.status_var.set("Creating book structure...")
        self.log_terminal("[CHECKPOINT] Creating book structure...")
        threading.Thread(target=self.run_all, args=(folder, prompt)).start()

    def run_all(self, folder, prompt):
        try:
            if not os.path.exists(folder):
                os.makedirs(folder, exist_ok=True)
                self.status_var.set(f"Created folder: {folder}")
                self.log_terminal(f"[CHECKPOINT] Created folder: {folder}")
            self.status_var.set(f"Creating book structure in '{folder}'...")
            self.log_terminal(f"[CHECKPOINT] Creating book structure in '{folder}'...")
            base_path = create_novel_folders_from_path(folder, prompt)
            self.status_var.set("Folders created. Starting AI generation...")
            self.log_terminal("[CHECKPOINT] Folders created. Starting AI generation...")
            fill_md_files(base_path, prompt, status_callback=self.log_terminal)
            self.status_var.set("[SUCCESS] All done!")
            self.log_terminal("[SUCCESS] All done!")
        except Exception as e:
            self.status_var.set(f"[ERROR] {e}")
            self.log_terminal(f"[ERROR] {e}")
        finally:
            self.start_btn.config(state='normal')

# Helper to allow using an explicit path instead of book name

def create_novel_folders_from_path(base_path, prompt=None):
    folders = [
        "overview", "books", "notes", "characters", "scenes", "research",
        "drafts", "synopsis", "outline", "backmatter", "frontmatter"
    ]
    for folder in folders:
        os.makedirs(os.path.join(base_path, folder), exist_ok=True)
    drafts_path = os.path.join(base_path, "drafts")
    for i in range(1, 31):
        chapter_file = os.path.join(drafts_path, f"chapter{i}.md")
        with open(chapter_file, 'w', encoding='utf-8') as f:
            f.write(f"# Chapter {i}\n\n")
    structure_file = os.path.join(base_path, "folder_structure.txt")
    with open(structure_file, 'w', encoding='utf-8') as f:
        for folder in folders:
            f.write(f"{folder}\n")
    prompt_file = os.path.join(base_path, "overview", "manifesto_prompt.txt")
    prompt_text = prompt if prompt else "[Add your book prompt here!]"
    with open(prompt_file, 'w', encoding='utf-8') as f:
        f.write(prompt_text)
    return base_path

if __name__ == "__main__":
    root = tk.Tk()
    app = BookstartApp(root)
    root.mainloop()
