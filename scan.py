#!/usr/bin/env python3
import argparse
import os
import sys

from database.connection import get_connection, init_db, upsert_opportunity
from scrapers.unstop import UnstopScraper
from scrapers.devpost import DevpostScraper
from scrapers.remoteok import RemoteOkScraper
from scrapers.weworkremotely import WeWorkRemotelyScraper
from scrapers.custom_rss import CustomRSSScraper
from utils.exporter import generate_markdown
from utils.tui import tui_main

EPILOG = """\
examples:
  oppy                        launch the interactive dashboard
  oppy --search "engineer"    query the local cache and print a table
  oppy --audit                rank cached listings against your resume
  oppy --headless             silent sync, ideal for cron and systemd timers
  oppy --export pdf           write the cached ledger to ./Opportunities.pdf
  oppy --export csv --out ~/Desktop/jobs.csv
"""


def build_scrapers():
    return [
        (UnstopScraper(), "scrape_internships", "internship"),
        (UnstopScraper(), "scrape_hackathons", "hackathon"),
        (DevpostScraper(), "scrape_hackathons", "hackathon"),
        (RemoteOkScraper(), "scrape_internships", "internship"),
        (WeWorkRemotelyScraper(), "scrape_internships", "internship"),
        (CustomRSSScraper(), "scrape_custom_feeds", "job"),
    ]


def get_version():
    try:
        from importlib.metadata import version
        return version("oppy-cli")
    except Exception:
        return "source checkout"


def cmd_search(search_query):
    init_db()
    conn = get_connection()
    cursor = conn.cursor()

    # Split terms for case-insensitive search
    words = [w.lower().rstrip('s') for w in search_query.split() if w]
    conditions = []
    params = []
    for word in words:
        conditions.append("(LOWER(title) LIKE ? OR LOWER(company) LIKE ? OR LOWER(platform) LIKE ?)")
        params.extend([f"%{word}%", f"%{word}%", f"%{word}%"])

    where_clause = " AND ".join(conditions) if conditions else "1"

    cursor.execute(f"""
        SELECT opportunity_type, platform, title, company, stipend_or_prize, deadline, opportunity_url
        FROM opportunities
        WHERE {where_clause}
        ORDER BY discovered_at DESC
        LIMIT 15
    """, params)
    rows = cursor.fetchall()
    conn.close()

    from rich.console import Console
    from rich.table import Table
    console = Console()

    if not rows:
        console.print(f"\n[bold red]No cached opportunities found matching query: '{search_query}'[/bold red]\n")
        return 0

    table = Table(title=f"Oppy Search Results (matching '{search_query}')", expand=True)
    table.add_column("Type", justify="center", style="cyan")
    table.add_column("Platform", justify="center", style="green")
    table.add_column("Opportunity & Company", justify="left")
    table.add_column("Compensation / Prize", justify="left", style="yellow")
    table.add_column("Deadline", justify="left", style="blue")

    for opp_type, platform, title, company, stipend, deadline, url in rows:
        display_cell = f"[bold white]{title}[/bold white]\n[dim]{company}[/dim]\n[blue]{url}[/blue]"
        table.add_row(
            opp_type.upper(),
            platform.upper(),
            display_cell,
            stipend if stipend else "Paid",
            deadline if deadline else "Open"
        )

    console.print(table)
    return 0


def cmd_edit():
    import subprocess
    from utils.config import load_config
    from utils.auditor import ensure_default_resume

    resume_path = load_config().get("resume_path")
    if ensure_default_resume(resume_path):
        print(f"Created a new skills profile at: {resume_path}")

    print(f"Opening resume for editing: {resume_path}")
    try:
        if sys.platform.startswith('win'):
            os.startfile(resume_path)
        elif sys.platform.startswith('darwin'):
            subprocess.run(['open', resume_path])
        else:
            editor = os.environ.get('EDITOR')
            if editor:
                import shlex
                subprocess.run(shlex.split(editor) + [resume_path])
            else:
                try:
                    subprocess.run(['xdg-open', resume_path])
                except FileNotFoundError:
                    for default_editor in ['nano', 'vi', 'vim']:
                        try:
                            subprocess.run([default_editor, resume_path])
                            break
                        except FileNotFoundError:
                            continue
    except Exception as e:
        print(f"Failed to open editor: {e}")
        print(f"Please open and edit the file manually at: {resume_path}")
        return 1
    return 0


