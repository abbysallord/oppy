import sys
import os
from database.connection import get_connection, init_db
from scrapers.unstop import UnstopScraper
from scrapers.devpost import DevpostScraper
from scrapers.remoteok import RemoteOkScraper
from scrapers.weworkremotely import WeWorkRemotelyScraper
from utils.exporter import generate_markdown

def main():
    print("🚀 Starting Automated Opportunities Scan...")
    
    # 1. Initialize Database
    init_db()
    
    conn = get_connection()
    cursor = conn.cursor()
    
    scrapers = [
        (UnstopScraper(), "scrape_internships", "internship"),
        (UnstopScraper(), "scrape_hackathons", "hackathon"),
        (DevpostScraper(), "scrape_hackathons", "hackathon"),
        (RemoteOkScraper(), "scrape_internships", "internship"),
        (WeWorkRemotelyScraper(), "scrape_internships", "internship")
    ]
    
    total_new = 0
    
    for scraper_instance, method_name, opp_type in scrapers:
        scraper_name = scraper_instance.__class__.__name__
        print(f"\n⚡ Running {scraper_name}.{method_name}...")
        try:
            method = getattr(scraper_instance, method_name)
            results = method()
            
            print(f"Scraped {len(results)} items from {scraper_name}.")
            
            # Save to database
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
                    # Ignore integrity errors for duplicate unique opportunity_url values
                    pass
            
            print(f"Saved {new_in_platform} new opportunities to database.")
            total_new += new_in_platform
            conn.commit()
            
        except Exception as e:
            print(f"❌ Error running {scraper_name}.{method_name}: {e}")
            # Keep processing remaining scrapers (avoids single point of failure)
            continue
            
    conn.close()
    print(f"\n✅ Scan execution complete. Total new opportunities: {total_new}")
    
    # 2. Re-generate Obsidian Markdown dashboard
    generate_markdown()

if __name__ == "__main__":
    main()
