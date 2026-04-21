#!/usr/bin/env python3
"""
Rename an OpenCode session programmatically.

This script updates the title field in the SQLite database directly,
bypassing the interactive /rename command.

Usage:
    # Command-line arguments (preferred)
    ./rename_session.py <session_id> <new_title>
    
    # Environment variables
    SESSION_ID="ses_..." NEW_TITLE="My New Title" ./rename_session.py
    
    # Python module
    python3 rename_session.py ses_abc123 "New Session Name"

Examples:
    ./rename_session.py ses_25dd535caffemzyEEcQaZZFdqZ "Index page redesign"
    SESSION_ID=ses_xyz NEW_TITLE="Bugfix PR" ./rename_session.py
"""

import os
import sqlite3
import sys
from pathlib import Path


def get_db_path() -> Path:
    """Return the path to the OpenCode SQLite database."""
    return Path.home() / ".local" / "share" / "opencode" / "opencode.db"


def rename_session(session_id: str, new_title: str) -> bool:
    """
    Rename a session in the OpenCode database.
    
    Args:
        session_id: The UUID of the session to rename
        new_title: The new title for the session
        
    Returns:
        True if successful, False otherwise
    """
    db_path = get_db_path()
    
    if not db_path.exists():
        print(f"Error: Database not found at {db_path}")
        print("Have you run opencode at least once?")
        return False
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Check current title
        cursor.execute("SELECT id, title FROM session WHERE id=?", (session_id,))
        result = cursor.fetchone()
        
        if not result:
            print(f"Error: Session '{session_id}' not found")
            conn.close()
            return False
        
        old_title = result[1]
        
        # Update title
        cursor.execute("UPDATE session SET title=? WHERE id=?", (new_title, session_id))
        conn.commit()
        
        print(f"Renamed session '{session_id}':")
        print(f"  From: {old_title}")
        print(f"  To:   {new_title}")
        
        conn.close()
        return True
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False


def main() -> int:
    """Main entry point."""
    # Get parameters from command-line args or environment variables
    if len(sys.argv) >= 3:
        session_id = sys.argv[1]
        new_title = sys.argv[2]
    else:
        session_id = os.environ.get("SESSION_ID", "")
        new_title = os.environ.get("NEW_TITLE", "")
    
    if not session_id or not new_title:
        print(__doc__)
        print("Error: Both session ID and new title are required.")
        print("")
        print("Usage: ./rename_session.py <session_id> <new_title>")
        print("       SESSION_ID=\"...\" NEW_TITLE=\"...\" ./rename_session.py")
        return 1
    
    success = rename_session(session_id, new_title)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
