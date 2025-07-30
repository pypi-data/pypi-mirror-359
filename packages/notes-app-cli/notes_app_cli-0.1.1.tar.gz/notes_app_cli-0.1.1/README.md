# NOTES CLI App

A CLI tool to add, review, and manage notes and todos.

## Semantic Search & Vector Database

This uses a vector database (ChromaDB) and a machine learning model (MiniLM) to enable semantic search:

- When you add a note, its meaning is converted into a vector (embedding) and stored in ChromaDB.
- When you use semantic search, your query is also converted to a vector, and the app finds notes with similar meaning (not just exact words).
- If no semantic match is found, the app automatically falls back to a keyword search for robust results.
- The vector database is stored locally in the `.chroma_db` directory (auto-created).
- Find notes by meaning, not just keywords (e.g., searching "remind mom" can find "call mom").

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repo name>
   cd review_and_append
   ```
2. **Create and activate a virtual environment (recommended):**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. **Install dependencies and the CLI tool:**
   ```bash
   pip install -e .
   ```

## Usage

### Command Line

Add a note:
```bash
notes "Remember to call mom"
```

Add a todo:
```bash
notes "Buy groceries" --tag todo
```

View today's notes:
```bash
notes today
```

View all todos:
```bash
notes todo
```

View notes for a period:
```bash
notes "this week"
notes "15 days"
notes "a month"
notes all
```

### Interactive Menu
Just run:
```bash
notes
```
And use the arrow keys to select actions:
- **Add TODO**: Add a new todo
- **Add Note**: Add a regular note
- **View Notes**: See all notes (except todos) in a beautiful table
- **View TODOs**: See all todos in a beautiful table
- **Semantic Search**: Find notes by meaning, with keyword fallback if no semantic match
- **Delete All TODOs**: Delete all todos (with confirmation)
- **Delete All Notes**: Delete all notes (with confirmation)
- **Other**: Run a custom SQL query on your notes database
- **Exit**: Quit the app

## Data Storage
- Notes are stored in a local SQLite database file: `notes.db`

## Uninstall
```bash
pip uninstall notes-app
```
