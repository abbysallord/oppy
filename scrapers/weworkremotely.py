import feedparser
from scrapers.base import BaseScraper

class WeWorkRemotelyScraper(BaseScraper):
    def scrape_internships(self):
        url = "https://weworkremotely.com/remote-jobs.rss"
        print(f"Scraping WeWorkRemotely internships from {url}...")
        
        # We fetch via Jina or direct, but direct feedparser works since RSS feeds are open
        # We throttle using fetch_url, but since feedparser parses URLs, we fetch text first
        response_text = self.fetch_url(url, use_jina=False)
        if not response_text:
            return []
            
        try:
            feed = feedparser.parse(response_text)
            return self.parse_entries(feed.entries)
        except Exception as e:
            print(f"Error parsing WeWorkRemotely RSS: {e}")
            return []

    def parse_entries(self, entries):
        opportunities = []
        intern_keywords = ["intern", "internship", "co-op", "junior", "student", "grad"]
        
        for entry in entries:
            full_title = entry.get('title', '')
            
            # WWR titles are usually formatted as: "Company Name: Position Title"
            if ":" in full_title:
                company, title = [part.strip() for part in full_title.split(":", 1)]
            else:
                company = "WeWorkRemotely Client"
                title = full_title.strip()
                
            # Filter for internship keywords
            is_intern = any(kw in title.lower() for kw in intern_keywords) or \
                        any(kw in entry.get('description', '').lower() for kw in intern_keywords)
                        
            if not is_intern:
                # Let's also check if it's a junior/entry-level tech opportunity
                # We can loosen slightly to get enough remote opportunities
                continue
                
            opp_url = entry.get('link', '').strip()
            
            opportunities.append({
                'title': title,
                'company': company,
                'platform': 'weworkremotely',
                'opportunity_type': 'internship',
                'opportunity_url': opp_url,
                'stipend_or_prize': 'Paid (Remote)',
                'deadline': 'N/A (Apply ASAP)',
                'is_remote': 1,
                'is_paid': 1
            })
            
        return opportunities

if __name__ == "__main__":
    scraper = WeWorkRemotelyScraper()
    res = scraper.scrape_internships()
    for r in res[:3]:
        print(r)
