import os
import sys
import time
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from rich.prompt import Prompt, Confirm
from rich.align import Align
from database.connection import get_connection, init_db
from utils.config import load_config, save_config

console = Console()

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def render_header():
    ascii_art = r"""
   ____   ____   ____  __  __ 
  / __ \ / __ \ / __ \|  \/  |
 | |  | | |  | | |  | | \  / |
 | |  | | |  | | |  | |  \/  |
 | |__| | |__| | |__| |      |
  \____/ \____/ \____/|_|  |_|
"""
    header_panel = Panel(
        Align.center(f"[bold magenta]{ascii_art}[/bold magenta]\n[dim]🛰️ Oppy — Terminal-Native Opportunity Scout[/dim]"),
        border_style="magenta"
    )
    console.print(header_panel)

def run_sync_progress(scrapers_to_run):
    """
    Executes the scrapers with a beautiful progress panel.
    Hides raw crawling logs, showing synchronization tasks.
    """
    clear_screen()
    render_header()
    
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    
    total_new = 0
    
    # Define tasks with clean enterprise-style descriptions
    sync_tasks = []
    for scraper_instance, method_name, opp_type in scrapers_to_run:
        platform_name = scraper_instance.__class__.__name__.replace("Scraper", "")
        task_desc = f"Syncing {platform_name} {opp_type.title()}s"
        sync_tasks.append((scraper_instance, method_name, opp_type, task_desc))
        
    console.print("\n[bold cyan]🔄 Initiating Ledger Synchronization...[/bold cyan]")
    
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
                # Run scraper
                results = method()
                
                # Save to db
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
                progress.update(main_task, description=f"[green]✓ Completed {task_desc} (+{new_count} new)[/green]")
                time.sleep(0.5)
                
            except Exception as e:
                progress.advance(main_task)
                progress.update(main_task, description=f"[red]❌ Failed {task_desc}: {str(e)[:40]}[/red]")
                time.sleep(1.0)
                
    conn.close()
    
    console.print(f"\n[bold green]✅ Sync execution complete. Discovered {total_new} new opportunities.[/bold green]")
    
    # Trigger dashboard generation
    from utils.exporter import generate_markdown
    generate_markdown()
    
    Prompt.ask("\n[bold yellow]Press Enter to return to main menu[/bold yellow]")

def browse_ledger():
    clear_screen()
    render_header()
    
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    
    # Get keywords filter if any
    keyword = Prompt.ask("\n🔍 [bold yellow]Enter search query (leave blank for all)[/bold yellow]").strip()
    
    # Paginated view loop
    limit = 10
    offset = 0
    
    while True:
        clear_screen()
        render_header()
        
        query_val = f"%{keyword}%"
        cursor.execute("""
            SELECT title, company, platform, opportunity_type, stipend_or_prize, deadline, opportunity_url
            FROM opportunities
            WHERE (title LIKE ? OR company LIKE ? OR platform LIKE ?)
            ORDER BY discovered_at DESC
            LIMIT ? OFFSET ?
        """, (query_val, query_val, query_val, limit, offset))
        
        rows = cursor.fetchall()
        
        cursor.execute("""
            SELECT COUNT(*) FROM opportunities
            WHERE (title LIKE ? OR company LIKE ? OR platform LIKE ?)
        """, (query_val, query_val, query_val))
        total_rows = cursor.fetchone()[0]
        
        table = Table(title=f"Opportunities Ledger (Showing {offset+1}-{offset+len(rows)} of {total_rows} matches)", expand=True)
        table.add_column("Type", justify="center", style="cyan")
        table.add_column("Platform", justify="center", style="green")
        table.add_column("Opportunity & Company", justify="left")
        table.add_column("Compensation / Prize", justify="left", style="yellow")
        table.add_column("Deadline", justify="left", style="blue")
        
        for title, company, platform, opp_type, stipend, deadline, url in rows:
            display_title = f"[bold white]{title}[/bold white]\n[dim]{company}[/dim]"
            table.add_row(
                opp_type.upper(),
                platform.upper(),
                display_title,
                stipend if stipend else "Paid",
                deadline if deadline else "Open"
            )
            
        console.print(table)
        
        console.print("\n[dim]Navigation: [N]ext Page  •  [P]revious Page  •  [Q]uit to Main Menu[/dim]")
        choice = Prompt.ask("Choose action", choices=["n", "p", "q"], default="q").lower()
        
        if choice == "n":
            if offset + limit < total_rows:
                offset += limit
        elif choice == "p":
            if offset - limit >= 0:
                offset -= limit
        elif choice == "q":
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
        
        settings_panel = Panel(
            f"[bold cyan]Current Synchronization Settings:[/bold cyan]\n\n"
            f"[bold white][1] Remote Only Filter  :[/bold white] {remote_val} (Internships)\n"
            f"[bold white][2] Paid Only Filter    :[/bold white] {paid_val} (Internships)\n"
            f"[bold white][3] Active Platforms    :[/bold white] {platforms_str}\n"
            f"[bold white][4] Dashboard Export Path:[/bold white] {export_path}\n"
            f"[bold white][5] Return to Main Menu[/bold white]",
            title="Settings Console",
            border_style="cyan"
        )
        console.print(settings_panel)
        
        choice = Prompt.ask("Select setting to edit [1-5]", choices=["1", "2", "3", "4", "5"], default="5")
        
        if choice == "1":
            config["remote_only"] = not config["remote_only"]
            save_config(config)
        elif choice == "2":
            config["paid_only"] = not config["paid_only"]
            save_config(config)
        elif choice == "3":
            # Select platforms interactively
            all_platforms = ["unstop", "devpost", "remoteok", "weworkremotely"]
            selected = []
            for plat in all_platforms:
                is_selected = Confirm.ask(f"Enable platform {plat.upper()}?")
                if is_selected:
                    selected.append(plat)
            if len(selected) > 0:
                config["selected_platforms"] = selected
                save_config(config)
            else:
                console.print("[bold red]Must select at least one platform![/bold red]")
                time.sleep(1)
        elif choice == "4":
            new_path = Prompt.ask("Enter new export absolute path", default=export_path)
            config["export_path"] = os.path.expanduser(new_path)
            save_config(config)
        elif choice == "5":
            break

