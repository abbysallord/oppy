import json
from scrapers.base import BaseScraper, EARLY_CAREER_WORDS, matches_any

class RemoteOkScraper(BaseScraper):
    def scrape_internships(self):
        url = "https://remoteok.com/api"
        response_json = self.fetch_url(url, use_jina=False)
        if not response_json:
            return None
            
        try:
            data = json.loads(response_json)
            # The first item is usually a legal disclaimer; skip it
            if isinstance(data, list) and len(data) > 1:
                return self.parse_data(data[1:])
            return []
        except Exception as e:
            self.note(f"Error parsing RemoteOk feed: {e}")
            return []

    def parse_data(self, job_list):
        opportunities = []
        
        for job in job_list:
            title = job.get('position', '').strip()
            tags = job.get('tags', [])

            # Whole-word match on the title and tags only: descriptions mention
            # "internal" and "international" far too often to be trusted.
            if not matches_any(title, EARLY_CAREER_WORDS) and \
               not matches_any(" ".join(str(tag) for tag in tags), EARLY_CAREER_WORDS):
                continue
                
            company = job.get('company', 'RemoteOk Company').strip()
            opp_url = job.get('url', '').strip()
            
            # Parse pay/salary info if available
            salary_min = job.get('salary_min')
            salary_max = job.get('salary_max')
            if salary_min or salary_max:
                pay = f"${salary_min:,} - ${salary_max:,}/yr" if salary_min and salary_max else f"${salary_min or salary_max:,}/yr"
            else:
                pay = "Paid (RemoteOk)"
                
            opportunities.append({
                'title': title,
                'company': company,
                'platform': 'remoteok',
                'opportunity_type': 'internship',
                'opportunity_url': opp_url,
                'stipend_or_prize': pay,
                'deadline': 'N/A (Apply ASAP)',
                'is_remote': 1,
                'is_paid': 1
            })
            
        return opportunities

if __name__ == "__main__":
    scraper = RemoteOkScraper()
    res = scraper.scrape_internships()
    for r in res[:3]:
        print(r)
