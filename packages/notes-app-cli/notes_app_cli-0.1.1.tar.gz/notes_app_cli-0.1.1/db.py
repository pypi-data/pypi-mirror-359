import sqlite3
import os
from datetime import datetime, timedelta

# Database file path
DB_FILE = "notes.db"

def init_db():
    """Initialize the database and create tables if they don't exist."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Create notes table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            tag TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

def add_note(text, tag=None):
    """Add a new note to the database."""
    init_db()
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute(
        "INSERT INTO notes (text, tag) VALUES (?, ?)",
        (text, tag)
    )
    
    conn.commit()
    conn.close()

def get_notes_by_period(period):
    """Get notes from a specific time period."""
    init_db()
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    if period == "all":
        cursor.execute("SELECT id, text, timestamp, tag FROM notes ORDER BY timestamp DESC")
    else:
        cursor.execute(
            "SELECT id, text, timestamp, tag FROM notes WHERE timestamp >= ? ORDER BY timestamp DESC",
            (period,)
        )
    
    notes = cursor.fetchall()
    conn.close()
    return notes

def get_notes_by_tag(tag):
    """Get all notes with a specific tag."""
    init_db()
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT id, text, timestamp, tag FROM notes WHERE tag = ? ORDER BY timestamp DESC",
        (tag,)
    )
    
    notes = cursor.fetchall()
    conn.close()
    return notes 