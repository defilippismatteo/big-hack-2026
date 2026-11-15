import {
  ArrowDownRight, ArrowLeftRight, ArrowRight, ArrowUpRight, BarChart3, Layers3,
  LayoutGrid, ListFilter, MousePointer2, Sparkles, UsersRound, WalletCards,
} from 'lucide-react';
import { useMemo, useState } from 'react';
import { useDashboardData } from '../data/useDashboardData';
import { sectionHref } from '../sections';
import { ForecastChart } from './ForecastChart';
import { fixed, leverNames, modelNames, money, overviewModel, pct, shortDate, verticalNames, whole } from './model';
import './overview.css';
import { DecisionBrief, CampaignDecisions } from './DecisionBrief';

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

function PanelLink({ to, href = sectionHref(to), children }) {
  return <a className="panel-link" href={href}>{children} <ArrowRight size={15} aria-hidden="true" /></a>;
}

function CreativeSpotlight({ creative }) {
  return (
    <section className="data-panel spotlight" aria-labelledby="creative-title">
      <div className="panel-head">
        <div><span className="data-tag tag-forecast">Previsione · 27 nov</span><h2 id="creative-title">Creatività da approfondire</h2></div>
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
          <div><dt>Clic per 100 visualizzazioni (CTR)</dt><dd>{pct(creative.ctr)}</dd></div>
          <div><dt>Costo di 1.000 visualizzazioni</dt><dd>{money(creative.cpm)}</dd></div>
        </dl>
        <p className="support-copy">Il miglior rapporto fra CTR e CPM nella selezione: {fixed(creative.efficiency)} clic stimati per euro speso.</p>
      </> : <p className="panel-empty">Nessuna previsione per il Black Friday nella selezione.</p>}
      <PanelLink to="creatives" href={creative ? sectionHref('creatives') + '?ad=' + encodeURIComponent(creative.id) : undefined}>
        {creative ? 'Apri il dettaglio creativo' : 'Vai a Creative Explorer'}
      </PanelLink>
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
        ? whole(hypotheses.length) + ' ipotesi per gli ad set selezionati. In evidenza quelle con CTR nello storico più alto.'
        : 'Non ci sono ipotesi per gli ad set selezionati.'}</p>
      <ul className="audience-list">
        {hypotheses.slice(0, 2).map((item) => <li key={item.adsetId}>
          <div className="audience-row"><strong>{item.adsetId}</strong><span>{pct(item.ctr)} CTR nello storico</span></div>
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
  const { phase, data, retry } = useDashboardData();
  const [campaign, setCampaign] = useState('');
  const [adset, setAdset] = useState('');
  const model = useMemo(() => data && overviewModel(data, campaign, adset), [data, campaign, adset]);
  const method = data && (modelNames[data.source.method] ?? data.source.method);
  const activeFilters = Boolean(campaign || adset);
  return (
    <div className="overview">
      <div className="overview-title">
        <div><p className="overview-kicker"><span aria-hidden="true" /> Analisi campagne</p>
        <h1 id="page-title" ref={headingRef} tabIndex={-1}>Dove investire, e perché.</h1>
        <p className="overview-description">ADERA confronta previsioni, budget e reazioni di persone sintetiche per preparare le campagne del Black Friday.</p></div>
        <span className="overview-status">Dataset simulato · Challenge Wevion</span>
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
        <DecisionBrief data={data} campaign={campaign} adset={adset} />
        <section className="metric-grid" aria-label="Indicatori chiave">
          <MetricCard icon={LayoutGrid} tone="violet" title="Campagne" value={whole(model.campaignCount)} note="Meta · kit Wevion" />
          <MetricCard icon={Layers3} tone="blue" title="Ad set" value={whole(model.adsetCount)} note="Gruppi di annunci" />
          <MetricCard icon={BarChart3} tone="violet" title="Previsioni" value={whole(model.predictionCount)} note="Righe annuncio / giorno" />
          <MetricCard icon={UsersRound} tone="mint" title="Profili sintetici"
            value={data.synthetic ? whole(data.synthetic.count) : '—'} note={data.synthetic ? 'Schede caricate · tutte le campagne' : 'Nessun export collegato'} />
          <MetricCard icon={MousePointer2} tone="blue" title="CTR nello storico" value={pct(model.observed.ctr)} note="Ponderato per impression" />
          <MetricCard icon={WalletCards} tone="sand" title="CPM nello storico" value={money(model.observed.cpm)} note="Costo per 1.000 impression" />
        </section>
        <div className="overview-grid first-row">
          <ForecastChart timeline={model.timeline} seasonal={model.seasonal} events={data.events} sourceMethod={method} />
          <CreativeSpotlight creative={model.best} />
        </div>
        <CampaignDecisions data={data} campaign={campaign} />
        <div className="product-explainer"><div><UsersRound size={22}/><h2>Cosa sono le nostre buyer persona?</h2><p>{data.synthetic?.count ?? 0} profili di persone inventate, con abitudini, bisogni e obiezioni diverse. Valutano gli annunci e aiutano a formulare domande e test: non sono clienti reali.</p><a className="panel-link" href="#/audience">Guarda un profilo e le reazioni <ArrowRight size={15}/></a></div><div><BarChart3 size={22}/><h2>Quanto fidarsi dei numeri?</h2><p>Le previsioni sono verificate su due finestre passate. Non abbiamo risultati futuri del Black Friday né intervalli d’incertezza calibrati. Il kit stesso è simulato.</p><a className="panel-link" href="#/validation">Esamina il confronto fra modelli <ArrowRight size={15}/></a></div></div>
        <p className="overview-source">Dati del kit simulato Wevion · Storico fino al {shortDate(data.source.cutoff)} 2026 · Output Market Mirror {data.source.commit.slice(0, 7)}.</p>
      </>}
    </div>
  );
}
