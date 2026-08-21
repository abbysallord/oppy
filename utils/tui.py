import os
import sys
import time
import webbrowser
from pathlib import Path

from rich.align import Align
from rich.console import Group
from rich.layout import Layout
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from rich.table import Table
from rich.text import Text

from database.connection import get_connection, init_db, get_stats, upsert_opportunity
from utils import theme
from utils.theme import ACCENT, INFO, WARN, DANGER, MUTED, console
from utils.config import load_config, save_config, record_sync

# Enable standard GNU readline wrapper with disabled filename auto-complete
try:
    import readline
    readline.set_completer(None)
    readline.parse_and_bind("tab: self-insert")
    readline.parse_and_bind("set disable-completion on")
except ImportError:
    pass

ENTER_KEYS = ("\r", "\n")
QUIT_KEYS = ("q", "\x03")


def read_key():
    """
    Reads a single keypress, supporting immediate returns for numbers,
    character commands, and ANSI escape sequences (Arrow keys).
    """
    if os.name == 'nt':
        import msvcrt
        try:
            ch = msvcrt.getch()
            if ch in (b'\x00', b'\xe0'): # Arrow key prefix
                ch2 = msvcrt.getch()
                if ch2 == b'M': return 'right'
                if ch2 == b'K': return 'left'
                if ch2 == b'H': return 'up'
                if ch2 == b'P': return 'down'
            return ch.decode('utf-8', errors='ignore').lower()
        except Exception:
            return ''
    else:
        import sys
        import tty
        import termios
        fd = sys.stdin.fileno()
        if not os.isatty(fd):
            # EOF on redirected input means no key will ever arrive; treat it as
            # quit so the menu loop cannot spin forever.
            return (sys.stdin.read(1) or "q").lower()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
            if ch == '':
                return 'q'
            if ch == '\x1b': # Escape sequence detector
                ch2 = sys.stdin.read(1)
                if ch2 == '[':
                    ch3 = sys.stdin.read(1)
                    if ch3 == 'C': return 'right'
                    if ch3 == 'D': return 'left'
                    if ch3 == 'A': return 'up'
                    if ch3 == 'B': return 'down'
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch.lower()


def current_stats():
    """Ledger counters plus a humanized age for the stats strip."""
    stats = get_stats()
    stats["last_sync"] = theme.humanize_since(load_config().get("last_sync"))
    return stats


def notice_screen(message, style=INFO, title="Notice"):
    """Render a centred message (newlines allowed) and wait for a keypress."""
    body = Panel(
        Align.center(Text(message, style=style, justify="center"), vertical="middle"),
        title=title,
        border_style=style,
    )
    theme.render_screen(body, [("any key", "continue")])
    read_key()


def ask_screen(question, title="Input", default=""):
    """Full-screen single-question prompt backed by readline editing."""
    # Clip only what is shown; the full default is still what Enter accepts.
    hint = f"\n\n[{theme.clip_path(default, theme.content_width() - 16)}]" if default else ""
    body = Panel(
        Align.center(Text(question + hint, style="bold white", justify="center"), vertical="middle"),
        title=title,
        border_style=INFO,
    )
    theme.render_screen(body, [("⏎", "confirm"), ("empty ⏎", "cancel")], reserve=2)
    console.show_cursor(True)
    try:
        answer = input("  > ").strip()
    except (EOFError, KeyboardInterrupt):
        return ""
    finally:
        console.show_cursor(False)
    return answer or default


def confirm_key(prompt_text):
    """
    Prompts the user with a single-key (y/n) question.
    Returns True for 'y', False for 'n'. Does not require hitting Enter.
    """
    console.print(f"{prompt_text} [dim](y/n)[/dim]: ", end="")
    while True:
        key = read_key()
        if key == 'y':
            console.print(f"[{ACCENT}]yes[/{ACCENT}]")
            return True
        elif key == 'n':
            console.print(f"[{DANGER}]no[/{DANGER}]")
            return False
        elif key in QUIT_KEYS:
            console.print(f"[{DANGER}]cancelled[/{DANGER}]")
            return False


