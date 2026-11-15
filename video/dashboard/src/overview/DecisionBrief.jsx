import { ArrowRight, ArrowRightLeft, Database, FlaskConical, TrendingUp, ShieldCheck } from 'lucide-react';
import { overviewModel, money, whole, pct, verticalNames } from './model';
import { useDashboardData } from '../data/useDashboardData';
import { chartDomain } from './chartModel';

export function DecisionBrief({ data, campaign, adset }) {
  const {data:validation} = useDashboardData('model-validation.json');
  const errors=validation?.combined;
  const m = overviewModel(data,campaign,adset);
  const delta=m.budget.scenarioClicks-m.budget.baseClicks;
  const costs=m.timeline.filter(d=>Number.isFinite(d.cpm));
  const domain=chartDomain(costs.map(d=>d.cpm));
  const points=costs.map((d,i)=>`${4+i/Math.max(1,costs.length-1)*292},${60-(d.cpm-domain.min)/(domain.max-domain.min)*50}`).join(' ');
  const uplift=m.budget.baseClicks>0?100*delta/m.budget.baseClicks:0;
  return <section className="decision-brief" aria-labelledby="decision-brief-title">
    <div className="decision-brief-main"><span className="data-tag tag-scenario"><ArrowRightLeft size={13} aria-hidden="true"/> Piano suggerito · 16–30 novembre</span><h2 id="decision-brief-title">Riallocare, senza aumentare il budget.</h2>
      <div className="brief-numbers"><div><strong>{money(m.budget.original/100)}</strong><span>budget pianificato</span></div><div><strong>+{whole(delta)} clic</strong><span>stimati nello scenario · +{pct(uplift)}</span></div></div>
      <p>Spostiamo budget verso i gruppi con più clic previsti per euro. Limite ±{whole(data.source.budgetBound*100)}% al giorno, senza aumentare il budget della campagna.</p>
      {adset&&<p className="scope-notice">Stai guardando un singolo gruppo: il totale si conserva sull’intera campagna, non sul gruppo.</p>}
      {costs.length>0&&<div className="brief-trend"><div><span>Costo previsto di 1.000 visualizzazioni</span><strong>{money(Math.min(...costs.map(d=>d.cpm)))} – {money(Math.max(...costs.map(d=>d.cpm)))}</strong></div><svg viewBox="0 0 300 70" preserveAspectRatio="none" role="img" aria-label="Andamento CPM previsto 16–30 novembre, scala di dettaglio"><polyline points={points} fill="none" stroke="currentColor" strokeWidth="2.5" vectorEffect="non-scaling-stroke"/></svg><div><span>16 novembre</span><span>Scala di dettaglio · 30 novembre</span></div></div>}
      <a className="panel-link" href={'#/budget'+(campaign?'?campaign='+campaign:'')}>Esplora il piano e cambia gli importi <ArrowRight size={15}/></a>
    </div>
    <div className="decision-brief-why"><h3>Perché questa raccomandazione?</h3>
      <ol className="method-steps"><li><Database size={18}/><div><strong>Partiamo dai dati</strong><span>91 giorni di costi, visualizzazioni e clic dal kit.</span></div></li><li><TrendingUp size={18}/><div><strong>Prevediamo giorno per giorno</strong><span>Nel primo test fra questi due metodi: baseline più precisa sul CTR, Timestral sul CPM. {whole(m.predictionCount)} righe nella selezione.</span></div></li><li><FlaskConical size={18}/><div><strong>Confrontiamo due piani</strong><span>Budget originale e riallocazione, a pubblicazione invariata.</span></div></li></ol>
      <p className="decision-caveat"><ShieldCheck size={15}/> Incremento non garantito. I segnali sintetici non modificano il forecast.</p>
      {errors&&<div className="visible-error"><strong>Errori storici globali dei componenti usati</strong><span>CTR baseline: {errors.ctr_baseline.wmae.toLocaleString('it-IT',{maximumFractionDigits:3})} punti percentuali · CPM Timestral: {money(errors.cpm_timestral_28m.wmae)}</span><small>Errori pesati su {whole(errors.righe)} righe passate. Non sono intervalli futuri o prove del beneficio budget.</small></div>}
      <a className="panel-link" href="#/validation">Vedi errori storici e limiti <ArrowRight size={15}/></a>
    </div>
  </section>;
}

export function CampaignDecisions({ data, campaign }) {
  return <section aria-labelledby="campaign-decisions-title"><div className="section-line"><h2 id="campaign-decisions-title">Tre campagne, decisioni da esplorare</h2><span>Apri una campagna per capire il pubblico</span></div><div className="campaign-decision-grid">{data.campaigns.filter(c=>!campaign||c.id===campaign).map(c=>{
    const m=overviewModel(data,c.id,'');
    return <a className="campaign-decision" key={c.id} href={'#/audience?campaign='+c.id}><div className="campaign-decision-name"><strong>{verticalNames[c.vertical]}</strong><ArrowRight size={18}/></div><span>{c.id} · {m.adsetCount} gruppi di annunci</span><div><strong>{money(m.budget.original/100)}</strong><span>budget del periodo</span></div><p>{m.budget.positive ? <>Più spazio a <b>{m.budget.positive.id}</b>: +{money(m.budget.positive.delta/100)}.</> : 'Apri il dettaglio della campagna.'}</p><span className="campaign-cta">Apri pubblico e insight</span></a>;
  })}</div></section>;
}
