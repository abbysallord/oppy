# Oppy (Opportunity Scout)

[![NPM Version](https://img.shields.io/npm/v/oppy-cli.svg)](https://www.npmjs.com/package/oppy-cli)
[![License](https://img.shields.io/npm/l/oppy-cli.svg)](https://github.com/abbysallord/oppy/blob/main/LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/abbysallord/oppy/blob/main/CONTRIBUTING.md)

Oppy is an automated, zero-config command-line utility to scrape, filter, and track active paid remote internships and cash-prize hackathons from Unstop, Devpost, RemoteOK, and WeWorkRemotely. It caches listings in a local SQLite database and exports a clean, links-enabled Markdown dashboard to your directory or Obsidian vault.

```
  ____  _____  _____ __     __
 / __ \|  __ \|  __ \\ \   / /
| |  | | |__) | |__) |\ \_/ / 
| |  | |  ___/|  ___/  \   /  
| |__| | |    | |       | |   
 \____/|_|    |_|       |_|   
```

---

## Quick Start (Zero Installation)

Run the interactive dashboard anywhere on your terminal using Node.js:

```bash
npx oppy-cli
```

*Oppy requires Python 3.8+ on the host system. Missing Python dependencies (such as `feedparser` and `rich`) are automatically verified and installed on first run.*

---

## Why Oppy? (Competitor Comparison)

While there are static lists and standalone scripts online, they either require manual search filtering, lack persistent storage, or run as paid cloud scrapers. Oppy was built to serve as a local-first opportunity aggregator that feeds directly into your personal knowledge base (Obsidian).

| Feature | Oppy | Static Lists (PittCSC / Simplify) | Apify Scrapers | General Job Scrapers |
| :--- | :---: | :---: | :---: | :---: |
| **Paid Remote Internships** | Yes | Yes (mostly static) | Yes | Yes (often single platform) |
| **Active Hackathons** | Yes | No | Yes (prizes only) | No |
| **SQLite WAL DB Cache** | Yes | No | No | No |
| **Obsidian Markdown Export** | Yes | No | No | No |
| **Interactive TUI Dashboard** | Yes | No | No | No |
| **Zero-Config Execution (`npx`)**| Yes | No | No | No |

---

## Features

* **Paid & Virtual Focus**: Filters internships specifically for remote availability and paid stipends, and hackathons for active submission windows with cash prizes.
* **Persistent & Deduplicated**: Utilizes a local SQLite database in Write-Ahead Logging (WAL) mode. Opportunities are uniquely indexed by URL to prevent duplicates.
* **Interactive Terminal Console**: Run synchronization tasks, query and filter the ledger database offline, and modify filter toggles from a native text menu.
* **Obsidian Ready**: Compiles opportunities directly into a clean Markdown dashboard (`Opportunities.md`) with direct application links.
* **Jina Reader Routing**: Routes dynamic listing queries through Jina Reader (`r.jina.ai`) to bypass Cloudflare scraping protection.

---

## Architecture

Oppy is built in Python and distributed via an executable Node.js CLI script:

```
oppy/
├── bin/
│   └── cli.js            # Node CLI wrapper (spawns Python, installs requirements)
├── database/
│   └── connection.py    # Database schema & connection setup (WAL mode)
├── scrapers/
│   ├── base.py          # Crawler base helper (User-Agents, Jina proxy)
│   ├── unstop.py        # Unstop crawler (block-splitting markdown parser)
│   ├── devpost.py       # Devpost crawler (subdomain regex parser)
│   ├── remoteok.py      # RemoteOK JSON feed parser
│   └── weworkremotely.py# WeWorkRemotely RSS feed crawler
├── utils/
│   ├── config.py        # Global settings manager (JSON persistence)
│   ├── exporter.py      # Markdown table generator
│   └── tui.py           # Rich terminal user interface
├── LICENSE
├── package.json
└── scan.py              # Execution mode entry point (TUI / Headless)
```

---

## Configuration

Custom environment variables can be declared to override settings:

* **`OPPY_EXPORT_PATH`**: Dashboard export file destination.
  * *Default*: `~/Documents/obsidian/Brain/00 Inbox/Opportunities.md` (falls back to local `Opportunities.md` if directories are missing).
* **`OPPY_DB_PATH`**: SQLite database location.
  * *Default*: `~/.config/oppy/opportunities.db`.

---

## Contributing

We welcome pull requests to expand Oppy! Read our **[CONTRIBUTING.md](file:///home/dhanush/Projects/OpenSource/oppy/CONTRIBUTING.md)** guidelines to get started.

---

## License

Distributed under the MIT License. See `LICENSE` for details.
