'use client';

import Link from 'next/link';
import { Terminal, Compass, Target, Github } from 'lucide-react';

export default function Navbar() {
  return (
    <nav className="sticky top-0 z-50 backdrop-blur-md bg-slate-950/80 border-b border-slate-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo & Brand */}
          <Link href="/" className="flex items-center space-x-3 group">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-purple-600 via-pink-500 to-indigo-500 p-0.5 shadow-lg shadow-purple-500/20 group-hover:scale-105 transition-transform duration-200">
              <div className="w-full h-full bg-slate-950 rounded-[10px] flex items-center justify-center">
                <Terminal className="w-5 h-5 text-purple-400" />
              </div>
            </div>
            <div>
              <span className="text-xl font-bold bg-gradient-to-r from-purple-400 via-pink-300 to-indigo-400 bg-clip-text text-transparent tracking-tight">
                OPPY
              </span>
              <span className="hidden sm:inline-block ml-2 text-xs px-2 py-0.5 rounded-full bg-purple-500/10 text-purple-300 border border-purple-500/20 font-medium">
                Scout Web
              </span>
            </div>
          </Link>

          {/* Navigation Links */}
          <div className="flex items-center space-x-1 sm:space-x-4">
            <Link
              href="/"
              className="flex items-center space-x-2 px-3 py-2 rounded-lg text-sm font-medium text-slate-200 hover:bg-slate-800/60 hover:text-white transition-colors"
            >
              <Compass className="w-4 h-4 text-purple-400" />
              <span>Explorer</span>
            </Link>

            <Link
              href="/audit"
              className="flex items-center space-x-2 px-3 py-2 rounded-lg text-sm font-medium text-slate-200 hover:bg-slate-800/60 hover:text-white transition-colors"
            >
              <Target className="w-4 h-4 text-pink-400" />
              <span>Skill Auditor</span>
            </Link>

            <a
              href="https://github.com/abbysallord/oppy"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center space-x-2 px-3 py-2 rounded-lg text-sm font-medium bg-purple-600/20 hover:bg-purple-600/30 text-purple-300 border border-purple-500/30 transition-all ml-2 shadow-sm"
            >
              <Github className="w-4 h-4" />
              <span className="hidden sm:inline">GitHub</span>
            </a>
          </div>
        </div>
      </div>
    </nav>
  );
}
