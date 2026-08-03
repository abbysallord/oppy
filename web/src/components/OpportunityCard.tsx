'use client';

import { useState } from 'react';
import { Opportunity } from '@/types/opportunity';
import { ExternalLink, Check, Copy, Calendar, Award, Globe } from 'lucide-react';

interface Props {
  opportunity: Opportunity;
  matchScore?: number;
}

export default function OpportunityCard({ opportunity, matchScore }: Props) {
  const [copied, setCopied] = useState(false);

  const getPlatformBadge = (platform: string) => {
    const p = platform.toLowerCase();
    if (p === 'devpost') {
      return { label: 'Devpost', bg: 'bg-cyan-500/10 text-cyan-400 border-cyan-500/30' };
    }
    if (p === 'unstop') {
      return { label: 'Unstop', bg: 'bg-purple-500/10 text-purple-400 border-purple-500/30' };
    }
    if (p === 'remoteok') {
      return { label: 'RemoteOK', bg: 'bg-red-500/10 text-red-400 border-red-500/30' };
    }
    if (p === 'weworkremotely') {
      return { label: 'WeWorkRemotely', bg: 'bg-amber-500/10 text-amber-400 border-amber-500/30' };
    }
    return { label: platform.toUpperCase(), bg: 'bg-slate-800 text-slate-300 border-slate-700' };
  };

  const getTypeBadge = (type: string) => {
    if (type === 'hackathon') {
      return { label: 'HACKATHON', bg: 'bg-pink-500/10 text-pink-400 border-pink-500/30' };
    }
    if (type === 'internship') {
      return { label: 'INTERNSHIP', bg: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30' };
    }
    return { label: 'JOB', bg: 'bg-blue-500/10 text-blue-400 border-blue-500/30' };
  };

  const handleCopyMarkdown = () => {
    const markdown = `* [${opportunity.title}](${opportunity.opportunity_url}) - **${opportunity.company}** | ${opportunity.stipend_or_prize} | Deadline: ${opportunity.deadline}`;
    navigator.clipboard.writeText(markdown);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const platformStyle = getPlatformBadge(opportunity.platform);
  const typeStyle = getTypeBadge(opportunity.opportunity_type);

  return (
    <div className="group relative bg-slate-900/60 hover:bg-slate-900/90 border border-slate-800 hover:border-purple-500/40 rounded-2xl p-5 transition-all duration-200 shadow-xl hover:shadow-purple-500/5 flex flex-col justify-between backdrop-blur-sm">
      {/* Top Header & Badges */}
      <div>
        <div className="flex flex-wrap items-center gap-2 mb-3">
          <span className={`text-xs font-bold px-2.5 py-1 rounded-full border ${typeStyle.bg}`}>
            {typeStyle.label}
          </span>
          <span className={`text-xs font-semibold px-2.5 py-1 rounded-full border ${platformStyle.bg}`}>
            {platformStyle.label}
          </span>
          {opportunity.is_remote && (
            <span className="text-xs font-medium px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700 flex items-center gap-1">
              <Globe className="w-3 h-3 text-cyan-400" />
              Remote
            </span>
          )}
          {typeof matchScore === 'number' && (
            <span className="ml-auto text-xs font-bold px-3 py-1 rounded-full bg-gradient-to-r from-purple-500 to-pink-500 text-white shadow-md">
              {matchScore}% Match
            </span>
          )}
        </div>

        {/* Title */}
        <h3 className="text-lg font-bold text-slate-100 group-hover:text-purple-300 transition-colors line-clamp-2 mb-1">
          {opportunity.title}
        </h3>

        {/* Company */}
        <p className="text-sm font-medium text-slate-400 mb-4">
          {opportunity.company}
        </p>

        {/* Details Pill */}
        <div className="space-y-2 mb-4 text-xs font-medium">
          <div className="flex items-center text-amber-300 bg-amber-500/10 border border-amber-500/20 px-3 py-1.5 rounded-lg w-fit">
            <Award className="w-4 h-4 mr-1.5 shrink-0 text-amber-400" />
            <span>{opportunity.stipend_or_prize || 'Paid'}</span>
          </div>

          <div className="flex items-center text-slate-400">
            <Calendar className="w-3.5 h-3.5 mr-1.5 shrink-0 text-purple-400" />
            <span>Deadline: {opportunity.deadline || 'Open'}</span>
          </div>
        </div>

        {/* Tags */}
        {opportunity.tags && opportunity.tags.length > 0 && (
          <div className="flex flex-wrap gap-1.5 mb-5">
            {opportunity.tags.map((tag, i) => (
              <span
                key={i}
                className="text-[11px] font-medium px-2 py-0.5 rounded-md bg-slate-800/80 text-slate-300 border border-slate-700/60"
              >
                {tag}
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Action Buttons */}
      <div className="flex items-center gap-2 pt-3 border-t border-slate-800/80">
        <a
          href={opportunity.opportunity_url}
          target="_blank"
          rel="noopener noreferrer"
          className="flex-1 inline-flex items-center justify-center space-x-1.5 px-4 py-2 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-semibold text-xs transition-colors shadow-md shadow-purple-600/20"
        >
          <span>View Listing</span>
          <ExternalLink className="w-3.5 h-3.5" />
        </a>

        <button
          onClick={handleCopyMarkdown}
          title="Copy as Obsidian Markdown"
          className="inline-flex items-center justify-center p-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white border border-slate-700 transition-colors"
        >
          {copied ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
        </button>
      </div>
    </div>
  );
}
