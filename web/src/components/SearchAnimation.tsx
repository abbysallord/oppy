'use client';

import { useState, useEffect } from 'react';
import { Terminal, CheckCircle2, Loader2, Database } from 'lucide-react';

interface Props {
  query: string;
  onComplete?: () => void;
}

export default function SearchAnimation({ query, onComplete }: Props) {
  const [step, setStep] = useState(0);

  const steps = [
    { name: 'Unstop Internships & Hackathons', status: 'indexing' },
    { name: 'Devpost Cash Hackathons', status: 'indexing' },
    { name: 'RemoteOK Paid Internships', status: 'indexing' },
    { name: 'WeWorkRemotely Listings', status: 'indexing' },
    { name: 'Executing SQLite WAL Query Filter', status: 'querying' },
  ];

  useEffect(() => {
    const timer1 = setTimeout(() => setStep(1), 250);
    const timer2 = setTimeout(() => setStep(2), 500);
    const timer3 = setTimeout(() => setStep(3), 750);
    const timer4 = setTimeout(() => setStep(4), 1000);
    const timer5 = setTimeout(() => {
      setStep(5);
      if (onComplete) onComplete();
    }, 1200);

    return () => {
      clearTimeout(timer1);
      clearTimeout(timer2);
      clearTimeout(timer3);
      clearTimeout(timer4);
      clearTimeout(timer5);
    };
  }, [query]);

  return (
    <div className="bg-slate-950 border border-slate-800 rounded-2xl p-5 shadow-2xl space-y-3 font-mono text-xs max-w-2xl mx-auto my-6 animate-in fade-in zoom-in-95 duration-200">
      {/* Terminal Bar */}
      <div className="flex items-center justify-between border-b border-slate-800/80 pb-2.5">
        <div className="flex items-center space-x-2">
          <div className="w-3 h-3 rounded-full bg-red-500/80" />
          <div className="w-3 h-3 rounded-full bg-yellow-500/80" />
          <div className="w-3 h-3 rounded-full bg-green-500/80" />
          <span className="text-slate-400 font-semibold ml-2 flex items-center gap-1.5 text-[11px]">
            <Terminal className="w-3.5 h-3.5 text-purple-400" />
            oppy-cli --search &quot;{query}&quot;
          </span>
        </div>
        <span className="text-[10px] text-purple-400 bg-purple-500/10 px-2 py-0.5 rounded border border-purple-500/20">
          Sync Engine Active
        </span>
      </div>

      {/* Progress Rows */}
      <div className="space-y-2 py-1">
        {steps.map((s, idx) => {
          const isDone = step > idx;
          const isCurrent = step === idx;

          return (
            <div key={idx} className="flex items-center justify-between text-slate-300">
              <div className="flex items-center space-x-2">
                {isDone ? (
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                ) : isCurrent ? (
                  <Loader2 className="w-4 h-4 text-purple-400 animate-spin shrink-0" />
                ) : (
                  <Database className="w-4 h-4 text-slate-700 shrink-0" />
                )}
                <span className={isDone ? 'text-slate-200' : isCurrent ? 'text-purple-300 font-bold' : 'text-slate-600'}>
                  {s.name}
                </span>
              </div>
              <span className="text-[11px]">
                {isDone ? (
                  <span className="text-emerald-400 font-semibold">[ OK ]</span>
                ) : isCurrent ? (
                  <span className="text-purple-400 animate-pulse">[ SCANNING... ]</span>
                ) : (
                  <span className="text-slate-700">[ QUEUED ]</span>
                )}
              </span>
            </div>
          );
        })}
      </div>

      {/* Footer Output */}
      {step >= 5 && (
        <div className="pt-2 border-t border-slate-800 text-emerald-400 font-semibold flex items-center justify-between text-[11px]">
          <span>✔ Cache Query Completed. Results Filtered Instantly.</span>
          <span className="text-slate-500 text-[10px]">WAL mode • oppy.db</span>
        </div>
      )}
    </div>
  );
}
