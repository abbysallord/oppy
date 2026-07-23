import sys
import os
from database.connection import get_connection, init_db
from scrapers.unstop import UnstopScraper
from scrapers.devpost import DevpostScraper
from scrapers.remoteok import RemoteOkScraper
from scrapers.weworkremotely import WeWorkRemotelyScraper
from utils.exporter import generate_markdown
from utils.tui import tui_main

def main():
    scrapers = [
        (UnstopScraper(), "scrape_internships", "internship"),
        (UnstopScraper(), "scrape_hackathons", "hackathon"),
        (DevpostScraper(), "scrape_hackathons", "hackathon"),
        (RemoteOkScraper(), "scrape_internships", "internship"),
        (WeWorkRemotelyScraper(), "scrape_internships", "internship")
    ]
    
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
            if platform_name not in active_platforms:
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
