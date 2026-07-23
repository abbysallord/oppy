import os
from datetime import datetime
from pathlib import Path
from database.connection import get_connection
from utils.config import load_config

config = load_config()
DEFAULT_OBSIDIAN = config.get("export_path")
# Support environment override for customized dashboard export paths using Oppy namespace
OBSIDIAN_PATH = os.environ.get("OPPY_EXPORT_PATH", DEFAULT_OBSIDIAN)

def generate_markdown():
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. Fetch Hackathons (Devpost + Unstop)
    cursor.execute("""
        SELECT title, company, platform, opportunity_url, stipend_or_prize, deadline, discovered_at
        FROM opportunities
        WHERE opportunity_type = 'hackathon'
        ORDER BY discovered_at DESC
        LIMIT 25
    """)
    hackathons = cursor.fetchall()
    
    # 2. Fetch Internships (Unstop + RemoteOk + WeWorkRemotely)
    cursor.execute("""
        SELECT title, company, platform, opportunity_url, stipend_or_prize, deadline, discovered_at
        FROM opportunities
        WHERE opportunity_type = 'internship'
        ORDER BY discovered_at DESC
        LIMIT 25
    """)
    internships = cursor.fetchall()
    
    conn.close()
    
    # Compile Markdown Document
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    md_lines = []
    md_lines.append("# Live Opportunities Dashboard")
    md_lines.append(f"*Last Scan Execution: {now_str}*")
    md_lines.append("\n*This dashboard aggregates paid/prize-pool hackathons and paid virtual internships. Updated automatically.*")
    md_lines.append("\n---\n")
    
    # Hackathons Section
    md_lines.append("## Top Active Hackathons")
    if len(hackathons) == 0:
        md_lines.append("*No open hackathons discovered yet. Run scanner to populate.*")
    else:
        md_lines.append("| Hackathon Title | Platform | Prize Pool / Stipend | Deadline | Apply Link |")
        md_lines.append("| :--- | :---: | :--- | :--- | :--- |")
        for title, company, platform, url, prize, deadline, _ in hackathons:
            clean_title = title.replace("|", "\\|")
            clean_prize = prize.replace("|", "\\|") if prize else "N/A"
            md_lines.append(f"| **{clean_title}** | `{platform.upper()}` | {clean_prize} | *{deadline}* | [Apply ↗]({url}) |")
            
    md_lines.append("\n---\n")
    
    # Internships Section
    md_lines.append("## Paid Remote Internships")
    if len(internships) == 0:
        md_lines.append("*No internships discovered yet. Run scanner to populate.*")
    else:
        md_lines.append("| Position Title | Company / Host | Platform | Stipend / Salary | Link |")
        md_lines.append("| :--- | :--- | :---: | :--- | :--- |")
        for title, company, platform, url, stipend, deadline, _ in internships:
            clean_title = title.replace("|", "\\|")
            clean_company = company.replace("|", "\\|") if company else "Unknown"
            clean_stipend = stipend.replace("|", "\\|") if stipend else "Paid"
            md_lines.append(f"| **{clean_title}** | {clean_company} | `{platform.upper()}` | {clean_stipend} | [Apply ↗]({url}) |")
            
    md_lines.append("\n---\n")
    md_lines.append("*Note: Opportunities are uniquely indexed in the database to prevent duplicate entries.*")
    
    markdown_content = "\n".join(md_lines)
    
    # Resolve write path safely
    global OBSIDIAN_PATH
    parent_dir = os.path.dirname(OBSIDIAN_PATH)
    if parent_dir and not os.path.exists(parent_dir):
        OBSIDIAN_PATH = os.path.join(os.getcwd(), "Opportunities.md")
        print(f"Target folder {parent_dir} not found. Exporting locally to: {OBSIDIAN_PATH}")
    else:
        os.makedirs(parent_dir, exist_ok=True)
    
    with open(OBSIDIAN_PATH, "w", encoding="utf-8") as f:
        f.write(markdown_content)
        
    print(f"Markdown dashboard generated successfully: {OBSIDIAN_PATH}")

if __name__ == "__main__":
    generate_markdown()