def cmd_audit():
    from utils.config import load_config
    from utils.auditor import audit_opportunities

    resume_path = load_config().get("resume_path")
    audited, resume_skills = audit_opportunities(resume_path)

    from rich.console import Console
    from rich.table import Table
    console = Console()

    if not resume_skills:
        console.print(f"\n[bold red]No resume skills detected. Add your skills at: '{resume_path}' (run `oppy --edit`)[/bold red]\n")
        return 1

    if not audited:
        console.print("\n[bold red]No cached opportunities found in the database. Run sync first to populate.[/bold red]\n")
        return 0

    console.print(f"\n[bold #00ff85]Analyzed {len(audited)} opportunities against your resume ({resume_path})[/bold #00ff85]")
    console.print(f"[bold #1e90ff]Detected Resume Skills:[/bold #1e90ff] {', '.join(sorted(resume_skills))}\n")

    table = Table(title="Oppy Resume Audit Rankings", expand=True)
    table.add_column("Fit", justify="center", style="bold #00ff85")
    table.add_column("Type & Platform", justify="center", style="#1e90ff")
    table.add_column("Opportunity & Company", justify="left")
    table.add_column("Matching Skills", justify="left", style="#00ff85")
    table.add_column("Missing Skills", justify="left", style="#ef4444")

    # Display top 15 matches
    for item in audited[:15]:
        matched_str = ", ".join(sorted(item['matched_skills'])) if item['matched_skills'] else "[dim]None[/dim]"
        missing_str = ", ".join(sorted(item['missing_skills'])) if item['missing_skills'] else "[dim]None[/dim]"
        display_cell = f"[bold white]{item['title']}[/bold white]\n[dim]{item['company']}[/dim]\n[blue]{item['url']}[/blue]"

        table.add_row(
            f"{item['match_score']}%",
            f"{item['opp_type'].upper()}\n`{item['platform'].upper()}`",
            display_cell,
            matched_str,
            missing_str
        )

    console.print(table)
    return 0


def cmd_export(fmt, out_path):
    from utils.exporter import export

    init_db()
    destination = out_path or os.path.join(os.getcwd(), f"Opportunities.{fmt}")
    try:
        written = export(fmt, destination)
    except Exception as e:
        print(f"Export failed: {e}")
        return 1

    print(f"Exported ledger as {fmt.upper()}: {written} ({os.path.getsize(written):,} bytes)")
    return 0


def cmd_headless(scrapers):
    """Silent background scan, ideal for systemd timers and cron jobs."""
    from utils.config import load_config, record_sync

    print("Starting headless opportunities scan...")
    init_db()

    config = load_config()
    active_platforms = config.get("selected_platforms", ["unstop", "devpost", "remoteok", "weworkremotely"])

    conn = get_connection()
    cursor = conn.cursor()
    total_new = 0
    total_updated = 0
    failed = 0

    for scraper_instance, method_name, opp_type in scrapers:
        platform_name = scraper_instance.__class__.__name__.replace("Scraper", "").lower()
        if platform_name not in active_platforms and platform_name != "customrss":
            continue

        print(f"Syncing {platform_name} ({opp_type})...")
        try:
            results = getattr(scraper_instance, method_name)()

            if results is None:
                print(f"  Failed: platform offline or request timed out.")
                failed += 1
                continue

            new_count = 0
            updated_count = 0
            rejected = 0
            for item in results:
                try:
                    outcome = upsert_opportunity(cursor, item)
                    if outcome == "new":
                        new_count += 1
                    elif outcome == "updated":
                        updated_count += 1
                except Exception as e:
                    rejected += 1
                    if rejected == 1:
                        print(f"  Warning: rejected a listing: {e}")

            conn.commit()
            total_new += new_count
            total_updated += updated_count
            print(f"  +{new_count} new, {updated_count} refreshed" + (f", {rejected} rejected" if rejected else ""))

        except Exception as e:
            failed += 1
            print(f"  Error syncing {platform_name}: {e}")
        finally:
            for note in scraper_instance.notes:
                print(f"  note: {note}")
            scraper_instance.notes.clear()

    conn.close()
    record_sync()
    print(f"Scan complete. {total_new} new, {total_updated} refreshed, {failed} platform(s) failed.")
    generate_markdown()
    return 1 if failed and not total_new else 0


def main():
    parser = argparse.ArgumentParser(
        prog="oppy",
        description="Scrape, filter and track paid remote internships and cash-prize hackathons.",
        epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("-s", "--search", metavar="QUERY",
                        help="search the local cache and print matches")
    parser.add_argument("-a", "--audit", action="store_true",
                        help="rank cached opportunities against your resume skills")
    parser.add_argument("-e", "--edit", action="store_true",
                        help="open your resume skills profile in an editor")
    parser.add_argument("-H", "--headless", action="store_true",
                        help="run a silent sync without the interactive dashboard")
    parser.add_argument("--export", metavar="FORMAT", choices=("md", "pdf", "csv"),
                        help="export the cached ledger as md, pdf or csv, then exit")
    parser.add_argument("--out", metavar="PATH",
                        help="destination for --export (default: ./Opportunities.<format>)")
    parser.add_argument("--version", action="version", version=f"oppy {get_version()}")

    args = parser.parse_args()

    if args.export:
        sys.exit(cmd_export(args.export, args.out))
    if args.search is not None:
        sys.exit(cmd_search(args.search))
    if args.edit:
        sys.exit(cmd_edit())
    if args.audit:
        sys.exit(cmd_audit())

    scrapers = build_scrapers()
    if args.headless:
        sys.exit(cmd_headless(scrapers))

    tui_main(scrapers)


if __name__ == "__main__":
    main()
