import { useRef } from 'react';
import { money, pct } from '../overview/model';
import { plotLimit, sectorTones, sortCreatives } from './model';
import { verticalNames } from '../overview/model';

const fractions = [0, 0.25, 0.5, 0.75, 1];

export function PerformanceMap({ rows, domain, onPreview, previewId }) {
  const points = useRef(new Map());
  const best = sortCreatives(rows, { key: 'efficiency', direction: -1 })[0];
  const active = rows.find((row) => row.id === previewId) ?? best;
  const maxCpm = plotLimit(Math.max(0, ...domain.map((row) => row.cpm)));
  const maxCtr = plotLimit(Math.max(0, ...domain.map((row) => row.ctr)));
  const sectors = Object.keys(sectorTones).filter((key) => rows.some((row) => row.vertical === key));

  function onPointKey(event, index) {
    const moves = { ArrowLeft: index - 1, ArrowRight: index + 1, ArrowUp: index - 1, ArrowDown: index + 1,
      Home: 0, End: rows.length - 1 };
    if (!Object.hasOwn(moves, event.key)) return;
    event.preventDefault();
    const next = rows[Math.min(Math.max(moves[event.key], 0), rows.length - 1)];
    points.current.get(next.id)?.focus();
  }

  return (
    <section className="data-panel map-panel" aria-labelledby="creative-map-title">
      <div className="explorer-panel-header">
        <div><h2 id="creative-map-title">Dove sono gli annunci più efficienti?</h2>
          <p>Ogni punto è un annuncio. In alto: più clic. A sinistra: minore costo. Passa su un punto o toccalo per leggere la scheda a fianco.</p></div>
        <span className="data-tag tag-forecast">Previsione</span>
      </div>
      {rows.length ? <>
        <div className="scatter-axis-title">CTR previsto</div>
        <div className="scatter">
          <div className="scatter-y" aria-hidden="true">
            {fractions.map((f) => <span key={f} style={{ bottom: f * 100 + '%' }}>{pct(f * maxCtr)}</span>)}
          </div>
          <div className="scatter-plot" role="group" aria-label="Annunci nel grafico" aria-describedby="scatter-help">
            {fractions.map((f) => <div key={f} className="scatter-gridline" aria-hidden="true"
              style={{ '--grid-position': f * 100 + '%' }} />)}
            {rows.map((row, i) => <button key={row.id} type="button" className="scatter-point"
              data-tone={row.tone} data-highlighted={active.id === row.id} data-best={best.id === row.id}
              style={{ left: row.cpm / maxCpm * 100 + '%', bottom: row.ctr / maxCtr * 100 + '%' }}
              tabIndex={active.id === row.id ? 0 : -1}
              aria-label={row.id + ', ' + row.headline + ', CPM ' + money(row.cpm) + ', CTR ' + pct(row.ctr) + ', ad set ' + row.adsetId}
              ref={(element) => { if (element) points.current.set(row.id, element); else points.current.delete(row.id); }}
              
              onPointerEnter={(event) => { if (event.pointerType === 'mouse') { onPreview(row.id); } }}
              onFocus={() => {onPreview(row.id);}} onKeyDown={(event) => onPointKey(event, i)}
              onClick={() => {onPreview(row.id);}} />)}
          </div>
          <div className="scatter-x" aria-hidden="true">
            {fractions.map((f) => <span key={f} style={{ left: f * 100 + '%' }}>{money(f * maxCpm)}</span>)}
          </div>
          <div className="scatter-axis-title scatter-x-title">CPM previsto</div>
        </div>
        <div className="scatter-caption">
          <div className="sector-legend">
            {sectors.map((key) => <span key={key} data-tone={sectorTones[key]}><i aria-hidden="true" />{verticalNames[key]}</span>)}
          </div>
          <p className="scatter-readout" title="Miglior rapporto tra CTR e CPM nella selezione"><strong>{active.id}</strong> <span>CTR {pct(active.ctr)} · CPM {money(active.cpm)}{active.id === best.id && ' · Miglior resa'}</span></p>
        </div>
        <p id="scatter-help" className="sr-only">Usa le frecce per scorrere gli annunci e aggiornare la scheda. Il pulsante nella scheda apre il dettaglio completo. Tutti gli annunci sono disponibili anche in tabella.</p>
      </> : <p className="panel-empty">Nessun annuncio corrisponde ai filtri.</p>}
    </section>
  );
}
