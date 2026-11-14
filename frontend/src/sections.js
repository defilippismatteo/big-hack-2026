import {
  ChartNoAxesCombined, LayoutGrid, PanelsTopLeft, ShieldCheck, UsersRound, WalletCards,
} from 'lucide-react';

export const groups = ['Workspace', 'Qualità'];

export const sections = [
  {
    id: 'overview', label: 'Overview', group: 'Workspace', icon: LayoutGrid,
  },
  {
    id: 'audience', label: 'Audience Lab', group: 'Workspace', icon: UsersRound, tone: 'violet',
    description: 'Esplora ipotesi sul pubblico e profili sintetici per segmento.',
  },
  {
    id: 'creatives', label: 'Creative Explorer', group: 'Workspace', icon: PanelsTopLeft, tone: 'blue',
    description: 'Confronta creatività, formati e leve delle campagne.',
  },
  {
    id: 'forecast', label: 'Forecast Analytics', group: 'Workspace', icon: ChartNoAxesCombined, tone: 'violet',
    description: 'Segui CTR e CPM previsti nel periodo del Black Friday.',
  },
  {
    id: 'budget', label: 'Budget Planner', group: 'Workspace', icon: WalletCards, tone: 'mint',
    description: 'Valuta scenari di allocazione a parità di budget.',
  },
  {
    id: 'validation', label: 'Model Validation', group: 'Qualità', icon: ShieldCheck, tone: 'sand',
    description: 'Consulta i backtest, le metriche e i limiti dei modelli.',
  },
];

export const sectionHref = (id) => '#/' + id;

export function getSection() {
  const id = window.location.hash.slice(2).split('?')[0];
  return sections.find((section) => window.location.hash.startsWith('#/') && section.id === id) ?? sections[0];
}
