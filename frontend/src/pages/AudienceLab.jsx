import { useState } from 'react';
import { money, pct, verticalNames, whole, leverNames } from '../overview/model';
import { AnalysisPage, Filter, Panel } from './AnalysisPage';

const bands = ['18-24', '25-34', '35-44', '45-54', '55-64', '65+'];
const actions = { scroll: 'Scroll / ignora', glance: 'Osserva', stop: 'Si sofferma', click: 'Apre / clicca' };
const label = (age) => age.replace('-', '–');
const sum = (groups) => groups.reduce((n, r) => n + r[3], 0);

function Distribution({ rows, title, total, onPick, selected, children }) {
  return <Panel title={title}>
    <div className="analysis-bars">{rows.map(([key, n]) =>
      <div className="analysis-bar" key={key}>
        {onPick ? <button type="button" className="clear-filters" aria-pressed={selected === key}
          onClick={() => onPick(selected === key ? '' : key)}>{label(key)}</button> : <span>{label(key)}</span>}
        <meter aria-label={label(key)} min="0" max={Math.max(1, total)} value={n}>{n}</meter><strong>{whole(n)}</strong>
      </div>)}</div>
    {children}
  </Panel>;
}

function AudienceContent({ data }) {
  const [campaign, setCampaign] = useState('');
  const [adset, setAdset] = useState('');
  const [age, setAge] = useState('');
  const [first, setFirst] = useState('');
  const [second, setSecond] = useState('');
  const availableSets = data.adsets.filter((set) => !campaign || set.campaignId === campaign);
  const vertical = data.campaigns.find((item) => item.id === campaign)?.vertical;
  const hypotheses = data.hypotheses.filter((item) => availableSets.some((set) => set.id === item.adsetId) && (!adset || adset === item.adsetId));
  const groups = (data.synthetic?.groups ?? []).filter((row) => !vertical || row[0] === vertical);
  const ages = [...new Set([...bands, ...groups.map((row) => row[1])])];
  const genders = [...new Set(groups.map((row) => row[2]))].sort();
  const activeGroups = groups.filter((row) => !age || row[1] === age);
  const runs = Object.entries(data.simulatedDecision ?? {}).filter(([, item]) => !vertical || item.vertical === vertical);
  const defaultA = ages[0], defaultB = ages[1];
  function commonInterests(band) {
    const totals = new Map();
    for (const [sector, group, counts] of data.synthetic?.interestGroups ?? []) {
      if (group !== band || (vertical && sector !== vertical)) continue;
      for (const [term, count] of Object.entries(counts)) totals.set(term, (totals.get(term) ?? 0) + count);
    }
    return [...totals].sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0])).slice(0, 4);
  }
  const references = (id) => '#/creatives?adset=' + encodeURIComponent(id);

  return <>
    <div className="data-panel analysis-filters" aria-label="Filtri Audience Lab" role="group">
      <Filter label="Campagna" value={campaign} onChange={(id) => { setCampaign(id); setAdset(''); setAge(''); }}
        options={[[ '', 'Tutte le campagne' ], ...data.campaigns.map((item) => [item.id, verticalNames[item.vertical] ?? item.name])]} />
      <Filter label="Ad set" value={adset} onChange={setAdset} options={[[ '', 'Tutti gli ad set' ], ...availableSets.map((item) => [item.id, item.id])]} />
    </div>
    <Panel title="Panoramica audience">
      <div className="analysis-stats">
        <div className="analysis-stat"><strong className="analysis-number">{hypotheses.length}</strong><span>Ad set con ipotesi</span></div>
        <div className="analysis-stat"><strong className="analysis-number">{data.synthetic ? whole(sum(groups)) : '—'}</strong><span>Profili sintetici nel perimetro</span></div>
        <div className="analysis-stat"><strong className="analysis-number">{runs.length}</strong><span>Asset con reazioni aggregate</span></div>
      </div>
      <p className="muted-copy">I profili T3 e le reazioni Decision sono riferiti al settore. Il filtro Ad set restringe le ipotesi storiche.</p>
    </Panel>
    {groups.length ? <>
      <div className="analysis-grid">
        <Distribution title="Distribuzione per età" total={sum(groups)} selected={age} onPick={setAge}
          rows={ages.map((key) => [key, sum(groups.filter((r) => r[1] === key))])} />
        <Distribution title="Distribuzione per genere" total={sum(activeGroups)}
          rows={genders.map((key) => [key, sum(activeGroups.filter((r) => r[2] === key))])} />
      </div>
      <Panel title="Età × genere" description="Numerosità dei profili sintetici.">
        <div className="analysis-scroll" tabIndex={0} role="region" aria-label="Matrice età per genere">
          <table className="analysis-table"><thead><tr><th scope="col">Età</th>{genders.map((g) => <th scope="col" key={g}>{g}</th>)}</tr></thead>
            <tbody>{ages.filter((key) => !age || key === age).map((band) => <tr key={band}><th scope="row">{label(band)}</th>
              {genders.map((gender) => {
                const n = sum(groups.filter((row) => row[1] === band && row[2] === gender));
                return <td key={gender} style={{ background: 'rgba(128,98,227,' + (0.5 * n / Math.max(1, ...groups.map((r) => r[3]))) + ')' }}>{n}</td>;
              })}</tr>)}</tbody></table>
        </div>
      </Panel>
      <Panel title="Confronto segmenti sintetici">
        <div className="analysis-filters">
          <Filter label="Fascia A" value={first || defaultA} onChange={setFirst} options={ages.map((key) => [key, label(key)])} />
          <Filter label="Fascia B" value={second || defaultB} onChange={setSecond} options={ages.map((key) => [key, label(key)])} />
        </div>
        <div className="analysis-grid">{[first || defaultA, second || defaultB].map((key, i) => {
          const group = groups.filter((row) => row[1] === key);
          const interests = commonInterests(key);
          return <Distribution key={i} title={label(key) + ' · ' + whole(sum(group)) + ' profili'} total={sum(group)}
            rows={genders.map((gender) => [gender, sum(group.filter((r) => r[2] === gender))])}>
            <p className="muted-copy">{interests.length ? 'Interessi ricorrenti · ' + interests.map(([term, n]) => term + ' (' + n + ')').join(' · ')
              : 'Nessun interesse riportato per questa fascia.'}</p>
          </Distribution>;
        })}</div>
        <p className="muted-copy">La ripartizione delle reazioni per fascia richiede valutazioni collegate ai singoli profili.</p>
      </Panel>
    </> : <Panel title="Profili sintetici" description="Nessun export di profili disponibile per la selezione. Le distribuzioni e la matrice saranno mostrate quando saranno disponibili dati T3." />}
    <Panel title="Reazioni simulate" description={runs.length
      ? 'Distribuzione delle azioni Decision per asset. Le probabilità sono punteggi del modello su profili sintetici.'
      : 'Nessun risultato Decision verificato disponibile per la selezione.'}>
      <div className="analysis-grid">{runs.map(([id, run]) => <article key={id} className="audience-card">
        <h3>{id}</h3><a className="analysis-link" href={'#/creatives?asset=' + encodeURIComponent(id)}>Cerca l’asset</a><p className="muted-copy">{run.n_personas} valutazioni · {run.model}</p>
        <div className="reaction-track" aria-hidden="true">{Object.keys(actions).map((key) =>
          <span key={key} style={{ width: run.actions[key] * 100 + '%' }} />)}</div>
        <p>{Object.entries(actions).map(([key, name]) => name + ' ' + pct(run.actions[key] * 100)).join(' · ')}</p>
        <p className="muted-copy">Motivi più frequenti · {Object.entries(run.reason_distribution).sort((a, b) => b[1] - a[1]).slice(0, 3).map(([reason, value]) => reason.replaceAll('_', ' ') + ' ' + pct(value * 100)).join(' · ')}</p>
      </article>)}</div>
    </Panel>
    <Panel title="Ipotesi comportamentali" description="Evidenze dallo storico del kit simulato. Le interpretazioni hanno confidenza qualitativa.">
      <div className="analysis-grid">{hypotheses.map((item) => {
        const evidence = item.evidence;
        return <article className="audience-card" key={item.adsetId}>
          <h3>{item.adsetId} · confidenza {item.confidence}</h3><p>{item.description}.</p>
          <div className="analysis-stats">
            <div className="analysis-stat"><strong>{pct(item.ctr)}</strong><span>CTR storico</span></div>
            {evidence && <><div className="analysis-stat"><strong>{money(evidence.cpm_storico_eur)}</strong><span>CPM storico</span></div>
              <div className="analysis-stat"><strong>{pct(evidence.ctr_recente_pct)}</strong><span>CTR ultimi 14 giorni</span></div></>}
          </div>
          {evidence && <details><summary>Evidenze e interpretazioni alternative</summary>
            <p className="muted-copy">Leva con CTR più alto · {leverNames[evidence.leva_con_ctr_piu_alto.lever] ?? evidence.leva_con_ctr_piu_alto.lever}
              {' · '}{pct(evidence.leva_con_ctr_piu_alto.ctr_pct)} su {whole(evidence.leva_con_ctr_piu_alto.impressions)} impression.</p>
            <p className="muted-copy">{item.strategy}</p>
            <ul className="muted-copy">{item.alternatives.map((text) => <li key={text}>{text}</li>)}</ul>
          </details>}
          <a className="analysis-link" href={references(item.adsetId)}>Esplora creatività dell’ad set</a>
        </article>;
      })}</div>
    </Panel>
  </>;
}

export function AudienceLab({ headingRef }) {
  return <AnalysisPage headingRef={headingRef} title="Audience Lab" subtitle="Ipotesi per ad set, profili sintetici e reazioni alle creatività.">
    {(data) => <AudienceContent data={data} />}
  </AnalysisPage>;
}
