# Cheesy Mamas

Cheesy Mamas is a local-first, multi-tab code editor built in Python with PyQt6. It’s designed for clean editing, with Git history and version tracking built directly into the interface. And cheesy accents.

There is no telemetry, no sync, no accounts (but there's a little cheese!). Cheesy Mamas is built to live on your machine and yours alone.

---

## Installation

```bash
pip install cheesymamas
cheesymamas
```

---

## Requirements

- Python 3.9+
- Git (installed and available in PATH)
- PyQt6

To install dependencies:

```bash
pip install PyQt6
```

---

## What It Does

- Multi-tab editing with save/save as support and dirty state tracking
- Git integration: each file shows its own commit timeline
- Clicking a commit highlights changed lines from that version
- Right-click any commit to:
  - View the diff
  - Revert the file to that version
  - Copy that version to clipboard
- Inline "Revert Line" buttons for changed lines
- Smart paste (indent-aware, like good mac & cheese)
- Live search with instant visual highlighting and match count
- Syntax highlighting for Python, C, and LaTeX
- Compile support for Python, C (via gcc), and LaTeX (via pdflatex)
- Bash button to run or edit saved terminal commands
- Give me more cheese please UI
- Exit protection: warns if unsaved files are open
- Single-instance file relay (new files open in the same window)
- Installable as a native app with icon and launcher integration
- I really would like more cheese, please send your cheese to Cheesy Mama's House

---

## Why It Exists

Cheesy Mamas was made because most editors either:

1. Assume you'll sync your code to the cloud
2. Don’t show file history visually, where you’re working
3. Require extensions, setup, or background services to track changes

Cheesy Mamas keeps the full Git history visible beside the file, so you always know what changed, when it changed, and why.

---

## Notes

If you see anything pop up in that little box in the bottom right corner, that's a bug! Send it to me!