'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Terminal, Compass, Target, BookOpen, Rocket } from 'lucide-react';

export default function Navbar() {
  const pathname = usePathname();

  const isActive = (path: string) => {
    if (path === '/' && pathname === '/') return true;
    if (path !== '/' && pathname.startsWith(path)) return true;
    return false;
  };

  return (
    <nav className="sticky top-0 z-50 w-full backdrop-blur-xl bg-black/80 border-b border-zinc-800/80 shadow-2xl">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16 gap-4">
          
          {/* Logo & Brand */}
          <Link href="/" className="flex items-center gap-3 group shrink-0">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-emerald-400 via-purple-500 to-indigo-500 p-[1.5px] shadow-lg shadow-emerald-500/20 group-hover:scale-105 transition-all">
              <div className="w-full h-full bg-zinc-950 rounded-[10.5px] flex items-center justify-center">
                <Terminal className="w-4 h-4 text-emerald-400" />
              </div>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-lg font-black tracking-tight text-white group-hover:text-emerald-400 transition-colors">
                OPPY
              </span>
              <span className="text-[10px] font-mono font-semibold px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                v1.0.7
              </span>
            </div>
          </Link>

          {/* Navigation Links */}
          <div className="flex items-center gap-1 sm:gap-2">
            <Link
              href="/"
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                isActive('/') && pathname === '/'
                  ? 'bg-zinc-800 text-emerald-400 border border-zinc-700'
                  : 'text-zinc-400 hover:text-white hover:bg-zinc-800/60'
              }`}
            >
              <span>Home</span>
            </Link>

            <Link
              href="/explorer"
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                isActive('/explorer')
                  ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                  : 'text-zinc-400 hover:text-white hover:bg-zinc-800/60'
              }`}
            >
              <Compass className="w-3.5 h-3.5 text-emerald-400" />
              <span>Explorer</span>
            </Link>

            <Link
              href="/audit"
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                isActive('/audit')
                  ? 'bg-purple-500/10 text-purple-400 border border-purple-500/30'
                  : 'text-zinc-400 hover:text-white hover:bg-zinc-800/60'
              }`}
            >
              <Target className="w-3.5 h-3.5 text-purple-400" />
              <span>Auditor</span>
            </Link>

            <Link
              href="/docs"
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                isActive('/docs')
                  ? 'bg-blue-500/10 text-blue-400 border border-blue-500/30'
                  : 'text-zinc-400 hover:text-white hover:bg-zinc-800/60'
              }`}
            >
              <BookOpen className="w-3.5 h-3.5 text-blue-400" />
              <span>Docs</span>
            </Link>

            {/* Launch App CTA */}
            <Link
              href="/explorer"
              className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg bg-emerald-400 hover:bg-emerald-300 text-black font-bold text-xs shadow-lg shadow-emerald-400/20 transition-all ml-1 shrink-0"
            >
              <Rocket className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">Launch App</span>
            </Link>
          </div>
        </div>
      </div>
    </nav>
  );
}
