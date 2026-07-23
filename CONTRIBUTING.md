# 🤝 Contributing to Oppy

Thank you for showing interest in contributing to **Oppy**! We are building a modular, community-driven tool to help developers, designers, and creators discover paid internships and hackathons globally.

Follow this guide to get your local environment set up and start shipping features.

---

## 🛠️ Local Development Setup

### 1. Prerequisite Checklist
*   **Python**: Version 3.8 or higher.
*   **Node.js**: Version 14 or higher (optional, for CLI testing).

### 2. Fork & Clone
1.  Fork the repository on GitHub.
2.  Clone your fork locally:
    ```bash
    git clone https://github.com/YOUR-USERNAME/oppy.git
    cd oppy
    ```

### 3. Python Environment Configuration
Initialize a Python virtual environment and install the required dependencies:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
pip install feedparser
```

### 4. Running the Scanner Local Copy
Verify the setup works by running the Python orchestrator:
```bash
python3 scan.py
```
This will initialize the database locally and export `Opportunities.md` to your current working directory.

---

## 📂 Code Layout Guidelines

To add a **new scraper** for another job board or hackathon site:
1.  Create a new scraper file in `scrapers/myplatform.py` extending the `BaseScraper` class:
    ```python
    from scrapers.base import BaseScraper
    
    class MyPlatformScraper(BaseScraper):
        def scrape_opportunities(self):
            # Fetch using base helper: self.fetch_url(url, use_jina=True)
            # Parse details and return structured list
            return []
    ```
2.  Register your scraper inside the execution array in **`scan.py`**.
3.  Add standard unit tests to verify the parser remains robust.

---

## 📬 Pull Request (PR) Checklist

1.  Create a feature branch from `main`:
    ```bash
    git checkout -b feat/my-new-scraper
    ```
2.  Follow the **Conventional Commits** format (e.g. `feat(scrapers): add new target`, `fix(db): resolve thread locks`).
3.  Ensure your code changes pass basic linting and local tests.
4.  Submit a Pull Request on GitHub and describe your additions.

We review PRs within 48 hours! Let's build the best open-source opportunity scout together. 🚀
