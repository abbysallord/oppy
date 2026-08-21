import feedparser
from scrapers.base import BaseScraper, EARLY_CAREER_WORDS, matches_any

class WeWorkRemotelyScraper(BaseScraper):
    def scrape_internships(self):
        url = "https://weworkremotely.com/remote-jobs.rss"
        
        # We fetch via Jina or direct, but direct feedparser works since RSS feeds are open
        # We throttle using fetch_url, but since feedparser parses URLs, we fetch text first
        response_text = self.fetch_url(url, use_jina=False)
        if not response_text:
            return None
            
        try:
            feed = feedparser.parse(response_text)
            return self.parse_entries(feed.entries)
        except Exception as e:
            self.note(f"Error parsing WeWorkRemotely feed: {e}")
            return []

    def parse_entries(self, entries):
        opportunities = []

        for entry in entries:
            full_title = entry.get('title', '')
            
            # WWR titles are usually formatted as: "Company Name: Position Title"
            if ":" in full_title:
                company, title = [part.strip() for part in full_title.split(":", 1)]
            else:
                company = "WeWorkRemotely Client"
                title = full_title.strip()
                
            # Title only: descriptions routinely say "internal" or "international",
            # which used to tag senior roles as internships.
            if not matches_any(title, EARLY_CAREER_WORDS):
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
