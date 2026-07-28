import sqlite3
import os
from pathlib import Path

HOME = str(Path.home())
# Dynamic path for persistent database storage using Oppy namespace
DB_PATH = os.environ.get("OPPY_DB_PATH", os.path.join(HOME, ".config", "oppy", "opportunities.db"))

def get_connection():
    # Ensure database directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH, timeout=5.0)
    # Enable WAL mode for concurrency and set busy timeout
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA busy_timeout = 5000;")
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS opportunities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            company TEXT NOT NULL,
            platform TEXT NOT NULL,
            opportunity_type TEXT NOT NULL,  -- 'internship', 'hackathon'
            opportunity_url TEXT UNIQUE NOT NULL,
            stipend_or_prize TEXT,
            deadline TEXT,
            is_remote INTEGER DEFAULT 1,
            is_paid INTEGER DEFAULT 1,
            discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    cursor.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS idx_opp_url ON opportunities (opportunity_url);
    """)
    conn.commit()
    conn.close()
    print(f"Database initialized at {DB_PATH} in WAL mode.")

if __name__ == "__main__":
    init_db()
