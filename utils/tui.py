import os
import sys
import time
from pathlib import Path
from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from rich.prompt import Prompt, Confirm
from rich.align import Align
from database.connection import get_connection, init_db
from utils.config import load_config, save_config

# Enable standard GNU readline wrapper with disabled filename auto-complete
try:
    import readline
    readline.set_completer(None)
    readline.parse_and_bind("tab: self-insert")
except ImportError:
    pass

console = Console()

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

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
            return sys.stdin.read(1).lower()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
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

def confirm_key(prompt_text):
    """
    Prompts the user with a single-key (y/n) question.
    Returns True for 'y', False for 'n'. Does not require hitting Enter.
    """
    console.print(f"{prompt_text} [dim](y/n)[/dim]: ", end="")
    while True:
        key = read_key()
        if key == 'y':
            console.print("[green]yes[/green]")
            return True
        elif key == 'n':
            console.print("[red]no[/red]")
            return False
        elif key in ('q', '\x03'):
            console.print("[red]cancelled[/red]")
            return False

def render_header():
    ascii_art = r"""
 ██████╗ ██████╗ ██████╗ ██╗   ██╗
██╔═══██╗██╔══██╗██╔══██╗╚██╗ ██╔╝
██║   ██║██████╔╝██████╔╝ ╚████╔╝ 
██║   ██║██╔═══╝ ██╔═══╝   ╚██╔╝  
╚██████╔╝██║     ██║        ██║   
 ╚═════╝ ╚═╝     ╚═╝        ╚═╝   
"""
    logo_lines = [line for line in ascii_art.split('\n') if line.strip()]
    max_len = max(len(line) for line in logo_lines)
    logo_clean = "\n".join(line.ljust(max_len) for line in logo_lines)
    
    logo_align = Align.center(f"[bold magenta]{logo_clean}[/bold magenta]")
    subtext_align = Align.center("\n[dim]Oppy - Terminal-Native Opportunity Scout & Indexer[/dim]")
    
    header_panel = Panel(
        Group(logo_align, subtext_align),
        border_style="magenta"
    )
    console.print(header_panel)

