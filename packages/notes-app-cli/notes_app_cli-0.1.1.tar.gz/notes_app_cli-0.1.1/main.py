#!/usr/bin/env python3
import os
import sys
import contextlib
import datetime

os.environ["CHROMA_TELEMETRY_ENABLED"] = "FALSE"

@contextlib.contextmanager
def suppress_stderr():
    with open(os.devnull, "w") as devnull:
        old_stderr = sys.stderr
        sys.stderr = devnull
        try:
            yield
        finally:
            sys.stderr = old_stderr

with suppress_stderr():
    # All imports and code run with stderr suppressed
    import argparse
    import questionary
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text
    from db import add_note, get_notes_by_period, get_notes_by_tag
    from utils import parse_period
    from notes_semantic_db import add_note_to_vector_db, semantic_search
    import sqlite3

console = Console()

def show_banner():
    """Display a nice banner when the app starts."""
    ascii_banner = '''
 _   _       _            
| \ | |     | |           
|  \| | ___ | |_ ___  ___ 
| . ` |/ _ \| __/ _ \/ __|
| |\  | (_) | ||  __/\__ \\
\_| \_/\___/ \__\___||___/
                          
                          
'''
    console.print(f"[bold blue]{ascii_banner}[/bold blue]")
    subtitle = Text("review and append notes/todos")
    panel = Panel(
        subtitle,
        border_style="blue",
        padding=(1, 2)
    )
    console.print(panel)

def interactive_menu():
    while True:
        choice = questionary.select(
            "What do you want to do?",
            choices=[
                "Add TODO",
                "Add Note",
                "View Notes",
                "View TODOs",
                "Semantic Search",
                "Delete All TODOs",
                "Delete All Notes",
                "Other",
                "Exit"
            ]
        ).ask()

        if choice == "Add TODO":
            note = questionary.text("Enter your TODO:").ask()
            note_id = add_note(note, "todo")
            add_note_to_vector_db(note_id, note, {"tag": "todo"})
            console.print("[bold green]TODO added![/bold green]")
        elif choice == "Add Note":
            note = questionary.text("Enter your note:").ask()
            note_id = add_note(note)
            add_note_to_vector_db(note_id, note)
            console.print("[bold green]Note added![/bold green]")
        elif choice == "View Notes":
            notes = get_notes_by_period("all")
            notes = [n for n in notes if not (n[3] and n[3].lower() == "todo")]
            if notes:
                table = Table(
                    title=f"All Notes ({len(notes)})",
                    show_header=True,
                    header_style="bold magenta",
                    box=None,
                    show_lines=True
                )
                table.add_column("ID", style="cyan", no_wrap=True)
                table.add_column("Text", style="white")
                table.add_column("Timestamp", style="green")
                table.add_column("Tag", style="bold yellow")

                tag_emoji = {
                    "todo": "📝",
                    "work": "💼",
                    "learning": "📚",
                    "health": "💪",
                    "travel": "✈️",
                    "home": "🏠",
                    "finance": "💰",
                    "writing": "✍️",
                    "food": "🍕",
                    "tech": "💻",
                    "career": "🚀",
                }

                def format_timestamp(ts):
                    try:
                        dt = datetime.datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
                        day = dt.day
                        suffix = 'th' if 11 <= day <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')
                        formatted = dt.strftime(f"%d{suffix} %B %Y")
                        formatted = formatted.lstrip('0')
                        return formatted
                    except Exception:
                        return ts

                for note in notes:
                    tag = note[3] if len(note) > 3 and note[3] else ""
                    emoji = tag_emoji.get(tag, "")
                    tag_display = f"{emoji} {tag}" if tag else ""
                    timestamp_display = format_timestamp(note[2])
                    table.add_row(str(note[0]), note[1], timestamp_display, tag_display)
                console.print(table)
                console.print(f"[bold green]Total notes: {len(notes)}[/bold green]")
            else:
                console.print("[bold red] No notes found.[/bold red]")
        elif choice == "View TODOs":
            notes = get_notes_by_tag("todo")
            if notes:
                table = Table(
                    title=f"TODOs ({len(notes)})",
                    show_header=True,
                    header_style="bold magenta",
                    box=None,
                    show_lines=True
                )
                table.add_column("ID", style="cyan", no_wrap=True)
                table.add_column("Text", style="white")
                table.add_column("Timestamp", style="green")
                table.add_column("Tag", style="bold yellow")

                tag_emoji = {
                    "todo": "📝",
                    "work": "💼",
                    "learning": "📚",
                    "health": "💪",
                    "travel": "✈️",
                    "home": "🏠",
                    "finance": "💰",
                    "writing": "✍️",
                    "food": "🍕",
                    "tech": "💻",
                    "career": "🚀",
                }

                def format_timestamp(ts):
                    try:
                        dt = datetime.datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
                        day = dt.day
                        suffix = 'th' if 11 <= day <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')
                        formatted = dt.strftime(f"%d{suffix} %B %Y")
                        formatted = formatted.lstrip('0')
                        return formatted
                    except Exception:
                        return ts

                for note in notes:
                    tag = note[3] if len(note) > 3 and note[3] else ""
                    emoji = tag_emoji.get(tag, "")
                    tag_display = f"{emoji} {tag}" if tag else ""
                    timestamp_display = format_timestamp(note[2])
                    table.add_row(str(note[0]), note[1], timestamp_display, tag_display)
                console.print(table)
                console.print(f"[bold green]Total TODOs: {len(notes)}[/bold green]")
            else:
                console.print("[bold red] No TODOs found.[/bold red]")
        elif choice == "Semantic Search":
            query = questionary.text("Enter your search query:").ask()
            results = semantic_search(query, top_k=5)
            if results:
                table = Table(title=f"Semantic Search Results for: {query}", show_header=True, header_style="bold magenta")
                table.add_column("ID", style="cyan", no_wrap=True)
                table.add_column("Text", style="white")
                table.add_column("Tag", style="yellow")
                table.add_column("Score", style="green")
                for hit in results:
                    tag = hit["metadata"].get("tag", "") if hit["metadata"] else ""
                    score = f"{hit['distance']:.3f}" if hit["distance"] is not None else ""
                    table.add_row(str(hit["id"]), hit["text"], tag, score)
                console.print(table)
            else:
                # Fallback to keyword search
                notes = get_notes_by_period("all")
                keyword_matches = []
                for note in notes:
                    note_id, text, timestamp, tag = note
                    if query.lower() in text.lower():
                        keyword_matches.append(note)
                if keyword_matches:
                    table = Table(title=f"Keyword Search Results for: {query}", show_header=True, header_style="bold yellow")
                    table.add_column("ID", style="cyan", no_wrap=True)
                    table.add_column("Text", style="white")
                    table.add_column("Timestamp", style="green")
                    table.add_column("Tag", style="yellow")
                    for note in keyword_matches:
                        tag = note[3] if len(note) > 3 and note[3] else ""
                        table.add_row(str(note[0]), note[1], note[2], tag)
                    console.print(table)
                else:
                    console.print("[bold red] No similar notes found (semantic or keyword).[/bold red]")
        elif choice == "Delete All TODOs":
            confirm = questionary.confirm("Are you sure you want to delete all TODOs? This cannot be undone.").ask()
            if confirm:
                conn = sqlite3.connect("notes.db")
                cursor = conn.cursor()
                cursor.execute("DELETE FROM notes WHERE tag = ?", ("todo",))
                conn.commit()
                conn.close()
                console.print("[bold red]All TODOs deleted![/bold red]")
            else:
                console.print("[yellow]Operation cancelled.[/yellow]")
        elif choice == "Delete All Notes":
            confirm = questionary.confirm("Are you sure you want to delete ALL notes? This cannot be undone.").ask()
            if confirm:
                conn = sqlite3.connect("notes.db")
                cursor = conn.cursor()
                cursor.execute("DELETE FROM notes")
                conn.commit()
                conn.close()
                console.print("[bold red]All notes deleted![/bold red]")
            else:
                console.print("[yellow]Operation cancelled.[/yellow]")
        elif choice == "Other":
            db_file = "notes.db"
            query = questionary.text("Enter a custom SQL query for the notes database:").ask()
            try:
                conn = sqlite3.connect(db_file)
                cursor = conn.cursor()
                cursor.execute(query)
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description] if cursor.description else []
                conn.close()
                if rows and columns:
                    table = Table(title="Custom Query Results", show_header=True, header_style="bold blue")
                    for col in columns:
                        table.add_column(col, style="white")
                    for row in rows:
                        table.add_row(*[str(cell) for cell in row])
                    console.print(table)
                elif rows:
                    console.print(str(rows))
                else:
                    console.print("[bold yellow]Query executed. No results to display.[/bold yellow]")
            except Exception as e:
                console.print(f"[bold red]Error executing query: {e}[/bold red]")
        elif choice == "Exit":
            sys.exit(0)

