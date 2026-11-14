import {
  ArrowDownRight, ArrowLeftRight, ArrowRight, ArrowUpRight, BarChart3, Layers3,
  LayoutGrid, ListFilter, MousePointer2, Sparkles, UsersRound, WalletCards,
} from 'lucide-react';
import { useEffect, useMemo, useState } from 'react';
import { sectionHref } from '../sections';
import { ForecastChart } from './ForecastChart';
import { fixed, leverNames, modelNames, money, overviewModel, pct, shortDate, verticalNames, whole } from './model';
import './overview.css';

const dataUrl = import.meta.env.BASE_URL + 'data/overview.json';

function useOverviewData() {
  const [state, setState] = useState({ phase: 'loading' });
  const [attempt, setAttempt] = useState(0);
  useEffect(() => {
    const controller = new AbortController();
    async function load() {
      try {
        const response = await fetch(dataUrl, { signal: controller.signal, cache: 'no-cache' });
        if (!response.ok) throw new Error('Dataset non disponibile');
        const data = await response.json();
        if (data?.schemaVersion !== 1 || !Array.isArray(data.forecast) || !Array.isArray(data.budgetScenario)) {
          throw new Error('Versione dei dati non supportata');
        }
        if (!controller.signal.aborted) setState({ phase: 'ready', data });
      } catch {
        if (!controller.signal.aborted) setState({ phase: 'error' });
      }
    }
    load();
    return () => controller.abort();
  }, [attempt]);
  return { ...state, retry: () => { setState({ phase: 'loading' }); setAttempt((n) => n + 1); } };
}

function MetricCard({ icon: Icon, title, value, note, tone }) {
  return (
    <div className="data-panel metric-card">
      <div className="metric-title"><span className={'metric-icon ' + tone}><Icon size={16} strokeWidth={1.9} aria-hidden="true" /></span>
        <span>{title}</span></div>
      <strong className="metric-value">{value}</strong>
      <p>{note}</p>
    </div>
  );
}

function PanelLink({ to, children }) {
  return <a className="panel-link" href={sectionHref(to)}>{children} <ArrowRight size={15} aria-hidden="true" /></a>;
}

function CreativeSpotlight({ creative }) {
  return (
    <section className="data-panel spotlight" aria-labelledby="creative-title">
      <div className="panel-head">
        <div><span className="data-tag tag-forecast">Previsione · 27 nov</span><h2 id="creative-title">Top Creative</h2></div>
        <span className="metric-icon violet"><Sparkles size={19} aria-hidden="true" /></span>
      </div>
      {creative ? <>
        <div className="creative-info">
          <p className="creative-asset">{creative.id} <span>·</span> {creative.assetId}</p>
          <h3>{creative.headline}</h3>
          <div className="creative-chips">
            <span>{leverNames[creative.lever] ?? creative.lever}</span>
            <span>{creative.format}</span>
            {creative.coldStart && <span>Nuovo annuncio</span>}
          </div>
        </div>
        <dl className="paired-metrics">
          <div><dt>CTR previsto</dt><dd>{pct(creative.ctr)}</dd></div>
          <div><dt>CPM previsto</dt><dd>{money(creative.cpm)}</dd></div>
        </dl>
        <p className="support-copy">Il miglior rapporto fra CTR e CPM nella selezione: {fixed(creative.efficiency)} clic stimati per euro speso.</p>
      </> : <p className="panel-empty">Nessuna previsione per il Black Friday nella selezione.</p>}
      <PanelLink to="creatives">Vai a Creative Explorer</PanelLink>
    </section>
  );
}

function AudienceHighlights({ hypotheses, synthetic }) {
  return (
    <section className="data-panel audience-panel" aria-labelledby="audience-title">
      <div className="panel-head">
        <div><span className="data-tag tag-hypothesis">Ipotesi</span><h2 id="audience-title">Audience Insights</h2></div>
        <span className="metric-icon violet"><UsersRound size={19} aria-hidden="true" /></span>
      </div>
      <p className="support-copy">{hypotheses.length
        ? whole(hypotheses.length) + ' ipotesi per gli ad set selezionati. In evidenza quelle con CTR storico più alto.'
        : 'Non ci sono ipotesi per gli ad set selezionati.'}</p>
      <ul className="audience-list">
        {hypotheses.slice(0, 2).map((item) => <li key={item.adsetId}>
          <div className="audience-row"><strong>{item.adsetId}</strong><span>{pct(item.ctr)} CTR storico</span></div>
          <p>{item.description}. Confidenza {item.confidence}.</p>
        </li>)}
      </ul>
      {synthetic?.count > 0
        ? <div className="audience-note">
          <strong>Profili sintetici · distribuzione globale</strong>
          <p>Età: {Object.entries(synthetic.age).map(([band, n]) => band + ' (' + whole(n) + ')').join(' · ')}</p>
          <p>Genere: {Object.entries(synthetic.gender).map(([gender, n]) => gender + ' (' + whole(n) + ')').join(' · ')}</p>
        </div>
        : <p className="audience-note">Nessun profilo sintetico collegato. Il kit non identifica età o genere del pubblico.</p>}
      <PanelLink to="audience">Vai ad Audience Lab</PanelLink>
    </section>
  );
}

