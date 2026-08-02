'use client';

import { useState, useEffect } from 'react';
import { Opportunity } from '@/types/opportunity';
import StatsHeader from '@/components/StatsHeader';
import OpportunityCard from '@/components/OpportunityCard';
import { Search, Filter, RefreshCw, SlidersHorizontal, Sparkles } from 'lucide-react';

export default function Home() {
  const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState('all');
  const [selectedPlatform, setSelectedPlatform] = useState('all');

  const fetchOpportunities = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (search) params.set('query', search);
      if (category !== 'all') params.set('category', category);
      if (selectedPlatform !== 'all') params.set('platform', selectedPlatform);

      const res = await fetch(`/api/opportunities?${params.toString()}`);
      const data = await res.json();
      if (data.success) {
        setOpportunities(data.opportunities);
      }
    } catch (err) {
      console.error('Failed to fetch opportunities:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const timer = setTimeout(() => {
      fetchOpportunities();
    }, 200);
    return () => clearTimeout(timer);
  }, [search, category, selectedPlatform]);

  const categories = [
    { id: 'all', label: 'All Listings' },
    { id: 'internship', label: 'Internships' },
    { id: 'hackathon', label: 'Hackathons' },
    { id: 'job', label: 'Jobs' },
  ];

  const platforms = [
    { id: 'all', label: 'All Platforms' },
    { id: 'devpost', label: 'Devpost' },
    { id: 'unstop', label: 'Unstop' },
    { id: 'remoteok', label: 'RemoteOK' },
    { id: 'weworkremotely', label: 'WeWorkRemotely' },
  ];

  return (
    <div className="space-y-8">
      {/* Hero Title Header */}
      <div className="text-center max-w-3xl mx-auto space-y-4 pt-4">
        <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-purple-500/10 border border-purple-500/20 text-purple-300 text-xs font-semibold">
          <Sparkles className="w-3.5 h-3.5" />
          <span>Real-time Remote Opportunity Scout</span>
        </div>

        <h1 className="text-4xl sm:text-5xl font-black text-slate-100 tracking-tight">
          Find Paid Internships &{' '}
          <span className="bg-gradient-to-r from-purple-400 via-pink-400 to-indigo-400 bg-clip-text text-transparent">
            Cash Hackathons
          </span>
        </h1>

        <p className="text-slate-400 text-sm sm:text-base">
          Scraped, filtered, and aggregated from Unstop, Devpost, RemoteOK, and WeWorkRemotely.
        </p>
      </div>

      {/* Stats Summary Bar */}
      <StatsHeader opportunities={opportunities} />

      {/* Search & Filter Control Bar */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-4 sm:p-6 space-y-4 backdrop-blur-md shadow-xl">
        {/* Search Bar */}
        <div className="relative">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by title, company, or tech stack (e.g. React, Python, Remote)..."
            className="w-full bg-slate-950/80 border border-slate-800 focus:border-purple-500 rounded-xl pl-12 pr-4 py-3.5 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-purple-500/20 transition-all"
          />
          {search && (
            <button
              onClick={() => setSearch('')}
              className="absolute right-4 top-1/2 -translate-y-1/2 text-xs text-slate-400 hover:text-slate-200"
            >
              Clear
            </button>
          )}
        </div>

        {/* Categories & Platforms */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pt-2 border-t border-slate-800/80">
          {/* Category Tabs */}
          <div className="flex items-center gap-1.5 overflow-x-auto pb-1 md:pb-0 scrollbar-none">
            {categories.map((cat) => (
              <button
                key={cat.id}
                onClick={() => setCategory(cat.id)}
                className={`px-3.5 py-1.5 rounded-xl text-xs font-semibold transition-all shrink-0 ${
                  category === cat.id
                    ? 'bg-purple-600 text-white shadow-lg shadow-purple-600/30'
                    : 'bg-slate-800/60 text-slate-400 hover:text-slate-200 hover:bg-slate-800'
                }`}
              >
                {cat.label}
              </button>
            ))}
          </div>

          {/* Platform Filters */}
          <div className="flex items-center gap-1.5 overflow-x-auto pb-1 md:pb-0 scrollbar-none">
            <SlidersHorizontal className="w-4 h-4 text-slate-500 shrink-0 mr-1" />
            {platforms.map((plat) => (
              <button
                key={plat.id}
                onClick={() => setSelectedPlatform(plat.id)}
                className={`px-3 py-1 rounded-lg text-xs font-medium border transition-all shrink-0 ${
                  selectedPlatform === plat.id
                    ? 'border-purple-500/50 bg-purple-500/10 text-purple-300'
                    : 'border-slate-800 bg-slate-950/40 text-slate-400 hover:border-slate-700'
                }`}
              >
                {plat.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Grid of Results */}
      {loading ? (
        <div className="flex flex-col items-center justify-center py-16 space-y-3">
          <RefreshCw className="w-8 h-8 text-purple-400 animate-spin" />
          <p className="text-sm text-slate-400 font-medium">Loading opportunities...</p>
        </div>
      ) : opportunities.length === 0 ? (
        <div className="bg-slate-900/40 border border-slate-800 rounded-2xl p-12 text-center space-y-3 max-w-md mx-auto">
          <Filter className="w-10 h-10 text-slate-600 mx-auto" />
          <h3 className="text-lg font-bold text-slate-200">No matches found</h3>
          <p className="text-xs text-slate-400">
            Try broadening your search keywords or switching category filters.
          </p>
          <button
            onClick={() => {
              setSearch('');
              setCategory('all');
              setSelectedPlatform('all');
            }}
            className="text-xs text-purple-400 hover:underline font-semibold"
          >
            Reset Filters
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {opportunities.map((opp) => (
            <OpportunityCard key={opp.id} opportunity={opp} />
          ))}
        </div>
      )}
    </div>
  );
}
