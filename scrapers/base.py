import re
import ssl
import time
import urllib.parse
import urllib.request

# Hyphens stay inside tokens so "co-op" survives; this is what stops "internal"
# and "international" from being read as "intern".
_WORD_RE = re.compile(r"[a-z0-9+#.\-]+")

EARLY_CAREER_WORDS = frozenset({
    "intern", "interns", "internship", "internships",
    "co-op", "coop", "junior", "jr", "trainee",
    "student", "students", "graduate", "grad",
    "apprentice", "apprenticeship", "entry-level",
})

CONTEST_WORDS = frozenset({
    "hackathon", "hackathons", "hack", "challenge", "challenges",
    "competition", "competitions", "datathon", "ideathon",
})


def matches_any(text, vocabulary):
    """Whole-word membership test against a vocabulary of keywords."""
    if not text:
        return False
    return bool(vocabulary & set(_WORD_RE.findall(text.lower())))


class BaseScraper:
    """Shared HTTP plumbing: throttling, TLS handling and error collection.

    Scrapers record problems on ``self.notes`` rather than printing, so the
    live TUI frame is never corrupted by stray output from worker threads.
    """

    # Set once per process if the interpreter turns out to have no trust store.
    _insecure_fallback = False

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
        }
        self.jina_prefix = "https://r.jina.ai/"
        self.notes = []

    def note(self, message):
        self.notes.append(message)

    def fetch_url(self, url, use_jina=False, delay=2.0):
        # Mandatory delay to throttle requests and respect rate limits
        time.sleep(delay)

        target_url = f"{self.jina_prefix}{url}" if use_jina else url
        req = urllib.request.Request(target_url, headers=self.headers)

        try:
            return self._open(req, ssl.create_default_context())
        except ssl.SSLCertVerificationError:
            # Some Python installs (notably python.org builds on macOS) ship
            # without a usable trust store. Fall back for this request only and
            # say so, instead of disabling verification process-wide.
            host = urllib.parse.urlparse(target_url).netloc
            if not BaseScraper._insecure_fallback:
                BaseScraper._insecure_fallback = True
                self.note(
                    "TLS certificates could not be verified. Run Python's "
                    "'Install Certificates.command' (macOS) or install the certifi "
                    "package to restore verification."
                )
            self.note(f"Fetched {host} without certificate verification.")
            try:
                return self._open(req, ssl._create_unverified_context())
            except Exception as e:
                self.note(f"Error fetching {target_url}: {e}")
                return None
        except Exception as e:
            self.note(f"Error fetching {target_url}: {e}")
            return None

    def _open(self, req, context):
        with urllib.request.urlopen(req, timeout=15, context=context) as response:
            if response.status == 200:
                return response.read().decode('utf-8')
            self.note(f"Failed to fetch {req.full_url}, status: {response.status}")
            return None
