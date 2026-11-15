import React from 'react';
import { Easing, interpolate, useCurrentFrame } from 'remotion';
import { ADERA, formatEurIT, formatIntIT, formatPctIT } from '../styles/theme';
import { PillBadge, SlideUpBlock } from '../components/MotionPrimitives';
import { VERIFIED_DATA } from '../data/verifiedData';

export const S04_ForecastGap: React.FC = () => {
  const frame = useCurrentFrame();

  const obs = VERIFIED_DATA.observedDaily; // 91 days
  const fct = VERIFIED_DATA.forecastDaily; // 15 days
  const allPoints = [
    ...obs.map((d) => ({ ...d, kind: 'obs' as const })),
    ...fct.map((d) => ({ ...d, kind: 'fct' as const })),
  ]; // 106 points

  // SVG full canvas dimensions inside card
  const svgW = 1560;
  const svgH = 560;
  const padL = 78;
  const padR = 96;
  const padT = 46;
  const padB = 64;
  const plotW = svgW - padL - padR;
  const plotH = svgH - padT - padB;
  const minCpm = 5.2;
  const maxCpm = 12.2;

  const coords = allPoints.map((pt, i) => {
    const x = padL + (i / (allPoints.length - 1)) * plotW;
    const y = padT + (1 - (pt.cpm - minCpm) / (maxCpm - minCpm)) * plotH;
    return { x, y, pt, i };
  });

  const cutoffIdx = obs.length - 1; // index 90 (2026-11-15)
  const cutoffX = coords[cutoffIdx].x;
  const fctStartX = coords[obs.length].x;

  // Phase 1 (0..180): Camera follows curve tip through late Oct -> Nov 15 cutoff
  // Phase 2 (180..270): Reveal gap + forecast starts drawing
  // Phase 3 (270..450): Smooth zoom-out from tip (scale 1.85 -> 1.0)
  const tipIndexFloat = interpolate(frame, [0, 175, 360], [58, cutoffIdx, allPoints.length - 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.inOut(Easing.cubic),
  });
  const tipIdx = Math.min(allPoints.length - 1, Math.floor(tipIndexFloat));
  const activeCoord = coords[tipIdx];

  const zoomScale = interpolate(frame, [0, 210, 340], [1.82, 1.72, 1.0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.inOut(Easing.cubic),
  });

  // Camera pan keeps active tip near center while zoomed in, relaxes to 0 when zoomed out
  const zoomWeight = interpolate(zoomScale, [1.0, 1.82], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const camCenterX = svgW / 2;
  const camCenterY = svgH / 2;
  const rawShiftX = (camCenterX - activeCoord.x) * zoomWeight * 0.72;
  const rawShiftY = (camCenterY - activeCoord.y) * zoomWeight * 0.45;

  const obsPath = coords
    .slice(0, obs.length)
    .map((c, i) => `${i === 0 ? 'M' : 'L'} ${c.x.toFixed(1)} ${c.y.toFixed(1)}`)
    .join(' ');

  const fctPath = coords
    .slice(obs.length)
    .map((c, i) => `${i === 0 ? 'M' : 'L'} ${c.x.toFixed(1)} ${c.y.toFixed(1)}`)
    .join(' ');

  const obsRevealProgress = interpolate(frame, [0, 170], [0.64, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const fctRevealProgress = interpolate(frame, [205, 360], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.out(Easing.cubic),
  });

  const gapHighlight = interpolate(frame, [170, 210], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  return (
    <div
      style={{
        width: ADERA.width,
        height: ADERA.height,
        backgroundColor: ADERA.colors.bgDark,
        position: 'relative',
        overflow: 'hidden',
        fontFamily: ADERA.fontFamily,
        color: '#FFFFFF',
      }}
    >
      {/* Top Header */}
      <div
        style={{
          position: 'absolute',
          left: ADERA.marginX,
          right: ADERA.marginX,
          top: 72,
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'flex-start',
        }}
      >
        <div>
          <SlideUpBlock startFrame={4} distance={18}>
            <PillBadge label="SCENA AGGIUNTA · CAMERA FOLLOW + ZOOM-OUT · METODO ctr_baseline14d__cpm_timestral28m" tone="dark" />
          </SlideUpBlock>
          <SlideUpBlock startFrame={10} distance={22}>
            <div style={{ fontSize: 54, fontWeight: 800, letterSpacing: '-0.03em', marginTop: 18 }}>
              Dalla serie nota allo stacco di previsione.
            </div>
          </SlideUpBlock>
        </div>

        {/* Live Telemetry Pill */}
        <div
          style={{
            backgroundColor: ADERA.colors.bgDarkCard,
            border: `1px solid ${ADERA.colors.borderDark}`,
            borderRadius: 18,
            padding: '18px 26px',
            minWidth: 340,
          }}
        >
          <div style={{ fontSize: 13, fontWeight: 700, color: ADERA.colors.accentSoft, letterSpacing: '0.07em' }}>
            {activeCoord.pt.kind === 'obs' ? 'SERIE OSSERVATA (SIMULATA)' : 'ORIZZONTE FORECAST (TIMESTRAL 28M)'}
          </div>
          <div style={{ display: 'flex', alignItems: 'baseline', justifyContent: 'space-between', marginTop: 8 }}>
            <span style={{ fontSize: 22, fontWeight: 700, color: '#EAE4F7' }}>{activeCoord.pt.day}</span>
            <span style={{ fontSize: 38, fontWeight: 900, color: activeCoord.pt.kind === 'obs' ? '#C2A5FF' : '#22E39B', fontVariantNumeric: 'tabular-nums' }}>
              {formatEurIT(activeCoord.pt.cpm)}
            </span>
          </div>
          <div style={{ fontSize: 14, color: '#9E93BA', marginTop: 6 }}>
            CTR {formatPctIT(activeCoord.pt.ctr, 2)} · {formatIntIT(VERIFIED_DATA.forecastRowsCount)} righe forecast totali
          </div>
        </div>
      </div>

      {/* Main Camera Viewport */}
      <div
        style={{
          position: 'absolute',
          left: ADERA.marginX,
          right: ADERA.marginX,
          top: 256,
          height: 600,
          backgroundColor: '#1E152C',
          border: `1px solid ${ADERA.colors.borderDark}`,
          borderRadius: 26,
          overflow: 'hidden',
          boxShadow: '0 28px 80px rgba(0,0,0,0.45)',
        }}
      >
        <div
          style={{
            width: svgW,
            height: svgH,
            margin: '20px auto 0',
            transform: `translate(${rawShiftX}px, ${rawShiftY}px) scale(${zoomScale})`,
            transformOrigin: 'center center',
          }}
        >
          <svg width={svgW} height={svgH} viewBox={`0 0 ${svgW} ${svgH}`}>
            {/* Horizontal grid */}
            {[6, 7.5, 9, 10.5, 12].map((v) => {
              const y = padT + (1 - (v - minCpm) / (maxCpm - minCpm)) * plotH;
              return (
                <g key={v}>
                  <line x1={padL} y1={y} x2={svgW - padR} y2={y} stroke="#2E2244" strokeWidth={1.5} />
                  <text x={padL - 14} y={y + 5} textAnchor="end" fontSize={14} fill="#8D80AC" fontWeight={600}>
                    €{v.toFixed(1).replace('.', ',')}
                  </text>
                </g>
              );
            })}

            {/* Future Forecast Region Shaded */}
            <rect
              x={cutoffX}
              y={padT}
              width={svgW - padR - cutoffX}
              height={plotH}
              fill="rgba(34, 227, 155, 0.06)"
              opacity={gapHighlight}
            />

            {/* Vertical Cutoff / Gap Divider */}
            <line
              x1={cutoffX}
              y1={padT}
              x2={cutoffX}
              y2={padT + plotH}
              stroke="#C2A5FF"
              strokeWidth={2.5}
              strokeDasharray="8 6"
            />
            <rect
              x={cutoffX - 88}
              y={padT + 10}
              width={176}
              height={32}
              rx={16}
              fill="#35214F"
              stroke="#8861E8"
              strokeWidth={1.5}
            />
            <text x={cutoffX} y={padT + 31} textAnchor="middle" fontSize={13} fill="#FFFFFF" fontWeight={750}>
              CUTOFF 15 NOV
            </text>

            {/* Observed Curve clipped up to cutoff */}
            <defs>
              <clipPath id="s04-obs-clip">
                <rect x={padL} y={0} width={(cutoffX - padL + 4) * obsRevealProgress} height={svgH} />
              </clipPath>
              <clipPath id="s04-fct-clip">
                <rect x={fctStartX - 4} y={0} width={(svgW - padR - fctStartX + 10) * fctRevealProgress} height={svgH} />
              </clipPath>
            </defs>

            <path
              d={obsPath}
              fill="none"
              stroke="#8861E8"
              strokeWidth={4.5}
              strokeLinecap="round"
              strokeLinejoin="round"
              clipPath="url(#s04-obs-clip)"
            />

            {/* Discontinuity / Gap connector dashed */}
            {fctRevealProgress > 0.02 && (
              <line
                x1={cutoffX}
                y1={coords[cutoffIdx].y}
                x2={fctStartX}
                y2={coords[obs.length].y}
                stroke="#9E93BA"
                strokeWidth={2.5}
                strokeDasharray="4 4"
              />
            )}

            {/* Forecast Curve */}
            <path
              d={fctPath}
              fill="none"
              stroke="#22E39B"
              strokeWidth={4.5}
              strokeLinecap="round"
              strokeLinejoin="round"
              clipPath="url(#s04-fct-clip)"
            />

            {/* X-axis key dates */}
            {[
              { idx: 0, label: '17 Ago (Inizio noto)', anchor: 'start' as const, dx: 0 },
              { idx: 45, label: '1 Ott', anchor: 'middle' as const, dx: 0 },
              { idx: 90, label: '15 Nov (Cutoff)', anchor: 'end' as const, dx: -10 },
              { idx: 105, label: '30 Nov', anchor: 'end' as const, dx: 0 },
            ].map((t) => (
              <text key={t.label} x={coords[t.idx].x + t.dx} y={svgH - 18} textAnchor={t.anchor} fontSize={14} fill="#A79CC4" fontWeight={650}>
                {t.label}
              </text>
            ))}

            {/* Following Tip Marker */}
            <circle cx={activeCoord.x} cy={activeCoord.y} r={16} fill="rgba(194,165,255,0.22)" />
            <circle
              cx={activeCoord.x}
              cy={activeCoord.y}
              r={7}
              fill={activeCoord.pt.kind === 'obs' ? '#C2A5FF' : '#22E39B'}
              stroke="#191224"
              strokeWidth={3}
            />
          </svg>
        </div>
      </div>

      {/* Bottom Legend strip (clear, legible, non-microscopic) */}
      <div
        style={{
          position: 'absolute',
          left: ADERA.marginX,
          right: ADERA.marginX,
          bottom: 70,
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          fontSize: 18,
          color: '#CFC7E2',
        }}
      >
        <div style={{ display: 'flex', gap: 36 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <span style={{ width: 22, height: 4, backgroundColor: '#8861E8', display: 'inline-block', borderRadius: 2 }} />
            <span>Storico noto simulato (91 giorni)</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <span style={{ width: 22, height: 4, backgroundColor: '#22E39B', display: 'inline-block', borderRadius: 2 }} />
            <span>Previsione Timestral 28M (16–30 nov, CPM €10,05–€11,22)</span>
          </div>
        </div>
        <div style={{ color: '#A79CC4', fontWeight: 600 }}>
          CTR forecast: baseline 14gg (circa 1,16–1,18%) · Nessun picco inventato
        </div>
      </div>
    </div>
  );
};
