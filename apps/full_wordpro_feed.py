import os
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import tkinter.font as tkfont
import subprocess
import sys
import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llamacorn-1.1b-chat.Q8_0:latest"
OLLAMA_FEATURES = [
    ("Add Profanity", "add profanity"),
    ("Add Spoilers", "add spoilers"),
    ("Add Humor", "add humor"),
    ("Add Literary Style", "add literary style"),
    ("Add Dialogue", "add dialogue"),
    ("Add Metaphors", "add metaphors"),
    ("Add Citations", "add citations"),
    ("Add Descriptions", "add descriptions"),
    ("Add Suspense", "add suspense"),
    ("Add Foreshadowing", "add foreshadowing"),
]

class FullWordProFeed(tk.Toplevel):
    def __init__(self, master=None, project_folder=None):
        super().__init__(master)
        self.title("Word Processor Mode - Project Feed")
        self.geometry("1000x800")
        self.configure(bg="#161821")
        self.project_folder = project_folder or os.getcwd()
        self.feed_file = os.path.join(self.project_folder, 'project_feed.txt')
        self.immersive = False
        self.typewriter_mode = False
        self._build_ui()
        self.refresh_feed()
        self.text.bind('<KeyRelease>', self.update_word_count)
        self.text.bind('<Button-3>', self.show_context_menu)
        self.text.bind('<Configure>', self._typewriter_scroll)

    def _build_ui(self):
        # Fonts
        self.font = tkfont.Font(family="Fira Mono", size=14)
        # Menu bar (File menu only, for Save, Export, Exit)
        self.menu = tk.Menu(self)
        file_menu = tk.Menu(self.menu, tearoff=0)
        file_menu.add_command(label="Save", command=self.save_feed_file)
        file_menu.add_command(label="Export", command=self.export_feed_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.destroy)
        self.menu.add_cascade(label="File", menu=file_menu)
        window_menu = tk.Menu(self.menu, tearoff=0)
        window_menu.add_command(label="Toggle Immersive Mode", command=self.toggle_immersive)
        window_menu.add_command(label="Toggle Typewriter Mode", command=self.toggle_typewriter)
        self.menu.add_cascade(label="Window", menu=window_menu)
        self.config(menu=self.menu)
        # Main text area
        self.text = tk.Text(self, wrap='word', font=self.font, bg="#232946", fg="#fff", insertbackground="#fff", undo=True, autoseparators=True, maxundo=-1)
        self.text.pack(fill="both", expand=True, padx=0, pady=(0, 0))
        # Context menu
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Copy", command=lambda: self.text.event_generate('<<Copy>>'))
        self.context_menu.add_command(label="Cut", command=lambda: self.text.event_generate('<<Cut>>'))
        self.context_menu.add_command(label="Paste", command=lambda: self.text.event_generate('<<Paste>>'))
        self.context_menu.add_command(label="Select All", command=lambda: self.text.event_generate('<<SelectAll>>'))
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Save As...", command=self.export_feed_file)
        self.context_menu.add_command(label="Open in Editor", command=self.open_feed_external)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Clear", command=self.clear_feed)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Look Up", command=self.lookup_selection)
        self.context_menu.add_command(label="Spelling/Grammar", command=self.open_spelling)
        self.context_menu.add_separator()
        # --- AI Actions: Selection ---
        selection_menu = tk.Menu(self.context_menu, tearoff=0)
        selection_menu.add_command(label="Rewrite as...", command=self.rewrite_as_ai)
        selection_menu.add_command(label="Summarize Selection", command=self.summarize_selection_ai)
        selection_menu.add_command(label="Extend Selection", command=self.extend_selection_ai)
        selection_menu.add_command(label="Fix Grammar/Spelling", command=self.fix_grammar_ai)
        selection_menu.add_command(label="Transform (Custom)", command=self.transform_selection_ai)
        self.context_menu.add_cascade(label="Selection AI Actions", menu=selection_menu)
        # --- Transform Submenu ---
        transform_menu = tk.Menu(self.context_menu, tearoff=0)
        transform_menu.add_command(label="Make More Vivid/Sensory", command=self.transform_vivid_ai)
        transform_menu.add_command(label="Turn Into Dialogue", command=self.transform_dialogue_ai)
        transform_menu.add_command(label="Add Suspense", command=self.transform_suspense_ai)
        transform_menu.add_command(label="Make Poetic", command=self.transform_poetic_ai)
        transform_menu.add_command(label="Condense to One Powerful Sentence", command=self.transform_condense_ai)
        self.context_menu.add_cascade(label="Transform", menu=transform_menu)
        # --- Imagine Submenu ---
        imagine_menu = tk.Menu(self.context_menu, tearoff=0)
        imagine_menu.add_command(label="Imagine a Scene", command=self.imagine_scene_ai)
        imagine_menu.add_command(label="Imagine a Character", command=self.imagine_character_ai)
        imagine_menu.add_command(label="Imagine a Twist", command=self.imagine_twist_ai)
        imagine_menu.add_command(label="Imagine a Setting", command=self.imagine_setting_ai)
        imagine_menu.add_command(label="Imagine a Backstory", command=self.imagine_backstory_ai)
        self.context_menu.add_cascade(label="Imagine", menu=imagine_menu)
        # --- Feature Toggles ---
        self.feature_vars = {}
        for label, _ in OLLAMA_FEATURES:
            var = tk.BooleanVar(value=False)
            self.feature_vars[label] = var
            self.context_menu.add_checkbutton(label=label, variable=var)
        # Bottom bar
        bottom_frame = tk.Frame(self, bg="#232946")
        bottom_frame.pack(fill='x', side='bottom')
        self.save_btn = tk.Button(bottom_frame, text="Save", command=self.save_feed_file, bg="#3da9fc", fg="#161821", font=self.font)
        self.save_btn.pack(side='left', padx=8, pady=8)
        self.export_btn = tk.Button(bottom_frame, text="Export", command=self.export_feed_file, bg="#232946", fg="#fff", font=self.font)
        self.export_btn.pack(side='left', padx=8, pady=8)
        self.refresh_btn = tk.Button(bottom_frame, text="Refresh", command=self.refresh_feed, bg="#232946", fg="#fff", font=self.font)
        self.refresh_btn.pack(side='left', padx=8, pady=8)
        self.word_count_var = tk.StringVar(value="Words: 0")
        self.word_count_label = tk.Label(bottom_frame, textvariable=self.word_count_var, bg="#232946", fg="#fff", font=self.font)
        self.word_count_label.pack(side='right', padx=16)
        # --- Keyboard Shortcut for AI ---
        self.text.bind('<Command-Return>', lambda e: self.continue_writing_ai())
        self.text.bind('<Control-Return>', lambda e: self.continue_writing_ai())

    def show_context_menu(self, event):
        self.context_menu.tk_popup(event.x_root, event.y_root)

    def get_ollama_prompt(self, base_prompt):
        toggles = [desc for label, desc in OLLAMA_FEATURES if self.feature_vars[label].get()]
        if toggles:
            return base_prompt + "\n\nFeatures: " + ", ".join(toggles)
        return base_prompt

    def call_ollama(self, prompt):
        data = {
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False
        }
        try:
            response = requests.post(OLLAMA_URL, json=data, timeout=60)
            response.raise_for_status()
            result = response.json()
            return result.get("response", "")
        except Exception as e:
            messagebox.showerror("Ollama Error", f"Failed to contact Ollama:\n{e}")
            return None

    def explain_selection_ai(self):
        selection = self.text.get(tk.SEL_FIRST, tk.SEL_LAST) if self.text.tag_ranges(tk.SEL) else ""
        if not selection:
            messagebox.showinfo("Explain This", "Please select text to explain.")
            return
        prompt = self.get_ollama_prompt(f"Explain the following text in detail:\n{selection}")
        result = self.call_ollama(prompt)
        if result:
            self.text.insert(tk.INSERT, f"\n\n[AI Explanation]:\n{result}\n")

    def continue_writing_ai(self):
        context = self.text.get('1.0', tk.END).strip()
        prompt = self.get_ollama_prompt(f"Continue writing based on the following context:\n{context}")
        result = self.call_ollama(prompt)
        if result:
            self.text.insert(tk.INSERT, f"\n{result}\n")

    def rewrite_as_ai(self):
        selection = self.text.get(tk.SEL_FIRST, tk.SEL_LAST) if self.text.tag_ranges(tk.SEL) else ""
        if not selection:
            messagebox.showinfo("Rewrite as...", "Please select text to rewrite.")
            return
        # Ask user for style/tone
        style = simpledialog.askstring("Rewrite as...", "Enter style/tone (e.g. Formal, Casual, Dramatic, Humorous, Literary):")
        if not style:
            return
        prompt = self.get_ollama_prompt(f"Rewrite the following text in a {style} style.\nText:\n{selection}")
        result = self.call_ollama(prompt)
        if result:
            self.text.delete(tk.SEL_FIRST, tk.SEL_LAST)
            self.text.insert(tk.INSERT, result.strip())

    def summarize_selection_ai(self):
        selection = self.text.get(tk.SEL_FIRST, tk.SEL_LAST) if self.text.tag_ranges(tk.SEL) else ""
        if not selection:
            messagebox.showinfo("Summarize Selection", "Please select text to summarize.")
            return
        prompt = self.get_ollama_prompt(f"Summarize the following text concisely:\n{selection}")
        result = self.call_ollama(prompt)
        if result:
            self.text.insert(tk.INSERT, f"\n[AI Summary]: {result.strip()}\n")

    def extend_selection_ai(self):
        selection = self.text.get(tk.SEL_FIRST, tk.SEL_LAST) if self.text.tag_ranges(tk.SEL) else ""
        if not selection:
            messagebox.showinfo("Extend Selection", "Please select text to extend.")
            return
        prompt = self.get_ollama_prompt(f"Continue and expand on the following text:\n{selection}")
        result = self.call_ollama(prompt)
        if result:
            self.text.insert(tk.SEL_LAST, f" {result.strip()}")

    def fix_grammar_ai(self):
        selection = self.text.get(tk.SEL_FIRST, tk.SEL_LAST) if self.text.tag_ranges(tk.SEL) else ""
        if not selection:
            messagebox.showinfo("Fix Grammar/Spelling", "Please select text to correct.")
            return
        prompt = self.get_ollama_prompt(f"Correct the grammar and spelling of the following text:\n{selection}")
        result = self.call_ollama(prompt)
        if result:
            self.text.delete(tk.SEL_FIRST, tk.SEL_LAST)
            self.text.insert(tk.INSERT, result.strip())

    def transform_selection_ai(self):
        selection = self.text.get(tk.SEL_FIRST, tk.SEL_LAST) if self.text.tag_ranges(tk.SEL) else ""
        if not selection:
            messagebox.showinfo("Transform Selection", "Please select text to transform.")
            return
        transformation = simpledialog.askstring(
            "Transform Selection",
            "Describe the creative transformation (e.g., 'Make this poetic', 'Turn into dialogue', 'Add suspense', 'Make vivid and sensory', 'Make this humorous', etc.):"
        )
        if not transformation:
            return
        prompt = self.get_ollama_prompt(f"{transformation} The following text:\n{selection}")
        result = self.call_ollama(prompt)
        if result:
            self.text.delete(tk.SEL_FIRST, tk.SEL_LAST)
            self.text.insert(tk.INSERT, result.strip())

    # --- Transform Commands ---
    def transform_vivid_ai(self):
        self._transform_selected_with_prompt("Rewrite the following text to be more vivid and sensory, adding rich detail and description.")

    def transform_dialogue_ai(self):
        self._transform_selected_with_prompt("Transform the following narrative into a realistic dialogue between characters.")

    def transform_suspense_ai(self):
        self._transform_selected_with_prompt("Rewrite the following text to add suspense and tension.")

    def transform_poetic_ai(self):
        self._transform_selected_with_prompt("Transform the following text into a poetic, lyrical style.")

    def transform_condense_ai(self):
        self._transform_selected_with_prompt("Condense the following text into a single, powerful, impactful sentence.")

    # --- Imagine Commands ---
    def imagine_scene_ai(self):
        self._transform_selected_with_prompt("Imagine and describe a vivid scene inspired by the following text.")

    def imagine_character_ai(self):
        self._transform_selected_with_prompt("Invent and describe a new character that could appear in the following text.")

    def imagine_twist_ai(self):
        self._transform_selected_with_prompt("Imagine a surprising plot twist that could happen next, based on the following text.")

    def imagine_setting_ai(self):
        self._transform_selected_with_prompt("Describe a rich, immersive setting where the following text could take place.")

    def imagine_backstory_ai(self):
        self._transform_selected_with_prompt("Invent a compelling backstory for the main character(s) in the following text.")

    def _transform_selected_with_prompt(self, base_prompt):
        selection = self.text.get(tk.SEL_FIRST, tk.SEL_LAST) if self.text.tag_ranges(tk.SEL) else ""
        if not selection:
            messagebox.showinfo("AI Action", "Please select text to use this action.")
            return
        prompt = self.get_ollama_prompt(f"{base_prompt}\n{selection}")
        result = self.call_ollama(prompt)
        if result:
            self.text.delete(tk.SEL_FIRST, tk.SEL_LAST)
            self.text.insert(tk.INSERT, result.strip())

    def save_feed_file(self):
        with open(self.feed_file, 'w', encoding='utf-8') as f:
            f.write(self.text.get('1.0', 'end-1c'))

    def export_feed_file(self):
        path = filedialog.asksaveasfilename(defaultextension='.txt', filetypes=[('Text Files', '*.txt'), ('Markdown Files', '*.md'), ('All Files', '*.*')])
        if path:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(self.text.get('1.0', 'end-1c'))

    def open_feed_external(self):
        if os.path.exists(self.feed_file):
            subprocess.Popen(['open', self.feed_file])

    def clear_feed(self):
        self.text.delete('1.0', 'end')

    def lookup_selection(self):
        self.text.event_generate('<<Lookup>>')

    def open_spelling(self):
        self.text.event_generate('<<CheckSpelling>>')

    def refresh_feed(self):
        content = self.aggregate_feed()
        self.text.config(state='normal')
        self.text.delete('1.0', 'end')
        self.text.insert('1.0', content)
        self.text.config(state='normal')
        self.save_feed_file()
        self.update_word_count()

    def aggregate_feed(self):
        folder = self.project_folder
        content = ''
        # Manifesto
        manifest_path = os.path.join(folder, 'overview', 'manifesto_prompt.txt')
        if os.path.exists(manifest_path):
            with open(manifest_path, 'r', encoding='utf-8') as f:
                content += '--- Manifesto ---\n' + f.read().strip() + '\n\n'
        # All .md files from drafts, outline, enhancer
        for root, dirs, files in os.walk(folder):
            for file in sorted(files):
                if file.endswith('.md'):
                    file_path = os.path.join(root, file)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        chapter_content = f.read().strip()
                    rel_path = os.path.relpath(file_path, folder)
                    content += f'--- {rel_path} ---\n{chapter_content}\n\n'
        # Terminal log (if present)
        terminal_log = os.path.join(folder, 'terminal_log.txt')
        if os.path.exists(terminal_log):
            with open(terminal_log, 'r', encoding='utf-8') as f:
                content += '--- Terminal Log ---\n' + f.read().strip() + '\n\n'
        return content

    def update_word_count(self, event=None):
        text = self.text.get('1.0', 'end-1c')
        words = len(text.split())
        self.word_count_var.set(f"Words: {words}")

    def toggle_immersive(self):
        self.immersive = not self.immersive
        if self.immersive:
            self.menu.entryconfig("File", state='disabled')
            self.menu.entryconfig("Window", state='disabled')
            self.save_btn.pack_forget()
            self.export_btn.pack_forget()
            self.refresh_btn.pack_forget()
            self.word_count_label.pack_forget()
            self.config(bg="#232946")
        else:
            self.menu.entryconfig("File", state='normal')
            self.menu.entryconfig("Window", state='normal')
            self.save_btn.pack(side='left', padx=8, pady=8)
            self.export_btn.pack(side='left', padx=8, pady=8)
            self.refresh_btn.pack(side='left', padx=8, pady=8)
            self.word_count_label.pack(side='right', padx=16)
            self.config(bg="#161821")

    def toggle_typewriter(self):
        self.typewriter_mode = not self.typewriter_mode
        self._typewriter_scroll()

    def _typewriter_scroll(self, event=None):
        if self.typewriter_mode:
            self.text.see('insert')
            self.text.yview_moveto(max(self.text.index('insert').split('.')[0], 1) / float(self.text.index('end-1c').split('.')[0]))

