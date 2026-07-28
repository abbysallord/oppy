"use client";

import { useState } from "react";
import Image from "next/image";
import Link from "next/link";
import { motion } from "motion/react";
import styles from "./page.module.css";

const FAQItem = ({ question, answer }: { question: string; answer: string }) => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className={styles.faqItem} onClick={() => setIsOpen(!isOpen)}>
      <div className={styles.faqHeader}>
        <span className={styles.faqQuestion}>{question}</span>
        <motion.span
          className={styles.faqIcon}
          animate={{ rotate: isOpen ? 45 : 0 }}
          transition={{ duration: 0.3, ease: [0.16, 1, 0.3, 1] }}
        >
          +
        </motion.span>
      </div>
      <motion.div
        className={styles.faqBody}
        initial={false}
        animate={{
          height: isOpen ? "auto" : 0,
          opacity: isOpen ? 1 : 0,
        }}
        transition={{ duration: 0.3, ease: [0.16, 1, 0.3, 1] }}
        style={{ overflow: "hidden" }}
      >
        <div style={{ paddingTop: "1rem" }}>
          <p>{answer}</p>
        </div>
      </motion.div>
    </div>
  );
};

export default function Home() {
  const [copyText, setCopyText] = useState("Copy");

  const handleCopy = () => {
    navigator.clipboard.writeText("npx @dshenoyh/oppy-cli");
    setCopyText("Copied!");
    setTimeout(() => {
      setCopyText("Copy");
    }, 2000);
  };

  const handleScrollToCLI = () => {
    document.getElementById("getting-started")?.scrollIntoView({ behavior: "smooth" });
  };

  return (
    <div className={styles.wrapper}>
      {/* Grid background overlay */}
      <div className={styles.gridBg} />

      {/* GitHub Star Eyebrow Banner */}
      <div className={styles.starBanner}>
        ★ Open-source & local-first. Help us grow:
        <a
          href="https://github.com/abbysallord/oppy"
          target="_blank"
          rel="noopener noreferrer"
          className={styles.starLink}
        >
          Star Oppy on GitHub
        </a>
      </div>

      {/* Navbar */}
      <header className={styles.navbar}>
        <div className={`${styles.container} ${styles.navContainer}`}>
          <div className={styles.brand}>
            <span className={styles.logoText}>Oppy</span>
            <span className={styles.logoVersion}>v1.0.6</span>
          </div>
          <nav className={styles.navLinks}>
            <Link href="/docs" className={styles.navLink}>
              Docs
            </Link>
            <a
              href="https://github.com/abbysallord/oppy"
              target="_blank"
              rel="noopener noreferrer"
              className={styles.navLink}
            >
              GitHub
            </a>
            <button onClick={handleCopy} className={styles.navCTA}>
              npx @dshenoyh/oppy-cli
            </button>
          </nav>
        </div>
      </header>

      {/* Hero Section */}
      <section className={styles.hero}>
        <div className={`${styles.container} ${styles.heroGrid}`}>
          <div className={styles.heroContent}>
            <h1 className={styles.heroTitle}>
              Scout opportunities. <br />
              Cache locally. <br />
              <span className={styles.heroTitleHighlight}>
                Sync to Obsidian.
              </span>
            </h1>
            <p className={styles.heroSubtext}>
              A local-first career scraper and resume compatibility auditor
              designed to help active tech developers, students, and personal
              knowledge base managers.
            </p>
            <div className={styles.heroButtons}>
              <button onClick={handleScrollToCLI} className={styles.buttonPrimary}>
                Run instant CLI
              </button>
              <a
                href="https://github.com/abbysallord/oppy"
                target="_blank"
                rel="noopener noreferrer"
                className={styles.buttonSecondary}
              >
                View Repository
              </a>
            </div>
          </div>
          <div className={styles.heroVisual}>
            <div className={styles.terminalMock}>
              <div className={styles.terminalHeader}>
                <div className={styles.terminalDots}>
                  <div className={`${styles.terminalDot} ${styles.dotRed}`} />
                  <div className={`${styles.terminalDot} ${styles.dotYellow}`} />
                  <div className={`${styles.terminalDot} ${styles.dotGreen}`} />
                </div>
                <span className={styles.terminalTitle}>oppy --interactive</span>
              </div>
              <div className={styles.terminalBody}>
                <div className={styles.terminalLogo}>
                  {`██████╗ ██████╗ ██████╗ ██╗   ██╗
██╔══██╗██╔══██╗██╔══██╗╚██╗ ██╔╝
██║  ██║██████╔╝██████╔╝ ╚████╔╝ 
██║  ██║██╔═══╝ ██╔═══╝   ╚██╔╝  
██████╔╝██║     ██║        ██║   
╚═════╝ ╚═╝     ╚═╝        ╚═╝   `}
                </div>
                <div className={styles.terminalSub}>
                  Oppy - Terminal-Native Opportunity Scout & Indexer
                </div>
                <div className={styles.terminalDivider}>
                  ────────────────── Main Menu ──────────────────
                </div>
                <div className={styles.terminalMenu}>
                  <div className={styles.menuItem}>
                    <span className={styles.menuIndex}>[1]</span> Synchronize Opportunities (Index Feeds)
                  </div>
                  <div className={styles.menuItem}>
                    <span className={styles.menuIndex}>[2]</span> Browse Opportunities Ledger (Query & Filter)
                  </div>
                  <div className={styles.menuItem}>
                    <span className={styles.menuIndex}>[3]</span> Configure Scan Settings (Filter Toggles)
                  </div>
                  <div className={styles.menuItem}>
                    <span className={styles.menuIndex}>[4]</span> Help & Repository Details
                  </div>
                  <div className={styles.menuItem}>
                    <span className={styles.menuIndex}>[5]</span> Exit Console
                  </div>
                </div>
                <div className={styles.terminalPrompt}>
                  Press key <span className={styles.promptAccent}>[1-5]</span> to select... <span className={styles.cursor}>█</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Quote / Narrative Section */}
      <section className={styles.storySection}>
        <div className={styles.storyContent}>
          <p className={styles.quoteText}>
            &ldquo;If you don&apos;t apply for internships, will internships
            apply to you?&rdquo;
          </p>
          <p className={styles.quoteAuthor}>— Developer&apos;s Mother</p>
          <p className={styles.storyBody}>
            Most career portals are bloated with advertisements, popups, and
            opaque algorithms. We designed Oppy to automate the discovery pipeline
            locally on your own host machine. By crawling listings silently in
            the background, formatting them, and exporting clean markdown
            databases, Oppy lets you track active opportunities directly inside
            your offline notes without clutter.
          </p>
        </div>
      </section>

      {/* Core Features Grid */}
      <section className={styles.features}>
        <div className={styles.container}>
          <div className={styles.sectionHeader}>
            <h2 className={styles.sectionTitle}>Built for Devs & Researchers</h2>
            <p className={styles.sectionSubtitle}>
              Oppy bypasses the friction of traditional web job portals to give
              you full local ownership of your search.
            </p>
          </div>
          <div className={styles.grid}>
            <div className={styles.card}>
              <span className={styles.cardIcon}>01 / SQLite</span>
              <h3 className={styles.cardTitle}>Local SQLite Cache</h3>
              <p className={styles.cardBody}>
                All opportunities are parsed and stored in a local SQLite
                database in WAL mode. Your search history remains private, offline,
                and permanent, even if listings are deleted from the web.
              </p>
            </div>
            <div className={styles.card}>
              <span className={styles.cardIcon}>02 / Match</span>
              <h3 className={styles.cardTitle}>Resume Skill Auditor</h3>
              <p className={styles.cardBody}>
                Pass your resume file locally to check your compatibility. Oppy
                uses case-insensitive keyword boundaries to cross-examine skills like
                FastAPI, React, or C++ and list exact missing requirements.
              </p>
            </div>
            <div className={styles.card}>
              <span className={styles.cardIcon}>03 / Feed</span>
              <h3 className={styles.cardTitle}>Custom RSS Feeds</h3>
              <p className={styles.cardBody}>
                Add custom RSS URLs directly through the interactive settings panel.
                Oppy dynamically integrates custom career pages, newsletters, or
                listings into the unified search pool.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Vault Sync Split Showcase */}
      <section className={styles.showcase}>
        <div className={`${styles.container} ${styles.showcaseGrid}`}>
          <div className={styles.showcaseContent}>
            <h2 className={styles.showcaseTitle}>
               Obsidian Vault Integration
            </h2>
            <p className={styles.showcaseBody}>
              Scour internships, jobs, and hackathons, filter out unpaid
              postings automatically, and beam a compiled list directly to your
              inbox. Oppy exports structured markdown tables with direct apply links
              and compensation details to match your second-brain structure.
            </p>
          </div>
          <div className={styles.showcaseVisual}>
            <Image
              src="/obsidian-screenshot.png"
              alt="Obsidian Markdown vault showing integrated tech opportunities table with platform, company, and deadline fields"
              width={800}
              height={500}
              className={styles.screenshot}
            />
          </div>
        </div>
      </section>

      {/* Meme Section */}
      <section className={styles.memeSection}>
        <div className={styles.container}>
          <h2 className={styles.sectionTitle}>The Job-Hunting Loop</h2>
          <p className={styles.sectionSubtitle}>
            We have all been there: keeping 20 tabs open, copying details manually, missing deadlines.
          </p>
          <div className={styles.memeWrapper}>
            <Image
              src="/meme.png"
              alt="Drake Hotline Bling Meme: Rejecting manual browser scouring, approving Oppy terminal Obsidian sync"
              width={736}
              height={660}
              className={styles.screenshot}
            />
          </div>
        </div>
      </section>

      {/* Interactive Command Panel */}
      <section id="getting-started" className={styles.gettingStarted}>
        <div className={styles.container}>
          <h2 className={styles.sectionTitle}>Get Started Instantly</h2>
          <p className={styles.sectionSubtitle}>
            No installers, no databases to configure. Bootstrap Oppy straight from your terminal.
          </p>
          <div className={styles.cliWrapper}>
            <div className={styles.cliHeader}>
              <div className={styles.cliDots}>
                <div className={styles.cliDot} />
                <div className={styles.cliDot} />
                <div className={styles.cliDot} />
              </div>
              <span className={styles.cliTitle}>terminal</span>
            </div>
            <div className={styles.cliContent}>
              <div className={styles.commandRow}>
                <span>
                  <span className={styles.prompt}>$</span> npx
                  @dshenoyh/oppy-cli
                </span>
                <button onClick={handleCopy} className={styles.copyButton}>
                  {copyText}
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* FAQ Disclosures */}
      <section className={styles.faqs}>
        <div className={styles.container}>
          <div className={styles.sectionHeader}>
            <h2 className={styles.sectionTitle}>Frequently Asked Questions</h2>
          </div>
          <div className={styles.faqWrapper}>
            <FAQItem
              question="Where is the cached database stored?"
              answer="Oppy caches all data in a local SQLite database in WAL mode at ~/.config/oppy/opportunities.db. Your data remains fully offline on your own machine."
            />
            <FAQItem
              question="Does the resume auditor send my file to any server?"
              answer="No. The auditor parses your local plain-text resume completely offline using fuzzy string boundary matches. No network queries or API keys are required."
            />
            <FAQItem
              question="How do I configure headless automation?"
              answer="Run oppy --headless to trigger a silent scraper cycle and update your markdown tables. This can be scheduled easily using crontabs or systemd timers."
            />
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className={styles.footer}>
        <div className={`${styles.container} ${styles.footerContainer}`}>
          <span className={styles.footerText}>
            &copy; {new Date().getFullYear()} Oppy. Open source under MIT.
          </span>
          <div className={styles.footerLinks}>
            <Link href="/docs" className={styles.footerLink}>
              Docs
            </Link>
            <a
              href="https://github.com/abbysallord/oppy"
              target="_blank"
              rel="noopener noreferrer"
              className={styles.footerLink}
            >
              GitHub
            </a>
            <a
              href="https://www.npmjs.com/package/@dshenoyh/oppy-cli"
              target="_blank"
              rel="noopener noreferrer"
              className={styles.footerLink}
            >
              NPM
            </a>
            <a
              href="https://pypi.org/project/oppy-cli/"
              target="_blank"
              rel="noopener noreferrer"
              className={styles.footerLink}
            >
              PyPI
            </a>
          </div>
        </div>
      </footer>
    </div>
  );
}
