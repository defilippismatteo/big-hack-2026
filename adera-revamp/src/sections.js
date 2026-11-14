import {
  Film, ChartNoAxesCombined, LayoutGrid, PanelsTopLeft, ShieldCheck, UsersRound, WalletCards,
} from 'lucide-react';

export const groups = ['Workspace', 'Qualità'];

export const sections = [
  {
    id: 'overview', label: 'Panoramica', group: 'Workspace', icon: LayoutGrid,
  },
  { id: 'process', label: 'Come funziona', group: 'Workspace', icon: Film },
  {
    id: 'audience', label: 'Pubblici e persone', group: 'Workspace', icon: UsersRound, tone: 'violet',
    description: 'Esplora ipotesi sul pubblico e profili sintetici per segmento.',
  },
  {
    id: 'creatives', label: 'Annunci e creatività', group: 'Workspace', icon: PanelsTopLeft, tone: 'blue',
    description: 'Confronta creatività, formati e leve delle campagne.',
  },
  {
    id: 'forecast', label: 'Previsioni', group: 'Workspace', icon: ChartNoAxesCombined, tone: 'violet',
    description: 'Segui CTR e CPM previsti nel periodo del Black Friday.',
  },
  {
    id: 'budget', label: 'Piano budget', group: 'Workspace', icon: WalletCards, tone: 'mint',
    description: 'Valuta scenari di allocazione a parità di budget.',
  },
  {
    id: 'validation', label: 'Affidabilità modelli', group: 'Qualità', icon: ShieldCheck, tone: 'sand',
    description: 'Consulta i backtest, le metriche e i limiti dei modelli.',
  },
];

export const sectionHref = (id) => '#/' + id;

export function getSection() {
  const id = window.location.hash.slice(2).split('?')[0];
  return sections.find((section) => window.location.hash.startsWith('#/') && section.id === id) ?? sections[0];
}
