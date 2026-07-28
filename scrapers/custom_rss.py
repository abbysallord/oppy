import feedparser
from scrapers.base import BaseScraper
from utils.config import load_config

class CustomRSSScraper(BaseScraper):
    def scrape_custom_feeds(self):
        config = load_config()
        feeds = config.get("custom_rss_feeds", [])
        if not feeds:
            return []
            
        opportunities = []
        for url in feeds:
            # We fetch via fetch_url (SSL-safe context is automatically inherited)
            response_text = self.fetch_url(url, use_jina=False)
            if not response_text:
                continue
                
            try:
                feed = feedparser.parse(response_text)
                for entry in feed.entries:
                    title = entry.get('title', 'Unknown Position').strip()
                    url_link = entry.get('link', '').strip()
                    summary = entry.get('summary', '').lower()
                    
                    # Heuristically evaluate if position is a job, internship, or hackathon
                    opp_type = "job"
                    title_lower = title.lower()
                    if "intern" in title_lower or "intern" in summary or "co-op" in title_lower:
                        opp_type = "internship"
                    elif "hackathon" in title_lower or "challenge" in title_lower or "competition" in title_lower:
                        opp_type = "hackathon"
                        
                    pay_info = "Paid"
                    if "stipend" in summary or "salary" in summary or "$" in summary or "inr" in summary:
                        pay_info = "Paid (custom feed)"
                    elif "unpaid" in summary or "volunteer" in summary:
                        pay_info = "Unpaid"
                        
                    # Respect remote toggles (heuristically flag as remote if mentioned)
                    is_remote = 1
                    if "on-site" in summary or "hybrid" in summary or "office" in summary:
                        # If explicitly local but user toggles remote-only, skip it
                        is_remote = 0
                        if config.get("remote_only"):
                            continue
                            
                    # Respect paid toggles
                    if config.get("paid_only") and pay_info == "Unpaid":
                        continue
                        
                    opportunities.append({
                        'title': title,
                        'company': feed.feed.get('title', 'Custom RSS Source').strip(),
                        'platform': 'custom_rss',
                        'opportunity_type': opp_type,
                        'opportunity_url': url_link,
                        'stipend_or_prize': pay_info,
                        'deadline': 'N/A (Apply ASAP)',
                        'is_remote': is_remote,
                        'is_paid': 1 if pay_info != "Unpaid" else 0
                    })
            except Exception:
                pass
                
        return opportunities
