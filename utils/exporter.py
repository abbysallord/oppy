import csv
import io
import os
from datetime import datetime

from database.connection import get_connection
from utils.config import load_config

SECTIONS = [
    ("hackathon", "Top Active Hackathons"),
    ("internship", "Paid Remote Internships"),
    ("job", "Remote Tech Jobs"),
]

FORMATS = ("md", "pdf", "csv")


def fetch_sections(limit=None):
    """Read the ledger grouped by opportunity type, newest first.

    ``limit`` caps rows per section; None exports everything.
    """
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT title, company, platform, opportunity_url, stipend_or_prize, deadline
        FROM opportunities
        WHERE opportunity_type = ?
        ORDER BY discovered_at DESC
    """
    params_suffix = ""
    if limit is not None:
        params_suffix = " LIMIT ?"

    sections = []
    for opp_type, heading in SECTIONS:
        params = [opp_type] + ([limit] if limit is not None else [])
        cursor.execute(query + params_suffix, params)
        sections.append((opp_type, heading, cursor.fetchall()))

    conn.close()
    return sections


def _timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# --------------------------------------------------------------------------
# Renderers
# --------------------------------------------------------------------------

def render_markdown(sections):
    lines = [
        "# Live Opportunities Dashboard",
        f"*Last Scan Execution: {_timestamp()}*",
        "\n*This dashboard aggregates paid/prize-pool hackathons, paid virtual internships, and remote tech jobs. Updated automatically.*",
        "\n---\n",
    ]

    headers = {
        "hackathon": "| Hackathon Title | Host | Platform | Prize Pool | Deadline | Apply Link |",
        "internship": "| Position Title | Company / Host | Platform | Stipend / Salary | Deadline | Apply Link |",
        "job": "| Job Title | Company | Platform / Feed | Salary / Comp | Deadline | Apply Link |",
    }

    for opp_type, heading, rows in sections:
        lines.append(f"## {heading}")
        if not rows:
            lines.append("*Nothing discovered yet. Run a sync to populate.*")
        else:
            lines.append(headers[opp_type])
            lines.append("| :--- | :--- | :---: | :--- | :--- | :--- |")
            for title, company, platform, url, reward, deadline in rows:
                cells = [
                    f"**{_md_cell(title)}**",
                    _md_cell(company) or "Unknown",
                    f"`{platform.upper()}`",
                    _md_cell(reward) or "N/A",
                    f"*{_md_cell(deadline) or 'Open'}*",
                    f"[Apply ↗]({url})",
                ]
                lines.append("| " + " | ".join(cells) + " |")
        lines.append("\n---\n")

    lines.append("*Note: Opportunities are uniquely indexed in the database to prevent duplicate entries.*")
    return "\n".join(lines)


def _md_cell(value):
    return (value or "").replace("|", "\\|").strip()


def render_csv(sections):
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["type", "title", "company", "platform", "reward", "deadline", "url"])
    for opp_type, _heading, rows in sections:
        for title, company, platform, url, reward, deadline in rows:
            writer.writerow([opp_type, title, company, platform, reward, deadline, url])
    return buffer.getvalue()


def render_pdf_lines(sections):
    """Build (text, bold) pairs for utils.pdf, which lays out monospaced text."""
    lines = [
        ("OPPY - LIVE OPPORTUNITIES DASHBOARD", True),
        (f"Generated {_timestamp()}", False),
        ("", False),
    ]

    for _opp_type, heading, rows in sections:
        lines.append((f"{heading.upper()} ({len(rows)})", True))
        lines.append(("-" * 88, False))
        if not rows:
            lines.append(("  Nothing discovered yet. Run a sync to populate.", False))
        for title, company, platform, url, reward, deadline in rows:
            lines.append((f"  {title.strip()}", True))
            meta = " | ".join(part for part in [
                (company or "Unknown").strip(),
                platform.upper(),
                (reward or "N/A").strip(),
                (deadline or "Open").strip(),
            ] if part)
            lines.append((f"    {meta}", False))
            lines.append((f"    {url}", False))
            lines.append(("", False))
        lines.append(("", False))

    return lines


# --------------------------------------------------------------------------
# Export
# --------------------------------------------------------------------------

def export(fmt, path, limit=None):
    """Write the ledger to ``path`` in ``fmt``. Returns the path written."""
    if fmt not in FORMATS:
        raise ValueError(f"Unsupported format '{fmt}'. Choose one of: {', '.join(FORMATS)}")

    path = os.path.abspath(os.path.expanduser(path))
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)

    sections = fetch_sections(limit=limit)

    if fmt == "pdf":
        from utils.pdf import write_pdf
        write_pdf(path, render_pdf_lines(sections), title="Oppy Opportunities")
    else:
        content = render_markdown(sections) if fmt == "md" else render_csv(sections)
        with open(path, "w", encoding="utf-8", newline="") as f:
            f.write(content)

    return path


def generate_markdown(quiet=False, path=None):
    """Write the Markdown dashboard to the configured export path.

    Used by --headless and the CLI; the TUI now exports on request instead.
    """
    config = load_config()
    target = path or os.environ.get("OPPY_EXPORT_PATH", config.get("export_path"))

    # Fall back to the working directory if the configured folder is missing.
    parent = os.path.dirname(target)
    if parent and not os.path.exists(parent):
        target = os.path.join(os.getcwd(), "Opportunities.md")
        if not quiet:
            print(f"Target folder {parent} not found. Exporting locally to: {target}")

    written = export("md", target)
    if not quiet:
        print(f"Markdown dashboard generated successfully: {written}")
    return written


if __name__ == "__main__":
    generate_markdown()
