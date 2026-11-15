export const ADERA = {
  width: 1920,
  height: 1080,
  fps: 30,
  durationInFrames: 4500, // 150 seconds exact
  colors: {
    bgLight: '#F6F5F9',
    bgSurface: '#FFFFFF',
    bgLavender: '#EFEAFA',
    bgDark: '#191224',
    bgDarkCard: '#231934',
    plum: '#35214F',
    action: '#7046CE',
    accent: '#8861E8',
    accentSoft: '#C2A5FF',
    ink: '#292339',
    inkSoft: '#514A64',
    inkMuted: '#6A637D',
    borderLight: '#E5DFEF',
    borderDark: '#3A2C52',
    mint: '#22A06B',
    amber: '#E59500',
    coral: '#DC4C64',
  },
  marginX: 154, // 8% of 1920px matching reference video grid
  fontFamily: "'Inter Variable', 'Inter', system-ui, -apple-system, sans-serif",
} as const;

export const SCENES = [
  { id: 'S01_Domanda', label: '01 · Domanda', start: 0, duration: 270 },
  { id: 'S02_AderaBrand', label: '02 · ADERA', start: 270, duration: 210 },
  { id: 'S03_DatiChallenge', label: '03 · Dati Challenge', start: 480, duration: 330 },
  { id: 'S04_ForecastGap', label: '04 · Forecast & Gap', start: 810, duration: 480 },
  { id: 'S05_EventiModelli', label: '05 · Eventi e Modelli', start: 1290, duration: 300 },
  { id: 'S06_Orchestrazione', label: '06 · Orchestrazione T3', start: 1590, duration: 360 },
  { id: 'S07_PersonaChiara', label: '07 · Chiara Bellini', start: 1950, duration: 330 },
  { id: 'S08_FeedDecision', label: '08 · Feed & Swipe Decision 1', start: 2280, duration: 570 },
  { id: 'S09_Scala10Avatar', label: '09 · Scala 10 → 600', start: 2850, duration: 270 },
  { id: 'S10_MorphSegnali', label: '10 · Morph Segnali', start: 3120, duration: 240 },
  { id: 'S11_IntervisteT3', label: '11 · Interviste T3', start: 3360, duration: 450 },
  { id: 'S12_PanDashboard', label: '12 · Pan & Dashboard', start: 3810, duration: 510 },
  { id: 'S13_Chiusura', label: '13 · Chiusura', start: 4320, duration: 180 },
] as const;

export const formatIntIT = (n: number): string =>
  Math.round(n).toString().replace(/\B(?=(\d{3})+(?!\d))/g, '.');

export const formatPctIT = (n: number, digits = 1): string =>
  n.toFixed(digits).replace('.', ',') + '%';

export const formatEurIT = (n: number, digits = 2): string =>
  '€' + n.toFixed(digits).replace('.', ',');
