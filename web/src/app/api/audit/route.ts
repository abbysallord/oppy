import { NextResponse } from 'next/server';
import opportunitiesData from '@/data/opportunities.json';
import { Opportunity, AuditResult } from '@/types/opportunity';

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const inputSkillsStr: string = body.skills || '';

    const userSkills = inputSkillsStr
      .toLowerCase()
      .split(/[,;\n\s]+/)
      .map(s => s.trim())
      .filter(s => s.length > 1);

    if (userSkills.length === 0) {
      return NextResponse.json({
        success: false,
        error: 'No valid skills provided'
      }, { status: 400 });
    }

    const items: Opportunity[] = opportunitiesData as Opportunity[];

    const results: AuditResult[] = items.map(opp => {
      const oppText = `${opp.title} ${opp.company} ${opp.opportunity_type} ${(opp.tags || []).join(' ')}`.toLowerCase();
      
      const matched = userSkills.filter(skill => oppText.includes(skill));
      
      let score = 0;
      if (userSkills.length > 0) {
        const ratio = matched.length / userSkills.length;
        score = Math.min(100, Math.round(ratio * 70 + (matched.length > 0 ? 30 : 0)));
      }

      return {
        opportunity: opp,
        score,
        matchedSkills: matched
      };
    });

    results.sort((a, b) => b.score - a.score);

    return NextResponse.json({
      success: true,
      userSkills,
      results
    });
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : 'Invalid payload';
    return NextResponse.json({ success: false, error: message }, { status: 500 });
  }
}
