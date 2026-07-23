# 🛰️ Oppy (Opportunity Scout)

[![NPM Version](https://img.shields.io/npm/v/oppy-cli.svg)](https://www.npmjs.com/package/oppy-cli)
[![License](https://img.shields.io/npm/l/oppy-cli.svg)](https://github.com/dshenoyh/oppy/blob/main/LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/dshenoyh/oppy/blob/main/CONTRIBUTING.md)

**Oppy** is a zero-config, automated command-line utility to scrape, filter, and aggregate remote paid internships and hackathons from **Unstop**, **Devpost**, **RemoteOK**, and **WeWorkRemotely**. It saves results directly to a local SQLite database and generates a clean, links-enabled Markdown dashboard in your local directory or Obsidian vault.

```
       _____  _____   _____                _ 
      |  _  ||  _  | |  _  |              | |
      | | | || | | | | | | | ___  ___  ___| |_ 
      | | | || | | | | | | |/ __|/ _ \/ _ \ __|
      \ \_/ /\ \_/ / \ \_/ /\__ \  __/  __/ |_ 
       \___/  \___/   \___/ |___/\___|\___|\__|
```

---

## ⚡ Quick Start (Zero Installation)

Run the scanner instantly anywhere on your terminal using Node.js:

```bash
npx oppy-cli
```

*Note: Oppy requires Python 3.8+ to execute its crawlers. If python dependencies like `feedparser` are missing, the runner will automatically attempt to install them on first execution.*

---

## ✨ Features

*   **Paid & Virtual Focus**: Automatically filters internships for paid stipends/salaries and remote availability. Filters hackathons by active, open submission windows with cash prizes.
*   **Persistent & Deduplicated**: Integrates a local SQLite database in Write-Ahead Logging (WAL) mode. Opportunities are uniquely indexed by URL; subsequent runs only fetch and save *new* items.
*   **Obsidian / Second Brain Ready**: Auto-generates a clean Markdown dashboard (`Opportunities.md`) containing organized tables and direct application links.
*   **Jina Reader Proxy Bypass**: Crawls dynamic client-side lists (like Unstop and Devpost) by routing requests through Jina Reader (`r.jina.ai`) to bypass Cloudflare bot blocks.
*   **Modular Crawler Architecture**: Each platform is parsed via its own isolated crawler module, making it easy to add new job boards and competitive sites.

---

## 🏗️ Architecture

Oppy is built in Python for robust parsing and wrapped in a Node.js CLI script for zero-config distribution:

```
oppy/
├── bin/
│   └── cli.js            # Node CLI wrapper (auto-installs requirements, spawns python)
├── database/
│   └── connection.py    # Database connection & schema setup (WAL mode)
├── scrapers/
│   ├── base.py          # Base scraper (user-agents & Jina reader proxies)
│   ├── unstop.py        # Unstop crawler (block-splitting markdown parser)
│   ├── devpost.py       # Devpost crawler (subdomain matching regex parser)
│   ├── remoteok.py      # RemoteOK JSON feed crawler
│   └── weworkremotely.py# WeWorkRemotely RSS feed crawler
├── utils/
│   └── exporter.py      # Obsidian/Local Markdown table generator
├── LICENSE
├── package.json
└── scan.py              # Main orchestrator (crawler execution loop)
```

---

## ⚙️ Customization

Customize Oppy paths by declaring environment variables before execution:

*   **`OPPY_EXPORT_PATH`**: The destination path for the Markdown dashboard. 
    *   *Default*: Fallback to `~/Documents/obsidian/Brain/00 Inbox/Opportunities.md` if the directory exists, otherwise outputs `Opportunities.md` to your current working directory.
*   **`OPPY_DB_PATH`**: Location of the SQLite database.
    *   *Default*: `~/.config/oppy/opportunities.db`.

```bash
# Example: Export to a custom path and use a local database
export OPPY_EXPORT_PATH="/path/to/my/folder/Jobs.md"
npx oppy-cli
```

---

## 🤝 Contributing

We welcome community contributions to expand Oppy! Please read our **[CONTRIBUTING.md](file:///home/dhanush/Projects/OpenSource/oppy/CONTRIBUTING.md)** guidelines to get started.

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for details.