def run_sync_progress(scrapers_to_run):
    clear_screen()
    render_header()
    
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    
    total_new = 0
    sync_tasks = []
    for scraper_instance, method_name, opp_type in scrapers_to_run:
        platform_name = scraper_instance.__class__.__name__.replace("Scraper", "")
        task_desc = f"Syncing {platform_name} {opp_type.title()}s"
        sync_tasks.append((scraper_instance, method_name, opp_type, task_desc))
        
    console.print("\n[bold cyan]Initiating Ledger Synchronization...[/bold cyan]")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        console=console
    ) as progress:
        
        main_task = progress.add_task("[bold white]Progress[/bold white]", total=len(sync_tasks))
        
        for scraper_instance, method_name, opp_type, task_desc in sync_tasks:
            progress.update(main_task, description=f"[bold yellow]{task_desc}...[/bold yellow]")
            
            try:
                method = getattr(scraper_instance, method_name)
                
                # Run blocking network call in a separate thread to keep spinner animated
                import io
                import contextlib
                import threading
                
                results = None
                exc = None
                
                def worker():
                    nonlocal results, exc
                    try:
                        with contextlib.redirect_stdout(io.StringIO()):
                            results = method()
                    except Exception as e:
                        exc = e
                
                t = threading.Thread(target=worker)
                t.start()
                
                while t.is_alive():
                    time.sleep(0.05)
                    
                if exc is not None:
                    raise exc
                
                if results is None:
                    raise Exception("Offline")
                
                new_count = 0
                for item in results:
                    try:
                        cursor.execute("""
                            INSERT INTO opportunities (
                                title, company, platform, opportunity_type, opportunity_url, stipend_or_prize, deadline, is_remote, is_paid
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            item['title'],
                            item['company'],
                            item['platform'],
                            item['opportunity_type'],
                            item['opportunity_url'],
                            item['stipend_or_prize'],
                            item['deadline'],
                            item['is_remote'],
                            item['is_paid']
                        ))
                        new_count += 1
                    except Exception:
                        pass
                
                total_new += new_count
                conn.commit()
                
                progress.advance(main_task)
                progress.update(main_task, description=f"[green]SUCCESS: {task_desc} (+{new_count} new)[/green]")
                time.sleep(0.5)
                
            except Exception as e:
                progress.advance(main_task)
                progress.update(main_task, description=f"[red]FAILED: {task_desc}: {str(e)[:40]}[/red]")
                time.sleep(1.0)
                
    conn.close()
    
    console.print(f"\n[bold green]Sync execution complete. Discovered {total_new} new opportunities.[/bold green]")
    
    from utils.exporter import generate_markdown
    generate_markdown()
    
    Prompt.ask("\n[bold yellow]Press Enter to return to main menu[/bold yellow]")

def browse_ledger():
    clear_screen()
    render_header()
    
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    
    keyword = Prompt.ask("\nSearch query (leave blank for all)").strip()
    
    limit = 10
    offset = 0
    filter_type = "all"
    message = ""
    
    while True:
        clear_screen()
        render_header()
        
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
            
        where_clause = " AND ".join(conditions) if conditions else "1"
        
        # Fetch rows
        query_params = params.copy()
        query_params.extend([limit, offset])
        cursor.execute(f"""
            SELECT title, company, platform, opportunity_type, stipend_or_prize, deadline, opportunity_url
            FROM opportunities
            WHERE {where_clause}
            ORDER BY discovered_at DESC
            LIMIT ? OFFSET ?
        """, query_params)
        rows = cursor.fetchall()
        
        # Count total matches
        cursor.execute(f"""
            SELECT COUNT(*) FROM opportunities
            WHERE {where_clause}
        """, params)
        total_rows = cursor.fetchone()[0]
        
        table = Table(title=f"Opportunities Ledger (Showing {offset+1}-{offset+len(rows)} of {total_rows} matches)", expand=True)
        table.add_column("Type", justify="center", style="cyan")
        table.add_column("Platform", justify="center", style="green")
        table.add_column("Opportunity, Company & URL", justify="left")
        table.add_column("Compensation / Prize", justify="left", style="yellow")
        table.add_column("Deadline", justify="left", style="blue")
        
        for title, company, platform, opp_type, stipend, deadline, url in rows:
            # Inline stacked display containing clickable link
            display_cell = f"[bold white]{title}[/bold white]\n[dim]{company}[/dim]\n[blue][link={url}]{url}[/link][/blue]"
            table.add_row(
                opp_type.upper(),
                platform.upper(),
                display_cell,
                stipend if stipend else "Paid",
                deadline if deadline else "Open"
            )
            
        console.print(table)
        
        if message:
            console.print(f"\n{message}")
            message = ""
            
        console.print(f"\n[dim]Navigation: [→ / N]ext Page  •  [← / P]revious Page  •  [T]oggle Type Filter ({filter_type.upper()})  •  [Q]uit[/dim]")
        
        choice = read_key()
        
        if choice in ("n", "right"):
            if offset + limit < total_rows:
                offset += limit
            else:
                message = "[bold red]Notice: You have reached the end of the ledger.[/bold red]"
        elif choice in ("p", "left"):
            if offset - limit >= 0:
                offset -= limit
            else:
                message = "[bold red]Notice: Already at the first page of the ledger.[/bold red]"
        elif choice == "t":
            if filter_type == "all":
                filter_type = "internship"
            elif filter_type == "internship":
                filter_type = "hackathon"
            elif filter_type == "hackathon":
                filter_type = "job"
            else:
                filter_type = "all"
            offset = 0
        elif choice == "q" or choice == "\x03":
            break
            
    conn.close()

def edit_settings():
    while True:
        clear_screen()
        render_header()
        
        config = load_config()
        
        remote_val = "[green]YES[/green]" if config.get("remote_only") else "[red]NO[/red]"
        paid_val = "[green]YES[/green]" if config.get("paid_only") else "[red]NO[/red]"
        platforms_str = ", ".join([p.upper() for p in config.get("selected_platforms")])
        export_path = config.get("export_path")
        
        active_feeds_count = len(config.get("custom_rss_feeds", []))
        
        settings_panel = Panel(
            f"[bold cyan]Current Synchronization Settings:[/bold cyan]\n\n"
            f"[bold white][1] Remote Only Filter  :[/bold white] {remote_val} (Internships)\n"
            f"[bold white][2] Paid Only Filter    :[/bold white] {paid_val} (Internships)\n"
            f"[bold white][3] Active Platforms    :[/bold white] {platforms_str}\n"
            f"[bold white][4] Dashboard Export Path:[/bold white] {export_path}\n"
            f"[bold white][5] Custom RSS Feeds     :[/bold white] {active_feeds_count} feeds\n"
            f"[bold white][6] Return to Main Menu[/bold white]",
            title="Settings Console",
            border_style="cyan"
        )
        console.print(settings_panel)
        
        console.print("[dim]Press key [1-6] to select...[/dim]", end="")
        choice = read_key()
        
        if choice == "1":
            config["remote_only"] = not config["remote_only"]
            save_config(config)
        elif choice == "2":
            config["paid_only"] = not config["paid_only"]
            save_config(config)
        elif choice == "3":
            all_platforms = ["unstop", "devpost", "remoteok", "weworkremotely"]
            selected = []
            for plat in all_platforms:
                is_selected = confirm_key(f"Enable platform {plat.upper()}?")
                if is_selected:
                    selected.append(plat)
            if len(selected) > 0:
                config["selected_platforms"] = selected
                save_config(config)
            else:
                console.print("[bold red]Must select at least one platform![/bold red]")
                time.sleep(1)
        elif choice == "4":
            new_path = Prompt.ask("Enter new export absolute path (Press Enter to keep current)", default=export_path)
            config["export_path"] = os.path.expanduser(new_path)
            save_config(config)
        elif choice == "5":
            while True:
                clear_screen()
                render_header()
                feeds = config.get("custom_rss_feeds", [])
                
                console.print("[bold cyan]Custom RSS Feeds Panel[/bold cyan]\n")
                if not feeds:
                    console.print("[dim]No custom RSS feeds active currently.[/dim]\n")
                else:
                    for idx, feed_url in enumerate(feeds):
                        console.print(f"[{idx + 1}] {feed_url}")
                    console.print("")
                
                console.print("[bold white][1][/bold white] Add New RSS Feed")
                if feeds:
                    console.print("[bold white][2][/bold white] Delete Existing RSS Feed")
                    console.print("[bold white][3][/bold white] Return to Settings Console")
                    console.print("\n[dim]Press key [1-3] to select...[/dim]", end="")
                    feed_choice = read_key()
                else:
                    console.print("[bold white][2][/bold white] Return to Settings Console")
                    console.print("\n[dim]Press key [1-2] to select...[/dim]", end="")
                    feed_choice = read_key()
                    if feed_choice == "2":
                        break
                        
                if feed_choice == "1":
                    new_feed = Prompt.ask("Enter custom RSS Feed URL").strip()
                    if new_feed.startswith("http"):
                        feeds.append(new_feed)
                        config["custom_rss_feeds"] = feeds
                        save_config(config)
                    else:
                        console.print("[bold red]Invalid URL schema! Must start with http/https.[/bold red]")
                        time.sleep(1)
                elif feed_choice == "2" and feeds:
                    del_idx_str = Prompt.ask("Enter feed number to delete")
                    try:
                        del_idx = int(del_idx_str) - 1
                        if 0 <= del_idx < len(feeds):
                            feeds.pop(del_idx)
                            config["custom_rss_feeds"] = feeds
                            save_config(config)
                        else:
                            console.print("[bold red]Index out of bounds![/bold red]")
                            time.sleep(1)
                    except ValueError:
                        console.print("[bold red]Invalid index number![/bold red]")
                        time.sleep(1)
                elif feed_choice == "3" or (feed_choice == "2" and not feeds):
                    break
        elif choice == "6" or choice == "q":
            break

def show_help():
    clear_screen()
    render_header()
    
    mascot = r"""
     .
    / \
   |   |
===|[-]|===   Oppy (Scouting Satellite)
   |   |
    \ /
     v
"""
    help_text = f"""
[bold cyan]Oppy CLI Help Console[/bold cyan]

Oppy scans popular developer databases to find career opportunities and export them to your second brain.

*   [bold yellow]Synchronize[/bold yellow]: Pulls current records from selected feeds and saves them to local SQLite.
*   [bold yellow]Markdown Exporter[/bold yellow]: Compiles entries to clean tables in your vault file.
*   [bold yellow]Global Configuration[/bold yellow]: Configurations persist in `~/.config/oppy/config.json`.
*   [bold yellow]Headless Execution[/bold yellow]: Run `oppy --headless` for background scripts or cron schedules.

[dim]Repository: https://github.com/abbysallord/oppy[/dim]
"""
    
    # Combined Layout Panel
    console.print(Panel(help_text + f"\n[dim]{mascot}[/dim]", border_style="yellow"))
    Prompt.ask("\n[bold yellow]Press Enter to return to main menu[/bold yellow]")

def tui_main(scrapers_full_list):
    """
    Main entry point for interactive TUI.
    """
    while True:
        clear_screen()
        render_header()
        
        menu_panel = Panel(
            "[bold white][1][/bold white] Synchronize Opportunities (Index Feeds)\n"
            "[bold white][2][/bold white] Browse Opportunities Ledger (Query & Filter)\n"
            "[bold white][3][/bold white] Configure Scan Settings (Filter Toggles)\n"
            "[bold white][4][/bold white] Help & Repository Details\n"
            "[bold white][5][/bold white] Exit Console",
            title="Main Menu",
            border_style="magenta"
        )
        console.print(menu_panel)
        
        console.print("[dim]Press key [1-5] to select...[/dim]", end="")
        choice = read_key()
        
        if choice == "1":
            config = load_config()
            active_platforms = config.get("selected_platforms", [])
            
            run_list = []
            for scraper_instance, method_name, opp_type in scrapers_full_list:
                platform_name = scraper_instance.__class__.__name__.replace("Scraper", "").lower()
                if platform_name in active_platforms or platform_name == "customrss":
                    run_list.append((scraper_instance, method_name, opp_type))
            
            run_sync_progress(run_list)
            
        elif choice == "2":
            browse_ledger()
        elif choice == "3":
            edit_settings()
        elif choice == "4":
            show_help()
        elif choice == "5" or choice == "q":
            clear_screen()
            console.print("[bold magenta]Goodbye! Keep scouting.[/bold magenta]")
            break
