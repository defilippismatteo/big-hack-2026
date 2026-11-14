import { CalendarDays } from 'lucide-react';
import { useId, useState } from 'react';
import { money, pct, shortDate } from './model';

const metrics = [{ key: 'ctr', label: 'CTR', format: pct }, { key: 'cpm', label: 'CPM', format: money }];
const weekLabel = 'Inizio Black Week';

function plotScale(max) {
  const magnitude = 10 ** Math.floor(Math.log10(max / 4 || 1));
  const step = ([1, 2, 2.5, 5, 10].find((n) => n * magnitude >= max / 4) ?? 10) * magnitude;
  return { ticks: Array.from({ length: 5 }, (_, i) => i * step), max: step * 4 };
}

export function ForecastChart({ timeline: forecast, seasonal, events, sourceMethod, title = 'Performance Forecast', note }) {
  const titleId = useId();
  const [active, setActive] = useState('ctr');
  const [view, setView] = useState('forecast');
  const isSeasonal = view === 'seasonal' && seasonal.length > 0;
  const timeline = isSeasonal ? seasonal : forecast;
  const [selectedDay, setSelectedDay] = useState(null);
  const [hoveredDay, setHoveredDay] = useState(null);
  const { format } = metrics.find((m) => m.key === active);
  const weekStart = timeline.findIndex(({ day }) => events[day] === weekLabel);
  const friday = timeline.find(({ day }) => events[day] === 'Black Friday')?.day;
  const selected = timeline.find(({ day }) => day === (hoveredDay ?? selectedDay ?? friday)) ?? timeline.at(-1);
  const selectedIndex = timeline.indexOf(selected);
  const valid = timeline.filter((item) => item[active] != null);
  const { ticks, max } = plotScale(Math.max(0, ...valid.map((item) => item[active])));
  const x = (i) => (i + 0.5) / timeline.length * 100;
  const y = (value) => 100 - 100 * value / max;
  const series = timeline.map((item, i) => item[active] == null ? null : [x(i), y(item[active])]);
  const paths = series.reduce((parts, point, i) => {
    if (point) {
      if (!series[i - 1]) parts.push([]);
      parts.at(-1).push(point);
    }
    return parts;
  }, []);
  const detailLabel = selected ? shortDate(selected.day) + (events[selected.day] ? ' · ' + events[selected.day] : '') : '';

  return (
    <section className="data-panel forecast-panel" aria-labelledby={titleId}>
      <div className="panel-head">
        <div><span className={'data-tag ' + (isSeasonal ? 'tag-scenario' : 'tag-forecast')}>{isSeasonal ? 'Scenario' : 'Previsione'}</span>
          <h2 id={titleId}>{title}</h2>
          <p>{isSeasonal ? 'Scenario centrale · benchmark Wevion 2025' : 'Andamento giornaliero · ' + sourceMethod}</p>
        </div>
        <div className="segmented" role="group" aria-label="Metrica del grafico">
          {metrics.map(({ key, label }) => <button type="button" key={key} aria-pressed={active === key}
            onClick={() => setActive(key)}>{label}</button>)}
        </div>
      </div>
      {seasonal.length > 0 && <div className="series-options" role="group" aria-label="Serie del grafico">
        <button type="button" aria-pressed={!isSeasonal} onClick={() => setView('forecast')}>Previsione base</button>
        <button type="button" aria-pressed={isSeasonal} onClick={() => setView('seasonal')}>Scenario stagionale</button>
      </div>}
      {!valid.length ? <p className="panel-empty">Non ci sono valori aggregabili per questa selezione.</p> : <>
        <div className="plot-summary" aria-live={hoveredDay ? 'off' : 'polite'}>
          <CalendarDays size={15} aria-hidden="true" />
          <span>{detailLabel}</span><strong>{format(selected?.[active])}</strong>
        </div>
        <div className="plot-layout">
          <div className="y-axis" aria-hidden="true">
            {[...ticks].reverse().map((tick) => <span key={tick}>{format(tick)}</span>)}
          </div>
          <div className="plot-body">
            <div className="plot-area">
              <svg viewBox="0 0 100 100" preserveAspectRatio="none" aria-hidden="true">
                {weekStart >= 0 && <rect x={weekStart / timeline.length * 100} y="0"
                  width={(timeline.length - weekStart) / timeline.length * 100} height="100" fill="#f2eefb" />}
                {ticks.map((tick) => <line key={tick} x1="0" y1={y(tick)} x2="100" y2={y(tick)}
                  stroke="#e9e5f1" vectorEffect="non-scaling-stroke" />)}
                {timeline.map(({ day }, i) => events[day] && <line key={day} x1={x(i)} y1="0" x2={x(i)} y2="100"
                  stroke="#8062e3" opacity=".5" strokeDasharray="4 4" vectorEffect="non-scaling-stroke" />)}
                <line x1={x(selectedIndex)} y1="0" x2={x(selectedIndex)} y2="100" stroke="#6044b2"
                  opacity=".32" vectorEffect="non-scaling-stroke" />
                {paths.map((points) => <polyline key={points[0][0]} points={points.map((p) => p.join(',')).join(' ')}
                  fill="none" stroke="#7653d3" strokeWidth="2.7" vectorEffect="non-scaling-stroke" />)}
              </svg>
              {series[selectedIndex] && <span className="plot-dot" aria-hidden="true" style={{
                left: x(selectedIndex) + '%', top: series[selectedIndex][1] + '%',
              }} />}
              <div className="plot-days" style={{ '--days': timeline.length }} onPointerLeave={() => setHoveredDay(null)}>
                {timeline.map((item) => <button key={item.day} type="button"
                  aria-pressed={selected.day === item.day}
                  aria-label={shortDate(item.day) + (events[item.day] ? ', ' + events[item.day] : '') + ': ' + format(item[active])}
                  onPointerEnter={(event) => { if (event.pointerType === 'mouse') setHoveredDay(item.day); }}
                  onFocus={() => { setHoveredDay(null); setSelectedDay(item.day); }}
                  onClick={() => { setHoveredDay(null); setSelectedDay(item.day); }} />)}
              </div>
            </div>
            <div className="x-axis" aria-hidden="true" style={{ '--days': timeline.length }}>
              {timeline.map(({ day }, i) => <span key={day} className={events[day] || i === 0 ? 'key-day' : ''}>
                {events[day] || i % 2 === 0 ? Number(day.slice(-2)) : ''}
              </span>)}
            </div>
          </div>
        </div>
        <div className="event-legend">
          {Object.entries(events).filter(([day]) => timeline.some((r) => r.day === day)).map(([day, event], i) =>
            <button key={day} type="button" className={i === 0 ? 'week-event' : ''}
              aria-pressed={selected.day === day} onClick={() => { setHoveredDay(null); setSelectedDay(day); }}>
              <span aria-hidden="true" />{event} <small>· {shortDate(day)}</small>
            </button>)}
        </div>
        <p className="chart-note">{note ?? (isSeasonal
          ? 'Medie ponderate sulle impression stimate. Lo scenario applica gli indici del 2025 del kit senza intervalli calibrati.'
          : 'Medie ponderate sulle impression stimate. Gli eventi di calendario evidenziano i giorni di interesse.')}</p>
      </>}
    </section>
  );
}
