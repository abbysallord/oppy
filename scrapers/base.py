import urllib.request
import urllib.parse
import time

class BaseScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
        }
        self.jina_prefix = "https://r.jina.ai/"

    def fetch_url(self, url, use_jina=False, delay=2.0):
        # Mandatory delay to throttle requests and respect rate limits
        time.sleep(delay)
        
        target_url = f"{self.jina_prefix}{url}" if use_jina else url
        req = urllib.request.Request(target_url, headers=self.headers)
        
        try:
            with urllib.request.urlopen(req, timeout=15) as response:
                if response.status == 200:
                    return response.read().decode('utf-8')
                else:
                    print(f"Failed to fetch {target_url}, status: {response.status}")
                    return None
        except Exception as e:
            print(f"Error fetching {target_url}: {e}")
            return None
