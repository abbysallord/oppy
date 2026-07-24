# Oppy (Opportunity Scout)

[![NPM Version](https://img.shields.io/npm/v/@dshenoyh/oppy-cli.svg)](https://www.npmjs.com/package/@dshenoyh/oppy-cli)
[![PyPI Version](https://img.shields.io/pypi/v/oppy-cli.svg)](https://pypi.org/project/oppy-cli/)
[![License](https://img.shields.io/github/license/abbysallord/oppy.svg)](https://github.com/abbysallord/oppy/blob/main/LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/abbysallord/oppy/blob/main/CONTRIBUTING.md)

Oppy is an automated, zero-config command-line utility to scrape, filter, and track active paid remote internships and cash-prize hackathons from Unstop, Devpost, RemoteOK, and WeWorkRemotely. It caches listings in a local SQLite database and exports a clean, links-enabled Markdown dashboard to your directory or Obsidian vault.

```text
 ██████╗ ██████╗ ██████╗ ██╗   ██╗
██╔═══██╗██╔══██╗██╔══██╗╚██╗ ██╔╝
██║   ██║██████╔╝██████╔╝ ╚████╔╝ 
██║   ██║██╔═══╝ ██╔═══╝   ╚██╔╝  
╚██████╔╝██║     ██║        ██║   
 ╚═════╝ ╚═╝     ╚═╝        ╚═╝   
```

---

## Quick Start (Zero Installation)

Run the interactive dashboard anywhere on your terminal using Node.js:

```bash
npx @dshenoyh/oppy-cli
```

*Oppy requires Python 3.8+ on the host system. Missing Python dependencies (such as `feedparser` and `rich`) are automatically verified and installed on first run.*

---

## Installation

### Node.js (Recommended)
Install globally to trigger using the direct `oppy` command:
```bash
npm install -g @dshenoyh/oppy-cli
oppy
```

### Python / Pip
Alternatively, install directly into your Python environment:
```bash
pip install oppy-cli
oppy
```

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

## Keyboard Controls (TUI)

*   **Main Menu**: Press keys `[1-5]` to trigger options immediately (no Enter key required).
*   **Ledger Paging**: Use **Left Arrow** / **P** to page backward, and **Right Arrow** / **N** to page forward.
*   **Ledger Filters**: Press **T** to cycle results between `ALL`, `INTERNSHIP`, `HACKATHON`, and `JOB` filters dynamically.
*   **Settings Toggles**: Press `Y` or `N` to toggle active settings instantly.
*   **Text Queries**: Binds standard GNU `readline` for smooth character editing, arrow cursor keys, and backspaces inside text fields.

---

## CLI Search Command

You can search and filter the database cache directly from your standard shell prompt without launching the full TUI dashboard:

```bash
oppy --search "engineer"
# or
oppy -s "GitLab"
```

Oppy will query the local SQLite database and display a clean, formatted table of matches directly to standard output.

---

## macOS & SSL Support

Python installations on macOS frequently raise `SSL: CERTIFICATE_VERIFY_FAILED` errors because they do not utilize the operating system's root SSL certificate bundle. 

Oppy features a native fallback that overrides the default HTTPS verification context when accessing public listings. **No certificate configuration steps or shell commands are needed on macOS.**

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
│   ├── base.py          # Crawler base helper (User-Agents, SSL overrides)
│   ├── unstop.py        # Unstop crawler (block-splitting markdown parser)
│   ├── devpost.py       # Devpost crawler (subdomain regex parser)
│   ├── remoteok.py      # RemoteOK JSON feed parser
│   ├── weworkremotely.py# WeWorkRemotely RSS feed crawler
│   └── custom_rss.py    # Custom RSS feed crawler (internships/hackathons/jobs matcher)
├── utils/
│   ├── config.py        # Global settings manager (JSON persistence)
│   ├── exporter.py      # Markdown table generator
│   └── tui.py           # Rich terminal user interface
├── pyproject.toml        # Python packaging config
├── LICENSE
├── package.json
└── scan.py              # Execution mode entry point (TUI / Headless)
```

---

## Configuration

Custom environment variables can be declared to override settings:

*   **`OPPY_EXPORT_PATH`**: Dashboard export file destination.
    *   *Default*: `~/Documents/obsidian/Brain/00 Inbox/Opportunities.md` (falls back to local `Opportunities.md` if directories are missing).
*   **`OPPY_DB_PATH`**: SQLite database location.
    *   *Default*: `~/.config/oppy/opportunities.db`.

---

## Contributing

We welcome pull requests to expand Oppy! Read our **[CONTRIBUTING.md](file:///home/dhanush/Projects/OpenSource/oppy/CONTRIBUTING.md)** guidelines to get started.

---

## License

Distributed under the MIT License. See `LICENSE` for details.
