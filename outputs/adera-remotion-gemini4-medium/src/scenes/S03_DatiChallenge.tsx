import React from 'react';
import { Easing, interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { ADERA, formatEurIT, formatIntIT, formatPctIT } from '../styles/theme';
import { CurtainWipeOverlay, PillBadge, SlideUpBlock } from '../components/MotionPrimitives';
import { VERIFIED_DATA } from '../data/verifiedData';

export const S03_DatiChallenge: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const summary = VERIFIED_DATA.observedSummary;
  const daily = VERIFIED_DATA.observedDaily;

  // Counter animation (easeOutCubic matching R4)
  const countP = interpolate(frame, [10, 82], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.out(Easing.cubic),
  });
  const currentImpr = Math.round(summary.impressions * countP);
  const currentRows = Math.round(summary.rows * countP);

  // Phase 1 (f=0..150): CSV rows visible; Phase 2 (f=135..220): morph rows into observed time series
  const tableOpacity = interpolate(frame, [130, 175], [1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.inOut(Easing.cubic),
  });
  const tableScale = interpolate(frame, [130, 175], [1, 0.92], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  const chartOpacity = interpolate(frame, [155, 200], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.out(Easing.cubic),
  });

  // Draw SVG curve progressively f=175..285
  const curveReveal = interpolate(frame, [170, 275], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.out(Easing.cubic),
  });

  const sampleRows = [
    daily[0],
    daily[29],
    daily[59],
    daily[76],
    daily[daily.length - 1],
  ];

  // SVG chart dimensions
  const cw = 820;
  const ch = 430;
  const padL = 62;
  const padR = 26;
  const padT = 36;
  const padB = 54;
  const plotW = cw - padL - padR;
  const plotH = ch - padT - padB;
  const minCpm = 5.4;
  const maxCpm = 10.2;

  const points = daily.map((d, idx) => {
    const x = padL + (idx / (daily.length - 1)) * plotW;
    const y = padT + (1 - (d.cpm - minCpm) / (maxCpm - minCpm)) * plotH;
    return { x, y, d };
  });

  const pathD = points.map((pt, i) => `${i === 0 ? 'M' : 'L'} ${pt.x.toFixed(1)} ${pt.y.toFixed(1)}`).join(' ');
  const visibleCount = Math.max(2, Math.round(curveReveal * points.length));
  const tipPt = points[Math.min(points.length - 1, visibleCount - 1)];

  return (
    <div
      style={{
        width: ADERA.width,
        height: ADERA.height,
        backgroundColor: ADERA.colors.bgLight,
        position: 'relative',
        overflow: 'hidden',
        fontFamily: ADERA.fontFamily,
        color: ADERA.colors.ink,
      }}
    >
      {/* Left column */}
      <div
        style={{
          position: 'absolute',
          left: ADERA.marginX,
          top: 124,
          width: 660,
        }}
      >
        <SlideUpBlock startFrame={4} distance={20}>
          <PillBadge label="SCENA AGGIUNTA · KIT ORGANIZZATORI SIMULATO" tone="light" />
        </SlideUpBlock>

        <SlideUpBlock startFrame={10} distance={26}>
          <div style={{ fontSize: 64, fontWeight: 800, letterSpacing: '-0.035em', lineHeight: 1.06, marginTop: 22 }}>
            Partiamo dai dati osservati.
          </div>
          <div style={{ fontSize: 23, color: ADERA.colors.inkSoft, marginTop: 14, lineHeight: 1.45 }}>
            Lo storico giornaliero simulato del kit ({summary.firstDay} → {summary.lastDay}) si trasforma in una serie temporale continua.
          </div>
        </SlideUpBlock>

        {/* Big Counter matching R4 easeOutCubic */}
        <div style={{ marginTop: 48 }}>
          <div style={{ fontSize: 16, fontWeight: 700, color: ADERA.colors.inkMuted, letterSpacing: '0.07em' }}>
            IMPRESSION STORICHE VERIFICATE ({formatIntIT(currentRows)} RIGHE)
          </div>
          <div
            style={{
              fontSize: 108,
              fontWeight: 900,
              letterSpacing: '-0.045em',
              lineHeight: 1,
              color: ADERA.colors.action,
              marginTop: 8,
              fontVariantNumeric: 'tabular-nums',
            }}
          >
            {formatIntIT(currentImpr)}
          </div>
        </div>

        {/* KPI cards */}
        <div style={{ marginTop: 42, display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 16 }}>
          {[
            { label: 'Giorni storici', val: `${summary.days} gg` },
            { label: 'CPM medio', val: formatEurIT(summary.cpmEur) },
            { label: 'CTR medio', val: formatPctIT(summary.ctrPct, 2) },
          ].map((k, idx) => (
            <SlideUpBlock key={k.label} startFrame={32 + idx * 10} distance={20}>
              <div
                style={{
                  backgroundColor: '#FFFFFF',
                  border: `1px solid ${ADERA.colors.borderLight}`,
                  borderRadius: 16,
                  padding: '18px 20px',
                }}
              >
                <div style={{ fontSize: 13, fontWeight: 650, color: ADERA.colors.inkMuted }}>{k.label}</div>
                <div style={{ fontSize: 30, fontWeight: 800, color: ADERA.colors.ink, marginTop: 6 }}>{k.val}</div>
              </div>
            </SlideUpBlock>
          ))}
        </div>
      </div>

      {/* Right stage: CSV Table transforming into Time Series */}
      <div
        style={{
          position: 'absolute',
          right: ADERA.marginX,
          top: 164,
          width: 860,
          height: 740,
        }}
      >
        {/* Phase 1: Structured CSV Rows */}
        <div
          style={{
            position: 'absolute',
            inset: 0,
            backgroundColor: '#FFFFFF',
            border: `1px solid ${ADERA.colors.borderLight}`,
            borderRadius: 24,
            padding: 32,
            boxShadow: '0 24px 60px rgba(41, 35, 57, 0.08)',
            opacity: tableOpacity,
            transform: `scale(${tableScale})`,
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'space-between',
          }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <div style={{ fontSize: 14, fontWeight: 700, color: ADERA.colors.action, letterSpacing: '0.06em' }}>
                STORICO_GIORNALIERO.CSV · ESTRATTO SIMULATO
              </div>
              <div style={{ fontSize: 24, fontWeight: 750, marginTop: 4 }}>
                Aggregazione giornaliera su 91 giorni consecutivi
              </div>
            </div>
            <PillBadge label="0 gap interni" tone="mint" />
          </div>

          <div style={{ marginTop: 20, display: 'flex', flexDirection: 'column', gap: 14 }}>
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: '1.2fr 1fr 0.8fr 0.9fr 0.9fr',
                fontSize: 13,
                fontWeight: 700,
                color: ADERA.colors.inkMuted,
                padding: '0 16px',
                textTransform: 'uppercase',
              }}
            >
              <span>Data</span>
              <span>Impression</span>
              <span>Click</span>
              <span>CTR</span>
              <span>CPM</span>
            </div>
            {sampleRows.map((row, idx) => {
              const rp = spring({
                frame: frame - (22 + idx * 12),
                fps,
                config: { damping: 20, stiffness: 170 },
              });
              return (
                <div
                  key={row.day}
                  style={{
                    display: 'grid',
                    gridTemplateColumns: '1.2fr 1fr 0.8fr 0.9fr 0.9fr',
                    alignItems: 'center',
                    padding: '18px 16px',
                    borderRadius: 14,
                    backgroundColor: idx === sampleRows.length - 1 ? '#EFEAFA' : '#F8F6FC',
                    border: `1px solid ${idx === sampleRows.length - 1 ? '#CBB9F2' : '#ECE7F5'}`,
                    fontSize: 18,
                    fontWeight: 650,
                    transform: `translateY(${interpolate(rp, [0, 1], [18, 0])}px)`,
                    opacity: interpolate(rp, [0, 1], [0, 1]),
                    fontVariantNumeric: 'tabular-nums',
                  }}
                >
                  <span style={{ color: ADERA.colors.plum }}>{row.day}</span>
                  <span>{formatIntIT(row.impressions)}</span>
                  <span>{formatIntIT(row.clicks)}</span>
                  <span>{formatPctIT(row.ctr, 2)}</span>
                  <span style={{ color: ADERA.colors.action }}>{formatEurIT(row.cpm)}</span>
                </div>
              );
            })}
          </div>

          <div style={{ fontSize: 15, color: ADERA.colors.inkMuted, marginTop: 12 }}>
            Spesa totale nel periodo osservato: <strong>{formatEurIT(summary.spend, 2)}</strong> · {formatIntIT(summary.clicks)} click
          </div>
        </div>

        {/* Phase 2: Transformed Time Series Card */}
        <div
          style={{
            position: 'absolute',
            inset: 0,
            backgroundColor: '#FFFFFF',
            border: `1px solid ${ADERA.colors.borderLight}`,
            borderRadius: 24,
            padding: 32,
            boxShadow: '0 24px 60px rgba(41, 35, 57, 0.10)',
            opacity: chartOpacity,
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'space-between',
          }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <div style={{ fontSize: 14, fontWeight: 700, color: ADERA.colors.action, letterSpacing: '0.06em' }}>
                SERIE TEMPORALE OSSERVATA · CPM (€)
              </div>
              <div style={{ fontSize: 26, fontWeight: 800, marginTop: 4 }}>
                Trend reale del kit dal 17 agosto al 15 novembre 2026
              </div>
            </div>
            <PillBadge label="Cutoff 15 Nov · €8,97" tone="accent" />
          </div>

          <svg width={cw} height={ch} viewBox={`0 0 ${cw} ${ch}`} style={{ overflow: 'visible' }}>
            {/* Y Grid */}
            {[6, 7, 8, 9, 10].map((v) => {
              const y = padT + (1 - (v - minCpm) / (maxCpm - minCpm)) * plotH;
              return (
                <g key={v}>
                  <line x1={padL} y1={y} x2={cw - padR} y2={y} stroke="#ECE7F5" strokeWidth={1.5} />
                  <text x={padL - 12} y={y + 5} textAnchor="end" fontSize={13} fill={ADERA.colors.inkMuted} fontWeight={600}>
                    €{v}
                  </text>
                </g>
              );
            })}

            {/* X axis labels */}
            {[
              { idx: 0, label: '17 Ago' },
              { idx: 30, label: '16 Set' },
              { idx: 60, label: '16 Ott' },
              { idx: 90, label: '15 Nov' },
            ].map((tick) => {
              const x = padL + (tick.idx / (daily.length - 1)) * plotW;
              return (
                <text key={tick.label} x={x} y={ch - 14} textAnchor="middle" fontSize={13} fill={ADERA.colors.inkMuted} fontWeight={650}>
                  {tick.label}
                </text>
              );
            })}

            {/* Clip reveal of curve */}
            <defs>
              <clipPath id="s03-curve-clip">
                <rect x={padL} y={0} width={plotW * curveReveal} height={ch} />
              </clipPath>
            </defs>

            <path
              d={pathD}
              fill="none"
              stroke={ADERA.colors.action}
              strokeWidth={4}
              strokeLinecap="round"
              strokeLinejoin="round"
              clipPath="url(#s03-curve-clip)"
            />

            {/* Moving tip dot */}
            {curveReveal > 0.05 && (
              <g>
                <circle cx={tipPt.x} cy={tipPt.y} r={14} fill="rgba(112,70,206,0.18)" />
                <circle cx={tipPt.x} cy={tipPt.y} r={6.5} fill={ADERA.colors.action} stroke="#FFFFFF" strokeWidth={2.5} />
              </g>
            )}
          </svg>

          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 15, color: ADERA.colors.inkSoft }}>
            <span>Inizio serie: <strong>€6,13</strong> (17 ago)</span>
            <span>Ultimo giorno noto al cutoff: <strong>€8,97</strong> (15 nov)</span>
          </div>
        </div>
      </div>

      {/* Bottom-to-top Wipe to dark S04 */}
      <CurtainWipeOverlay startFrame={318} durationFrames={12} color={ADERA.colors.bgDark} direction="bottom-to-top" />
    </div>
  );
};