def show_help():
    clear_screen()
    render_header()
    
    help_text = """
[bold cyan]Oppy CLI Help Console[/bold cyan]

Oppy scans popular developer databases to find career opportunities and export them to your second brain.

*   [bold yellow]Synchronize[/bold yellow]: Pulls current records from selected feeds and saves them to local SQLite.
*   [bold yellow]Markdown Exporter[/bold yellow]: Compiles entries to clean tables in your vault file.
*   [bold yellow]Global Configuration[/bold yellow]: Configurations persist in `~/.config/oppy/config.json`.
*   [bold yellow]Headless Execution[/bold yellow]: Run `oppy --headless` for background scripts or cron schedules.

[dim]Repository: https://github.com/abbysallord/oppy[/dim]
"""
    console.print(Panel(help_text, border_style="yellow"))
    Prompt.ask("\n[bold yellow]Press Enter to return to main menu[/bold yellow]")

def tui_main(scrapers_full_list):
    """
    Main entry point for interactive TUI.
    """
    while True:
        clear_screen()
        render_header()
        
        menu_panel = Panel(
            "[bold white][1][/bold white] 🔄 Synchronize Opportunities\n"
            "[bold white][2][/bold white] 🔍 Browse Opportunities Ledger\n"
            "[bold white][3][/bold white] ⚙️ Configure Scan Settings\n"
            "[bold white][4][/bold white] ❓ Help & Repository Info\n"
            "[bold white][5][/bold white] 🚪 Exit Console",
            title="Main Menu",
            border_style="magenta"
        )
        console.print(menu_panel)
        
        choice = Prompt.ask("Select option [1-5]", choices=["1", "2", "3", "4", "5"], default="1")
        
        if choice == "1":
            # Load active platforms from config and run sync
            config = load_config()
            active_platforms = config.get("selected_platforms", [])
            
            run_list = []
            for scraper_instance, method_name, opp_type in scrapers_full_list:
                platform_name = scraper_instance.__class__.__name__.replace("Scraper", "").lower()
                if platform_name in active_platforms:
                    run_list.append((scraper_instance, method_name, opp_type))
            
            run_sync_progress(run_list)
            
        elif choice == "2":
            browse_ledger()
        elif choice == "3":
            edit_settings()
        elif choice == "4":
            show_help()
        elif choice == "5":
            clear_screen()
            console.print("[bold magenta]Goodbye! Keep scouting.[/bold magenta] 🛰️")
            break
