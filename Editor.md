# Editor: Real-Time Autosave & Live Book Context

## 1. Real-Time Integration

- **Live Write-Through:**  
  - As soon as any part of the app generates content (e.g.,  
    `[CHECKPOINT] Folders created. Starting AI generation...`  
    `Generating chapter 1...`  
    `Wrote content to .../chapter1.md`),  
    the same content is immediately sent to the Editor for display and autosave.
  - This includes:
    - All chapter content as soon as it’s generated
    - All outlines, enhancements, and notes as they are created or updated
    - Any logs or checkpoints if desired

- **Autosave:**  
  - The Editor maintains a live, persistent record of all received/generated content.
  - It autosaves this context (e.g., to a `.editor_context.json` or `.md` file in the project root) so nothing is lost, even if the app is closed or crashes.
  - Each update (new chapter, enhancement, outline, etc.) is appended/merged into the Editor’s context in real time.

---

## 2. Implementation Approach

- **Hook Points:**  
  - Update the main generation logic (e.g., after each `Wrote content to .../chapterX.md`) to call a method like `Editor.update_context(new_content, file_path, event_type)` whenever new content is written.
  - The same hook is used for outline generation, enhancements, and any other mod.

- **Editor Autosave Logic:**  
  - The Editor listens for these updates and:
    - Updates its in-memory context
    - Immediately writes the update to disk (autosave)
    - Refreshes the Editor window UI if it is open (so the user always sees the latest state)

- **UI/UX:**  
  - The Editor window/tab always displays the most up-to-date version of the book, outline, and enhancements.
  - If the Editor is not open, it still autosaves everything in the background.

- **Thread Safety:**  
  - Updates and autosaves are handled in a thread-safe manner to avoid race conditions when multiple mods write at once.

---

## 3. Menu & Access

- **Menu Integration:**  
  - “Editor” remains as a top-level menu row.
  - The Editor window can be opened/closed at any time, always displaying the current, autosaved state.

---

## 4. AI Chat Context

- **When the user “talks to the book”:**  
  - The AI receives the latest, autosaved, unified context (all chapters, outlines, enhancements, etc.) for maximum relevance and up-to-date answers.

---

## 5. Summary Table

| Feature                        | Description                                                        |
|--------------------------------|--------------------------------------------------------------------|
| Real-Time Write-Through        | Yes, every generation event updates the Editor instantly           |
| Autosave                       | Yes, persistent, robust against crashes                            |
| Unified Book Context           | Yes, always current, always available                              |
| Thread Safe                    | Yes, safe for concurrent updates                                   |
| Menu/Window Integration        | Yes, as before                                                     |
| AI Chat                        | Uses latest autosaved context                                      |

---

## Next Steps

1. **Implement hook/callback system** so all generation and enhancement processes notify the Editor on content creation.
2. **Implement Editor autosave logic** (in-memory + file).
3. **Update Editor UI** to always show the latest content.
4. **Test with long-running and concurrent generation/enhancement workflows.**