# Usage: from your main app, call FullWordProFeed(master, project_folder=...) to launch
if __name__ == "__main__":
    import sys
    import traceback
    root = tk.Tk()
    root.withdraw()  # Hide root window
    folder = None
    try:
        # Accept project folder as command line arg
        if len(sys.argv) > 1 and os.path.isdir(sys.argv[1]):
            folder = sys.argv[1]
            print(f"[WP] Using folder from argv: {folder}")
        else:
            folder = filedialog.askdirectory(title="Select Project Folder")
            print(f"[WP] Using folder from dialog: {folder}")
        if not folder or not os.path.isdir(folder):
            messagebox.showerror("Word Processor Mode", "No valid project folder selected. Please select a folder.")
            print("[WP] No valid folder selected, exiting.")
            root.destroy()
            sys.exit(1)
        print(f"[WP] Launching FullWordProFeed with folder: {folder}")
        wp = FullWordProFeed(master=root, project_folder=folder)
        wp.mainloop()
    except Exception as e:
        tb = traceback.format_exc()
        print(f"[WP] Exception at launch: {e}\n{tb}")
        messagebox.showerror("Word Processor Error", f"An error occurred while launching Word Processor Mode:\n{e}\n\n{tb}")
        root.destroy()
        sys.exit(1)
