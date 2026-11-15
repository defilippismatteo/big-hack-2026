import { useState } from 'react';
import { useDashboardData } from '../data/useDashboardData';
import { ForecastChart } from '../overview/ForecastChart';
import { money, pct, shortDate, verticalNames } from '../overview/model';
import { AnalysisPage, Filter, Panel } from './AnalysisPage';
import { dailyForecast, forecastSelection } from './forecastModel.js';

const variants = { baseline: 'Riferimento · CTR baseline 14g, CPM Timestral-28M', pilot: 'Forecast pilota · CTR baseline, CPM CatBoost + Timestral-28M', enriched: 'Scenario stagionale pilota · benchmark 2025' };

function ForecastContent({ data }) {
  const { data: pilot, phase, retry } = useDashboardData('pilot-forecast.json');
  const [campaign, setCampaign] = useState('');
  const [adset, setAdset] = useState('');
  const [ad, setAd] = useState('');
  const [date, setDate] = useState('');
  const [variant, setVariant] = useState('baseline');
  const [metric, setMetric] = useState('ctr');
  const [cell, setCell] = useState(null);

  const sets = data.adsets.filter((item) => !campaign || item.campaignId === campaign);
  const ads = Object.keys(data.ads).filter((id) => sets.some((set) => set.id === data.ads[id][0]) && (!adset || data.ads[id][0] === adset));
  const dates = date ? [date] : data.dates;
  const scoped = { campaign, adset, ad, dates };
  const rows = forecastSelection(data, pilot, { ...scoped, variant });
  const indexed = new Map(rows.map((item) => [item.id + ':' + item.day, item]));
  const selected = cell && indexed.get(cell);
  const ids = [...new Set(rows.map((row) => row.id))].sort();
  const format = metric === 'ctr' ? pct : money;
  const max = Math.max(1e-8, ...rows.map((item) => item[metric]));
  const compare = pilot && variant !== 'baseline' ? (variant === 'pilot' ? 'enriched' : 'pilot') : null;
  const compareRows = compare ? forecastSelection(data, pilot, { ...scoped, variant: compare }) : [];
  const compareCells = new Map(compareRows.map((row) => [row.id + ':' + row.day, row]));
  const source = variant === 'baseline' ? ' · ADERA ' + data.source.commit.slice(0, 8)
    : ' · Export pilota ' + pilot.commit.slice(0, 8);

  return <>
    <div className="data-panel analysis-filters" role="group" aria-label="Filtri previsioni">
      <Filter label="Campagna" value={campaign} onChange={(id) => { setCampaign(id); setAdset(''); setAd(''); }}
        options={[[ '', 'Tutte' ], ...data.campaigns.map((item) => [item.id, verticalNames[item.vertical] ?? item.name])]} />
      <Filter label="Ad set" value={adset} onChange={(id) => { setAdset(id); setAd(''); }}
        options={[[ '', 'Tutti' ], ...sets.map((item) => [item.id, item.id])]} />
      <Filter label="Annuncio" value={ad} onChange={setAd} options={[[ '', 'Tutti' ], ...ads.map((id) => [id, id])]} />
      <Filter label="Data" value={date} onChange={setDate} options={[[ '', '16–30 nov' ], ...data.dates.map((d) => [d, shortDate(d)])]} />
      <Filter label="Serie" value={variant} onChange={setVariant}
        options={Object.entries(variants).filter(([key]) => key === 'baseline' || pilot)} />
    </div>
    {phase === 'error' && <p className="muted-copy">Export pilota non disponibile. <button className="clear-filters" onClick={retry}>Riprova</button></p>}
    <ForecastChart title="Timeline CTR / CPM" timeline={dailyForecast(rows, dates)} seasonal={[]} events={data.events}
      sourceMethod={variants[variant]} scenario={variant === 'enriched'} note="Rapporti aggregati usando spesa effettiva stimata e quote di pubblicazione del riferimento ADERA." />
    {compare && <ForecastChart title="Serie di confronto" timeline={dailyForecast(compareRows, dates)} seasonal={[]}
      events={data.events} sourceMethod={variants[compare]} scenario={compare === 'enriched'} note="Stessa selezione e stesse ipotesi di spesa della timeline principale." />}
    <Panel title="Heatmap annuncio × giorno" description={rows.length + ' previsioni nella selezione' + source}>
      <div className="segmented" role="group" aria-label="Metrica heatmap">
        {['ctr', 'cpm'].map((key) => <button key={key} type="button" aria-pressed={key === metric}
          onClick={() => setMetric(key)}>{key.toUpperCase()}</button>)}
      </div>
      <p className="muted-copy">Il colore indica il valore relativo al massimo della selezione. Il trattino indica un giorno senza previsione.</p>
      <div className="analysis-scroll" tabIndex={0} role="region" aria-label="Matrice delle previsioni">
        <table className="analysis-table forecast-matrix">
          <thead><tr><th scope="col">Annuncio</th>{dates.map((day) => <th key={day} scope="col" title={data.events[day]}
            className={data.events[day] ? 'event-column' : undefined}>{shortDate(day)}{data.events[day] && <small>{data.events[day]}</small>}</th>)}</tr></thead>
          <tbody>{ids.map((id) => <tr key={id}><th scope="row">{id}{data.ads[id][5] && <small>Nuovo</small>}</th>
            {dates.map((day) => {
              const key = id + ':' + day;
              const item = indexed.get(key);
              return <td key={day}>{item ? <button type="button" title={id + ' · ' + shortDate(day) + ' · ' + format(item[metric])}
                aria-pressed={cell === key} aria-label={id + ', ' + shortDate(day) + ', ' + format(item[metric])}
                style={{ backgroundColor: 'rgba(128,98,227,' + (0.07 + 0.39 * item[metric] / max) + ')' }}
                onClick={() => setCell(key)}>{format(item[metric])}</button> : <span aria-label="Dato assente">—</span>}</td>;
            })}</tr>)}</tbody>
        </table>
      </div>
      {!rows.length && <p className="muted-copy">Nessuna previsione corrisponde ai filtri selezionati.</p>}
    </Panel>
    <div aria-live="polite">{selected && <Panel title={selected.id + ' · ' + shortDate(selected.day)}>
      <p className="muted-copy">{data.ads[selected.id][2]} · {data.ads[selected.id][0]}</p>
      <div className="analysis-stats">
        <div className="analysis-stat"><strong>{pct(selected.ctr)}</strong><span>CTR · {variants[variant]}</span></div>
        <div className="analysis-stat"><strong>{money(selected.cpm)}</strong><span>CPM · {variants[variant]}</span></div>
        {compareCells.has(cell) && <div className="analysis-stat"><strong>{pct(compareCells.get(cell).ctr)} · {money(compareCells.get(cell).cpm)}</strong><span>{variants[compare]}</span></div>}
      </div>
      <a className="analysis-link" href={'#/creatives?ad=' + encodeURIComponent(selected.id) + '&date=' + selected.day}>Apri dettaglio creativo</a>
    </Panel>}</div>
    <p className="muted-copy">Cutoff dei modelli · {shortDate(data.source.cutoff)} 2026. Intervalli calibrati non disponibili.</p>
  </>;
}

export function ForecastAnalytics({ headingRef }) {
  return <AnalysisPage headingRef={headingRef} title="Forecast Analytics" subtitle="Previsioni per annuncio e giorno dal 16 al 30 novembre 2026.">
    {(data) => <ForecastContent data={data} />}
  </AnalysisPage>;
}
