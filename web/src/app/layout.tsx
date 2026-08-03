import type { Metadata } from "next";
import { Bricolage_Grotesque, Space_Mono } from "next/font/google";
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
  title: "Oppy — Local-First Career & Hackathon Scout",
  description:
    "Oppy is a local-first command-line scout that aggregates remote internships and hackathons, caches listings in a local SQLite WAL database, and compiles Obsidian second-brain dashboards.",
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
    title: "Oppy — Local-First Career & Hackathon Scout",
    description:
      "Automate your career scout locally. Scrape listings silently, filter out unpaid work, audit resume compatibility offline, and compile Obsidian dashboards.",
    url: "https://oppy-cli.vercel.app",
    siteName: "Oppy",
    images: [
      {
        url: "https://oppy-cli.vercel.app/opengraph-image.png",
        width: 1200,
        height: 630,
        alt: "Oppy — Local-First Career & Hackathon Scout",
      },
    ],
    locale: "en_US",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "Oppy — Local-First Career & Hackathon Scout",
    description:
      "Automate your career scout locally. Scrape listings silently, filter out unpaid work, audit resume compatibility offline, and compile Obsidian dashboards.",
    images: ["https://oppy-cli.vercel.app/opengraph-image.png"],
    creator: "@dshenoyh",
  },
  other: {
    "og:logo": "https://oppy-cli.vercel.app/icon.svg",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${bricolage.variable} ${spaceMono.variable}`}>
      <body>{children}</body>
    </html>
  );
}
