'use client';

import { Sparkles, Trophy, Briefcase, Globe } from 'lucide-react';
import { Opportunity } from '@/types/opportunity';

interface Props {
  opportunities: Opportunity[];
}

export default function StatsHeader({ opportunities }: Props) {
  const total = opportunities.length;
  const hackathons = opportunities.filter(o => o.opportunity_type === 'hackathon').length;
  const internships = opportunities.filter(o => o.opportunity_type === 'internship').length;
  const remoteCount = opportunities.filter(o => o.is_remote).length;

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
      <div className="bg-slate-900/40 border border-slate-800/80 rounded-2xl p-4 flex items-center space-x-3 backdrop-blur-sm">
        <div className="p-3 rounded-xl bg-purple-500/10 text-purple-400 border border-purple-500/20">
          <Sparkles className="w-5 h-5" />
        </div>
        <div>
          <p className="text-2xl font-black text-slate-100">{total}</p>
          <p className="text-xs font-medium text-slate-400">Total Indexed</p>
        </div>
      </div>

      <div className="bg-slate-900/40 border border-slate-800/80 rounded-2xl p-4 flex items-center space-x-3 backdrop-blur-sm">
        <div className="p-3 rounded-xl bg-pink-500/10 text-pink-400 border border-pink-500/20">
          <Trophy className="w-5 h-5" />
        </div>
        <div>
          <p className="text-2xl font-black text-slate-100">{hackathons}</p>
          <p className="text-xs font-medium text-slate-400">Cash Hackathons</p>
        </div>
      </div>

      <div className="bg-slate-900/40 border border-slate-800/80 rounded-2xl p-4 flex items-center space-x-3 backdrop-blur-sm">
        <div className="p-3 rounded-xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
          <Briefcase className="w-5 h-5" />
        </div>
        <div>
          <p className="text-2xl font-black text-slate-100">{internships}</p>
          <p className="text-xs font-medium text-slate-400">Paid Internships</p>
        </div>
      </div>

      <div className="bg-slate-900/40 border border-slate-800/80 rounded-2xl p-4 flex items-center space-x-3 backdrop-blur-sm">
        <div className="p-3 rounded-xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
          <Globe className="w-5 h-5" />
        </div>
        <div>
          <p className="text-2xl font-black text-slate-100">{remoteCount}</p>
          <p className="text-xs font-medium text-slate-400">100% Remote</p>
        </div>
      </div>
    </div>
  );
}
