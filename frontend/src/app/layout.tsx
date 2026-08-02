import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import Navbar from '@/components/Navbar';
import './globals.css';

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
});

export const metadata: Metadata = {
  title: 'Oppy - Terminal-Native & Web Opportunity Scout',
  description: 'Scrape, filter, and track active paid remote internships and cash-prize hackathons from Unstop, Devpost, RemoteOK, and WeWorkRemotely.',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.variable} min-h-screen flex flex-col bg-slate-950 text-slate-100 antialiased selection:bg-purple-500/30 selection:text-purple-200`}>
        <Navbar />
        <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {children}
        </main>
        <footer className="border-t border-slate-900 bg-slate-950 py-6 text-center text-xs text-slate-500">
          <p>© {new Date().getFullYear()} Oppy Scout. Dual CLI + Web Application.</p>
        </footer>
      </body>
    </html>
  );
}
