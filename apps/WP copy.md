# Word Processor (WP) – Ollama Integration & Feature Roadmap

This document outlines all possible and planned changes to the Word Processor (WP) app, focusing on integration with Ollama and related enhancements.

---

## 1. **Ollama Integration**
- **Model:** Use `llamacorn-1.1b-chat.Q8_0:latest` for all AI interactions in WP.
- **API:** Communicate with Ollama via HTTP API using `requests`.
- **Error Handling:** Show errors in a messagebox or inline feedback.

## 2. **Right-Click Context Menu (AI Controls)**
- **AI Actions:**
  - "Explain This" (send selected text to Ollama for explanation)
  - "Continue Writing" (send current context to Ollama to continue)
  - (Optional) "Rewrite as...", "Summarize", "Fix Grammar", "Ask a Question", etc.
- **Ollama Feature Toggles:**
  - All feature toggles (e.g., Add Profanity, Add Spoilers, Add Humor, Add Literary Style, Add Dialogue, Add Metaphors, Add Citations, Add Descriptions, Add Suspense, Add Foreshadowing) are implemented as checkable items in the right-click menu.
  - These toggles modify the prompt sent to Ollama.
- **No on-screen sidebar** for Ollama controls (all toggles are in the context menu).
- **Keyboard Shortcuts:**
  - Ctrl+Return (Cmd+Return on Mac): Triggers "Continue Writing" via Ollama.

## 3. **General WP Features**
- **Editing:** Cut, Copy, Paste, Undo, Redo, Select All, Delete, etc.
- **Apple-native integration:** Spellcheck, "Look Up", Dictation (macOS only).
- **Typewriter Mode, Immersive Mode, Word Count.**
- **Export/Save/Open in External Editor.**
- **Resizable, Dark Mode, Retina support.**

## 4. **Possible Future Enhancements**
- **Additional AI Actions:**
  - "Rewrite as..." (choose tone or style)
  - "Summarize Selection"
  - "Ask a Question" dialog
  - "Fix Grammar/Spelling" via Ollama
  - "Insert AI Suggestion" at cursor
- **Prompt Templates:**
  - Allow users to create and save custom prompt templates for Ollama.
- **Conversation/Chat Panel:**
  - Optional collapsible chat panel to show AI history (not always inline).
- **Session Memory:**
  - Remember last used toggles and AI settings per session.
- **Multi-language Support:**
  - Option to set language or dialect for Ollama responses.
- **Image Insertion:**
  - Insert image/file support in the editor and via AI prompt.
- **Find/Replace, Search AI Help.**
- **Plugin System:**
  - Allow users to add custom AI actions/plugins.

---

## 5. **Design Principles**
- All AI controls should be easily accessible but not clutter the UI.
- Context menu is the main place for Ollama controls and toggles.
- All features degrade gracefully on non-macOS systems.
- Privacy: No data is sent externally except to local Ollama instance.

---

## 6. **Implementation Notes**
- All prompts are dynamically composed based on enabled toggles.
- AI responses are inserted inline at the cursor unless otherwise specified.
- Clear error messages for API or network failures.

---

*This document should be updated as new features are added or requirements change.*
