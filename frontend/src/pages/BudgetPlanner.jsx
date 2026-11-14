import { useState } from 'react';
import { money, pct, shortDate, verticalNames, whole } from '../overview/model';
import { AnalysisPage, Filter, Panel } from './AnalysisPage';
import { budgetAllocation, budgetTotals, transferLimit } from './budgetModel.js';

const euros = (cents) => money(cents / 100);

function BudgetContent({ data }) {
  const params = new URLSearchParams(window.location.hash.split('?')[1]);
  const contextSet = data.adsets.find((set) => set.id === params.get('adset'));
  const contextCampaign = data.campaigns.find((item) => item.id === params.get('campaign'));
  const [campaign, setCampaign] = useState(contextSet?.campaignId ?? contextCampaign?.id ?? '');
  const [date, setDate] = useState(data.dates.includes(params.get('date')) ? params.get('date') : '');
  const [mode, setMode] = useState('recommended');
  const [donor, setDonor] = useState('');
  const [receiver, setReceiver] = useState(contextSet?.id ?? '');
  const [amount, setAmount] = useState(0);

  const campaignRows = data.adsets.filter((set) => !campaign || campaign === set.campaignId);
  const sets = campaignRows.map((set) => set.id);
  const campaignRowsInScope = data.budgetScenario.filter((row) => sets.includes(row[1]) && (!date || date === row[0]));
  const to = sets.includes(receiver) ? receiver : sets[1];
  const from = sets.includes(donor) && donor !== to ? donor : sets.find((id) => id !== to);
  const bound = data.source.budgetBound;
  const limit = campaign ? transferLimit(campaignRowsInScope, from, to, bound) : 0;
  const transfer = Math.min(amount, limit);
  const effectiveMode = mode === 'custom' && !campaign ? 'recommended' : mode;
  const rows = budgetAllocation(campaignRowsInScope, { mode: effectiveMode, from, to, amount: transfer, bound });
  const totals = budgetTotals(rows);
  const delta = totals.baseClicks > 0 ? (totals.clicks / totals.baseClicks - 1) * 100 : null;
  const grouped = campaignRows.map((set) => ({ ...set, ...budgetTotals(rows.filter((row) => row.id === set.id)) }));
  const incoming = [...grouped].sort((a, b) => (b.budget - b.base) - (a.budget - a.base)).filter((set) => set.budget > set.base);
  const totalByCampaign = data.campaigns.filter((item) => !campaign || item.id === campaign).map((item) => ({
    ...item, ...budgetTotals(rows.filter((row) => campaignRows.some((set) => set.id === row.id && set.campaignId === item.id))),
  }));

  return <>
    {contextSet && <p className="muted-copy">Ad set di provenienza · {contextSet.id}</p>}
    <div className="data-panel analysis-filters" role="group" aria-label="Filtri scenario budget">
      <Filter label="Campagna" value={campaign} onChange={(id) => { setCampaign(id); setDonor(''); setReceiver(''); setAmount(0); }}
        options={[[ '', 'Tutte' ], ...data.campaigns.map((item) => [item.id, verticalNames[item.vertical] ?? item.name])]} />
      <Filter label="Data" value={date} onChange={(value) => { setDate(value); setAmount(0); }}
        options={[[ '', '16–30 nov' ], ...data.dates.map((value) => [value, shortDate(value)])]} />
      <Filter label="Scenario" value={effectiveMode} onChange={setMode}
        options={[[ 'base', 'Pianificato' ], [ 'recommended', 'Riallocazione Market Mirror' ], ...(campaign ? [[ 'custom', 'Riallocazione manuale' ]] : [])]} />
    </div>
    <Panel title="Budget e rendimento stimato" description="Scenario condizionale con pacing, quote di pubblicazione e rendimenti unitari fissi.">
      <div className="analysis-stats">
        <div className="analysis-stat"><strong className="analysis-number">{euros(totals.base)}</strong><span>Pianificato</span></div>
        <div className="analysis-stat"><strong className="analysis-number">{euros(totals.budget)}</strong><span>Scenario</span></div>
        <div className="analysis-stat"><strong className="analysis-number">{whole(totals.clicks)}</strong><span>Click stimati{delta != null && ' · ' + (delta > 0 ? '+' : '') + pct(delta)}</span></div>
        <div className="analysis-stat"><strong>{pct(totals.ctr)} · {money(totals.cpm)} · {money(totals.cpc)}</strong><span>CTR · CPM · CPC stimati</span></div>
      </div>
    </Panel>
    {effectiveMode === 'custom' && <Panel title="Trasferimento fra ad set" description={'Il trasferimento vale per ciascun giorno selezionato. Limite ±' + whole(bound * 100) + '% per ad set al giorno.'}>
      <div className="analysis-filters">
        <Filter label="Da" value={from ?? ''} onChange={(value) => { setDonor(value); setAmount(0); }}
          options={sets.filter((id) => id !== to).map((id) => [id, id])} />
        <Filter label="A" value={to ?? ''} onChange={(value) => { setReceiver(value); setAmount(0); }}
          options={sets.filter((id) => id !== from).map((id) => [id, id])} />
        <label className="analysis-filter budget-range"><span>Trasferimento giornaliero · {euros(transfer)}</span>
          <input type="range" min="0" max={limit} step="1" value={transfer} disabled={!limit}
            aria-valuetext={euros(transfer)} onChange={(event) => setAmount(Number(event.target.value))} />
        </label>
        <button className="clear-filters" type="button" onClick={() => setAmount(0)} disabled={!transfer}>Azzera trasferimento</button>
      </div>
      <p className="muted-copy">Massimo giornaliero · {euros(limit)}. Totale trasferito nel periodo · {euros(transfer * (date ? 1 : data.dates.length))}.</p>
    </Panel>}
    <Panel title="Allocazione per campagna e ad set" description="Il saldo è calcolato per ad set. Ogni campagna conserva il proprio totale giornaliero.">
      <div className="budget-campaigns">{totalByCampaign.map((item) => <div className="audience-card" key={item.id}>
        <h3>{verticalNames[item.vertical] ?? item.name}</h3><span>{euros(item.budget)}</span>
        <meter value={item.budget} max={Math.max(1, totals.budget)} aria-label={'Quota budget ' + item.id} />
      </div>)}</div>
      <div className="analysis-scroll" role="region" tabIndex={0} aria-label="Budget per ad set"><table className="analysis-table budget-table">
        <thead><tr>{['Ad set', 'Pianificato', 'Scenario', 'Differenza', 'Click stimati', 'CTR', 'CPM', 'CPC'].map((name) => <th key={name} scope="col">{name}</th>)}</tr></thead>
        <tbody>{grouped.map((item) => <tr key={item.id} className={contextSet?.id === item.id ? 'budget-context' : undefined}>
          <th scope="row">{item.id}</th><td>{euros(item.base)}</td><td>{euros(item.budget)}</td>
          <td>{item.budget > item.base ? '+' : ''}{euros(item.budget - item.base)}</td><td>{whole(item.clicks)}</td>
          <td>{pct(item.ctr)}</td><td>{money(item.cpm)}</td><td>{money(item.cpc)}</td>
        </tr>)}</tbody>
      </table></div>
    </Panel>
    <Panel title="Raccomandazione">
      {effectiveMode === 'recommended' && incoming.length ? <p className="muted-copy">
        Considera {incoming.slice(0, 3).map((set) => set.id + ' (+' + euros(set.budget - set.base) + ')').join(', ')}.
        {' '}Market Mirror dà priorità ai click attesi per euro di budget, tenendo conto del pacing storico.
      </p> : <p className="muted-copy">Confronta i click stimati a parità di budget. Per modificare le quote, seleziona una campagna e la riallocazione manuale.</p>}
      <p className="muted-copy">Fonte · Market Mirror {data.source.commit.slice(0, 8)}, baseline a 14 giorni. Le stime dipendono dalle ipotesi di delivery e d’asta.</p>
    </Panel>
  </>;
}

export function BudgetPlanner({ headingRef }) {
  return <AnalysisPage headingRef={headingRef} title="Budget Planner" subtitle="Valuta una riallocazione con lo stesso budget per campagna e giorno.">
    {(data) => <BudgetContent data={data} />}
  </AnalysisPage>;
}
