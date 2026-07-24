import sys
import os
from database.connection import get_connection, init_db
from scrapers.unstop import UnstopScraper
from scrapers.devpost import DevpostScraper
from scrapers.remoteok import RemoteOkScraper
from scrapers.weworkremotely import WeWorkRemotelyScraper
from scrapers.custom_rss import CustomRSSScraper
from utils.exporter import generate_markdown
from utils.tui import tui_main

def main():
    scrapers = [
        (UnstopScraper(), "scrape_internships", "internship"),
        (UnstopScraper(), "scrape_hackathons", "hackathon"),
        (DevpostScraper(), "scrape_hackathons", "hackathon"),
        (RemoteOkScraper(), "scrape_internships", "internship"),
        (WeWorkRemotelyScraper(), "scrape_internships", "internship"),
        (CustomRSSScraper(), "scrape_custom_feeds", "job")
    ]
    
    # Check for CLI search argument
    search_query = None
    if "--search" in sys.argv or "-s" in sys.argv:
        try:
            idx = sys.argv.index("--search") if "--search" in sys.argv else sys.argv.index("-s")
            if idx + 1 < len(sys.argv):
                search_query = sys.argv[idx + 1]
        except ValueError:
            pass
            
    if search_query is not None:
        init_db()
        conn = get_connection()
        cursor = conn.cursor()
        
        # Split terms for case-insensitive search
        words = [w.lower().rstrip('s') for w in search_query.split() if w]
        conditions = []
        params = []
        for word in words:
            conditions.append("(LOWER(title) LIKE ? OR LOWER(company) LIKE ? OR LOWER(platform) LIKE ?)")
            params.extend([f"%{word}%", f"%{word}%", f"%{word}%"])
            
        where_clause = " AND ".join(conditions) if conditions else "1"
        
        cursor.execute(f"""
            SELECT opportunity_type, platform, title, company, stipend_or_prize, deadline, opportunity_url
            FROM opportunities
            WHERE {where_clause}
            ORDER BY discovered_at DESC
            LIMIT 15
        """, params)
        rows = cursor.fetchall()
        conn.close()
        
        from rich.console import Console
        from rich.table import Table
        console = Console()
        
        if not rows:
            console.print(f"\n[bold red]No cached opportunities found matching query: '{search_query}'[/bold red]\n")
            sys.exit(0)
            
        table = Table(title=f"Oppy Search Results (matching '{search_query}')", expand=True)
        table.add_column("Type", justify="center", style="cyan")
        table.add_column("Platform", justify="center", style="green")
        table.add_column("Opportunity & Company", justify="left")
        table.add_column("Compensation / Prize", justify="left", style="yellow")
        table.add_column("Deadline", justify="left", style="blue")
        
        for opp_type, platform, title, company, stipend, deadline, url in rows:
            display_cell = f"[bold white]{title}[/bold white]\n[dim]{company}[/dim]\n[blue]{url}[/blue]"
            table.add_row(
                opp_type.upper(),
                platform.upper(),
                display_cell,
                stipend if stipend else "Paid",
                deadline if deadline else "Open"
            )
            
        console.print(table)
        sys.exit(0)

    if "--headless" in sys.argv or "-h" in sys.argv:
        # Run silent background scan (ideal for systemd timers and cron jobs)
        print("🚀 Starting Headless Opportunities Scan...")
        init_db()
        
        from utils.config import load_config
        config = load_config()
        active_platforms = config.get("selected_platforms", ["unstop", "devpost", "remoteok", "weworkremotely"])
        
        conn = get_connection()
        cursor = conn.cursor()
        total_new = 0
        
        for scraper_instance, method_name, opp_type in scrapers:
            platform_name = scraper_instance.__class__.__name__.replace("Scraper", "").lower()
            if platform_name not in active_platforms and platform_name != "customrss":
                continue
                
            print(f"Syncing platform {platform_name} ({opp_type})...")
            try:
                method = getattr(scraper_instance, method_name)
                results = method()
                
                if results is None:
                    print(f"Failed to sync {platform_name}: Platform offline or request timed out.")
                    continue
                
                new_in_platform = 0
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
                        new_in_platform += 1
                    except Exception:
                        pass
                
                total_new += new_in_platform
                conn.commit()
                
            except Exception as e:
                print(f"Error syncing {platform_name}: {e}")
                continue
                
        conn.close()
        print(f"Scan complete. Total new opportunities saved: {total_new}")
        generate_markdown()
    else:
        # Launch the rich-rendered terminal user interface (TUI)
        tui_main(scrapers)

if __name__ == "__main__":
    main()
