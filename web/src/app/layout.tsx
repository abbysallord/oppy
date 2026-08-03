import type { Metadata } from "next";
import { Bricolage_Grotesque, Space_Mono } from "next/font/google";
import Navbar from "@/components/Navbar";
import "./globals.css";

const bricolage = Bricolage_Grotesque({
  variable: "--font-bricolage",
  subsets: ["latin"],
  display: "swap",
});

const spaceMono = Space_Mono({
  variable: "--font-mono",
  weight: ["400", "700"],
  subsets: ["latin"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "Oppy — Local-First & Web Career & Hackathon Scout",
  description:
    "Oppy is a local-first command-line and web scout that aggregates remote internships and hackathons, caches listings in SQLite, and compiles Obsidian second-brain dashboards.",
  keywords: [
    "job scraper",
    "internship crawler",
    "hackathon aggregator",
    "local-first CLI",
    "Obsidian career tracker",
    "sqlite jobs db",
    "remote internships",
    "scout utility",
    "resume compatibility auditor"
  ],
  authors: [{ name: "Dhanush Shenoy" }],
  metadataBase: new URL("https://oppy-cli.vercel.app"),
  openGraph: {
    title: "Oppy — Local-First & Web Career Scout",
    description:
      "Automate your career scout locally & on the web. Scrape listings silently, filter out unpaid work, audit resume compatibility offline, and compile Obsidian dashboards.",
    url: "https://oppy-cli.vercel.app",
    siteName: "Oppy",
    locale: "en_US",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "Oppy — Local-First & Web Career Scout",
    description:
      "Automate your career scout locally & on the web. Scrape listings silently, filter out unpaid work, audit resume compatibility offline, and compile Obsidian dashboards.",
    creator: "@dshenoyh",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${bricolage.variable} ${spaceMono.variable}`}>
      <body className="bg-slate-950 text-slate-100 min-h-screen flex flex-col antialiased">
        <Navbar />
        <main className="flex-1">{children}</main>
      </body>
    </html>
  );
}