function BudgetRecommendation({ budget, bound, singleAdset }) {
  const delta = budget.baseClicks > 0 ? 100 * (budget.scenarioClicks / budget.baseClicks - 1) : null;
  return (
    <section className="data-panel budget-panel" aria-labelledby="budget-title">
      <div className="panel-head">
        <div><span className="data-tag tag-scenario">Scenario</span><h2 id="budget-title">Budget Recommendation</h2></div>
        <span className="metric-icon mint"><ArrowLeftRight size={19} aria-hidden="true" /></span>
      </div>
      <dl className="paired-metrics budget-metrics">
        <div><dt>Budget pianificato</dt><dd>{money(budget.original / 100)}</dd></div>
        <div><dt>Scenario alternativo</dt><dd>{money(budget.proposed / 100)}</dd></div>
      </dl>
      {budget.positive && budget.negative && <div className="moves">
        <span><ArrowUpRight size={15} aria-hidden="true" />{budget.positive.id} <strong>+{money(budget.positive.delta / 100)}</strong></span>
        <span><ArrowDownRight size={15} aria-hidden="true" />{budget.negative.id} <strong>−{money(-budget.negative.delta / 100)}</strong></span>
      </div>}
      <p className="support-copy">{singleAdset
        ? 'Vista del singolo ad set. Il totale resta invariato nel perimetro della campagna.'
        : budget.reallocated > 0 ? 'Trasferimenti netti fra ad set nel periodo: ' + money(budget.reallocated / 100) + '.'
          : 'Nessuna riallocazione netta nel periodo per la selezione.'}
        {' '}Lo scenario privilegia gli ad set con più clic stimati per euro, entro ±{whole(bound * 100)}% per ad set al giorno.</p>
      {delta != null && <p className="budget-delta"><strong>{delta > 0 ? '+' : ''}{pct(delta)}</strong> clic stimati rispetto al budget pianificato</p>}
      <p className="chart-note">Stima condizionale con pacing e quote di pubblicazione invariati.</p>
      <PanelLink to="budget">Vai a Budget Planner</PanelLink>
    </section>
  );
}

export function Overview({ headingRef }) {
  const { phase, data, retry } = useOverviewData();
  const [campaign, setCampaign] = useState('');
  const [adset, setAdset] = useState('');
  const model = useMemo(() => data && overviewModel(data, campaign, adset), [data, campaign, adset]);
  const method = data && (modelNames[data.source.method] ?? data.source.method);
  const activeFilters = Boolean(campaign || adset);
  return (
    <div className="overview">
      <div className="overview-title">
        <p className="overview-kicker"><span aria-hidden="true" /> Analisi campagne</p>
        <h1 id="page-title" ref={headingRef} tabIndex={-1}>Overview</h1>
        <p>Performance delle campagne e decisioni per il Black Friday.</p>
      </div>
      {phase === 'loading' && <p className="data-panel feedback-state" role="status">Caricamento dell’Overview…</p>}
      {phase === 'error' && <div className="data-panel feedback-state" role="alert">
        <p>Impossibile caricare l’Overview. Verifica che sia disponibile l’export dei dati.</p>
        <button type="button" className="primary-button" onClick={retry}>Riprova</button>
      </div>}
      {model && <>
        <div className="overview-filters" aria-label="Filtri Overview" role="group">
          <span className="filter-title"><ListFilter size={17} aria-hidden="true" /> Filtri</span>
          <label><span>Campagna</span>
            <select value={campaign} onChange={(e) => { setCampaign(e.target.value); setAdset(''); }}>
              <option value="">Tutte le campagne</option>
              {data.campaigns.map((r) => <option key={r.id} value={r.id}>{verticalNames[r.vertical] ?? r.name}</option>)}
            </select>
          </label>
          <label><span>Ad set</span>
            <select value={adset} onChange={(e) => setAdset(e.target.value)}>
              <option value="">Tutti gli ad set</option>
              {model.adsets.map((r) => <option key={r.id} value={r.id}>{r.id}</option>)}
            </select>
          </label>
          {activeFilters && <button type="button" className="clear-filters"
            onClick={() => { setCampaign(''); setAdset(''); }}>Ripristina filtri</button>}
        </div>
        <section className="metric-grid" aria-label="Indicatori chiave">
          <MetricCard icon={LayoutGrid} tone="violet" title="Campagne" value={whole(model.campaignCount)} note="Meta · kit Wevion" />
          <MetricCard icon={Layers3} tone="blue" title="Ad set" value={whole(model.adsetCount)} note="Gruppi di annunci" />
          <MetricCard icon={BarChart3} tone="violet" title="Previsioni" value={whole(model.predictionCount)} note="Righe annuncio / giorno" />
          <MetricCard icon={UsersRound} tone="mint" title="Profili sintetici"
            value={data.synthetic ? whole(data.synthetic.count) : '—'} note={data.synthetic ? 'Schede caricate · tutte le campagne' : 'Nessun export collegato'} />
          <MetricCard icon={MousePointer2} tone="blue" title="CTR storico" value={pct(model.observed.ctr)} note="Ponderato per impression" />
          <MetricCard icon={WalletCards} tone="sand" title="CPM storico" value={money(model.observed.cpm)} note="Costo per 1.000 impression" />
        </section>
        <div className="overview-grid first-row">
          <ForecastChart timeline={model.timeline} seasonal={model.seasonal} events={data.events} sourceMethod={method} />
          <CreativeSpotlight creative={model.best} />
        </div>
        <div className="overview-grid second-row">
          <AudienceHighlights hypotheses={model.hypotheses} synthetic={data.synthetic} />
          <BudgetRecommendation budget={model.budget} bound={data.source.budgetBound} singleAdset={Boolean(adset)} />
        </div>
        <p className="overview-source">Dati del kit simulato Wevion · Storico fino al {shortDate(data.source.cutoff)} 2026 · Output Market Mirror {data.source.commit.slice(0, 7)}.</p>
      </>}
    </div>
  );
}