def main():
    show_banner()

    parser = argparse.ArgumentParser(
        description="A CLI tool for adding and reviewing notes",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  notes "Buy groceries" --tag todo
  notes "Remember to call mom"
  notes today
  notes todo
  notes "this week"
  notes "all"
        """
    )
    parser.add_argument("input", nargs="*", help="Note text or command")
    parser.add_argument("--tag", help="Tag to attach to the note")
    
    args = parser.parse_args()

    if not args.input:
        interactive_menu()
        return

    command = " ".join(args.input).strip().lower()

    if command in ["today", "yesterday", "this week", "15 days", "a month", "all"]:
        notes = get_notes_by_period(parse_period(command))
        if notes:
            table = Table(title=f"Notes: {command.title()}", show_header=True, header_style="bold magenta")
            table.add_column("ID", style="cyan", no_wrap=True)
            table.add_column("Text", style="white")
            table.add_column("Timestamp", style="green")
            table.add_column("Tag", style="yellow")
            for note in notes:
                tag = note[3] if len(note) > 3 and note[3] else ""
                table.add_row(str(note[0]), note[1], note[2], tag)
            console.print(table)
        else:
            console.print("[bold red] No notes found.[/bold red]")
    elif command == "todo":
        notes = get_notes_by_tag("todo")
        if notes:
            table = Table(title="TODO Notes", show_header=True, header_style="bold magenta")
            table.add_column("ID", style="cyan", no_wrap=True)
            table.add_column("Text", style="white")
            table.add_column("Timestamp", style="green")
            table.add_column("Tag", style="yellow")
            for note in notes:
                tag = note[3] if len(note) > 3 and note[3] else ""
                table.add_row(str(note[0]), note[1], note[2], tag)
            console.print(table)
        else:
            console.print("[bold red] No TODO notes found.[/bold red]")
    else:
        note_id = add_note(" ".join(args.input), args.tag)
        add_note_to_vector_db(note_id, " ".join(args.input), {"tag": args.tag} if args.tag else None)
        if args.tag and args.tag.lower() == "todo":
            console.print("[bold green] TODO added![/bold green]")
        else:
            console.print("[bold green] Note added![/bold green]")

if __name__ == "__main__":
    main()