# --------------------------------------------------------------------------
# Synchronization
# --------------------------------------------------------------------------

def sync_body(progress, log_lines):
    # Keep only the tail that fits, so a long run never overflows the frame.
    room = max(1, theme.body_height() - 6)
    visible = log_lines[-room:]
    return Panel(
        Group(progress, Text(""), *visible),
        title="Synchronizing Ledger",
        border_style=ACCENT,
        padding=(1, 2),
    )


def run_sync_progress(scrapers_to_run):
    init_db(quiet=True)
    conn = get_connection()
    cursor = conn.cursor()

    progress = Progress(
        SpinnerColumn(style=ACCENT),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(complete_style=ACCENT, finished_style=ACCENT, pulse_style=MUTED),
        TextColumn(f"[{MUTED}]{{task.completed}}/{{task.total}}"),
        console=console,
        expand=True,
    )

    sync_tasks = []
    for scraper_instance, method_name, opp_type in scrapers_to_run:
        platform_name = scraper_instance.__class__.__name__.replace("Scraper", "")
        sync_tasks.append((scraper_instance, method_name, opp_type, f"{platform_name} {opp_type}s"))

    main_task = progress.add_task("[bold white]Starting…", total=len(sync_tasks))
    log_lines = []
    hints = [("", "working — please wait")]

    totals = {"new": 0, "updated": 0, "failed": 0}

    # No rich.Live here: we are already inside the alternate screen buffer and
    # Live would emit its own alt-screen escape codes, dropping us back to the
    # normal buffer when it stops. Repainting the frame ourselves keeps the
    # spinner animating (Progress advances on elapsed time) through the exact
    # same path every other screen uses.
    def repaint():
        theme.render_screen(sync_body(progress, log_lines), hints)

    for scraper_instance, method_name, opp_type, label in sync_tasks:
        progress.update(main_task, description=f"[bold {WARN}]Syncing {label}…")
        repaint()

        try:
            method = getattr(scraper_instance, method_name)

            # Run the blocking network call off the main thread so the
            # spinner keeps animating.
            import threading

            results = None
            exc = None

            def worker():
                nonlocal results, exc
                try:
                    results = method()
                except Exception as e:
                    exc = e

            t = threading.Thread(target=worker)
            t.start()
            while t.is_alive():
                repaint()
                time.sleep(0.12)

            if exc is not None:
                raise exc
            if results is None:
                raise Exception("platform offline or request timed out")

            new_count = 0
            updated_count = 0
            errors = 0
            for item in results:
                try:
                    outcome = upsert_opportunity(cursor, item)
                    if outcome == "new":
                        new_count += 1
                    elif outcome == "updated":
                        updated_count += 1
                except Exception:
                    errors += 1

            conn.commit()
            totals["new"] += new_count
            totals["updated"] += updated_count

            detail = f"+{new_count} new, {updated_count} refreshed"
            if errors:
                detail += f", {errors} rejected"
            line = Text("  ✓ ", style=f"bold {ACCENT}")
            line.append(f"{label:<34}", style="white")
            line.append(detail, style=MUTED)
            log_lines.append(line)

        except Exception as e:
            totals["failed"] += 1
            line = Text("  ✗ ", style=f"bold {DANGER}")
            line.append(f"{label:<34}", style="white")
            line.append(str(e)[:48], style=DANGER)
            log_lines.append(line)

        # Surface anything the scraper recorded (TLS fallbacks, parse errors).
        for note in scraper_instance.notes:
            log_lines.append(Text(f"      {theme.truncate(note, 88)}", style=MUTED))
        scraper_instance.notes.clear()

        progress.advance(main_task)
        repaint()

    progress.update(main_task, description=f"[bold {ACCENT}]Complete")
    repaint()
    time.sleep(0.4)

    conn.close()
    record_sync()

    summary = Text()
    summary.append(f"{totals['new']}", style=f"bold {ACCENT}")
    summary.append(" new  ", style=MUTED)
    summary.append(f"{totals['updated']}", style=f"bold {INFO}")
    summary.append(" refreshed  ", style=MUTED)
    summary.append(f"{totals['failed']}", style=f"bold {DANGER if totals['failed'] else MUTED}")
    summary.append(" platforms failed", style=MUTED)

    body = Panel(
        Align.center(
            Group(
                Text("Synchronization complete", style=f"bold {ACCENT}", justify="center"),
                Text(""),
                Align.center(summary),
                Text(""),
                Text("Nothing was written to disk — press e to export.",
                     style=MUTED, justify="center"),
            ),
            vertical="middle",
        ),
        title="Sync Report",
        border_style=ACCENT,
    )

    hints = [("v", "view results"), ("e", "export"), ("any key", "back to menu")]
    while True:
        theme.render_screen(body, hints, current_stats())
        choice = read_key()
        if choice == "v":
            browse_ledger()
        elif choice == "e":
            export_screen()
        else:
            break


