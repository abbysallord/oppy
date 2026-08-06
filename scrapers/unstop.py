import json
from scrapers.base import BaseScraper

class UnstopScraper(BaseScraper):
    def scrape_internships(self):
        from utils.config import load_config
        config = load_config()
        
        opportunities = []
        # Page through first 3 pages of listings
        for page in range(1, 4):
            url = f"https://unstop.com/api/public/opportunity/search-result?opportunity=internships&oppstatus=open&page={page}"
            response_json = self.fetch_url(url, use_jina=False)
            if not response_json:
                break
                
            try:
                data = json.loads(response_json)
                opps = data.get("data", {}).get("data", [])
                if not opps:
                    break
                    
                for opp in opps:
                    job_detail = opp.get('jobDetail') or {}
                    
                    # 1. Paid filter
                    is_paid = 1 if (job_detail.get('paid_unpaid') == 'paid' or opp.get('isPaid') is True) else 0
                    if config.get("paid_only") and not is_paid:
                        continue
                        
                    # 2. Remote filter
                    is_remote = 0
                    locations = opp.get('locations') or []
                    if job_detail.get('type') == 'wfh' or any('home' in str(loc).lower() for loc in locations):
                        is_remote = 1
                    if config.get("remote_only") and not is_remote:
                        continue
                        
                    title = opp.get("title", "").strip()
                    opp_url = f"https://unstop.com/{opp.get('public_url')}"
                    company = opp.get("organisation", {}).get("name", "Unstop Company") or "Unstop Company"
                    
                    # Stipend parsing
                    min_sal = job_detail.get('min_salary')
                    max_sal = job_detail.get('max_salary')
                    if min_sal or max_sal:
                        stipend = f"INR {min_sal:,}- {max_sal:,}/Month" if min_sal and max_sal else f"INR {min_sal or max_sal:,}/Month"
                    else:
                        stipend = "Paid" if is_paid else "Unpaid"
                        
                    deadline = self.format_deadline(opp.get("end_date"))
                    
                    opportunities.append({
                        'title': title,
                        'company': company,
                        'platform': 'unstop',
                        'opportunity_type': 'internship',
                        'opportunity_url': opp_url,
                        'stipend_or_prize': stipend,
                        'deadline': deadline,
                        'is_remote': is_remote,
                        'is_paid': is_paid
                    })
            except Exception as e:
                print(f"Error parsing Unstop internships page {page}: {e}")
                continue
                
        return opportunities

    def scrape_hackathons(self):
        opportunities = []
        # Page through first 3 pages of listings
        for page in range(1, 4):
            url = f"https://unstop.com/api/public/opportunity/search-result?opportunity=hackathons&oppstatus=open&page={page}"
            response_json = self.fetch_url(url, use_jina=False)
            if not response_json:
                break
                
            try:
                data = json.loads(response_json)
                opps = data.get("data", {}).get("data", [])
                if not opps:
                    break
                    
                for opp in opps:
                    title = opp.get("title", "").strip()
                    opp_url = f"https://unstop.com/{opp.get('public_url')}"
                    company = opp.get("organisation", {}).get("name", "Unstop Host") or "Unstop Host"
                    
                    # Prize parsing
                    prizes = opp.get('prizes') or []
                    cash_prizes = [p.get('cash') for p in prizes if p.get('cash')]
                    if cash_prizes:
                        total_cash = sum(cash_prizes)
                        stipend = f"INR {total_cash:,}"
                    else:
                        others = [p.get('others') for p in prizes if p.get('others')]
                        stipend = others[0] if others else "Prizes / Travel"
                        
                    deadline = self.format_deadline(opp.get("end_date"))
                    
                    opportunities.append({
                        'title': title,
                        'company': company,
                        'platform': 'unstop',
                        'opportunity_type': 'hackathon',
                        'opportunity_url': opp_url,
                        'stipend_or_prize': stipend,
                        'deadline': deadline,
                        'is_remote': 1,
                        'is_paid': 1
                    })
            except Exception as e:
                print(f"Error parsing Unstop hackathons page {page}: {e}")
                continue
                
        return opportunities

    def format_deadline(self, iso_str):
        if not iso_str:
            return "Open"
        try:
            from datetime import datetime
            date_part = iso_str.split("T")[0]
            dt = datetime.strptime(date_part, "%Y-%m-%d")
            return dt.strftime("%d %b %Y")
        except Exception:
            return iso_str.split("T")[0]

