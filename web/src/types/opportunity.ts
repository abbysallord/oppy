export type OpportunityType = 'internship' | 'hackathon' | 'job';

export type PlatformType = 'unstop' | 'devpost' | 'remoteok' | 'weworkremotely' | 'customrss';

export interface Opportunity {
  id: number | string;
  title: string;
  company: string;
  platform: PlatformType | string;
  opportunity_type: OpportunityType;
  opportunity_url: string;
  stipend_or_prize: string;
  deadline: string;
  is_remote: boolean;
  is_paid: boolean;
  discovered_at?: string;
  tags?: string[];
}

export interface AuditResult {
  opportunity: Opportunity;
  score: number;
  matchedSkills: string[];
}
