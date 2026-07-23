import json
from scrapers.base import BaseScraper

class RemoteOkScraper(BaseScraper):
    def scrape_internships(self):
        url = "https://remoteok.com/api"
        print(f"Scraping RemoteOk internships from {url}...")
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
            print(f"Error parsing RemoteOk JSON: {e}")
            return []

    def parse_data(self, job_list):
        opportunities = []
        
        # Filtering terms to target internships specifically
        intern_keywords = ["intern", "internship", "co-op", "junior", "student", "grad"]
        
        for job in job_list:
            title = job.get('position', '').strip()
            tags = job.get('tags', [])
            
            # Match keywords in title or tag array
            is_intern = any(kw in title.lower() for kw in intern_keywords) or \
                        any(any(kw in tag.lower() for kw in intern_keywords) for tag in tags)
            
            if not is_intern:
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
