import sqlite3
import os

DB_PATH = "db/members.db"

def init_db(db_path=None):
    """Initialize the database. Uses DB_PATH by default, or a custom path if provided."""
    path = db_path if db_path is not None else DB_PATH
    
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)  # ensure parent folder exists
        conn = sqlite3.connect(path)
        cur = conn.cursor()
        cur.execute("""
        CREATE TABLE members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            gender TEXT NOT NULL,
            student_id TEXT NOT NULL UNIQUE,
            society_name TEXT NOT NULL,
            date_joined TEXT NOT NULL,
            position TEXT NOT NULL
        )
        """)
        conn.commit()
        conn.close()

def set_db_path(new_path):
    """Allow changing the database path (useful for testing)"""
    global DB_PATH
    DB_PATH = new_path
