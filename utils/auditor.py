import os
import re
from database.connection import get_connection

# Comprehensive dictionary of technical skills to track
TECH_SKILLS = [
    # Languages
    "python", "javascript", "typescript", "golang", "go", "rust", "c++", "c#", "java", "kotlin", "swift", "php", "ruby", "sql", "bash", "shell",
    # Frontend
    "react", "vue", "angular", "next.js", "nextjs", "nuxt", "svelte", "tailwind", "html", "css", "sass", "bootstrap",
    # Backend & Frameworks
    "node.js", "nodejs", "express", "fastapi", "django", "flask", "spring boot", "laravel", "rails", "asp.net",
    # Databases & Caching
    "postgresql", "postgres", "mysql", "sqlite", "mongodb", "redis", "elasticsearch", "cassandra", "dynamodb", "mariadb",
    # DevOps, Cloud & Containers
    "docker", "kubernetes", "k8s", "aws", "gcp", "azure", "terraform", "ansible", "jenkins", "git", "github", "gitlab", "ci/cd", "linux", "nginx",
    # Data Science, ML & AI
    "pytorch", "tensorflow", "keras", "scikit-learn", "numpy", "pandas", "opencv", "llm", "langchain", "llama", "huggingface"
]

# Normalization map for fuzzy match variations
NORMALIZATION_MAP = {
    "golang": "go",
    "postgres": "postgresql",
    "nextjs": "next.js",
    "nodejs": "node.js",
    "k8s": "kubernetes"
}

def normalize_skill(skill):
    return NORMALIZATION_MAP.get(skill.lower(), skill.lower())

def extract_skills(text):
    if not text:
        return set()
    found = set()
    text_lower = text.lower()
    for skill in TECH_SKILLS:
        # Match using boundary rules helper (special handling for c++, c#, next.js)
        if not re.match(r'^[a-zA-Z0-9]+$', skill):
            pattern = r'(?<![a-zA-Z0-9])' + re.escape(skill) + r'(?![a-zA-Z0-9])'
        else:
            pattern = r'\b' + re.escape(skill) + r'\b'
            
        if re.search(pattern, text_lower):
            found.add(normalize_skill(skill))
    return found

RESUME_TEMPLATE = """# Oppy Resume Skills Profile
# Replace the placeholders below with your own details, then run `oppy --audit`.
# Everything is parsed locally; nothing leaves your machine.
# Keywords are matched case-insensitively, so a plain comma-separated list works.

Name:
Email:
Title:

[Languages]
Python, JavaScript, SQL

[Frameworks & Tools]
React, Git, Docker

[Databases]
PostgreSQL, SQLite

[Cloud & AI]
AWS
"""


def ensure_default_resume(resume_path):
    """Create the skills profile on first use. Returns True if it was created."""
    if os.path.exists(resume_path):
        return False
    try:
        parent = os.path.dirname(resume_path)
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(resume_path, "w", encoding="utf-8") as f:
            f.write(RESUME_TEMPLATE)
        return True
    except Exception:
        return False

def audit_opportunities(resume_path):
    ensure_default_resume(resume_path)
    
    try:
        with open(resume_path, "r", encoding="utf-8") as f:
            resume_text = f.read()
    except Exception:
        return [], set()
        
    resume_skills = extract_skills(resume_text)
    if not resume_skills:
        return [], set()
        
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT opportunity_type, platform, title, company, stipend_or_prize, deadline, opportunity_url
        FROM opportunities
        ORDER BY discovered_at DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    
    audited = []
    for opp_type, platform, title, company, stipend, deadline, url in rows:
        job_context = f"{title} {company} {stipend}"
        required_skills = extract_skills(job_context)
        
        if not required_skills:
            match_score = 50  # Neutral score if no specific stack matches detected
            matched_skills = set()
            missing_skills = set()
        else:
            matched_skills = required_skills.intersection(resume_skills)
            missing_skills = required_skills.difference(resume_skills)
            match_score = int((len(matched_skills) / len(required_skills)) * 100)
            
        audited.append({
            'opp_type': opp_type,
            'platform': platform,
            'title': title,
            'company': company,
            'stipend': stipend,
            'deadline': deadline,
            'url': url,
            'match_score': match_score,
            'matched_skills': matched_skills,
            'missing_skills': missing_skills,
            'required_skills': required_skills
        })
        
    audited.sort(key=lambda x: x['match_score'], reverse=True)
    return audited, resume_skills
