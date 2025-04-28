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
        self.title("WordPro Feed (AI Tab Editor)")
        self.geometry("1100x780")
        self.tabs = []
        self.tab_frames = []
        self.tab_buttons = []
        self.current_tab = None
        self.project_folder = project_folder or os.getcwd()
        self.feed_file = os.path.join(self.project_folder, 'project_feed.txt')
        self.immersive = False
        self.typewriter_mode = False
        self._build_tab_ui()
        self._build_context_menu()
        self._build_bottom_bar()
        self.new_tab()

    def _build_tab_ui(self):
        self.tab_bar = tk.Frame(self, bg="#232946")
        self.tab_bar.pack(side=tk.TOP, fill=tk.X)
        self.add_tab_button = tk.Button(self.tab_bar, text="+", command=self.new_tab)
        self.add_tab_button.pack(side=tk.LEFT, padx=2)
        self.tab_button_frame = tk.Frame(self.tab_bar, bg="#232946")
        self.tab_button_frame.pack(side=tk.LEFT, fill=tk.X)
        self.editor_area = tk.Frame(self, bg="#181c24")
        self.editor_area.pack(fill=tk.BOTH, expand=True)

    def new_tab(self):
        tab_index = len(self.tabs)
        tab_name = f"Untitled-{tab_index+1}"
        btn = tk.Button(self.tab_button_frame, text=tab_name, command=lambda idx=tab_index: self.switch_tab(idx))
        btn.pack(side=tk.LEFT, padx=2)
        self.tab_buttons.append(btn)
        frame = tk.Frame(self.editor_area, bg="#181c24")
        text = tk.Text(frame, bg="#181c24", fg="#d6deeb", insertbackground="#ffd580", font=("Fira Mono", 13), wrap="word")
        text.pack(fill=tk.BOTH, expand=True)
        text.bind("<KeyRelease>", self.apply_markdown_highlighting)
        text.bind("<Button-3>", self.show_context_menu)
        text.bind("<Configure>", self._typewriter_scroll)
        text.bind("<<Modified>>", self.on_text_change)
        frame.pack(fill=tk.BOTH, expand=True)
        self.tabs.append(text)
        self.tab_frames.append(frame)
        self.switch_tab(tab_index)

    def switch_tab(self, idx):
        for i, frame in enumerate(self.tab_frames):
            frame.pack_forget()
        self.tab_frames[idx].pack(fill=tk.BOTH, expand=True)
        self.current_tab = idx
        self.apply_markdown_highlighting()
        self.apply_chapter_heading_style()
        self.update_word_count()

    def get_active_text(self):
        return self.tabs[self.current_tab]

    def _build_context_menu(self):
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Copy", command=lambda: self.get_active_text().event_generate('<<Copy>>'))
        self.context_menu.add_command(label="Cut", command=lambda: self.get_active_text().event_generate('<<Cut>>'))
        self.context_menu.add_command(label="Paste", command=lambda: self.get_active_text().event_generate('<<Paste>>'))
        self.context_menu.add_command(label="Select All", command=lambda: self.get_active_text().event_generate('<<SelectAll>>'))
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
        # --- /make Submenu ---
        make_menu = tk.Menu(self.context_menu, tearoff=0)
        make_menu.add_command(label="Make Much Longer", command=self.make_much_longer_ai)
        make_menu.add_command(label="Make More Detailed", command=self.make_more_detailed_ai)
        make_menu.add_command(label="Make Into a Short Story", command=self.make_short_story_ai)
        make_menu.add_command(label="Make Into a Book Premise", command=self.make_book_premise_ai)
        make_menu.add_command(label="Make Into a Chapter Outline", command=self.make_chapter_outline_ai)
        self.context_menu.add_cascade(label="/make", menu=make_menu)
        # --- Highlights Menu ---
        highlight_menu = tk.Menu(self.context_menu, tearoff=0)
        highlight_menu.add_command(label="Yellow Highlight", command=lambda: self.highlight_selection("yellow"))
        highlight_menu.add_command(label="Green Highlight", command=lambda: self.highlight_selection("light green"))
        highlight_menu.add_command(label="Blue Highlight", command=lambda: self.highlight_selection("light blue"))
        highlight_menu.add_command(label="Pink Highlight", command=lambda: self.highlight_selection("pink"))
        highlight_menu.add_command(label="Clear Highlight", command=lambda: self.highlight_selection(None))
        self.context_menu.add_cascade(label="Highlight", menu=highlight_menu)
        # --- Feature Toggles ---
        self.feature_vars = {}
        for label, _ in OLLAMA_FEATURES:
            var = tk.BooleanVar(value=False)
            self.feature_vars[label] = var
            self.context_menu.add_checkbutton(label=label, variable=var)

    def _build_bottom_bar(self):
        self.bottom_bar = tk.Frame(self, relief=tk.RAISED, bd=1)
        self.bottom_bar.pack(side=tk.BOTTOM, fill=tk.X)
        tk.Button(self.bottom_bar, text="Bold", command=self.bold_selection).pack(side=tk.LEFT)
        tk.Button(self.bottom_bar, text="Underline", command=self.underline_selection).pack(side=tk.LEFT)
        tk.Button(self.bottom_bar, text="Font", command=self.change_font).pack(side=tk.LEFT)
        self.refresh_btn = tk.Button(self.bottom_bar, text="Refresh", command=self.refresh_text, font=("Fira Mono", 12), bg="#232946", fg="#fff", activebackground="#3da9fc", activeforeground="#161821", relief='flat', padx=10, pady=4, borderwidth=0, highlightthickness=0)
        self.refresh_btn.pack(side="left", padx=6)
        self.word_count_label = tk.Label(self.bottom_bar, text="Words: 0")
        self.word_count_label.pack(side=tk.RIGHT)

    def show_context_menu(self, event):
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

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
        selection = self.get_active_text().get(tk.SEL_FIRST, tk.SEL_LAST) if self.get_active_text().tag_ranges(tk.SEL) else ""
        if not selection:
            messagebox.showinfo("Explain This", "Please select text to explain.")
            return
        prompt = self.get_ollama_prompt(f"Explain the following text in detail:\n{selection}")
        result = self.call_ollama(prompt)
        if result:
            self.get_active_text().insert(tk.INSERT, f"\n\n[AI Explanation]:\n{result}\n")

    def continue_writing_ai(self):
        context = self.get_active_text().get('1.0', tk.END).strip()
        prompt = self.get_ollama_prompt(f"Continue writing based on the following context:\n{context}")
        result = self.call_ollama(prompt)
        if result:
            self.get_active_text().insert(tk.INSERT, f"\n{result}\n")

    def rewrite_as_ai(self):
        selection = self.get_active_text().get(tk.SEL_FIRST, tk.SEL_LAST) if self.get_active_text().tag_ranges(tk.SEL) else ""
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
            self.get_active_text().delete(tk.SEL_FIRST, tk.SEL_LAST)
            self.get_active_text().insert(tk.INSERT, result.strip())

    def summarize_selection_ai(self):
        selection = self.get_active_text().get(tk.SEL_FIRST, tk.SEL_LAST) if self.get_active_text().tag_ranges(tk.SEL) else ""
        if not selection:
            messagebox.showinfo("Summarize Selection", "Please select text to summarize.")
            return
        prompt = self.get_ollama_prompt(f"Summarize the following text concisely:\n{selection}")
        result = self.call_ollama(prompt)
        if result:
            self.get_active_text().insert(tk.INSERT, f"\n[AI Summary]: {result.strip()}\n")

    def extend_selection_ai(self):
        selection = self.get_active_text().get(tk.SEL_FIRST, tk.SEL_LAST) if self.get_active_text().tag_ranges(tk.SEL) else ""
        if not selection:
            messagebox.showinfo("Extend Selection", "Please select text to extend.")
            return
        prompt = self.get_ollama_prompt(f"Continue and expand on the following text:\n{selection}")
        result = self.call_ollama(prompt)
        if result:
            self.get_active_text().insert(tk.SEL_LAST, f" {result.strip()}")

    def fix_grammar_ai(self):
        selection = self.get_active_text().get(tk.SEL_FIRST, tk.SEL_LAST) if self.get_active_text().tag_ranges(tk.SEL) else ""
        if not selection:
            messagebox.showinfo("Fix Grammar/Spelling", "Please select text to correct.")
            return
        prompt = self.get_ollama_prompt(f"Correct the grammar and spelling of the following text:\n{selection}")
        result = self.call_ollama(prompt)
        if result:
            self.get_active_text().delete(tk.SEL_FIRST, tk.SEL_LAST)
            self.get_active_text().insert(tk.INSERT, result.strip())

    def transform_selection_ai(self):
        selection = self.get_active_text().get(tk.SEL_FIRST, tk.SEL_LAST) if self.get_active_text().tag_ranges(tk.SEL) else ""
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
            self.get_active_text().delete(tk.SEL_FIRST, tk.SEL_LAST)
            self.get_active_text().insert(tk.INSERT, result.strip())

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
        selection = self.get_active_text().get(tk.SEL_FIRST, tk.SEL_LAST) if self.get_active_text().tag_ranges(tk.SEL) else ""
        if not selection:
            messagebox.showinfo("AI Action", "Please select text to use this action.")
            return
        prompt = self.get_ollama_prompt(f"{base_prompt}\n{selection}")
        result = self.call_ollama(prompt)
        if result:
            self.get_active_text().delete(tk.SEL_FIRST, tk.SEL_LAST)
            self.get_active_text().insert(tk.INSERT, result.strip())

    def save_feed_file(self):
        with open(self.feed_file, 'w', encoding='utf-8') as f:
            f.write(self.get_active_text().get('1.0', 'end-1c'))

    def export_feed_file(self):
        path = filedialog.asksaveasfilename(defaultextension='.txt', filetypes=[('Text Files', '*.txt'), ('Markdown Files', '*.md'), ('All Files', '*.*')])
        if path:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(self.get_active_text().get('1.0', 'end-1c'))

    def open_feed_external(self):
        if os.path.exists(self.feed_file):
            subprocess.Popen(['open', self.feed_file])

    def clear_feed(self):
        self.get_active_text().delete('1.0', 'end')

    def lookup_selection(self):
        self.get_active_text().event_generate('<<Lookup>>')

    def open_spelling(self):
        self.get_active_text().event_generate('<<CheckSpelling>>')

    def refresh_feed(self):
        content = self.aggregate_feed()
        self.get_active_text().config(state='normal')
        self.get_active_text().delete('1.0', 'end')
        self.get_active_text().insert('1.0', content)
        self.get_active_text().config(state='normal')
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
        text = self.get_active_text().get('1.0', 'end-1c')
        words = len(text.split())
        self.word_count_label.config(text=f"Words: {words}")

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
            self.get_active_text().see('insert')
            self.get_active_text().yview_moveto(max(self.get_active_text().index('insert').split('.')[0], 1) / float(self.get_active_text().index('end-1c').split('.')[0]))

    # --- /make Commands ---
    def make_much_longer_ai(self):
        self._make_transform_with_prompt("Expand the following text into a much longer, detailed, and immersive passage. Add depth, description, and new content while staying on topic.")

    def make_more_detailed_ai(self):
        self._make_transform_with_prompt("Add significant detail and depth to the following text, elaborating on descriptions, actions, and background.")

    def make_short_story_ai(self):
        self._make_transform_with_prompt("Transform the following text into a complete, well-structured short story. Add a beginning, middle, and end, with character development, conflict, and resolution.")

    def make_book_premise_ai(self):
        self._make_transform_with_prompt("Expand the following text into a full premise for a novel or book. Include the main concept, central conflict, protagonist and antagonist, key themes, and a brief outline of the story’s progression.")

    def make_chapter_outline_ai(self):
        self._make_transform_with_prompt("Transform the following text into a detailed chapter-by-chapter outline for a novel. For each chapter, provide a title and a 1-2 sentence summary of its main events.")

    def _make_transform_with_prompt(self, base_prompt):
        # Use selection if present, otherwise use current paragraph at cursor
        if self.get_active_text().tag_ranges(tk.SEL):
            target_text = self.get_active_text().get(tk.SEL_FIRST, tk.SEL_LAST)
            start, end = tk.SEL_FIRST, tk.SEL_LAST
        else:
            # Get current line/paragraph
            index = self.get_active_text().index(tk.INSERT)
            line_start = self.get_active_text().index(f"{index} linestart")
            line_end = self.get_active_text().index(f"{index} lineend")
            target_text = self.get_active_text().get(line_start, line_end)
            start, end = line_start, line_end
        if not target_text.strip():
            messagebox.showinfo("/make", "Please select text or place the cursor in a non-empty paragraph.")
            return
        prompt = self.get_ollama_prompt(f"{base_prompt}\n{target_text}")
        result = self.call_ollama(prompt)
        if result:
            self.get_active_text().delete(start, end)
            self.get_active_text().insert(start, result.strip())

    def highlight_selection(self, color):
        try:
            self.get_active_text().tag_remove('highlight', tk.SEL_FIRST, tk.SEL_LAST)
        except tk.TclError:
            return
        if color:
            self.get_active_text().tag_add('highlight', tk.SEL_FIRST, tk.SEL_LAST)
            self.get_active_text().tag_config('highlight', background=color)

    def bold_selection(self):
        try:
            self.get_active_text().tag_add('bold', tk.SEL_FIRST, tk.SEL_LAST)
            bold_font = tkfont.Font(self.get_active_text(), self.get_active_text().cget("font"))
            bold_font.configure(weight="bold")
            self.get_active_text().tag_config('bold', font=bold_font)
        except tk.TclError:
            pass

    def underline_selection(self):
        try:
            self.get_active_text().tag_add('underline', tk.SEL_FIRST, tk.SEL_LAST)
            underline_font = tkfont.Font(self.get_active_text(), self.get_active_text().cget("font"))
            underline_font.configure(underline=True)
            self.get_active_text().tag_config('underline', font=underline_font)
        except tk.TclError:
            pass

    def change_font(self):
        # Simple font change dialog (expand as needed)
        font = simpledialog.askstring("Font", "Enter font family (e.g., Arial, Times)")
        if font:
            try:
                self.get_active_text().configure(font=(font, 12))
            except Exception:
                messagebox.showinfo("Font", "Could not set font.")

    def refresh_text(self):
        # Placeholder: Implement actual refresh logic as needed
        self.apply_markdown_highlighting()
        self.apply_chapter_heading_style()
        self.update_word_count()
        # Optionally reload from file or source

    def select_all(self):
        self.get_active_text().tag_add(tk.SEL, "1.0", tk.END)
        self.get_active_text().mark_set(tk.INSERT, "1.0")
        self.get_active_text().see(tk.INSERT)

    def copy(self):
        try:
            self.get_active_text().event_generate('<<Copy>>')
        except Exception:
            pass

    def cut(self):
        try:
            self.get_active_text().event_generate('<<Cut>>')
        except Exception:
            pass

    def paste(self):
        try:
            self.get_active_text().event_generate('<<Paste>>')
        except Exception:
            pass

    def undo(self):
        try:
            self.get_active_text().edit_undo()
        except Exception:
            pass

    def redo(self):
        try:
            self.get_active_text().edit_redo()
        except Exception:
            pass

    def find_text(self):
        # Basic find dialog
        query = simpledialog.askstring("Find", "Enter text to find:")
        if query:
            start = '1.0'
            idx = self.get_active_text().search(query, start, tk.END)
            if idx:
                end = f"{idx}+{len(query)}c"
                self.get_active_text().tag_add('find', idx, end)
                self.get_active_text().tag_config('find', background='yellow')
                self.get_active_text().mark_set(tk.INSERT, idx)
                self.get_active_text().see(idx)
            else:
                messagebox.showinfo("Find", "Text not found.")

    def replace_text(self):
        # Basic replace dialog
        find = simpledialog.askstring("Replace", "Find:")
        replace = simpledialog.askstring("Replace", "Replace with:")
        if find and replace is not None:
            text = self.get_active_text().get('1.0', 'end-1c')
            new_text = text.replace(find, replace)
            self.get_active_text().delete('1.0', tk.END)
            self.get_active_text().insert('1.0', new_text)

    def goto_line(self):
        line = simpledialog.askinteger("Go to Line", "Enter line number:")
        if line:
            idx = f"{line}.0"
            self.get_active_text().mark_set(tk.INSERT, idx)
            self.get_active_text().see(idx)

    # --- Chapter Heading Styling ---
    def apply_chapter_heading_style(self):
        # Apply heading style to lines starting with 'Chapter'
        self.get_active_text().tag_remove('chapter_heading', '1.0', tk.END)
        lines = self.get_active_text().get('1.0', 'end-1c').split('\n')
        for i, line in enumerate(lines):
            if line.strip().lower().startswith('chapter'):
                start = f"{i+1}.0"
                end = f"{i+1}.end"
                self.get_active_text().tag_add('chapter_heading', start, end)
        heading_font = tkfont.Font(self.get_active_text(), self.get_active_text().cget("font"))
        heading_font.configure(size=18, weight="bold")
        self.get_active_text().tag_config('chapter_heading', font=heading_font, foreground="#2a2a6f")

    # Call apply_chapter_heading_style after text changes
    def on_text_change(self, event=None):
        self.apply_chapter_heading_style()
        self.update_word_count()

    def apply_markdown_highlighting(self, event=None):
        # Remove all tags
        for tag in self.get_active_text().tag_names():
            self.get_active_text().tag_remove(tag, "1.0", tk.END)
        text = self.get_active_text().get("1.0", tk.END)
        lines = text.split('\n')
        for i, line in enumerate(lines):
            lineno = f"{i+1}.0"
            # Headings
            if line.startswith("### "):
                self.get_active_text().tag_add("h3", lineno, f"{i+1}.end")
            elif line.startswith("## "):
                self.get_active_text().tag_add("h2", lineno, f"{i+1}.end")
            elif line.startswith("# "):
                self.get_active_text().tag_add("h1", lineno, f"{i+1}.end")
            # Blockquotes
            elif line.strip().startswith(">"):
                self.get_active_text().tag_add("blockquote", lineno, f"{i+1}.end")
            # Lists
            elif line.strip().startswith(('- ', '* ', '+ ')):
                self.get_active_text().tag_add("list", lineno, f"{i+1}.end")
            # Horizontal rule
            elif line.strip() == '---':
                self.get_active_text().tag_add("hr", lineno, f"{i+1}.end")
        # Inline formatting
        import re
        for match in re.finditer(r"\*\*(.+?)\*\*", text):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            self.get_active_text().tag_add("bold", start, end)
        for match in re.finditer(r"\*(.+?)\*", text):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            self.get_active_text().tag_add("italic", start, end)
        for match in re.finditer(r"`([^`]+)`", text):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            self.get_active_text().tag_add("code", start, end)
        for match in re.finditer(r"\[(.+?)\]\((.+?)\)", text):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            self.get_active_text().tag_add("link", start, end)
        # Tag configs
        self.get_active_text().tag_config("h1", font=("Fira Mono", 20, "bold"), foreground="#ff6363", spacing1=10, spacing3=8)
        self.get_active_text().tag_config("h2", font=("Fira Mono", 16, "bold"), foreground="#ffd580", spacing1=8, spacing3=6)
        self.get_active_text().tag_config("h3", font=("Fira Mono", 14, "bold"), foreground="#c792ea", spacing1=6, spacing3=4)
        self.get_active_text().tag_config("bold", font=("Fira Mono", 13, "bold"), foreground="#e7c664")
        self.get_active_text().tag_config("italic", font=("Fira Mono", 13, "italic"), foreground="#7fdbca")
        self.get_active_text().tag_config("code", font=("Fira Mono", 13), background="#232946", foreground="#80cbc4")
        self.get_active_text().tag_config("link", foreground="#80cbc4", underline=True)
        self.get_active_text().tag_config("list", lmargin1=30, foreground="#a6accd")
        self.get_active_text().tag_config("blockquote", lmargin1=20, foreground="#ffd580", background="#232946")
        self.get_active_text().tag_config("hr", font=("Fira Mono", 13), foreground="#ff6363", underline=True)

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
