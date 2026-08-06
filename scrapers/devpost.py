import json
import re
from scrapers.base import BaseScraper

class DevpostScraper(BaseScraper):
    def scrape_hackathons(self):
        from utils.config import load_config
        config = load_config()
        
        params = []
        if config.get("remote_only"):
            params.append("challenge_type[]=online")
            
        opportunities = []
        # Page through first 3 pages of listings
        for page in range(1, 4):
            url = f"https://devpost.com/api/hackathons?page={page}"
            if params:
                url += f"&{'&'.join(params)}"
                
            response_json = self.fetch_url(url, use_jina=False)
            if not response_json:
                break
                
            try:
                data = json.loads(response_json)
                hackathons = data.get("hackathons", [])
                if not hackathons:
                    break
                    
                for item in hackathons:
                    # Filter for active/open state
                    if item.get("open_state") != "open":
                        continue
                        
                    title = item.get("title", "").strip()
                    opp_url = item.get("url", "").strip()
                    
                    # Clean currency/prize amount html tags
                    prize_html = item.get("prize_amount", "Paid / Prizes")
                    prize = re.sub(r'<[^>]+>', '', prize_html).strip() if prize_html else "Paid / Prizes"
                    
                    # Estimate deadline
                    deadline = item.get("time_left_to_submission", "Open")
                    
                    opportunities.append({
                        'title': title,
                        'company': item.get("organization_name", "Devpost Host") or "Devpost Host",
                        'platform': 'devpost',
                        'opportunity_type': 'hackathon',
                        'opportunity_url': opp_url,
                        'stipend_or_prize': prize,
                        'deadline': deadline,
                        'is_remote': 1,
                        'is_paid': 1
                    })
            except Exception as e:
                print(f"Error parsing Devpost page {page}: {e}")
                continue
                
        return opportunities

