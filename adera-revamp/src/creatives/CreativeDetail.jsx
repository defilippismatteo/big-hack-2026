import { useLayoutEffect, useRef } from 'react';
import { FileText, X } from 'lucide-react';
import { money, pct, shortDate } from '../overview/model';
import { plotLimit } from './model';

const metrics = [
  { key: 'ctr', label: 'CTR previsto', format: pct },
  { key: 'cpm', label: 'CPM previsto', format: money },
  { key: 'cpc', label: 'CPC derivato', format: money },
];

export function CreativeMetrics({ values }) {
  return <dl className="creative-metrics">{metrics.map(({ key, label, format }) =>
    <div key={key}><dt>{label}</dt><dd>{format(values?.[key])}</dd></div>)}</dl>;
}

function DailyTrend({ creative, dates, day }) {
  const available = dates.filter((date) => creative.series.has(date));
  const x = (date) => 4 + dates.indexOf(date) / Math.max(1, dates.length - 1) * 92;
  return <section className="detail-section" aria-labelledby="trend-title">
    <h3 id="trend-title">Andamento giornaliero</h3>
    <p className="explorer-muted">{available.length} giorni con previsione · {shortDate(available[0])}–{shortDate(available.at(-1))}</p>
    <div className="detail-trends">
      {metrics.slice(0, 2).map(({ key, label, format }) => {
        const limit = plotLimit(Math.max(...available.map((date) => creative.series.get(date)[key])));
        const y = (value) => 44 - value / limit * 39;
        const runs = [];
        dates.forEach((date, i) => {
          const point = creative.series.get(date);
          if (!point) return;
          if (!creative.series.has(dates[i - 1])) runs.push([]);
          runs.at(-1).push([x(date), y(point[key])]);
        });
        return <div className="detail-trend" key={key}>
          <div><strong>{label}</strong><span>{format(limit)}</span></div>
          <svg viewBox="0 0 100 48" preserveAspectRatio="none" aria-hidden="true">
            {[5, 24.5, 44].map((tick) => <line key={tick} x1="0" x2="100" y1={tick} y2={tick}
              stroke="#e5dfef" vectorEffect="non-scaling-stroke" />)}
            <line x1={x(day)} x2={x(day)} y1="4" y2="44" stroke="#b09cdd" strokeDasharray="3 3"
              vectorEffect="non-scaling-stroke" />
            {runs.map((points) => <g key={points[0][0]}>
              <polyline points={points.map((point) => point.join(',')).join(' ')} fill="none"
                stroke="#7452d0" strokeWidth="2" vectorEffect="non-scaling-stroke" />
              <circle cx={points[0][0]} cy={points[0][1]} r="0.7" fill="#7452d0" />
            </g>)}
          </svg>
          <div><span>{shortDate(dates[0])}</span><span>{shortDate(dates.at(-1))}</span></div>
        </div>;
      })}
    </div>
    <details className="daily-values">
      <summary>Valori per giorno</summary>
      <table>
        <thead><tr><th scope="col">Data</th><th scope="col">CTR</th><th scope="col">CPM</th></tr></thead>
        <tbody>{available.map((date) => {
          const item = creative.series.get(date);
          return <tr key={date}><th scope="row">{shortDate(date)}</th><td>{pct(item.ctr)}</td><td>{money(item.cpm)}</td></tr>;
        })}</tbody>
      </table>
    </details>
  </section>;
}

export function CreativeDetail({ creative, feedback, day, dates, checked, canSelect, onCompare, onClose }) {
  const panel = useRef(null);
  useLayoutEffect(() => { panel.current.showModal(); }, []);

  const values = creative.series.get(day);
  return <dialog className="creative-drawer" ref={panel} aria-labelledby="detail-title" onClose={onClose}
    onClick={(event) => { if (event.target === event.currentTarget) panel.current.close(); }}>
    <div className="detail-content">
      <div className="detail-top">
        <div><p className="creative-id">{creative.id} · {creative.assetId}</p><h2 id="detail-title">{creative.headline}</h2></div>
        <button className="icon-button" type="button" aria-label="Chiudi dettaglio" onClick={() => panel.current.close()}>
          <X size={19} aria-hidden="true" />
        </button>
      </div>
      <div className="creative-chips detail-chips">
        {[creative.sector, creative.adsetId, creative.lever, creative.format].map((tag) => <span key={tag}>{tag}</span>)}
        {creative.coldStart && <span>Nuovo annuncio</span>}
      </div>
      <section className="detail-section">
        <h3>Previsione base · {shortDate(day)}</h3>
        {values ? <CreativeMetrics values={values} /> : <p className="explorer-muted">Nessuna previsione per questa data.</p>}
      </section>
      <section className="detail-section">
        <h3>Contenuto dell’asset</h3>
        <dl className="asset-copy">
          <div><dt>Testo</dt><dd>{creative.asset?.body || 'Non disponibile nel kit'}</dd></div>
          <div><dt>Call to action</dt><dd>{creative.asset?.cta || 'Non disponibile nel kit'}</dd></div>
          <div className="asset-description"><dt><FileText size={15} aria-hidden="true" /> Descrizione del visual</dt>
            <dd>{creative.asset?.visual || 'Non disponibile nel kit'}</dd></div>
        </dl>
      </section>
      {feedback && <section className="detail-section">
        <h3>Reazioni simulate · {feedback.n_personas} valutazioni</h3>
        <p className="explorer-muted">Decision · {feedback.model}. La quota stimata di «Apre / clicca» è {pct(feedback.actions.click * 100)}.</p>
        <p className="explorer-muted">{Object.entries(feedback.reason_distribution).sort((a, b) => b[1] - a[1]).slice(0, 3)
          .map(([reason, weight]) => reason.replaceAll('_', ' ') + ' ' + pct(weight * 100)).join(' · ')}</p>
      </section>}
      <DailyTrend creative={creative} dates={dates} day={day} />
      <button type="button" className="explorer-button" aria-pressed={checked} disabled={!checked && !canSelect}
        onClick={() => onCompare(creative.id)}>
        {checked ? 'Rimuovi dal confronto' : 'Aggiungi al confronto'}
      </button>
      {!checked && !canSelect && <p className="explorer-muted">Rimuovi un annuncio dalla selezione per aggiungerne un altro.</p>}
      <p className="explorer-muted"><a className="analysis-link" href={'#/budget?' + new URLSearchParams({
        campaign: creative.campaignId, adset: creative.adsetId, date: day,
      })}>Esplora scenari di budget</a></p>
    </div>
  </dialog>;
}
