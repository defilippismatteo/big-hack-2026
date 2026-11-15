import { useState } from 'react';
import { useDashboardData } from '../data/useDashboardData';
import { shortDate, verticalNames, whole } from '../overview/model';
import { AnalysisPage, Filter, Panel } from './AnalysisPage';

const models = { baseline: 'Baseline 14 giorni', catboost: 'CatBoost', timestral_28m: 'Timestral-28M',
  mix_50_50: 'Media 50/50 CatBoost–Timestral' };
const errorFormat = new Intl.NumberFormat('it-IT', { minimumFractionDigits: 4, maximumFractionDigits: 4 });

function ModelBars({ results, metric, target }) {
  const rows = Object.entries(models).map(([key, label]) => [label, results[target + '_' + key]?.[metric]]);
  const max = Math.max(0.001, ...rows.map(([, n]) => n ?? 0));
  const unit = target === 'ctr' ? ' pp' : ' €';
  return <Panel title={metric.toUpperCase() + ' ' + target.toUpperCase()} description={target === 'ctr' ? 'Errore in punti percentuali.' : 'Errore in euro per 1.000 impression.'}>
    <div className="analysis-bars validation-bars">{rows.map(([label, n]) => <div className="validation-bar" key={label}>
      <div><span>{label}</span><strong>{n == null ? '—' : errorFormat.format(n) + unit}</strong></div>
      {n != null && <meter value={n} max={max} aria-label={label + unit}>{n}</meter>}
    </div>)}</div>
  </Panel>;
}

function ValidationContent({ baseline }) {
  const [window, setWindow] = useState('combined');
  const [slice, setSlice] = useState('all');
  const [metric, setMetric] = useState('mae');
  const fold = baseline.folds.find((item) => item.dal === window);
  const slices = fold
    ? [['all', 'Tutti'], ['annunci_nuovi', 'Annunci nuovi'], ['annunci_gia_visti', 'Annunci con storico'],
      ...Object.keys(fold.settori).map((key) => [key, verticalNames[key] ?? key])]
    : [['all', 'Tutte le righe']];
  const results = !fold ? baseline.combined : slice === 'all' ? fold.tutti : fold[slice] ?? fold.settori[slice];

  return <>
    <div className="data-panel analysis-filters" role="group" aria-label="Filtri backtest">
      <Filter label="Finestra" value={window} onChange={(value) => { setWindow(value); setSlice('all'); }}
        options={[[ 'combined', 'Due finestre · ' + whole(baseline.combined.righe) + ' righe' ], ...baseline.folds.map((f) => [f.dal, shortDate(f.dal) + ' – ' + shortDate(f.al)])]} />
      <Filter label="Campione" value={slice} onChange={setSlice} options={slices} />
      <Filter label="Metrica" value={metric} onChange={setMetric}
        options={[[ 'mae', 'MAE · errore assoluto medio' ], ['wmae', 'WMAE · pesato per impression']]} />
    </div>
    <p className="muted-copy">{whole(results.righe)} righe annuncio–giorno · {whole(results.impression)} impression{fold && ' · Cutoff ' + shortDate(fold.cutoff)}. Un errore più basso indica stime più vicine ai valori del kit in questa finestra.</p>
    <div className="analysis-grid"><ModelBars results={results} metric={metric} target="ctr" /><ModelBars results={results} metric={metric} target="cpm" /></div>
    <Panel title="Backtest cronologici">
      <div className="analysis-grid">{baseline.folds.map((f) => <article className="audience-card" key={f.dal}>
        <h3>{shortDate(f.dal)} – {shortDate(f.al)}</h3>
        <p className="muted-copy">Cutoff · {shortDate(f.cutoff)} · {whole(f.righe_train)} righe di training · {whole(f.tutti.righe)} di test</p>
        <button className="clear-filters" type="button" onClick={() => { setWindow(f.dal); setSlice('annunci_nuovi'); }}>
          Vedi {whole(f.annunci_nuovi.righe)} righe su annunci nuovi
        </button>
      </article>)}</div>
    </Panel>
    <Panel title="Provenienza e limiti">
      <p className="muted-copy">Backtest sullo storico simulato Wevion fino al 15 novembre. Le finestre precedono il Black Friday e il Cyber Monday. Le impression del test entrano soltanto nel calcolo del WMAE.</p>
      <p className="muted-copy">CatBoost {baseline.versions.CatBoost} · PyTorch {baseline.versions.PyTorch} · Pesi Timestral {baseline.modelHash.slice(0, 12)}.</p>
      <a className="analysis-link" href={'https://github.com/defilippismatteo/big-hack-2026/blob/' + baseline.commit + '/Prima_Analisi/Validazione_Modelli/README.md'}>Protocollo e risultati pubblicati</a>
    </Panel>
  </>;
}

export function ModelValidation({ headingRef }) {
  const { data, phase, retry } = useDashboardData('model-validation.json');
  return <AnalysisPage headingRef={headingRef} title="Model Validation" subtitle="Errori a confronto sulle stesse finestre temporali.">
    {() => phase === 'loading' ? <p role="status">Caricamento delle metriche…</p>
      : phase === 'ready' && data?.folds?.length === 2 ? <ValidationContent baseline={data} />
        : <Panel title="Metriche non disponibili"><button className="clear-filters" type="button" onClick={retry}>Riprova</button></Panel>}
  </AnalysisPage>;
}
