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
    chapter_files = [os.path.join(chapters_dir, f) for f in sorted(os.listdir(chapters_dir)) if f.endswith(".md")]
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

# --- Enhance Chapters Sidebar Panel (Docked) ---
class EnhanceChaptersSidebar(tk.Frame):
    def __init__(self, master, get_project_folder, terminal_log_callback, *args, **kwargs):
        super().__init__(master, bg="#161821", *args, **kwargs)
        self.get_project_folder = get_project_folder
        self.terminal_log_callback = terminal_log_callback
        self.pack_propagate(False)
        self.configure(width=420, padx=18, pady=18)
        # Status Bar
        self.status_var = tk.StringVar(value="Disconnected")
        status_label = tk.Label(self, textvariable=self.status_var, fg="#fff", bg="#232946", font=("Helvetica Neue", 11, "bold"), anchor="w")
        status_label.pack(fill="x", pady=(0, 10))
        # Mode
        self.mode_var = tk.StringVar(value="auto")
        mode_frame = tk.Frame(self, bg="#161821")
        auto_btn = tk.Radiobutton(mode_frame, text="Auto", variable=self.mode_var, value="auto", bg="#161821", fg="#fff", selectcolor="#232946", font=("Helvetica Neue", 12), command=self.switch_mode)
        manual_btn = tk.Radiobutton(mode_frame, text="Manual", variable=self.mode_var, value="manual", bg="#161821", fg="#fff", selectcolor="#232946", font=("Helvetica Neue", 12), command=self.switch_mode)
        auto_btn.pack(side="left", padx=8)
        manual_btn.pack(side="left", padx=8)
        mode_frame.pack(fill="x", pady=(0, 10))
        # Progress Bar
        self.progress = ttk.Progressbar(self, orient="horizontal", length=300, mode="determinate")
        self.progress.pack(fill="x", pady=(0, 10))
        # Log Area (mirrored/shared with main app)
        self.log_box = scrolledtext.ScrolledText(self, height=10, bg="#232946", fg="#fff", font=("Fira Mono", 12))
        self.log_box.pack(fill="both", expand=True, pady=(0, 10))
        # Controls
        control_frame = tk.Frame(self, bg="#161821")
        self.enhance_btn = tk.Button(control_frame, text="Enhance Now", command=self.run_manual, font=("Helvetica Neue", 12), bg="#3da9fc", fg="#161821", activebackground="#232946", activeforeground="#fff", relief='flat', padx=18, pady=6, borderwidth=0, highlightthickness=0)
        self.enhance_btn.pack(side="left", padx=6)
        self.refresh_btn = tk.Button(control_frame, text="Refresh", command=self.refresh_status, font=("Helvetica Neue", 12), bg="#232946", fg="#fff", activebackground="#3da9fc", activeforeground="#161821", relief='flat', padx=18, pady=6, borderwidth=0, highlightthickness=0)
        self.refresh_btn.pack(side="left", padx=6)
        self.wp_btn = tk.Button(control_frame, text="Word Processor Mode", command=self.launch_wordpro_feed, font=("Helvetica Neue", 12), bg="#232946", fg="#fff", activebackground="#3da9fc", activeforeground="#161821", relief='flat', padx=18, pady=6, borderwidth=0, highlightthickness=0)
        self.wp_btn.pack(side="left", padx=6)
        control_frame.pack(fill="x", pady=(0, 0))
        # Watcher thread for auto mode
        self.watcher_thread = None
        self.stop_event = threading.Event()
        self.switch_mode()
        self.refresh_status()

    def switch_mode(self):
        mode = self.mode_var.get()
        if mode == "auto":
            self.enhance_btn.config(state="disabled")
            self.start_watcher()
        else:
            self.enhance_btn.config(state="normal")
            self.stop_watcher()

    def start_watcher(self):
        if self.watcher_thread and self.watcher_thread.is_alive():
            return
        self.stop_event.clear()
        self.watcher_thread = threading.Thread(target=self.watch_for_checkpoints, daemon=True)
        self.watcher_thread.start()

    def stop_watcher(self):
        self.stop_event.set()
        if self.watcher_thread and self.watcher_thread.is_alive():
            self.watcher_thread.join(timeout=0.5)
        self.watcher_thread = None

    def watch_for_checkpoints(self):
        """Watches the log box for checkpoints and triggers actions on key events."""
        last_log_size = 0
        chapter1_created = False
        chapter2_created = False
        enhance_triggered = False
        while not self.stop_event.is_set():
            # Check for checkpoint lines in the log
            log_content = self.log_box.get("1.0", "end-1c")
            lines = log_content.splitlines()
            new_lines = lines[last_log_size:]
            for line in new_lines:
                if "[CHECKPOINT] Folders created. Starting AI generation" in line:
                    self.status_var.set("Folders created. Watching for chapter1.md...")
                    self.log_box.insert("end", "[AUTO] Detected folders created checkpoint.\n")
                    self.log_box.see("end")
                if not chapter1_created and "chapter1.md" in line:
                    chapter1_created = True
                    self.status_var.set("chapter1.md created. Watching for chapter2.md...")
                    self.log_box.insert("end", "[AUTO] Detected chapter1.md creation.\n")
                    self.log_box.see("end")
                if chapter1_created and not chapter2_created and "chapter2.md" in line:
                    chapter2_created = True
                    self.status_var.set("chapter2.md created. Triggering enhancement for chapter1.md...")
                    self.log_box.insert("end", "[AUTO] Detected chapter2.md creation. Triggering enhancement for chapter1.md...\n")
                    self.log_box.see("end")
                    if not enhance_triggered:
                        self.trigger_enhance_chapter1()
                        enhance_triggered = True
            last_log_size = len(lines)
            # Optionally also check the filesystem for chapter1.md and chapter2.md
            folder = self.get_project_folder()
            if folder:
                drafts_dir = os.path.join(folder, "drafts")
                chapter1_path = os.path.join(drafts_dir, "chapter1.md")
                chapter2_path = os.path.join(drafts_dir, "chapter2.md")
                if os.path.exists(chapter1_path) and not chapter1_created:
                    chapter1_created = True
                    self.status_var.set("chapter1.md created (fs). Watching for chapter2.md...")
                    self.log_box.insert("end", "[AUTO] Detected chapter1.md in filesystem.\n")
                    self.log_box.see("end")
                if chapter1_created and os.path.exists(chapter2_path) and not chapter2_created:
                    chapter2_created = True
                    self.status_var.set("chapter2.md created (fs). Triggering enhancement for chapter1.md...")
                    self.log_box.insert("end", "[AUTO] Detected chapter2.md in filesystem. Triggering enhancement for chapter1.md...\n")
                    self.log_box.see("end")
                    if not enhance_triggered:
                        self.trigger_enhance_chapter1()
                        enhance_triggered = True
            self.stop_event.wait(1)

    def trigger_enhance_chapter1(self):
        """Immediately run 03_enhance_chapters.py to enhance chapter1.md as soon as chapter2.md is created."""
        folder = self.get_project_folder()
        if not folder:
            self.log_box.insert("end", "[AUTO] Cannot enhance: project folder not set.\n")
            self.log_box.see("end")
            return
        drafts_dir = os.path.join(folder, "drafts")
        chapter1_path = os.path.join(drafts_dir, "chapter1.md")
        if not os.path.exists(chapter1_path):
            self.log_box.insert("end", f"[AUTO] Cannot enhance: {chapter1_path} does not exist.\n")
            self.log_box.see("end")
            return
        # Run 03_enhance_chapters.py for chapter1.md
        self.log_box.insert("end", f"[AUTO] Starting enhancement for {chapter1_path}...\n")
        self.log_box.see("end")
        import subprocess
        try:
            # Run the enhancement script for chapter1.md
            script_path = os.path.join(os.path.dirname(__file__), "03_enhance_chapters.py")
            result = subprocess.run([
                "python3", script_path,
                "--project", folder,
                "--chapter", chapter1_path
            ], capture_output=True, text=True, timeout=600)
            self.log_box.insert("end", f"[AUTO] Enhancement complete. Output:\n{result.stdout}\n")
            if result.stderr:
                self.log_box.insert("end", f"[AUTO] Enhancement errors:\n{result.stderr}\n")
            self.log_box.see("end")
        except Exception as e:
            self.log_box.insert("end", f"[AUTO] Enhancement failed: {e}\n")
            self.log_box.see("end")

    def refresh_status(self):
        folder = self.get_project_folder()
        connected = bool(folder)
        self.status_var.set(f"Connected: {folder if connected else 'None'}")
        # Optionally, update progress bar color/appearance here

    def run_manual(self):
        # Placeholder for manual enhance logic
        self.terminal_log_callback("Manual enhancement triggered.")
        self.log_box.insert("end", "Manual enhancement triggered.\n")
        self.log_box.see("end")

    def launch_wordpro_feed(self):
        import subprocess
        folder = self.get_project_folder()
        if not folder or not os.path.isdir(folder):
            from tkinter import messagebox
            messagebox.showerror("Word Processor Mode", "Please select a valid project folder first.")
            return
        script = os.path.join(os.path.dirname(__file__), "../full_wordpro_feed.py")
        script = os.path.abspath(script)
        subprocess.Popen(["python3", script, folder], cwd=os.path.dirname(script))

