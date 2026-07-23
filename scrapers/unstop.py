import re
from scrapers.base import BaseScraper

class UnstopScraper(BaseScraper):
    def scrape_internships(self):
        from utils.config import load_config
        config = load_config()
        
        params = ["opportunityStatus=open"]
        if config.get("paid_only"):
            params.append("financials=paid")
        if config.get("remote_only"):
            params.append("workMode=virtual")
            
        url = f"https://unstop.com/internships?{'&'.join(params)}"
        print(f"Scraping Unstop internships from {url}...")
        markdown_content = self.fetch_url(url, use_jina=True)
        if not markdown_content:
            return []
        
        return self.parse_content(markdown_content, opportunity_type="internship")

    def scrape_hackathons(self):
        url = "https://unstop.com/hackathons?opportunityStatus=open"
        print(f"Scraping Unstop open hackathons from {url}...")
        markdown_content = self.fetch_url(url, use_jina=True)
        if not markdown_content:
            return []
        
        return self.parse_content(markdown_content, opportunity_type="hackathon")

    def parse_content(self, md_content, opportunity_type):
        opportunities = []
        
        # Split blocks by headers
        blocks = md_content.split("### [")
        if len(blocks) <= 1:
            return []
            
        for block in blocks[1:]:
            # Find opportunity URL within block
            url_match = re.search(r"\]\((https://unstop\.com/(?:internships|competitions|hackathons)/[^\)\?]+)\)", block)
            if not url_match:
                continue
                
            opp_url = url_match.group(1).strip()
            
            # The title text is in the block before the first closing markdown bracket/image
            title_part = block.split("](")[0]
            # Strip images and redundant spaces
            title_clean = re.sub(r"!\[[^\]]*\]\([^\)]*\)", "", title_part)
            title_clean = re.sub(r"\s+", " ", title_clean).strip()
            
            # Heuristically split Title and Company using the slug structure to ensure clean output
            opp_title, comp_name = self.extract_title_company(title_clean, opp_url, opportunity_type)
            
            # Stipend / Prize Parsing
            stipend_match = re.search(r"(\d+\s*K\s*-\s*\d+\s*K/Month|\d+,\d+/Month|\d+/Month|\*\*.*Month\*\*|\d+\s*K\s*-\s*\d+\s*K/Week)", block, re.IGNORECASE)
            stipend = stipend_match.group(1).replace("**", "").strip() if stipend_match else "Paid"
            
            if opportunity_type == "hackathon":
                # Look for prize pool
                prize_match = re.search(r"(?:Cash|Prize|Pool|Worth|INR|Rs\.?)\s*(?:Pool\s+of\s+)?(\d+(?:,\d+)*(?:\s*K)?)", block, re.IGNORECASE)
                stipend = f"Prize: {prize_match.group(1)}" if prize_match else "Prizes / Travel"
                
            # Deadline / Days left
            deadline_match = re.search(r"(\d+\s+days?\s+left|Ended|Ends\s+[A-Za-z0-9\s]+)", block, re.IGNORECASE)
            deadline = deadline_match.group(1).strip() if deadline_match else "Open"
            
            opportunities.append({
                'title': opp_title,
                'company': comp_name,
                'platform': 'unstop',
                'opportunity_type': opportunity_type,
                'opportunity_url': opp_url,
                'stipend_or_prize': stipend,
                'deadline': deadline,
                'is_remote': 1,
                'is_paid': 1
            })
            
        return opportunities

    def extract_title_company(self, block_text, url, opp_type):
        # Extract title using slug segment logic
        slug = url.split("/")[-1]
        slug_parts = slug.split("-")
        if slug_parts[-1].isdigit():
            slug_parts = slug_parts[:-1]
            
        # Common indicator keywords to split
        split_indicators = [
            "No prior experience", "Full Time", "Part Time", "Work from Home", 
            "Work From Home", "In Office", "experience required", "Ambassador"
        ]
        header = block_text
        for ind in split_indicators:
            if ind in header:
                header = header.split(ind)[0]
        header = header.strip()
        
        opp_keywords = ["internship", "intern", "hackathon", "ambassador", "challenge", "quiz", "competition", "modelling"]
        split_idx = -1
        for kw in opp_keywords:
            if kw in slug_parts:
                split_idx = slug_parts.index(kw)
                break
                
        if split_idx != -1:
            opp_slug_len = split_idx + 1
        else:
            opp_slug_len = len(slug_parts) // 2 if len(slug_parts) > 2 else 1
            
        header_words = header.split()
        opp_title = " ".join(header_words[:opp_slug_len])
        comp_name = " ".join(header_words[opp_slug_len:])
        
        if not comp_name:
            comp_name = "-".join(slug_parts[opp_slug_len:]).replace("-", " ").title()
        if not opp_title:
            opp_title = "-".join(slug_parts[:opp_slug_len]).replace("-", " ").title()
            
        return opp_title.strip(), comp_name.strip()
