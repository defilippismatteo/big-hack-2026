import { CalendarDays, MoveHorizontal, Search } from 'lucide-react';
import { useId, useState } from 'react';
import { money, pct, shortDate } from './model';
import { chartDomain } from './chartModel';

const metrics = [{ key: 'cpm', label: 'Costo di 1.000 visualizzazioni', short: 'CPM', format: money }, { key: 'ctr', label: 'Quota di visualizzazioni che generano un clic', short: 'CTR', format: pct }];
export function ForecastChart({ timeline: forecast, seasonal, events, sourceMethod, title, note, scenario = false }) {
  const titleId = useId();
  const [active, setActive] = useState('cpm');
  const [view, setView] = useState('forecast');
  const [zoom, setZoom] = useState(true);
  const [start, setStart] = useState('');
  const [end, setEnd] = useState('');
  const [selectedDay, setSelectedDay] = useState(null);
  const [hoveredDay, setHoveredDay] = useState(null);
  const isSeasonal = view === 'seasonal' && seasonal.length > 0;
  const all = isSeasonal ? seasonal : forecast;
  const from = all.some(d => d.day === start) ? start : all[0]?.day;
  const to = all.some(d => d.day === end) ? end : all.at(-1)?.day;
  const timeline = all.filter(d => d.day >= from && d.day <= to);
  const spec = metrics.find(m => m.key === active), { format } = spec;
  const friday = timeline.find(({ day }) => events[day] === 'Black Friday')?.day;
  const selected = timeline.find(({ day }) => day === (hoveredDay ?? selectedDay ?? friday)) ?? timeline.at(-1);
  const selectedIndex = timeline.indexOf(selected);
  const valid = timeline.filter(item => Number.isFinite(item[active]));
  const { ticks, min, max } = chartDomain(valid.map(item => item[active]), zoom);
  const x = i => (i + .5) / Math.max(1, timeline.length) * 100;
  const y = value => 100 - 100 * (value - min) / (max - min);
  const series = timeline.map((item, i) => Number.isFinite(item[active]) ? [x(i), y(item[active])] : null);
  const paths = series.reduce((parts, point, i) => { if (point) { if (!series[i - 1]) parts.push([]); parts.at(-1).push(point); } return parts; }, []);
  const values = valid.map(d => d[active]);
  const range = values.length ? [Math.min(...values), Math.max(...values)] : null;
  return <section className="data-panel forecast-panel" aria-labelledby={titleId}>
    <div className="panel-head"><div><span className={'data-tag '+(isSeasonal || scenario ? 'tag-scenario' : 'tag-forecast')}>{isSeasonal || scenario ? 'Scenario ipotetico' : 'Previsione del modello'}</span><h2 id={titleId}>{title ?? (active==='cpm'?'Come cambiano i costi nei prossimi giorni':'Come cambia la quota di clic')}</h2><p>{spec.label}. {active === 'cpm' ? 'Un costo più basso permette di raggiungere più persone a parità di spesa.' : 'Una quota più alta indica più clic a parità di visualizzazioni.'}</p></div>
      <div className="segmented" role="group" aria-label="Metrica del grafico">{metrics.map(m => <button type="button" key={m.key} aria-pressed={active===m.key} onClick={()=>setActive(m.key)}>{m.short}</button>)}</div>
    </div>
    {seasonal.length > 0 && <div className="series-options" role="group" aria-label="Serie del grafico"><button type="button" aria-pressed={!isSeasonal} onClick={()=>setView('forecast')}>Previsione base</button><button type="button" aria-pressed={isSeasonal} onClick={()=>setView('seasonal')}>Ipotesi stagionale 2025</button></div>}
    <div className="chart-controls"><label>Dal <select aria-label="Inizio periodo grafico" value={from ?? ''} onChange={e=>{setStart(e.target.value);if(e.target.value>to)setEnd(e.target.value);}}>{all.map(d=><option key={d.day} value={d.day}>{shortDate(d.day)}</option>)}</select></label><label>Al <select aria-label="Fine periodo grafico" value={to ?? ''} onChange={e=>{setEnd(e.target.value);if(e.target.value<from)setStart(e.target.value);}}>{all.map(d=><option key={d.day} value={d.day}>{shortDate(d.day)}</option>)}</select></label><button type="button" className="chart-zoom" aria-pressed={zoom} onClick={()=>setZoom(!zoom)}><Search size={12} aria-hidden="true"/>{zoom ? 'Dettaglio · asse ingrandito' : 'Vista da zero'}</button></div>
    {range && <div className="chart-takeaway"><span>Nel periodo selezionato</span><strong>{format(range[0])} – {format(range[1])}</strong></div>}
    {!valid.length ? <p className="panel-empty">Nessuna previsione per questo periodo.</p> : <>
      <div className="plot-summary" aria-live={hoveredDay ? 'off' : 'polite'}><CalendarDays size={15} aria-hidden="true"/><span>{shortDate(selected.day)}{events[selected.day] ? ' · '+events[selected.day] : ''}</span><strong>{format(selected[active])}</strong></div>
      <div className="plot-layout"><div className="y-axis" aria-hidden="true">{[...ticks].reverse().map(t=><span key={t}>{active==='ctr' ? t.toLocaleString('it-IT',{minimumFractionDigits:3,maximumFractionDigits:3})+'%' : format(t)}</span>)}</div><div className="plot-body"><div className="plot-area"><svg viewBox="0 0 100 100" preserveAspectRatio="none" aria-hidden="true">
        {ticks.map(t=><line key={t} x1="0" x2="100" y1={y(t)} y2={y(t)} stroke="#e9e5f1" vectorEffect="non-scaling-stroke"/>)}
        {timeline.map(({day},i)=>events[day]&&<line key={day} x1={x(i)} x2={x(i)} y1="0" y2="100" stroke="#8062e3" opacity=".5" strokeDasharray="4 4" vectorEffect="non-scaling-stroke"/>)}
        <line x1={x(selectedIndex)} x2={x(selectedIndex)} y1="0" y2="100" stroke="#8062e3" strokeDasharray="2 3" vectorEffect="non-scaling-stroke"/>
        {paths.map(points=><polyline key={points[0][0]} points={points.map(p=>p.join(',')).join(' ')} fill="none" stroke="#7653d3" strokeWidth="2.7" vectorEffect="non-scaling-stroke"/>)}
      </svg>{series[selectedIndex]&&<span className="plot-dot" aria-hidden="true" style={{left:x(selectedIndex)+'%',top:series[selectedIndex][1]+'%'}}/>}
      <div className="plot-days" style={{'--days':timeline.length}} onPointerLeave={()=>setHoveredDay(null)}>{timeline.map(item=><button key={item.day} type="button" aria-pressed={selected.day===item.day} aria-label={shortDate(item.day)+': '+format(item[active])} onPointerEnter={e=>{if(e.pointerType==='mouse')setHoveredDay(item.day);}} onFocus={()=>{setHoveredDay(null);setSelectedDay(item.day);}} onClick={()=>{setHoveredDay(null);setSelectedDay(item.day);}}/>)}</div></div>
      <div className="x-axis" aria-hidden="true" style={{'--days':timeline.length}}>{timeline.map(({day},i)=><span key={day} className={events[day]||i===0?'key-day':''}>{events[day]||i%2===0||i===timeline.length-1 ? Number(day.slice(-2)) : ''}</span>)}</div></div></div>
      <div className="event-legend">{Object.entries(events).filter(([day])=>timeline.some(d=>d.day===day)).map(([day,event])=><button type="button" key={day} aria-pressed={selected.day===day} onClick={()=>setSelectedDay(day)}><span aria-hidden="true"/>{event} · {shortDate(day)}</button>)}</div>
    </>}
    <p className="chart-note chart-axis-note"><MoveHorizontal size={13} aria-hidden="true"/>{zoom ? 'Asse verticale ingrandito: rende visibili anche piccole variazioni.' : 'Asse verticale da zero: mostra l’ampiezza assoluta delle variazioni.'}</p>
    <p className="chart-note">{active==='ctr'&&!isSeasonal&&!scenario ? 'Il CTR base è costante per ciascun annuncio; la media cambia con il mix di annunci. Lo zoom non aumenta l’effetto previsto.' : isSeasonal||scenario ? 'Scenario basato sul benchmark 2025: non è un risultato futuro osservato.' : note ?? 'Media pesata sulle visualizzazioni stimate; nessun risultato futuro osservato.'}</p>
    <details className="chart-method"><summary>Metodo e limiti della previsione</summary><p className="chart-note">{sourceMethod}. Le verifiche storiche si fermano al 15 novembre. Intervalli di incertezza calibrati non disponibili. <a href="#/validation">Apri la validazione</a>.</p></details>
  </section>;
}
