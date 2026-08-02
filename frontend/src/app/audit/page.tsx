'use client';

import { useState } from 'react';
import { AuditResult } from '@/types/opportunity';
import OpportunityCard from '@/components/OpportunityCard';
import { Target, Sparkles, RefreshCw, Code, CheckCircle2 } from 'lucide-react';

export default function SkillAuditor() {
  const [skillsText, setSkillsText] = useState('Python, React, TypeScript, Next.js, SQL');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<AuditResult[] | null>(null);

  const handleAudit = async () => {
    if (!skillsText.trim()) return;
    setLoading(true);
    try {
      const res = await fetch('/api/audit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ skills: skillsText }),
      });
      const data = await res.json();
      if (data.success) {
        setResults(data.results);
      }
    } catch (err) {
      console.error('Audit failed:', err);
    } finally {
      setLoading(false);
    }
  };

  const presetSkillPills = [
    'Python, React, TypeScript, SQL',
    'Go, Docker, Kubernetes, Linux',
    'Next.js, Tailwind, Node.js',
    'AI, LLMs, LangChain, FastAPI',
  ];

  return (
    <div className="space-y-8 max-w-4xl mx-auto">
      {/* Header */}
      <div className="text-center space-y-3 pt-4">
        <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-pink-500/10 border border-pink-500/20 text-pink-300 text-xs font-semibold">
          <Target className="w-3.5 h-3.5" />
          <span>Skill-Matching Fit Scoring Auditor</span>
        </div>

        <h1 className="text-3xl sm:text-4xl font-black text-slate-100 tracking-tight">
          Audit Your Skills Against Active Opportunities
        </h1>

        <p className="text-slate-400 text-sm max-w-xl mx-auto">
          Enter your tech stack or paste your resume skills to calculate your fit compatibility score across all indexed internships and hackathons.
        </p>
      </div>

      {/* Input Box Panel */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 space-y-4 backdrop-blur-md shadow-xl">
        <label className="block text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2">
          <Code className="w-4 h-4 text-purple-400" />
          Enter Skills or Tech Stack (comma separated)
        </label>

        <textarea
          rows={3}
          value={skillsText}
          onChange={(e) => setSkillsText(e.target.value)}
          placeholder="e.g. Python, React, Go, Docker, Machine Learning, SQL..."
          className="w-full bg-slate-950/80 border border-slate-800 focus:border-pink-500 rounded-xl p-4 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-pink-500/20 transition-all font-mono"
        />

        {/* Quick Presets */}
        <div className="flex flex-wrap items-center gap-2 pt-1">
          <span className="text-xs text-slate-500 font-medium">Quick Presets:</span>
          {presetSkillPills.map((preset, idx) => (
            <button
              key={idx}
              onClick={() => setSkillsText(preset)}
              className="text-xs px-2.5 py-1 rounded-lg bg-slate-800/60 hover:bg-slate-800 text-slate-300 border border-slate-700/60 transition-colors"
            >
              {preset}
            </button>
          ))}
        </div>

        {/* Action Button */}
        <button
          onClick={handleAudit}
          disabled={loading || !skillsText.trim()}
          className="w-full py-3.5 rounded-xl bg-gradient-to-r from-pink-600 via-purple-600 to-indigo-600 hover:opacity-95 text-white font-bold text-sm transition-all shadow-lg shadow-pink-600/20 flex items-center justify-center space-x-2 disabled:opacity-50"
        >
          {loading ? (
            <>
              <RefreshCw className="w-4 h-4 animate-spin" />
              <span>Auditing Skill Compatibility...</span>
            </>
          ) : (
            <>
              <Sparkles className="w-4 h-4" />
              <span>Run Compatibility Audit</span>
            </>
          )}
        </button>
      </div>

      {/* Results Listing */}
      {results && (
        <div className="space-y-6 pt-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-4">
            <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2">
              <CheckCircle2 className="w-5 h-5 text-emerald-400" />
              <span>Audit Results ({results.length} Matches)</span>
            </h2>
            <span className="text-xs text-slate-400">Sorted by compatibility score</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {results.map((res, i) => (
              <OpportunityCard
                key={res.opportunity.id || i}
                opportunity={res.opportunity}
                matchScore={res.score}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
