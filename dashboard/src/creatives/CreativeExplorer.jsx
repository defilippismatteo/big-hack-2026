import { ArrowDown, ArrowLeftRight, ArrowUp, ArrowUpDown, ArrowUpRight, CalendarDays, Search, X } from 'lucide-react';
import { useEffect, useMemo, useRef, useState, useSyncExternalStore } from 'react';
import { useDashboardData } from '../data/useDashboardData';
import { sectionHref } from '../sections';
import { fixed, modelNames, money, pct, shortDate, verticalNames } from '../overview/model';
import { CreativeDetail, CreativeMetrics } from './CreativeDetail';
import { PerformanceMap } from './PerformanceMap';
import { creativeCatalog, creativesForDay, sortCreatives } from './model';
import './creatives.css';

const columns = [
  { key: 'id', label: 'Annuncio' },
  { key: 'ctr', label: 'CTR', format: pct, direction: -1 },
  { key: 'cpm', label: 'CPM', format: money, direction: 1 },
  { key: 'efficiency', label: 'Click stimati/€', format: (value) => value == null ? '—' : fixed(value), direction: -1 },
  { key: 'cpc', label: 'CPC', format: money, direction: 1 },
  { key: 'assetId', label: 'Asset' },
  { key: 'sector', label: 'Settore' },
  { key: 'lever', label: 'Leva' },
  { key: 'format', label: 'Formato' },
];

function subscribeHash(listener) {
  window.addEventListener('hashchange', listener);
  return () => window.removeEventListener('hashchange', listener);
}

const getHash = () => window.location.hash;

function Ranking({ rows, sort, onSort, selected, onCompare, onOpen, onViewComparison }) {
  return <section className="data-panel ranking-panel" aria-labelledby="ranking-title">
    <div className="explorer-panel-header">
      <div><h2 id="ranking-title" tabIndex={-1}>Tutti gli annunci</h2><p>Seleziona due annunci per confrontarli sulla stessa data.</p></div>
      <div className="ranking-actions">
        <span className="result-count" aria-live="polite">{rows.length} {rows.length === 1 ? 'annuncio' : 'annunci'}</span>
        {selected.length > 0 && <button type="button" className="comparison-jump" onClick={onViewComparison}>
          {selected.length}/2 al confronto <ArrowDown size={13} aria-hidden="true" />
        </button>}
      </div>
    </div>
    <p className="table-scroll-help">Scorri la tabella in orizzontale per vedere tutti i dettagli. Le stime principali sono già nella scheda annuncio.</p>
    {rows.length ? <div className="ranking-scroll" role="region" aria-label="Tabella delle previsioni"
      tabIndex={0}>
      <table className="ranking-table">
        <thead><tr>
          <th scope="col" className="compare-column"><span className="sr-only">Confronto</span></th>
          {columns.map(({ key, label, direction = 1 }) => {
            const active = sort.key === key;
            const Icon = !active ? ArrowUpDown : sort.direction === 1 ? ArrowUp : ArrowDown;
            const sortOrder = sort.direction === 1 ? 'ascending' : 'descending';
            return <th key={key} scope="col" aria-sort={active ? sortOrder : undefined}>
              <button type="button" onClick={() => onSort({ key, direction: active ? -sort.direction : direction })}
                aria-label={'Ordina per ' + label}>{label}<Icon size={12} aria-hidden="true" /></button>
            </th>;
          })}
        </tr></thead>
        <tbody>{rows.map((row) => {
          const checked = selected.includes(row.id);
          return <tr key={row.id} data-selected={checked}>
            <td className="compare-column"><input type="checkbox" checked={checked} disabled={!checked && selected.length >= 2}
              aria-label={'Confronta ' + row.id} onChange={() => onCompare(row.id)} /></td>
            <th scope="row">
              <button className="ranking-open" type="button" onClick={(event) => onOpen(row.id, event.currentTarget)}>
                <span>{row.headline} <ArrowUpRight size={13} aria-hidden="true" /></span>
                <small>{row.id} · {row.adsetId}{row.coldStart && <em>Nuovo</em>}</small>
              </button>
            </th>
            {columns.slice(1).map(({ key, format }) => <td key={key} className={format ? 'rank-value' : undefined}>
              {key === 'sector' ? <span className="sector-label" data-tone={row.tone}>{row[key]}</span>
                : format ? format(row[key]) : row[key]}
            </td>)}
          </tr>;
        })}</tbody>
      </table>
    </div> : <p className="panel-empty">Nessun annuncio corrisponde ai filtri.</p>}
    <p className="explorer-muted">Il CPC è derivato da CPM ÷ (10 × CTR in percentuale). Se il CTR è zero, il CPC non è calcolabile.</p>
  </section>;
}

