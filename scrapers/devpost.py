import re
from scrapers.base import BaseScraper

class DevpostScraper(BaseScraper):
    def scrape_hackathons(self):
        from utils.config import load_config
        config = load_config()
        
        if config.get("remote_only"):
            url = "https://devpost.com/hackathons?challenge_type[]=online"
        else:
            url = "https://devpost.com/hackathons"
            
        print(f"Scraping Devpost hackathons from {url}...")
        markdown_content = self.fetch_url(url, use_jina=True)
        if not markdown_content:
            return []
            
        return self.parse_content(markdown_content)

    def parse_content(self, md_content):
        opportunities = []
        
        # Pattern matching the outer card anchor containing image, title, and metadata
        # Excluding help, secure, info, blog, team, software, users, gallery, jobs
        exclude_subs = r"help|secure|info|blog|team|software|users|gallery|jobs"
        pattern = r"\[\!\[Image\s+\d+\]\([^\)]+\)\s+###\s+([^\]]+)\]\((https://(?!(" + exclude_subs + r")\.)[a-zA-Z0-9\-]+\.devpost\.com/[^\)]*)\)"
        
        matches = list(re.finditer(pattern, md_content))
        for i, match in enumerate(matches):
            details = match.group(1).strip()
            opp_url = match.group(2).strip()
            
            # Split on common deadline indicators to isolate the title
            split_indicators = ["days left", "day left", "month left", "months left", "hours left", "days to go", "to go"]
            title = details
            deadline = "Open"
            
            for ind in split_indicators:
                if ind in details:
                    parts = details.split(ind)
                    title = parts[0].strip()
                    # Extract number of days/months left
                    words = title.split()
                    if len(words) > 0:
                        deadline = f"{words[-1]} {ind}"
                        title = " ".join(words[:-1]).strip()
                    break
            
            # Clean up trailing words like 'about', 'around', 'ends'
            title = re.sub(r"\s+(?:about|around|ends|ends in|in)$", "", title, flags=re.IGNORECASE).strip()
            
            # Extract prize pool
            prize_match = re.search(r"(\$[0-9,]+\s*(?:in\s+prizes|cash)?|\$[0-9,]+)", details, re.IGNORECASE)
            prize = prize_match.group(1).strip() if prize_match else "Paid / Prizes"
            
            opportunities.append({
                'title': title,
                'company': 'Devpost Host',
                'platform': 'devpost',
                'opportunity_type': 'hackathon',
                'opportunity_url': opp_url,
                'stipend_or_prize': prize,
                'deadline': deadline,
                'is_remote': 1,
                'is_paid': 1
            })
            
        return opportunities

if __name__ == "__main__":
    scraper = DevpostScraper()
    res = scraper.scrape_hackathons()
    for r in res[:3]:
        print(r)
