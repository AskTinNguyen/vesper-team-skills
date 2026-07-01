---
name: apple-notes
description: Manage Apple Notes and Apple Reminders via the `memo` CLI on macOS (create, view, edit, delete, search, move, export notes, and complete reminders). Use when a user asks OpenClaw to add a note, list notes, search notes, manage note folders, or work with reminders.
homepage: https://github.com/antoniorodr/memo
metadata:
  {
    "openclaw":
      {
        "emoji": "📝",
        "os": ["darwin"],
        "requires": { "bins": ["memo"] },
        "install":
          [
            {
              "id": "brew",
              "kind": "brew",
              "formula": "antoniorodr/memo/memo",
              "bins": ["memo"],
              "label": "Install memo via Homebrew",
            },
          ],
      },
  }
---

# Apple Notes CLI

Use `memo notes` to manage Apple Notes directly from the terminal and `memo rem` to manage Apple Reminders. Create, view, edit, delete, search, move notes between folders, export to HTML/Markdown, and complete reminders.

Setup

- Install (Homebrew): `brew tap antoniorodr/memo && brew install antoniorodr/memo/memo`
- Manual (pip): `git clone https://github.com/antoniorodr/memo && cd memo && pip install .`
- uv: `uv tool install git+https://github.com/antoniorodr/memo`
- Manual and `uv` installs require Python 3.13 or newer.
- Set `$EDITOR` before adding or editing notes, for example `export EDITOR="vim"`.
- macOS-only; if prompted, grant Automation access to Notes.app and Reminders.app.

View Notes

- List all notes: `memo notes`
- Filter by folder: `memo notes -f "Folder Name"`
- Search notes (fuzzy): `memo notes -s "query"`

Create Notes

- Add a new note: `memo notes -a`
  - Opens an interactive editor to compose the note.
- Quick add with title: `memo notes -a "Note Title"`

Edit Notes

- Edit existing note: `memo notes -e`
  - Interactive selection of note to edit.

Delete Notes

- Delete a note: `memo notes -d`
  - Interactive selection of note to delete.

Move Notes

- Move note to folder: `memo notes -m`
  - Interactive selection of note and destination folder.

Export Notes

- Export to HTML/Markdown: `memo notes -ex`
  - Exports selected note; uses Mistune for markdown processing.

Reminders

- Inspect reminder commands: `memo rem --help`
- Use `memo rem` when the user asks to list or complete Apple Reminders.

Limitations

- Notes containing images can be edited, but Memo represents images with `[MEMO_IMG_N]` placeholders in the editor.
- Preserve a placeholder to keep the corresponding image; remove it to delete that image.
- Because of AppleScript limitations, preserved images are appended to the end of the note after editing even if placeholders appear elsewhere.
- Interactive prompts may require terminal access.

Notes

- macOS-only.
- Requires Apple Notes.app and Apple Reminders.app to be accessible for the relevant commands.
- For automation, grant permissions in System Settings > Privacy & Security > Automation.