function Comparison({ items, day, onCompare, onOpen, onReset }) {
  const ctrDelta = items.length === 2 && items[0].series.has(day) && items[1].series.has(day)
    ? items[1].series.get(day).ctr - items[0].series.get(day).ctr : null;
  const deltaText = ctrDelta == null ? null
    : new Intl.NumberFormat('it-IT', { maximumFractionDigits: 2, signDisplay: 'exceptZero' }).format(ctrDelta);
  return <section className="data-panel creative-comparison" aria-labelledby="comparison-title">
    <div className="explorer-panel-header">
      <div><h2 id="comparison-title" tabIndex={-1}>Confronta annunci</h2><p>Previsione base · {shortDate(day)}</p></div>
      <button type="button" className="comparison-jump" onClick={onReset}><ArrowLeftRight size={14} aria-hidden="true" /> Azzera confronto</button>
    </div>
    <div className="comparison-grid">
      {items.map((item) => <article key={item.id} className="comparison-card">
        <div className="comparison-head">
          <button type="button" className="ranking-open" onClick={(event) => onOpen(item.id, event.currentTarget)}>
            <small>{item.id} · {item.assetId}</small><span>{item.headline}<ArrowUpRight size={13} aria-hidden="true" /></span>
          </button>
          <button type="button" className="icon-button" aria-label={'Rimuovi ' + item.id + ' dal confronto'}
            onClick={() => onCompare(item.id)}><X size={16} aria-hidden="true" /></button>
        </div>
        <p className="explorer-muted">{item.sector} · {item.lever} · {item.format}</p>
        {item.series.has(day) ? <CreativeMetrics values={item.series.get(day)} />
          : <p className="panel-empty">Nessuna previsione per questa data.</p>}
      </article>)}
      {items.length === 1 && <p className="compare-empty">Seleziona un secondo annuncio dalla classifica.</p>}
    </div>
    {deltaText != null && <p className="explorer-muted">{items[1].id} rispetto a {items[0].id} · {deltaText} punti percentuali di CTR previsto.</p>}
  </section>;
}

