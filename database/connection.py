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
    
    try:
        prune_expired_opportunities()
    except Exception as e:
        print(f"Warning: Failed to prune expired opportunities: {e}")

def prune_expired_opportunities():
    from datetime import datetime, timedelta
    
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, title, deadline, discovered_at FROM opportunities")
    rows = cursor.fetchall()
    
    ids_to_delete = []
    now = datetime.now()
    today = now.date()
    
    for row in rows:
        opp_id, title, deadline, discovered_at_str = row
        if not deadline:
            continue
            
        deadline_lower = deadline.lower().strip()
        
        # Check explicit expired keywords
        if any(w in deadline_lower for w in ["ended", "closed", "expired"]):
            ids_to_delete.append(opp_id)
            continue
            
        # Parse discovered_at datetime
        try:
            disc_dt = datetime.strptime(discovered_at_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            try:
                disc_dt = datetime.fromisoformat(discovered_at_str.replace("Z", "+00:00")).replace(tzinfo=None)
            except Exception:
                disc_dt = now
                
        # Case A: Parse absolute date 'DD MMM YYYY' (e.g., '13 Aug 2026')
        is_absolute = False
        try:
            dt = datetime.strptime(deadline_lower, "%d %b %Y")
            is_absolute = True
            if dt.date() < today:
                ids_to_delete.append(opp_id)
                continue
        except ValueError:
            pass
            
        # Case B: Parse absolute date 'YYYY-MM-DD'
        if not is_absolute:
            try:
                date_part = deadline_lower.split("t")[0].strip()
                dt = datetime.strptime(date_part, "%Y-%m-%d")
                is_absolute = True
                if dt.date() < today:
                    ids_to_delete.append(opp_id)
                    continue
            except ValueError:
                pass
                
        # Case C: Parse relative deadline like "11 days left", "4 days left"
        if not is_absolute:
            import re
            match = re.search(r"(\d+)\s+day", deadline_lower)
            if match:
                days_val = int(match.group(1))
                expire_dt = disc_dt + timedelta(days=days_val)
                if expire_dt < now:
                    ids_to_delete.append(opp_id)
                    continue
                    
            match_hour = re.search(r"(\d+)\s+hour", deadline_lower)
            if match_hour:
                hours_val = int(match_hour.group(1))
                expire_dt = disc_dt + timedelta(hours=hours_val)
                if expire_dt < now:
                    ids_to_delete.append(opp_id)
                    continue
                    
    if ids_to_delete:
        cursor.execute(
            f"DELETE FROM opportunities WHERE id IN ({','.join(map(str, ids_to_delete))})"
        )
        conn.commit()
        print(f"Pruned {len(ids_to_delete)} expired/outdated opportunities from the ledger database.")
        try:
            from utils.exporter import generate_markdown
            generate_markdown()
        except Exception as ex:
            print(f"Warning: Failed to regenerate markdown after pruning: {ex}")
        
    conn.close()


if __name__ == "__main__":
    init_db()