# --------------------------------------------------------------------------
# Ledger
# --------------------------------------------------------------------------

FILTER_CYCLE = ["all", "internship", "hackathon", "job"]

TYPE_STYLES = {
    "internship": INFO,
    "hackathon": ACCENT,
    "job": WARN,
}


def build_ledger_query(keyword, filter_type):
    # Build query conditions case-insensitively, splitting terms & removing plural 's'
    words = [w.lower().rstrip('s') for w in keyword.split() if w]
    conditions = []
    params = []
    for word in words:
        conditions.append("(LOWER(title) LIKE ? OR LOWER(company) LIKE ? OR LOWER(platform) LIKE ?)")
        params.extend([f"%{word}%", f"%{word}%", f"%{word}%"])

    if filter_type != "all":
        conditions.append("opportunity_type = ?")
        params.append(filter_type)

    return (" AND ".join(conditions) if conditions else "1"), params


def ledger_table(rows, offset, total_rows, keyword, filter_type):
    caption = f"showing {offset + 1}-{offset + len(rows)} of {total_rows}" if rows else "no matches"
    if keyword:
        caption += f"  ·  query “{keyword}”"

    table = Table(
        title=f"[bold white]Opportunities Ledger[/bold white]  [{MUTED}]({filter_type.upper()})",
        caption=f"[{MUTED}]{caption}",
        expand=True,
        border_style=MUTED,
        header_style=f"bold {ACCENT}",
        padding=(0, 1),
    )
    table.add_column("#", justify="right", width=3, no_wrap=True, style=MUTED)
    table.add_column("Source", justify="left", width=16, no_wrap=True)
    table.add_column("Opportunity", justify="left", ratio=1, no_wrap=True)
    table.add_column("Reward", justify="left", width=20, no_wrap=True, style=ACCENT)
    table.add_column("Deadline", justify="left", width=13, no_wrap=True, style=INFO)

    if not rows:
        table.add_row("", Text("Nothing indexed yet — run a sync to populate.", style=MUTED), "", "")
        return table

    # Every cell is clipped so a row is exactly three lines tall, which keeps
    # the page-size arithmetic in browse_ledger() honest.
    detail_width = max(20, theme.content_width() - 16 - 20 - 13 - 13)

    for i, (title, company, platform, opp_type, stipend, deadline, url) in enumerate(rows, 1):
        source = Text()
        source.append(theme.truncate(opp_type.upper(), 15), style=f"bold {TYPE_STYLES.get(opp_type, MUTED)}")
        source.append("\n")
        source.append(theme.truncate(platform.upper(), 15), style=MUTED)

        clean_title = theme.truncate(title.strip(), detail_width)
        clean_url = theme.truncate(url.replace("https://", ""), detail_width)
        cell = Text()
        cell.append(clean_title, style="bold white")
        cell.append("\n")
        cell.append(theme.truncate(company.strip() if company else "Unknown", detail_width), style=MUTED)
        cell.append("\n")
        url_start = len(cell)
        cell.append(clean_url, style=f"{INFO} dim underline")
        cell.stylize(f"link {url}", 0, len(clean_title))
        cell.stylize(f"link {url}", url_start, url_start + len(clean_url))

        table.add_row(
            str(i),
            source,
            cell,
            theme.truncate(stipend if stipend else "Paid", 19),
            theme.truncate(deadline if deadline else "Open", 12),
        )
    return table