function ExplorerContent({ data, headingRef }) {
  const { data: story } = useDashboardData('product-story.json');
  const catalog = useMemo(() => creativeCatalog(data), [data]);
  const hash = useSyncExternalStore(subscribeHash, getHash);
  const linkedAd = new URLSearchParams(hash.split('?')[1]).get('ad');
  const [dismissedHash, setDismissedHash] = useState(null);
  const [detail, setDetail] = useState(null);
  const openedFrom = useRef(null);
  const defaultDay = data.dates.find((date) => data.events[date] === 'Black Friday') ?? data.dates[0];
  const [day, setDay] = useState(() => {
    const fromUrl = new URLSearchParams(hash.split('?')[1]).get('date');
    return data.dates.includes(fromUrl) ? fromUrl : defaultDay;
  });
  const [campaign, setCampaign] = useState(() => {const id=new URLSearchParams(hash.split('?')[1]).get('campaign');return data.campaigns.some(c=>c.id===id)?id:'';});
  const [preview, setPreview] = useState(null);
  const [adset, setAdset] = useState(() => {
    const id = new URLSearchParams(hash.split('?')[1]).get('adset');
    return data.adsets.some((item) => item.id === id) ? id : '';
  });
  const [query, setQuery] = useState(() => new URLSearchParams(hash.split('?')[1]).get('asset') ?? '');
  const [sort, setSort] = useState({ key: 'efficiency', direction: -1 });
  const [selected, setSelected] = useState([]);
  const matchesDay = useMemo(() => creativesForDay(catalog, day), [catalog, day]);
  const term = query.trim().toLocaleLowerCase('it');
  const filtered = matchesDay.filter((r) => (!campaign || r.campaignId === campaign) && (!adset || r.adsetId === adset)
    && [r.id, r.assetId, r.adsetId, r.headline, r.lever, r.format].some((value) => value.toLocaleLowerCase('it').includes(term)));
  const rows = sortCreatives(filtered, sort);
  const previewAd = filtered.find(r=>r.id===preview) ?? sortCreatives(filtered,{key:'efficiency',direction:-1})[0];
  const detailAd = catalog.get(detail ?? (dismissedHash === hash ? null : linkedAd));
  const method = modelNames[data.source.method] ?? data.source.method;

  useEffect(() => {
    if (!linkedAd) setDismissedHash(null);
  }, [linkedAd]);

  function openDetail(id, element) {
    openedFrom.current = element;
    setDetail(id);
  }

  function closeDetail() {
    if (linkedAd) {
      setDismissedHash(hash);
      window.location.replace(sectionHref('creatives'));
    }
    setDetail(null);
    (openedFrom.current?.isConnected ? openedFrom.current : headingRef.current)?.focus({ preventScroll: true });
    openedFrom.current = null;
  }

  function toggleCompare(id) {
    setSelected((previous) => {
      if (previous.includes(id)) return previous.filter((item) => item !== id);
      return previous.length < 2 ? [...previous, id] : previous;
    });
  }

  return <>
    <div className="creative-filters" role="group" aria-label="Filtri creatività">
      <label><span><CalendarDays size={15} aria-hidden="true" /> Data</span>
        <select value={day} onChange={(event) => setDay(event.target.value)}>
          {data.dates.map((date) => <option key={date} value={date}>
            {shortDate(date)}{data.events[date] ? ' · ' + data.events[date] : ''}
          </option>)}
        </select>
      </label>
      <label><span>Campagna</span>
        <select value={campaign} onChange={(event) => { setCampaign(event.target.value); setAdset(''); }}>
          <option value="">Tutte le campagne</option>
          {data.campaigns.map((item) => <option key={item.id} value={item.id}>{verticalNames[item.vertical] ?? item.name}</option>)}
        </select>
      </label>
      <label><span>Ad set</span>
        <select value={adset} onChange={(event) => setAdset(event.target.value)}>
          <option value="">Tutti gli ad set</option>
          {data.adsets.filter((item) => !campaign || item.campaignId === campaign).map((item) =>
            <option key={item.id} value={item.id}>{item.id}</option>)}
        </select>
      </label>
      <label className="search-field"><span>Cerca</span>
        <span className="search-input"><Search size={17} aria-hidden="true" />
          <input type="search" placeholder="Headline, ID, leva o formato" value={query}
            onChange={(event) => setQuery(event.target.value)} />
        </span>
      </label>
      {(campaign || adset || query || day !== defaultDay) &&
        <button type="button" className="clear-filters" onClick={() => {
          setCampaign(''); setAdset(''); setQuery('');
          setDay(defaultDay);
        }}>Ripristina filtri</button>}
    </div>
    <section className="creative-picks" aria-labelledby="creative-picks-title"><div className="section-line"><h2 id="creative-picks-title">Da quali annunci partire?</h2><span>Più clic previsti per euro · {shortDate(day)}</span></div><div className="creative-pick-grid">{sortCreatives(filtered,{key:'efficiency',direction:-1}).slice(0,3).map((r,i)=><button type="button" className="creative-pick" key={r.id} aria-pressed={previewAd?.id===r.id} onClick={()=>setPreview(r.id)}><span className="pick-rank">{i===0?'Migliore resa stimata':'Alternativa da confrontare'}</span><strong>{r.headline}</strong><span>{r.sector} · {r.id}</span><div><b>{fixed(r.efficiency)} clic / €</b><span>CTR {pct(r.ctr)} · CPM {money(r.cpm)}</span></div><span className="campaign-cta">Mostra la scheda <ArrowUpRight size={15}/></span></button>)}</div><p className="explorer-muted">Classifica di stime, non di risultati misurati. Non include margini d’errore calibrati.</p></section>
    <div className="creative-workbench"><PerformanceMap rows={filtered} domain={matchesDay} onPreview={setPreview} previewId={previewAd?.id}/><aside className="data-panel creative-live-preview" aria-label="Anteprima annuncio selezionato">{previewAd ? <><span className="data-tag tag-forecast">Anteprima · {shortDate(day)}</span><p className="creative-preview-id">{previewAd.id} · {previewAd.adsetId}</p><h2>{previewAd.headline}</h2><div className="creative-chips"><span>{previewAd.sector}</span><span>{previewAd.format}</span><span>{previewAd.lever}</span></div><p className="preview-copy">{previewAd.asset?.body ?? 'Testo non disponibile.'}</p><dl className="preview-key-metrics"><div><dt>Clic per 100 visualizzazioni</dt><dd>{pct(previewAd.ctr)} <small>CTR</small></dd></div><div><dt>Costo di 1.000 visualizzazioni</dt><dd>{money(previewAd.cpm)} <small>CPM</small></dd></div><div><dt>Resa per euro speso</dt><dd>{fixed(previewAd.efficiency)} <small>clic stimati</small></dd></div></dl><div className="insight-next"><p><strong>Come leggere questa scelta</strong>Il rapporto fra CTR e costo produce {fixed(previewAd.efficiency)} clic stimati per euro. È un criterio di confronto per questa data, non una promessa di rendimento.</p></div><button type="button" className="primary-button" onClick={e=>openDetail(previewAd.id,e.currentTarget)}>Apri contenuto e analisi <ArrowUpRight size={16}/></button></> : <p>Nessun annuncio corrisponde ai filtri. Prova a rimuoverli.</p>}</aside></div>
    {selected.length > 0 && <Comparison items={selected.map((id) => catalog.get(id))}
      day={day} onCompare={toggleCompare} onOpen={openDetail} onReset={() => { setSelected([]); document.getElementById('ranking-title')?.focus(); }} />}
    <details className="data-panel evidence-details ranking-disclosure"><summary>Confronta tutti i {rows.length} annunci <ArrowDown size={16}/></summary>
    <Ranking rows={rows} sort={sort} onSort={setSort} selected={selected} onCompare={toggleCompare} onOpen={openDetail}
      onViewComparison={() => {
        const title = document.getElementById('comparison-title');
        title?.scrollIntoView({ block: 'start' });
        title?.focus({ preventScroll: true });
      }} />
    </details>
    <div className="creative-source explorer-muted">
      {method} · {catalog.size} annunci con forecast nel periodo · Kit simulato Wevion
    </div>
    {detailAd && <CreativeDetail key={detailAd.id} creative={detailAd} feedback={data.simulatedDecision?.[detailAd.assetId]} interviewFeedback={story?.assetInterviews?.[detailAd.assetId]} day={day} dates={data.dates}
      checked={selected.includes(detailAd.id)} canSelect={selected.length < 2}
      onCompare={toggleCompare} onClose={closeDetail} />}
  </>;
}

export function CreativeExplorer({ headingRef }) {
  const { phase, data, retry } = useDashboardData();
  return <div className="creative-explorer">
    <div className="overview-title">
      <h1 id="page-title" ref={headingRef} tabIndex={-1}>Scegliere le creatività</h1>
      <p>Parti dalle proposte più efficienti. Esplora ogni annuncio sulla mappa e leggi subito il suo contenuto.</p>
    </div>
    {phase === 'loading' && <p className="data-panel feedback-state" role="status">Caricamento degli annunci…</p>}
    {phase === 'error' && <div className="data-panel feedback-state" role="alert">
      <p>Impossibile caricare gli annunci.</p>
      <button type="button" className="primary-button" onClick={retry}>Riprova</button>
    </div>}
    {data && <ExplorerContent data={data} headingRef={headingRef} />}
  </div>;
}
