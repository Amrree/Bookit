import os
import tkinter as tk
import tkinter.font as tkfont
import threading
import requests
import time

OLLAMA_MODEL = "Ocuteus-v1-mmproj-f16:latest"
OLLAMA_PORT = 11500  # Dedicated port for this mod
OLLAMA_URL = f"http://localhost:{OLLAMA_PORT}/api/generate"

class AITabEditor(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("AI Tab Editor")
        self.geometry("900x700")
        self.tabs = []
        self.tab_frames = []
        self.current_tab = None
        self.suggestions = {}  # {tab_index: {level: suggestion}}
        self._build_ui()
        self.ensure_ollama_running()

    def _build_ui(self):
        self.tab_bar = tk.Frame(self, bg="#232946")
        self.tab_bar.pack(side=tk.TOP, fill=tk.X)
        self.add_tab_button = tk.Button(self.tab_bar, text="+", command=self.new_tab)
        self.add_tab_button.pack(side=tk.LEFT, padx=2)
        self.tab_buttons = []
        self.editor_area = tk.Frame(self, bg="#181c24")
        self.editor_area.pack(fill=tk.BOTH, expand=True)
        self.new_tab()

    def new_tab(self):
        tab_index = len(self.tabs)
        tab_name = f"Untitled-{tab_index+1}"
        btn = tk.Button(self.tab_bar, text=tab_name, command=lambda idx=tab_index: self.switch_tab(idx))
        btn.pack(side=tk.LEFT, padx=2)
        self.tab_buttons.append(btn)
        frame = tk.Frame(self.editor_area, bg="#181c24")
        text = tk.Text(frame, bg="#181c24", fg="#d6deeb", insertbackground="#ffd580", font=("Fira Mono", 13), wrap="word")
        text.pack(fill=tk.BOTH, expand=True)
        text.bind("<KeyRelease>", lambda e, idx=tab_index: self.on_text_change(idx))
        text.bind("<Tab>", lambda e, idx=tab_index: self.accept_suggestion(idx) or "break")
        frame.pack(fill=tk.BOTH, expand=True)
        self.tabs.append(text)
        self.tab_frames.append(frame)
        self.switch_tab(tab_index)

    def switch_tab(self, idx):
        for i, frame in enumerate(self.tab_frames):
            frame.pack_forget()
        self.tab_frames[idx].pack(fill=tk.BOTH, expand=True)
        self.current_tab = idx
        self.update_suggestion_display(idx)

    def on_text_change(self, idx):
        text_widget = self.tabs[idx]
        content = text_widget.get("1.0", tk.END)
        # Debounce: Start a new thread for suggestions
        threading.Thread(target=self.fetch_suggestions, args=(idx, content), daemon=True).start()

    def fetch_suggestions(self, idx, content):
        # Call Ollama for all 5 suggestion levels
        prompt = (
            "You are an expert writing assistant. Given the following text, provide suggestions for the next word, next line, next sentence, next paragraph, "
            "and correct any spelling or grammar mistakes.\n"
            "Text:\n" + content.strip() +
            "\nFormat your response as JSON with keys: word, line, sentence, paragraph, spelling."
        )
        try:
            response = requests.post(OLLAMA_URL, json={"model": OLLAMA_MODEL, "prompt": prompt}, timeout=30)
            response.raise_for_status()
            result = response.json()
            # Expected: result = {"word": ..., "line": ..., "sentence": ..., "paragraph": ..., "spelling": ...}
            self.suggestions[idx] = result
        except Exception as e:
            self.suggestions[idx] = {"error": str(e)}
        self.update_suggestion_display(idx)

    def update_suggestion_display(self, idx):
        text_widget = self.tabs[idx]
        text_widget.tag_remove('suggestion', "1.0", tk.END)
        suggestion = self.suggestions.get(idx, {})
        if suggestion.get("error"):
            # Optionally show error in status bar
            return
        # Show ghost text for the most relevant suggestion (e.g., word, line, etc.)
        # For demo, show word-level suggestion inline
        word = suggestion.get("word")
        if word:
            end = text_widget.index(tk.INSERT)
            text_widget.insert(end, word, 'suggestion')
            text_widget.tag_config('suggestion', foreground="#4e5579")
            text_widget.mark_set(tk.INSERT, end)

    def accept_suggestion(self, idx):
        suggestion = self.suggestions.get(idx, {})
        text_widget = self.tabs[idx]
        if suggestion.get("word"):
            text_widget.insert(tk.INSERT, suggestion["word"])
        elif suggestion.get("line"):
            text_widget.insert(tk.INSERT, suggestion["line"])
        elif suggestion.get("sentence"):
            text_widget.insert(tk.INSERT, suggestion["sentence"])
        elif suggestion.get("paragraph"):
            text_widget.insert(tk.INSERT, suggestion["paragraph"])
        elif suggestion.get("spelling"):
            # Replace misspelled word at cursor
            pass
        # After accepting, clear suggestion
        self.suggestions[idx] = {}
        self.update_suggestion_display(idx)

    def ensure_ollama_running(self):
        import socket, subprocess
        try:
            sock = socket.create_connection(("localhost", OLLAMA_PORT), timeout=2)
            sock.close()
        except Exception:
            env = os.environ.copy()
            env["OLLAMA_PORT"] = str(OLLAMA_PORT)
            subprocess.Popen(["ollama", "serve"], env=env)
            time.sleep(2)
            # Pull the model if needed
            subprocess.run(["ollama", "pull", OLLAMA_MODEL], check=False)

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    app = AITabEditor()
    app.mainloop()