def browse_ledger():
    init_db(quiet=True)
    conn = get_connection()
    cursor = conn.cursor()

    keyword = ""
    offset = 0
    filter_type = "all"

    hints = [
        ("←/→", "page"),
        ("t", "type filter"),
        ("/", "search"),
        ("o", "open #"),
        ("c", "clear"),
        ("q", "back"),
    ]

    while True:
        # Each row occupies three lines; fit as many whole rows as the window allows.
        rows_available = theme.body_height() - 5
        limit = max(3, rows_available // 3)

        where_clause, params = build_ledger_query(keyword, filter_type)

        cursor.execute(f"SELECT COUNT(*) FROM opportunities WHERE {where_clause}", params)
        total_rows = cursor.fetchone()[0]

        if offset >= total_rows:
            offset = max(0, (max(total_rows, 1) - 1) // limit * limit)

        cursor.execute(
            f"""
            SELECT title, company, platform, opportunity_type, stipend_or_prize, deadline, opportunity_url
            FROM opportunities
            WHERE {where_clause}
            ORDER BY discovered_at DESC
            LIMIT ? OFFSET ?
            """,
            params + [limit, offset],
        )
        rows = cursor.fetchall()

        theme.render_screen(ledger_table(rows, offset, total_rows, keyword, filter_type), hints)

        choice = read_key()

        if choice in ("n", "right"):
            if offset + limit < total_rows:
                offset += limit
        elif choice in ("p", "left"):
            offset = max(0, offset - limit)
        elif choice == "t":
            filter_type = FILTER_CYCLE[(FILTER_CYCLE.index(filter_type) + 1) % len(FILTER_CYCLE)]
            offset = 0
        elif choice == "/":
            keyword = ask_screen("Search titles, companies and platforms", title="Ledger Search")
            offset = 0
        elif choice == "c":
            keyword = ""
            filter_type = "all"
            offset = 0
        elif choice == "o":
            answer = ask_screen(f"Open which row? (1-{len(rows)})", title="Open Link")
            if answer.strip().isdigit() and 1 <= int(answer) <= len(rows):
                webbrowser.open(rows[int(answer) - 1][-1])
        elif choice in QUIT_KEYS:
            break

    conn.close()


# --------------------------------------------------------------------------
# Settings
# --------------------------------------------------------------------------

def _plural(count, noun):
    return f"{count} {noun}" if count == 1 else f"{count} {noun}s"


def settings_body(config, selected):
    rows = [
        ("Remote only filter", "YES" if config.get("remote_only") else "NO", "skip on-site internships"),
        ("Paid only filter", "YES" if config.get("paid_only") else "NO", "skip unpaid listings"),
        ("Active platforms", ", ".join(p.upper() for p in config.get("selected_platforms", [])), "sources to index"),
        ("Dashboard export path", config.get("export_path", ""), "where the Markdown lands"),
        ("Custom RSS feeds", _plural(len(config.get("custom_rss_feeds", [])), "feed"), "extra sources to poll"),
        ("Return to main menu", "", ""),
    ]

    grid = Table.grid(padding=(0, 2))
    grid.add_column(width=2)
    grid.add_column(width=4, no_wrap=True)
    grid.add_column(width=22, no_wrap=True)
    grid.add_column(width=34, no_wrap=True)
    grid.add_column(width=30, no_wrap=True)

    for index, (label, value, hint) in enumerate(rows):
        active = index == selected
        cursor = Text("▸" if active else " ", style=f"bold {ACCENT}")
        key = Text(f"[{index + 1}]", style=f"bold {ACCENT}" if active else MUTED)
        name = Text(label, style="bold white" if active else "white")

        if value in ("YES", "NO"):
            detail = Text(value, style=f"bold {ACCENT if value == 'YES' else DANGER}")
        else:
            # Paths are clipped from the left so the filename stays visible.
            detail = Text(theme.clip_path(value, 34), style=INFO)

        grid.add_row(cursor, key, name, detail, Text(hint, style=MUTED))

    return Panel(
        Align.center(grid, vertical="middle"),
        title="Scan Settings",
        border_style=ACCENT,
        padding=(1, 2),
    )


def manage_feeds(config):
    selected = 0
    while True:
        feeds = config.get("custom_rss_feeds", [])

        grid = Table.grid(padding=(0, 2))
        grid.add_column(width=2)
        grid.add_column(width=4, no_wrap=True)
        grid.add_column(ratio=1)
        if not feeds:
            grid.add_row("", "", Text("No custom feeds configured.", style=MUTED))
        for index, feed_url in enumerate(feeds):
            active = index == selected
            grid.add_row(
                Text("▸" if active else " ", style=f"bold {ACCENT}"),
                Text(f"[{index + 1}]", style=f"bold {ACCENT}" if active else MUTED),
                Text(feed_url, style="bold white" if active else MUTED),
            )

        body = Panel(
            Align.center(grid, vertical="middle"),
            title="Custom RSS Feeds",
            border_style=ACCENT,
            padding=(1, 2),
        )
        theme.render_screen(body, [("↑↓", "move"), ("a", "add feed"), ("d", "delete"), ("q", "back")])

        choice = read_key()
        if choice == "up" and feeds:
            selected = (selected - 1) % len(feeds)
        elif choice == "down" and feeds:
            selected = (selected + 1) % len(feeds)
        elif choice == "a":
            new_feed = ask_screen("Enter an RSS feed URL", title="Add Feed")
            if new_feed.startswith("http"):
                feeds.append(new_feed)
                config["custom_rss_feeds"] = feeds
                save_config(config)
            elif new_feed:
                notice_screen("Invalid URL — must start with http:// or https://", DANGER, "Rejected")
        elif choice == "d" and feeds:
            feeds.pop(selected)
            selected = max(0, min(selected, len(feeds) - 1))
            config["custom_rss_feeds"] = feeds
            save_config(config)
        elif choice in QUIT_KEYS:
            break


def edit_settings():
    selected = 0
    hints = [("↑↓", "move"), ("⏎", "toggle / edit"), ("1-6", "jump"), ("q", "back")]

    while True:
        config = load_config()
        theme.render_screen(settings_body(config, selected), hints)

        choice = read_key()

        if choice == "up":
            selected = (selected - 1) % 6
            continue
        if choice == "down":
            selected = (selected + 1) % 6
            continue
        if choice in ENTER_KEYS:
            action = selected
        elif choice in "123456" and choice.strip():
            action = int(choice) - 1
            selected = action
        elif choice in QUIT_KEYS:
            break
        else:
            continue

        if action == 0:
            config["remote_only"] = not config.get("remote_only")
            save_config(config)
        elif action == 1:
            config["paid_only"] = not config.get("paid_only")
            save_config(config)
        elif action == 2:
            select_platforms(config)
        elif action == 3:
            new_path = ask_screen(
                "Enter the absolute export path for the Markdown dashboard",
                title="Export Path",
                default=config.get("export_path", ""),
            )
            if new_path:
                config["export_path"] = os.path.expanduser(new_path)
                save_config(config)
        elif action == 4:
            manage_feeds(config)
        elif action == 5:
            break


def select_platforms(config):
    all_platforms = ["unstop", "devpost", "remoteok", "weworkremotely"]
    active = set(config.get("selected_platforms", []))
    selected = 0

    while True:
        grid = Table.grid(padding=(0, 2))
        grid.add_column(width=2)
        grid.add_column(width=6, no_wrap=True)
        grid.add_column(ratio=1)
        for index, platform in enumerate(all_platforms):
            enabled = platform in active
            grid.add_row(
                Text("▸" if index == selected else " ", style=f"bold {ACCENT}"),
                Text("[on]" if enabled else "[off]", style=f"bold {ACCENT}" if enabled else DANGER),
                Text(platform.upper(), style="bold white" if index == selected else MUTED),
            )

        body = Panel(
            Align.center(grid, vertical="middle"),
            title="Active Platforms",
            border_style=ACCENT,
            padding=(1, 2),
        )
        theme.render_screen(body, [("↑↓", "move"), ("space/⏎", "toggle"), ("q", "save & back")])

        choice = read_key()
        if choice == "up":
            selected = (selected - 1) % len(all_platforms)
        elif choice == "down":
            selected = (selected + 1) % len(all_platforms)
        elif choice in ENTER_KEYS or choice == " ":
            platform = all_platforms[selected]
            active.symmetric_difference_update({platform})
        elif choice in QUIT_KEYS:
            if not active:
                notice_screen("At least one platform must stay enabled.", DANGER, "Rejected")
                continue
            config["selected_platforms"] = [p for p in all_platforms if p in active]
            save_config(config)
            break


# --------------------------------------------------------------------------
# Export
# --------------------------------------------------------------------------

EXPORT_FORMATS = [
    ("Markdown", "md", "Obsidian, or any Markdown editor"),
    ("PDF", "pdf", "printable, monospaced text"),
    ("CSV", "csv", "spreadsheets and data tools"),
]


def default_export_dir():
    """Prefer the configured dashboard folder, then Downloads, then cwd."""
    configured = os.path.dirname(load_config().get("export_path") or "")
    if configured and os.path.isdir(configured):
        return configured
    downloads = os.path.join(os.path.expanduser("~"), "Downloads")
    return downloads if os.path.isdir(downloads) else os.getcwd()


def export_screen():
    selected = 0
    hints = [("↑↓", "move"), ("⏎", "choose"), ("1-3", "jump"), ("q", "back")]

    while True:
        stats = current_stats()

        grid = Table.grid(padding=(0, 2))
        grid.add_column(width=2)
        grid.add_column(width=4, no_wrap=True)
        grid.add_column(width=12, no_wrap=True)
        grid.add_column(width=8, no_wrap=True)
        grid.add_column(ratio=1, no_wrap=True)

        for index, (label, ext, hint) in enumerate(EXPORT_FORMATS):
            active = index == selected
            grid.add_row(
                Text("▸" if active else " ", style=f"bold {ACCENT}"),
                Text(f"[{index + 1}]", style=f"bold {ACCENT}" if active else MUTED),
                Text(label, style=f"bold {ACCENT}" if active else "white"),
                Text(f".{ext}", style=INFO),
                Text(hint, style=MUTED),
            )

        body = Panel(
            Align.center(
                Group(
                    Text(f"{stats['total']} listings will be written",
                         style="bold white", justify="center"),
                    Text(f"{stats['internship']} internships · {stats['hackathon']} hackathons · {stats['job']} jobs",
                         style=MUTED, justify="center"),
                    Text(""),
                    grid,
                ),
                vertical="middle",
            ),
            title="Export Dashboard",
            border_style=ACCENT,
            padding=(1, 2),
        )
        theme.render_screen(body, hints)

        choice = read_key()

        if choice == "up":
            selected = (selected - 1) % len(EXPORT_FORMATS)
            continue
        if choice == "down":
            selected = (selected + 1) % len(EXPORT_FORMATS)
            continue
        if choice in ENTER_KEYS:
            pass
        elif choice in "123" and choice.strip():
            selected = int(choice) - 1
        elif choice in QUIT_KEYS:
            return
        else:
            continue

        label, ext, _hint = EXPORT_FORMATS[selected]
        suggested = os.path.join(default_export_dir(), f"Opportunities.{ext}")
        destination = ask_screen(
            f"Save the {label} export to…",
            title=f"Export {label}",
            default=suggested,
        )
        if not destination:
            continue

        from utils.exporter import export as export_ledger
        try:
            written = export_ledger(ext, destination)
            size = os.path.getsize(written)
            shown = theme.clip_path(written, theme.content_width() - 8)
            notice_screen(
                f"Wrote {stats['total']} listings as {label}\n\n{shown}\n\n{size:,} bytes",
                ACCENT,
                "Export complete",
            )
        except Exception as e:
            notice_screen(f"Could not write the export:\n\n{e}", DANGER, "Export failed")
        return


# --------------------------------------------------------------------------
# Help
# --------------------------------------------------------------------------

def show_help():
    sections = [
        ("Ledger", [
            ("← / →", "page backward and forward"),
            ("t", "cycle ALL → INTERNSHIP → HACKATHON → JOB"),
            ("/", "search titles, companies and platforms"),
            ("o", "open a row's link in your browser"),
            ("c", "clear search and filters"),
        ]),
        ("Export", [
            ("Markdown (.md)", "Obsidian or any Markdown editor"),
            ("PDF (.pdf)", "printable monospaced text"),
            ("CSV (.csv)", "spreadsheets and data tools"),
            ("after a sync", "press e to export, v to browse"),
        ]),
        ("Settings", [
            ("↑ / ↓", "move between options"),
            ("⏎", "toggle a filter or edit a value"),
            ("1 - 6", "jump straight to an option"),
        ]),
        ("Command line", [
            ("oppy --search TERM", "query the cache without the TUI"),
            ("oppy --audit", "rank listings against your resume"),
            ("oppy --edit", "edit your resume skills file"),
            ("oppy --headless", "silent sync for cron and systemd"),
        ]),
    ]

    blocks = []
    for title, entries in sections:
        grid = Table.grid(padding=(0, 2))
        grid.add_column(width=20, no_wrap=True)
        grid.add_column(ratio=1)
        for key, description in entries:
            grid.add_row(Text(key, style=f"bold {ACCENT}"), Text(description, style=MUTED))
        blocks.append(Text(title, style=f"bold {INFO}"))
        blocks.append(grid)
        blocks.append(Text(""))

    blocks.append(Text("github.com/abbysallord/oppy", style=MUTED))

    body = Panel(
        Align.center(Group(*blocks), vertical="middle"),
        title="Help",
        border_style=ACCENT,
        padding=(1, 2),
    )
    theme.render_screen(body, [("any key", "back to menu")])
    read_key()


# --------------------------------------------------------------------------
# Main menu
# --------------------------------------------------------------------------

MENU_ITEMS = [
    ("Synchronize Opportunities", "sync"),
    ("Browse Ledger", "browse"),
    ("Export Dashboard", "export"),
    ("Scan Settings", "settings"),
    ("Help", "help"),
    ("Exit", "exit"),
]


def menu_body(selected, config, stats):
    platforms = config.get("selected_platforms", [])
    filters = [name for name, key in (("remote", "remote_only"), ("paid", "paid_only")) if config.get(key)]
    details = [
        f"pull latest from {len(platforms)} platform{'s' if len(platforms) != 1 else ''}",
        f"{stats['total']} listings cached",
        "write markdown, pdf or csv",
        ("filters: " + " · ".join(filters)) if filters else "no filters active",
        "keybindings and CLI flags",
        "leave the console",
    ]

    grid = Table.grid(padding=(0, 2))
    grid.add_column(width=2)
    grid.add_column(width=4, no_wrap=True)
    grid.add_column(width=30, no_wrap=True)
    grid.add_column(ratio=1)

    for index, (label, _) in enumerate(MENU_ITEMS):
        active = index == selected
        grid.add_row(
            Text("▸" if active else " ", style=f"bold {ACCENT}"),
            Text(f"[{index + 1}]", style=f"bold {ACCENT}" if active else MUTED),
            Text(label, style=f"bold {ACCENT}" if active else "white"),
            Text(details[index], style=MUTED),
        )

    return Panel(
        grid,
        title="Main Menu",
        border_style=ACCENT,
        padding=(1, 2),
    )


MENU_PANEL_HEIGHT = len(MENU_ITEMS) + 4  # rows + padding + borders


def recent_panel(limit):
    """Fill the space under the menu with the newest listings in the ledger."""
    rows = []
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT title, company, platform, opportunity_type, deadline
            FROM opportunities ORDER BY discovered_at DESC LIMIT ?
            """,
            (max(1, limit),),
        )
        rows = cursor.fetchall()
        conn.close()
    except Exception:
        pass

    grid = Table.grid(padding=(0, 2))
    grid.add_column(width=12, no_wrap=True)
    grid.add_column(width=42, no_wrap=True)
    grid.add_column(width=22, no_wrap=True)
    grid.add_column(ratio=1, no_wrap=True)

    if not rows:
        grid.add_row(Text("Ledger is empty — press 1 to run your first sync.", style=MUTED), "", "", "")

    for title, company, platform, opp_type, deadline in rows:
        grid.add_row(
            Text(opp_type.upper()[:11], style=TYPE_STYLES.get(opp_type, MUTED)),
            Text(theme.truncate(title.strip(), 42), style="white"),
            Text(theme.truncate(company.strip() if company else "Unknown", 22), style=MUTED),
            Text(theme.truncate(deadline or "Open", 18), style=MUTED),
        )

    return Panel(grid, title="Recently Indexed", border_style=MUTED, padding=(0, 2))


def menu_screen(selected, config, stats):
    body = Layout()
    body.split_column(
        Layout(menu_body(selected, config, stats), name="menu", size=MENU_PANEL_HEIGHT),
        Layout(recent_panel(theme.body_height(has_stats=True) - MENU_PANEL_HEIGHT - 2), name="recent", ratio=1),
    )
    return body


def tui_main(scrapers_full_list):
    """
    Main entry point for interactive TUI.
    """
    entered_fullscreen = theme.enter_fullscreen()
    try:
        menu_loop(scrapers_full_list)
    finally:
        theme.exit_fullscreen(entered_fullscreen)

    console.print(f"[bold {ACCENT}]Goodbye! Keep scouting.[/bold {ACCENT}]")


def menu_loop(scrapers_full_list):
    selected = 0
    hints = [("↑↓", "move"), ("⏎", "select"), ("1-6", "jump"), ("q", "quit")]

    init_db(quiet=True)

    while True:
        config = load_config()
        stats = current_stats()
        theme.render_screen(menu_screen(selected, config, stats), hints, stats)

        choice = read_key()

        if choice == "up":
            selected = (selected - 1) % len(MENU_ITEMS)
            continue
        if choice == "down":
            selected = (selected + 1) % len(MENU_ITEMS)
            continue
        if choice in ENTER_KEYS:
            action = MENU_ITEMS[selected][1]
        elif choice in "123456" and choice.strip():
            selected = int(choice) - 1
            action = MENU_ITEMS[selected][1]
        elif choice in QUIT_KEYS:
            action = "exit"
        else:
            continue

        if action == "sync":
            active_platforms = config.get("selected_platforms", [])
            run_list = []
            for scraper_instance, method_name, opp_type in scrapers_full_list:
                platform_name = scraper_instance.__class__.__name__.replace("Scraper", "").lower()
                if platform_name in active_platforms or platform_name == "customrss":
                    run_list.append((scraper_instance, method_name, opp_type))

            if not run_list:
                notice_screen("No platforms are enabled. Turn one on in Settings.", DANGER, "Nothing to sync")
            else:
                run_sync_progress(run_list)
        elif action == "browse":
            browse_ledger()
        elif action == "export":
            export_screen()
        elif action == "settings":
            edit_settings()
        elif action == "help":
            show_help()
        elif action == "exit":
            break
