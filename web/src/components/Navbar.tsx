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
    <nav 
      className="sticky top-0 z-50 w-full backdrop-blur-xl bg-black/85 border-b border-zinc-800/80 shadow-2xl"
      style={{
        width: '100%',
        backgroundColor: 'rgba(10, 10, 10, 0.9)',
        borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
        backdropFilter: 'blur(16px)',
        position: 'sticky',
        top: 0,
        zIndex: 50,
      }}
    >
      <div 
        className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8"
        style={{
          maxWidth: '80rem',
          margin: '0 auto',
          padding: '0.75rem 1.5rem',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: '1rem',
          width: '100%',
          boxSizing: 'border-box'
        }}
      >
        {/* Logo & Brand */}
        <Link 
          href="/" 
          className="flex items-center gap-3 group shrink-0"
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.75rem',
            textDecoration: 'none'
          }}
        >
          <div 
            className="w-9 h-9 rounded-xl bg-gradient-to-tr from-emerald-400 via-purple-500 to-indigo-500 p-[1.5px] shadow-lg shadow-emerald-500/20 group-hover:scale-105 transition-all"
            style={{
              width: '2.25rem',
              height: '2.25rem',
              borderRadius: '0.75rem',
              background: 'linear-gradient(to top right, #34d399, #a855f7, #6366f1)',
              padding: '1.5px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}
          >
            <div 
              className="w-full h-full bg-zinc-950 rounded-[10.5px] flex items-center justify-center"
              style={{
                width: '100%',
                height: '100%',
                backgroundColor: '#09090b',
                borderRadius: '10.5px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}
            >
              <Terminal className="w-4 h-4 text-emerald-400" style={{ width: '1rem', height: '1rem', color: '#34d399' }} />
            </div>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span 
              className="text-lg font-black tracking-tight text-white group-hover:text-emerald-400 transition-colors"
              style={{ fontSize: '1.125rem', fontWeight: 900, color: '#ffffff', letterSpacing: '-0.025em' }}
            >
              OPPY
            </span>
            <span 
              className="text-[10px] font-mono font-semibold px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30"
              style={{
                fontSize: '0.625rem',
                fontFamily: 'monospace',
                fontWeight: 600,
                padding: '0.125rem 0.5rem',
                borderRadius: '9999px',
                backgroundColor: 'rgba(52, 211, 153, 0.1)',
                color: '#34d399',
                border: '1px solid rgba(52, 211, 153, 0.3)'
              }}
            >
              v1.0.7
            </span>
          </div>
        </Link>

        {/* Navigation Links */}
        <div 
          className="flex items-center gap-1 sm:gap-2"
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            flexWrap: 'wrap'
          }}
        >
          <Link
            href="/"
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.375rem',
              padding: '0.375rem 0.75rem',
              borderRadius: '0.5rem',
              fontSize: '0.75rem',
              fontWeight: 600,
              textDecoration: 'none',
              backgroundColor: isActive('/') && pathname === '/' ? 'rgba(255, 255, 255, 0.1)' : 'transparent',
              color: isActive('/') && pathname === '/' ? '#34d399' : '#a1a1aa',
              border: isActive('/') && pathname === '/' ? '1px solid rgba(255, 255, 255, 0.15)' : '1px solid transparent'
            }}
          >
            <span>Home</span>
          </Link>

          <Link
            href="/explorer"
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.375rem',
              padding: '0.375rem 0.75rem',
              borderRadius: '0.5rem',
              fontSize: '0.75rem',
              fontWeight: 600,
              textDecoration: 'none',
              backgroundColor: isActive('/explorer') ? 'rgba(52, 211, 153, 0.1)' : 'transparent',
              color: isActive('/explorer') ? '#34d399' : '#a1a1aa',
              border: isActive('/explorer') ? '1px solid rgba(52, 211, 153, 0.3)' : '1px solid transparent'
            }}
          >
            <Compass style={{ width: '0.875rem', height: '0.875rem', color: '#34d399' }} />
            <span>Explorer</span>
          </Link>

          <Link
            href="/audit"
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.375rem',
              padding: '0.375rem 0.75rem',
              borderRadius: '0.5rem',
              fontSize: '0.75rem',
              fontWeight: 600,
              textDecoration: 'none',
              backgroundColor: isActive('/audit') ? 'rgba(168, 85, 247, 0.1)' : 'transparent',
              color: isActive('/audit') ? '#c084fc' : '#a1a1aa',
              border: isActive('/audit') ? '1px solid rgba(168, 85, 247, 0.3)' : '1px solid transparent'
            }}
          >
            <Target style={{ width: '0.875rem', height: '0.875rem', color: '#c084fc' }} />
            <span>Auditor</span>
          </Link>

          <Link
            href="/docs"
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.375rem',
              padding: '0.375rem 0.75rem',
              borderRadius: '0.5rem',
              fontSize: '0.75rem',
              fontWeight: 600,
              textDecoration: 'none',
              backgroundColor: isActive('/docs') ? 'rgba(96, 165, 250, 0.1)' : 'transparent',
              color: isActive('/docs') ? '#60a5fa' : '#a1a1aa',
              border: isActive('/docs') ? '1px solid rgba(96, 165, 250, 0.3)' : '1px solid transparent'
            }}
          >
            <BookOpen style={{ width: '0.875rem', height: '0.875rem', color: '#60a5fa' }} />
            <span>Docs</span>
          </Link>

          {/* Launch App CTA */}
          <Link
            href="/explorer"
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.375rem',
              padding: '0.4rem 0.85rem',
              borderRadius: '0.5rem',
              fontSize: '0.75rem',
              fontWeight: 700,
              textDecoration: 'none',
              backgroundColor: '#34d399',
              color: '#000000',
              boxShadow: '0 4px 14px rgba(52, 211, 153, 0.25)',
              marginLeft: '0.25rem'
            }}
          >
            <Rocket style={{ width: '0.875rem', height: '0.875rem' }} />
            <span>Launch App</span>
          </Link>
        </div>
      </div>
    </nav>
  );
}
