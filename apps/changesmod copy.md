# WP Mod Change Log & Feature Outline

## Overview
This document provides a detailed outline of all major changes, enhancements, and architectural decisions made in the development of the WordPro Feed (WP) mod. The focus is on QOL improvements, AI integration, UI/UX modernization, and extensibility for future features.

---

## 1. Tab System Integration
- **Multi-Tab Editor:**
  - Added a tab bar at the top of the editor window.
  - Each tab is an independent text editor instance (Markdown/text).
  - Tabs can be added with a "+" button; each new tab is "Untitled-N".
  - Switching tabs updates the main editor area to the selected document.
  - All editor actions (AI, formatting, save, etc.) operate on the active tab.

- **Underlying Model:**
  - All logic previously using a single text widget now operates on `self.tabs[self.current_tab]`.
  - Context menu, markdown highlighting, chapter heading styling, and all features are per-tab.

---

## 2. Markdown & Visual Improvements
- **VSCode-like Dark Theme:**
  - Modern dark background, light foreground, high contrast.
  - Fira Mono font for code/text.
- **Live Markdown Highlighting:**
  - Headings (H1/H2/H3): Large, bold, colored.
  - Bold, italic, inline code, links: styled inline.
  - Lists, blockquotes, horizontal rules: visually distinct.
  - Styles update live as you type or load text.
- **Chapter Headings:**
  - Lines starting with "Chapter" are auto-styled as headings.

---

## 3. Context Menu & Quick Actions
- **Right-Click Context Menu:**
  - Accessible via right-click (`<Button-3>`).
  - Includes copy, cut, paste, select all, save as, open in editor, clear, look up, spelling/grammar, and all AI actions.
  - All transformation and AI features are accessible from this menu (not bottom bar).
- **Bottom Bar:**
  - Quick action buttons for bold, underline, font, and a dedicated Refresh button.
  - Live word count display.

---

## 4. AI & Ollama Integration
- **Ollama API:**
  - All AI features use Ollama backend (default: `llamacorn-1.1b-chat.Q8_0:latest`).
  - Prompts and completions are context-aware and operate on the selected tab.
- **AI Actions:**
  - /make submenu: Make Much Longer, More Detailed, Into a Short Story, Book Premise, Chapter Outline.
  - Explain, Continue Writing, Rewrite, Summarize, Extend, Fix Grammar, Transform, etc.
  - Feature toggles for AI prompt enrichment (profanity, spoilers, humor, literary style, etc.).

---

## 5. Keybindings & QOL Features
- **Standard Keybindings:**
  - Copy, Cut, Paste, Undo, Redo, Bold, Underline, Select All, Save, Find, Replace, Go to Line.
- **Highlighting:**
  - Multi-color text highlighting via context menu.
- **Spellcheck/Grammar:**
  - Spelling and grammar corrections available via context menu.

---

## 6. Refactor & Architecture
- **All editor logic refactored** to use per-tab context (`get_active_text`).
- **Functions modularized** for easier future extension (AI suggestion engine, MPC/Git integration, etc.).
- **Refresh button restored** to bottom bar for manual update of highlights and word count.

---

## 7. Planned/Future Features
- **Advanced Tab Features:** Tab closing, renaming, drag-to-reorder, session persistence.
- **AI Suggestion Engine:** On-the-fly word/line/sentence/paragraph suggestions (planned for dedicated LLM backend).
- **Distributed/Collaborative Editing:** MPC server/Git integration hooks.

---

## Summary
The WP mod is now a robust, modern, AI-powered multi-tab text editor with a focus on usability, extensibility, and a beautiful writing experience. All major QOL and AI features are accessible per tab, with a future-proof architecture for further enhancements.
