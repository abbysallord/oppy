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

def init_db(quiet=False):
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
        return prune_expired_opportunities(quiet=quiet)
    except Exception as e:
        if not quiet:
            print(f"Warning: Failed to prune expired opportunities: {e}")
        return 0

def prune_expired_opportunities(quiet=False):
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
        placeholders = ",".join("?" for _ in ids_to_delete)
        cursor.execute(
            f"DELETE FROM opportunities WHERE id IN ({placeholders})", ids_to_delete
        )
        conn.commit()
        # Deliberately does not rewrite any export here: exporting is an
        # explicit user action, so opening the app never touches your files.
        if not quiet:
            print(f"Pruned {len(ids_to_delete)} expired/outdated opportunities from the ledger database.")

    conn.close()
    return len(ids_to_delete)


# Columns refreshed when a listing we already track is seen again, so changed
# deadlines and prize pools do not go stale in the ledger.
_REFRESHABLE = (
    "title", "company", "opportunity_type", "stipend_or_prize",
    "deadline", "is_remote", "is_paid",
)


def upsert_opportunity(cursor, item):
    """Insert a scraped listing, refreshing it if the URL is already tracked.

    Returns "new", "updated" or "unchanged". Raises on real database errors so
    callers can surface them instead of silently dropping rows.
    """
    cursor.execute(
        """
        INSERT OR IGNORE INTO opportunities (
            title, company, platform, opportunity_type, opportunity_url,
            stipend_or_prize, deadline, is_remote, is_paid
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            item["title"],
            item["company"],
            item["platform"],
            item["opportunity_type"],
            item["opportunity_url"],
            item["stipend_or_prize"],
            item["deadline"],
            item["is_remote"],
            item["is_paid"],
        ),
    )
    if cursor.rowcount == 1:
        return "new"

    assignments = ", ".join(f"{column} = ?" for column in _REFRESHABLE)
    values = [item[column] for column in _REFRESHABLE]
    values.append(item["opportunity_url"])
    cursor.execute(
        f"UPDATE opportunities SET {assignments} WHERE opportunity_url = ?", values
    )
    return "updated" if cursor.rowcount else "unchanged"


def get_stats():
    """Ledger totals used by the TUI stats strip."""
    stats = {"total": 0, "internship": 0, "hackathon": 0, "job": 0}
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT opportunity_type, COUNT(*) FROM opportunities GROUP BY opportunity_type")
        for opp_type, count in cursor.fetchall():
            stats["total"] += count
            if opp_type in stats:
                stats[opp_type] += count
        conn.close()
    except Exception:
        pass
    return stats


if __name__ == "__main__":
    init_db()
