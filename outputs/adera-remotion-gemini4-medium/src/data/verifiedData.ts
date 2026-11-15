import rawData from './aderaVerifiedData.json';

export interface DailyPoint {
  day: string;
  impressions: number;
  clicks: number;
  spend: number;
  ctr: number;
  cpm: number;
  event?: string | null;
}

export interface CreativeOpinion {
  persona_id: string;
  name: string;
  cohort: string;
  positive: string;
  negative: string;
}

export interface CreativeEntry {
  asset_id: 'FGR-U3' | 'FGR-B1' | 'FGR-S1';
  headline: string;
  formato: string;
  leva: string;
  body: string;
  cta: string;
  visual: string;
  decision: {
    n_personas: number;
    run_id: string;
    model: string;
    actions: {
      scroll: number;
      glance: number;
      stop: number;
      click: number;
    };
  };
  interviews: {
    most_useful_count: number;
    least_useful_count: number;
    net_mentions: number;
    n_responses: number;
    sample_opinions: CreativeOpinion[];
  };
}

export interface PersonaSlot {
  slot: number;
  avatar: string;
  persona_id: string;
  vertical: string;
  age_band: string;
  motivation: string;
  social_habit: string;
}

export interface AderaVerifiedData {
  source: {
    commit: string;
    kitSha256: string;
    cutoff: string;
    method: string;
    budgetBound: number;
  };
  observedSummary: {
    rows: number;
    days: number;
    firstDay: string;
    lastDay: string;
    impressions: number;
    clicks: number;
    spend: number;
    ctrPct: number;
    cpmEur: number;
  };
  observedDaily: DailyPoint[];
  forecastDaily: DailyPoint[];
  forecastRowsCount: number;
  events: Record<string, string>;
  validation: {
    combined: {
      righe: number;
      impression: number;
      ctr_baseline: { mae: number; wmae: number };
      cpm_baseline: { mae: number; wmae: number };
      ctr_catboost: { mae: number; wmae: number };
      cpm_catboost: { mae: number; wmae: number };
      ctr_timestral_28m: { mae: number; wmae: number };
      cpm_timestral_28m: { mae: number; wmae: number };
      ctr_mix_50_50: { mae: number; wmae: number };
      cpm_mix_50_50: { mae: number; wmae: number };
    };
    folds: Array<{
      dal: string;
      al: string;
      cutoff: string;
      tutti: {
        righe: number;
        impression: number;
        ctr_baseline: { mae: number; wmae: number };
        cpm_baseline: { mae: number; wmae: number };
        ctr_catboost: { mae: number; wmae: number };
        cpm_catboost: { mae: number; wmae: number };
        ctr_timestral_28m: { mae: number; wmae: number };
        cpm_timestral_28m: { mae: number; wmae: number };
        ctr_mix_50_50: { mae: number; wmae: number };
        cpm_mix_50_50: { mae: number; wmae: number };
      };
    }>;
  };
  budget: {
    originalTotal: number;
    proposedTotal: number;
    baseClicks: number;
    scenarioClicks: number;
  };
  syntheticCount: number;
  chiara: {
    persona_id: string;
    name: string;
    age_years: number;
    occupation: string;
    persona_summary: string;
    trust_requirements: string;
    ad_avoidance: string;
    provider: string;
    model: string;
  };
  personas10: PersonaSlot[];
  creatives: {
    'FGR-U3': CreativeEntry;
    'FGR-B1': CreativeEntry;
    'FGR-S1': CreativeEntry;
  };
  overallStory: {
    headline: string;
    executive_verdict: string;
  };
}

export const VERIFIED_DATA = rawData as AderaVerifiedData;
