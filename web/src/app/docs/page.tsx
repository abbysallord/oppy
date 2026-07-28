import Link from "next/link";
import styles from "./page.module.css";

export default function Docs() {
  return (
    <div className={styles.wrapper}>
      {/* Navbar */}
      <header className={styles.navbar}>
        <div className={`${styles.container} ${styles.navContainer}`}>
          <div className={styles.brand}>
            <Link href="/" className={styles.logoText}>
              Oppy
            </Link>
            <span className={styles.logoVersion}>v1.0.6</span>
          </div>
          <nav className={styles.navLinks}>
            <Link href="/" className={styles.navLink}>
              Home
            </Link>
            <a
              href="https://github.com/abbysallord/oppy"
              target="_blank"
              rel="noopener noreferrer"
              className={styles.navLink}
            >
              GitHub
            </a>
          </nav>
        </div>
      </header>

      {/* Docs Layout */}
      <div className={styles.layout}>
        {/* Sidebar */}
        <aside className={styles.sidebar}>
          <h3 className={styles.sidebarTitle}>Navigation</h3>
          <nav className={styles.sidebarNav}>
            <a href="#introduction" className={styles.sidebarLink}>
              Introduction
            </a>
            <a href="#installation" className={styles.sidebarLink}>
              Installation
            </a>
            <a href="#commands" className={styles.sidebarLink}>
              CLI Commands
            </a>
            <a href="#configuration" className={styles.sidebarLink}>
              Configuration
            </a>
            <a href="#resume-auditor" className={styles.sidebarLink}>
              Resume Auditor
            </a>
          </nav>
        </aside>

        {/* Content */}
        <main className={styles.content}>
          <section id="introduction" className={styles.section}>
            <h1 className={styles.title}>Documentation</h1>
            <p className={styles.paragraph}>
              Oppy is an automated command-line utility to scrape, cache, filter,
              and track active paid remote internships and cash-prize hackathons.
              It caches listings in a local SQLite database and exports them
              directly to your Obsidian vault.
            </p>
          </section>

          <section id="installation" className={styles.section}>
            <h2 className={styles.sectionTitle}>Installation</h2>
            <p className={styles.paragraph}>
              You can run Oppy instantly using Node.js without compiling or
              installing Python dependencies manually:
            </p>
            <pre className={styles.code}>npx @dshenoyh/oppy-cli</pre>
            <p className={styles.paragraph}>
              Alternatively, install it globally on your system:
            </p>
            <pre className={styles.code}>
{`# Global Node install (Recommended)
npm install -g @dshenoyh/oppy-cli

# Pip Python environment install
pip install oppy-cli`}
            </pre>
          </section>

          <section id="commands" className={styles.section}>
            <h2 className={styles.sectionTitle}>CLI Commands</h2>
            <p className={styles.paragraph}>
              Query, synchronize, and examine opportunities directly from your
              standard shell terminal:
            </p>
            <table className={styles.table}>
              <thead>
                <tr>
                  <th className={styles.th}>Command</th>
                  <th className={styles.th}>Action</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td className={styles.td}>
                    <code>oppy</code>
                  </td>
                  <td className={styles.td}>
                    Launches the interactive terminal TUI dashboard panel.
                  </td>
                </tr>
                <tr>
                  <td className={styles.td}>
                    <code>oppy -s &quot;query&quot;</code>
                  </td>
                  <td className={styles.td}>
                    Search cached opportunities in console output without loading the TUI.
                  </td>
                </tr>
                <tr>
                  <td className={styles.td}>
                    <code>oppy -a</code>
                  </td>
                  <td className={styles.td}>
                    Audits your local resume file against opportunity listings to rank compatibility.
                  </td>
                </tr>
                <tr>
                  <td className={styles.td}>
                    <code>oppy -h</code> or <code>--headless</code>
                  </td>
                  <td className={styles.td}>
                    Trigger background crawler synchronization. Ideal for crontabs or systemd timers.
                  </td>
                </tr>
              </tbody>
            </table>
          </section>

          <section id="configuration" className={styles.section}>
            <h2 className={styles.sectionTitle}>Configuration</h2>
            <p className={styles.paragraph}>
              Oppy persists configuration schema locally in your home directory at:
              <br />
              <code className={styles.inlineCode}>
                ~/.config/oppy/config.json
              </code>
            </p>
            <pre className={styles.code}>
{`{
  "remote_only": true,
  "paid_only": true,
  "selected_platforms": ["unstop", "devpost", "remoteok", "weworkremotely"],
  "export_path": "/home/user/Obsidian/Vault/Opportunities.md",
  "resume_path": "/home/user/.config/oppy/resume.txt",
  "custom_rss_feeds": [
    "https://weworkremotely.com/categories/remote-full-stack-programming-jobs.rss"
  ]
}`}
            </pre>
          </section>

          <section id="resume-auditor" className={styles.section}>
            <h2 className={styles.sectionTitle}>Resume Auditor</h2>
            <p className={styles.paragraph}>
              Oppy features a local-first resume auditor. When running
              {" "}<code className={styles.inlineCode}>oppy --audit</code> for the first
              time, it initializes a template file at:
              <br />
              <code className={styles.inlineCode}>
                ~/.config/oppy/resume.txt
              </code>
            </p>
            <p className={styles.paragraph}>
              Open this file in any text editor and fill in your technical stack
              details (languages, libraries, frameworks). Oppy extracts your skills,
              cross-references them against active database opportunities, and renders
              a fit rating alongside missing prerequisites.
            </p>
          </section>
        </main>
      </div>

      {/* Footer */}
      <footer className={styles.footer}>
        <div className={styles.footerContainer}>
          <span className={styles.footerText}>
            &copy; {new Date().getFullYear()} Oppy. Open source under MIT.
          </span>
          <div className={styles.footerLinks}>
            <Link href="/" className={styles.footerLink}>
              Home
            </Link>
            <a
              href="https://github.com/abbysallord/oppy"
              target="_blank"
              rel="noopener noreferrer"
              className={styles.footerLink}
            >
              GitHub
            </a>
          </div>
        </div>
      </footer>
    </div>
  );
}
