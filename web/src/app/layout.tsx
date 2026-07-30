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
  title: "Oppy — Automate your internship & hackathon scout",
  description:
    "Oppy is a local-first CLI utility that crawls listings, filters out unpaid work, and compiles career opportunity dashboards directly to your notes and Obsidian vault.",
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
