import { NextResponse } from 'next/server';
import opportunitiesData from '@/data/opportunities.json';
import { Opportunity } from '@/types/opportunity';

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const query = (searchParams.get('query') || '').toLowerCase().trim();
  const category = (searchParams.get('category') || 'all').toLowerCase();
  const platform = (searchParams.get('platform') || 'all').toLowerCase();

  let filtered: Opportunity[] = opportunitiesData as Opportunity[];

  if (category !== 'all') {
    filtered = filtered.filter(item => item.opportunity_type.toLowerCase() === category);
  }

  if (platform !== 'all') {
    filtered = filtered.filter(item => item.platform.toLowerCase() === platform);
  }

  if (query) {
    const terms = query.split(/\s+/).filter(Boolean);
    filtered = filtered.filter(item => {
      const searchTarget = `${item.title} ${item.company} ${item.platform} ${(item.tags || []).join(' ')}`.toLowerCase();
      return terms.every(term => searchTarget.includes(term));
    });
  }

  return NextResponse.json({
    success: true,
    total: filtered.length,
    opportunities: filtered
  });
}