# --- ChapterFeedWordProcessor class ---
class ChapterFeedWordProcessor(tk.Frame):
    def __init__(self, master, get_project_folder, *args, **kwargs):
        super().__init__(master, bg="#161821", *args, **kwargs)
        self.get_project_folder = get_project_folder
        self.feed_file = None  # Will be set on refresh
        self.text = tk.Text(self, wrap='word', font=("Fira Mono", 13), bg="#232946", fg="#fff", insertbackground="#fff", undo=True, autoseparators=True, maxundo=-1)
        self.text.pack(fill="both", expand=True, padx=0, pady=0)
        self.text.bind("<Button-3>", self.show_context_menu)
        self.text.bind("<Control-s>", self.save_feed_file)
        self.text.config(state='normal')
        self.menu = tk.Menu(self, tearoff=0)
        self.menu.add_command(label="Copy", command=lambda: self.text.event_generate('<<Copy>>'))
        self.menu.add_command(label="Cut", command=lambda: self.text.event_generate('<<Cut>>'))
        self.menu.add_command(label="Paste", command=lambda: self.text.event_generate('<<Paste>>'))
        self.menu.add_command(label="Select All", command=lambda: self.text.event_generate('<<SelectAll>>'))
        self.menu.add_separator()
        self.menu.add_command(label="Save Feed As...", command=self.save_feed_as)
        self.menu.add_command(label="Open Feed in Editor", command=self.open_feed_external)
        self.menu.add_separator()
        self.menu.add_command(label="Clear", command=self.clear_feed)
        self.menu.add_separator()
        self.menu.add_command(label="Look Up", command=self.lookup_selection)
        self.menu.add_command(label="Spelling/Grammar", command=self.open_spelling)
        # Apple native tools (spellcheck, dictionary, etc) are available in Tkinter Text on macOS
        # Optionally add formatting commands (bold, italic, underline) here
        self.refresh_feed()

    def show_context_menu(self, event):
        self.menu.tk_popup(event.x_root, event.y_root)
    def save_feed_file(self, event=None):
        if self.feed_file:
            with open(self.feed_file, 'w', encoding='utf-8') as f:
                f.write(self.text.get('1.0', 'end-1c'))
    def save_feed_as(self):
        path = filedialog.asksaveasfilename(defaultextension='.txt', filetypes=[('Text Files', '*.txt'), ('All Files', '*.*')])
        if path:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(self.text.get('1.0', 'end-1c'))
    def open_feed_external(self):
        if self.feed_file and os.path.exists(self.feed_file):
            subprocess.Popen(['open', self.feed_file])
    def clear_feed(self):
        self.text.delete('1.0', 'end')
    def lookup_selection(self):
        # macOS Look Up (dictionary) integration
        self.text.event_generate('<<Lookup>>')
    def open_spelling(self):
        self.text.event_generate('<<CheckSpelling>>')
    def refresh_feed(self):
        folder = self.get_project_folder()
        if not folder:
            self.text.delete('1.0', 'end')
            self.text.insert('1.0', '[No project folder selected.]')
            return
        feed_path = os.path.join(folder, 'project_feed.txt')
        self.feed_file = feed_path
        # Aggregate manifesto + chapters
        manifest_path = os.path.join(folder, 'overview', 'manifesto_prompt.txt')
        drafts_dir = os.path.join(folder, 'drafts')
        content = ''
        if os.path.exists(manifest_path):
            with open(manifest_path, 'r', encoding='utf-8') as f:
                content += '--- Manifesto ---\n' + f.read().strip() + '\n\n'
        if os.path.isdir(drafts_dir):
            for i in range(1, 31):
                chapter_file = os.path.join(drafts_dir, f'chapter{i}.md')
                if os.path.exists(chapter_file):
                    with open(chapter_file, 'r', encoding='utf-8') as f:
                        chapter_content = f.read().strip()
                    content += f'--- Chapter {i} ---\n{chapter_content}\n\n'
        with open(feed_path, 'w', encoding='utf-8') as f:
            f.write(content)
        self.text.config(state='normal')
        self.text.delete('1.0', 'end')
        self.text.insert('1.0', content)
        self.text.config(state='normal')

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
        browse_btn = tk.Button(folder_row, text="Browse", font=button_font, command=self.browse_folder, bg="#394867", fg="#e0e0e0", activebackground="#3da9fc", activeforeground="#161821", relief='flat', padx=18, pady=6, borderwidth=0, highlightthickness=0)
        browse_btn.grid(row=0, column=1, padx=(10,0))
        create_btn = tk.Button(folder_row, text="New", font=button_font, command=self.create_new_folder, bg="#394867", fg="#e0e0e0", activebackground="#3da9fc", activeforeground="#161821", relief='flat', padx=18, pady=6, borderwidth=0, highlightthickness=0)
        create_btn.grid(row=0, column=2, padx=(10,0))
        open_btn = tk.Button(folder_row, text="Open", font=button_font, command=self.open_in_finder, bg="#394867", fg="#e0e0e0", activebackground="#3da9fc", activeforeground="#161821", relief='flat', padx=18, pady=6, borderwidth=0, highlightthickness=0)
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

        # Add the sidebar as a right-docked panel
        self.sidebar = EnhanceChaptersSidebar(root, lambda: self.folder_var.get().strip(), terminal_log_callback=self.log_terminal)
        self.sidebar.grid(row=0, column=2, rowspan=8, sticky="nsew", padx=10, pady=10)
        self.add_save_menu()

        # Add the ChapterFeedWordProcessor as a bottom-docked panel
        self.feed_window = ChapterFeedWordProcessor(root, lambda: self.folder_var.get().strip())
        self.feed_window.grid(row=8, column=0, columnspan=3, sticky="nsew", padx=10, pady=10)

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

    def add_save_menu(self):
        # --- Robustly recreate the full menu bar: File, Edit, Window, Help, Save ---
        menubar = tk.Menu(self.root)
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New", command=self.new_project)
        file_menu.add_command(label="Open", command=self.load_project)
        file_menu.add_command(label="Save", command=self.save_project, accelerator="Ctrl+S")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        # Save/Load section inside File menu
        file_menu.add_separator()
        file_menu.add_command(label="New Project", command=self.new_project)
        file_menu.add_command(label="Save Project", command=self.save_project)
        file_menu.add_command(label="Save Project As...", command=self.save_project_as)
        file_menu.add_command(label="Load Project...", command=self.load_project)
        self.file_recent_projects_menu = tk.Menu(file_menu, tearoff=0)
        file_menu.add_cascade(label="Recent Projects", menu=self.file_recent_projects_menu)
        menubar.add_cascade(label="File", menu=file_menu)
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Undo")
        edit_menu.add_command(label="Redo")
        edit_menu.add_separator()
        edit_menu.add_command(label="Cut")
        edit_menu.add_command(label="Copy")
        edit_menu.add_command(label="Paste")
        menubar.add_cascade(label="Edit", menu=edit_menu)
        # Window menu
        window_menu = tk.Menu(menubar, tearoff=0)
        window_menu.add_command(label="Minimize")
        window_menu.add_command(label="Zoom")
        menubar.add_cascade(label="Window", menu=window_menu)
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About")
        menubar.add_cascade(label="Help", menu=help_menu)
        # --- Dedicated Save menu ---
        save_menu = tk.Menu(menubar, tearoff=0)
        save_menu.add_command(label="New Project", command=self.new_project)
        save_menu.add_command(label="Save Project", command=self.save_project, accelerator="Ctrl+S")
        save_menu.add_command(label="Save Project As...", command=self.save_project_as)
        save_menu.add_command(label="Load Project...", command=self.load_project)
        self.recent_projects_menu = tk.Menu(save_menu, tearoff=0)
        save_menu.add_cascade(label="Recent Projects", menu=self.recent_projects_menu)
        menubar.add_cascade(label="Save", menu=save_menu)
        # Set the menu bar
        self.root.config(menu=menubar)
        # Update both recent projects menus
        self.update_recent_projects_menu()
        self.update_file_recent_projects_menu()
        # Keyboard shortcut Ctrl+S to open Save menu (show Save menu as a dropdown)
        def open_save_menu(event=None):
            # Try to post the Save menu under the menubar
            try:
                x = self.root.winfo_rootx() + 200
                y = self.root.winfo_rooty() + 30
                save_menu.post(x, y)
            except Exception:
                pass
            return "break"
        self.root.bind_all('<Control-s>', open_save_menu)
        self.root.bind_all('<Command-s>', open_save_menu)  # For Mac

    def update_file_recent_projects_menu(self):
        if hasattr(self, 'file_recent_projects_menu'):
            self.file_recent_projects_menu.delete(0, 'end')
            recent = self.get_recent_projects()
            for path in recent:
                self.file_recent_projects_menu.add_command(label=path, command=lambda p=path: self.load_project(p))

    def update_recent_projects_menu(self):
        self.recent_projects_menu.delete(0, 'end')
        recent = self.get_recent_projects()
        for path in recent:
            self.recent_projects_menu.add_command(label=path, command=lambda p=path: self.load_project(p))

    def get_recent_projects(self):
        # Load recent projects from a config file in user's home directory
        cfg_path = os.path.expanduser("~/.bookstart_recent.json")
        if os.path.exists(cfg_path):
            try:
                with open(cfg_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def add_to_recent_projects(self, path):
        cfg_path = os.path.expanduser("~/.bookstart_recent.json")
        recent = self.get_recent_projects()
        if path in recent:
            recent.remove(path)
        recent.insert(0, path)
        recent = recent[:10]
        with open(cfg_path, 'w', encoding='utf-8') as f:
            json.dump(recent, f)
        self.update_recent_projects_menu()
        self.update_file_recent_projects_menu()

    def save_project(self):
        folder = self.folder_var.get().strip()
        if not folder:
            messagebox.showerror("Save Project", "No project folder selected.")
            return
        manifest = self.collect_project_state()
        manifest_path = os.path.join(folder, "bookstart_project.json")
        try:
            with open(manifest_path, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, indent=2)
            self.add_to_recent_projects(folder)
            self.log_terminal(f"[INFO] Project saved to {manifest_path}")
        except Exception as e:
            messagebox.showerror("Save Project", f"Failed to save project: {e}")

    def save_project_as(self):
        folder = filedialog.askdirectory(title="Select Folder to Save Project")
        if not folder:
            return
        self.folder_var.set(folder)
        self.save_project()

    def load_project(self, path=None):
        if not path:
            folder = filedialog.askdirectory(title="Select Project Folder to Load")
        else:
            folder = path
        if not folder:
            return
        manifest_path = os.path.join(folder, "bookstart_project.json")
        if not os.path.exists(manifest_path):
            messagebox.showerror("Load Project", f"No manifest found at {manifest_path}")
            return
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
            self.restore_project_state(manifest)
            self.folder_var.set(folder)
            self.add_to_recent_projects(folder)
            self.log_terminal(f"[INFO] Project loaded from {manifest_path}")
        except Exception as e:
            messagebox.showerror("Load Project", f"Failed to load project: {e}")

    def new_project(self):
        folder = filedialog.askdirectory(title="Select Parent Directory for New Project")
        if not folder:
            return
        name = simpledialog.askstring("New Project", "Enter new project name:")
        if not name:
            return
        new_path = os.path.join(folder, name)
        if not os.path.exists(new_path):
            os.makedirs(new_path)
        self.folder_var.set(new_path)
        self.save_project()

    def collect_project_state(self):
        # Gather all state/UI/logs/etc.
        state = {
            "project_folder": self.folder_var.get().strip(),
            "idea_text": self.idea_text.get("1.0", "end-1c"),
            "prompt_text": self.prompt_text.get("1.0", "end-1c"),
            "status_var": self.status_var.get(),
            "sidebar_mode": getattr(self.sidebar, 'mode_var', None).get() if hasattr(self, 'sidebar') else None,
            "sidebar_log": getattr(self.sidebar, 'log_box', None).get("1.0", "end-1c") if hasattr(self, 'sidebar') else None,
            "terminal_log": self.terminal_box.get("1.0", "end-1c"),
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            # Add more fields as needed (recent commands, UI state, etc)
        }
        return state

    def restore_project_state(self, manifest):
        self.idea_text.delete("1.0", "end")
        self.idea_text.insert("1.0", manifest.get("idea_text", ""))
        self.prompt_text.delete("1.0", "end")
        self.prompt_text.insert("1.0", manifest.get("prompt_text", ""))
        self.status_var.set(manifest.get("status_var", ""))
        if hasattr(self, 'sidebar') and manifest.get("sidebar_mode"):
            self.sidebar.mode_var.set(manifest["sidebar_mode"])
        if hasattr(self, 'sidebar') and manifest.get("sidebar_log"):
            self.sidebar.log_box.delete("1.0", "end")
            self.sidebar.log_box.insert("1.0", manifest["sidebar_log"])
        self.terminal_box.config(state='normal')
        self.terminal_box.delete("1.0", "end")
        self.terminal_box.insert("1.0", manifest.get("terminal_log", ""))
        self.terminal_box.config(state='disabled')

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

# --- Main App Launch ---
if __name__ == "__main__":
    root = tk.Tk()
    app = BookstartApp(root)
    root.mainloop()
