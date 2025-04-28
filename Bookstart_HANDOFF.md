# BookStart Save/Load System — Handoff Documentation

## Overview
This document summarizes the design, implementation, and usage of the new **full-project save/load system** for the BookStart application. The system is designed for robustness, cross-platform compatibility (including macOS), and seamless user experience.

---

## Features Implemented

### 1. **Dedicated Save/Load Menu**
- A new top-level menu labeled **Save** is always present alongside existing menus (File, Edit, Window, Help).
- `/Save` menu options:
  - **New Project**: Create a new project/session.
  - **Save Project**: Save all current state to disk.
  - **Save Project As...**: Save state to a new location.
  - **Load Project...**: Load a previously saved session.
  - **Recent Projects**: Submenu for quickly reopening recent projects.

### 2. **Full Project State Preservation**
- All user input (idea, prompts, etc.), generated data (outline, summaries), logs, terminal history, and UI state are saved.
- State is serialized into a manifest file: `bookstart_project.json` in the project folder.
- Markdown and text files for chapters, notes, etc., remain in their respective directories.
- UI state (mode, sidebar, etc.) and logs are saved/restored.

### 3. **Cross-Platform Menu Bar Robustness**
- If no menubar exists (common on macOS), the app creates one and adds standard File, Edit, Window, and Help menus for compatibility.
- The `/Save` menu is always appended, never replaces or removes any original menus.

### 4. **No Overwrite of Existing Functionality**
- All original menus and their logic are preserved.
- The new system only adds functionality; it does not remove or interfere with existing menu options.

### 5. **Recent Projects Management**
- Recent project folders are tracked in `~/.bookstart_recent.json` for quick access.

---

## Key Methods and Integration Points

- `add_save_menu(self)`: Ensures the `/Save` menu is present, creates standard menus if needed.
- `save_project(self)`, `save_project_as(self)`, `load_project(self, path=None)`, `new_project(self)`: Main entry points for project management.
- `collect_project_state(self)`, `restore_project_state(self, manifest)`: Serialize/deserialize all relevant app state.
- **Menu bar is set up in `BookstartApp.__init__`** — `/Save` menu is always appended after all others.

---

## Usage Notes
- On launch, the menu bar will always include: File, Edit, Window, Help, and Save.
- Use the `/Save` menu for all project/session management.
- All project state is saved and restored, including UI and logs.
- Recent projects are managed automatically.

---

## April 2025: Standalone Word Processor Mode Handover

### Overview
- A new standalone Word Processor (WP) app has been integrated into the BookStart project. This app is designed for immersive, distraction-free editing and aggregation of all project-generated content (manifesto, chapters, terminal logs, etc.).

### Features
- **Standalone Launch:** The WP is a separate script: `apps/full_wordpro_feed.py`.
- **Aggregates Content:** On launch and refresh, it gathers all `.md` files (from drafts, outliner, enhancer), the manifesto, and terminal logs from the selected project folder.
- **Immersive Editing:** Rich text editing, full right-click/context menu, word count, typewriter mode, and Apple intelligence integration.
- **Multiple Launch Methods:**
  - From the main app's File menu ("Word Processor Mode")
  - Via Ctrl+W
  - (Optional) Extender panel button
  - Or directly from the terminal
- **Robust Error Handling:** Any startup errors are shown in a messagebox and printed to the terminal for diagnostics.

### How to Use
- **From Terminal:**
  ```sh
  python3 apps/full_wordpro_feed.py /path/to/your/project
  ```
- **From Main App:**
  - File menu → "Word Processor Mode"
  - Ctrl+W
  - (Optional) Extender panel button
- **On Launch:**
  - If no folder is provided, the WP prompts the user to select one.
  - If an error occurs, a dialog and terminal output will explain the issue.

### Troubleshooting
- If the WP window does not appear, check for error dialogs or terminal output.
- The WP script is fully decoupled from the main app and can be run independently.
- Ensure the project folder exists and is accessible.

### Next Steps
- You can further customize or extend the WP as needed; it is modular and standalone.
- For further integration or automation, update the main app or WP script as required.

---

## Known Issues & Next Steps
- If running in a non-standard environment or virtual display, further tweaks may be needed for menu visibility.
- For additional robustness, consider auto-saving or exporting/importing projects as ZIP files in the future.

---

## Contact/Support
For further development or troubleshooting, please refer to this handoff or contact the original developer.

---

**This document reflects the state of the BookStart save/load system as of 2025-04-26.**
