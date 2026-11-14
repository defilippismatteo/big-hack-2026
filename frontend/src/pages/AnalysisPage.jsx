import { useDashboardData } from '../data/useDashboardData';
import './analysis.css';

export function AnalysisPage({ headingRef, title, subtitle, children }) {
  const { phase, data, retry } = useDashboardData();
  return <div className="analysis-page">
    <header className="overview-title">
      <h1 id="page-title" ref={headingRef} tabIndex={-1}>{title}</h1>
      <p>{subtitle}</p>
    </header>
    {phase === 'loading' && <p className="data-panel feedback-state" role="status">Caricamento dei dati…</p>}
    {phase === 'error' && <div className="data-panel feedback-state" role="alert">
      <p>Impossibile caricare gli artefatti di ADERA.</p>
      <button type="button" className="primary-button" onClick={retry}>Riprova</button>
    </div>}
    {data && children(data)}
  </div>;
}

export function Panel({ title, description, children, className = '' }) {
  return <section className={'data-panel analysis-panel ' + className}>
    <h2>{title}</h2>
    {description && <p className="muted-copy">{description}</p>}
    {children}
  </section>;
}

export function Filter({ label, value, onChange, options }) {
  return <label className="analysis-filter"><span>{label}</span>
    <select value={value} onChange={(event) => onChange(event.target.value)}>
      {options.map(([id, name]) => <option value={id} key={id}>{name}</option>)}
    </select>
  </label>;
}
