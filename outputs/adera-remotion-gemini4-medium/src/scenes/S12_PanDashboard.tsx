import React from 'react';
import { ArrowLeft } from 'lucide-react';
import { Easing, interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { ADERA, formatEurIT, formatIntIT, formatPctIT } from '../styles/theme';
import { PillBadge, SlideUpBlock } from '../components/MotionPrimitives';
import { AderaOriginalLogo } from '../components/BrandLogo';
import { VERIFIED_DATA } from '../data/verifiedData';

export const S12_PanDashboard: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Arrow-guided camera pan LEFT (f=36..146):
  // World spans 3840px wide; starts viewing right bridge (x=-1920), arrow points LEFT, camera pans LEFT to x=0 (Dashboard)
  const panP = interpolate(frame, [36, 148], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.inOut(Easing.cubic),
  });
  const worldX = interpolate(panP, [0, 1], [-1920, 0]);

  // Arrow bounce & travel during pan
  const arrowPulse = Math.sin(frame / 7) * 10;

  // R10 -> R11 7-frame card scale-collapse transition at end of S12 (f=500..510)
  const collapseScale = interpolate(frame, [500, 509], [1, 0.88], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.in(Easing.cubic),
  });
  const collapseOpacity = interpolate(frame, [500, 509], [1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  const fct = VERIFIED_DATA.forecastDaily;
  const budget = VERIFIED_DATA.budget;
  const u3 = VERIFIED_DATA.creatives['FGR-U3'];
  const b1 = VERIFIED_DATA.creatives['FGR-B1'];
  const s1 = VERIFIED_DATA.creatives['FGR-S1'];

  // Mini SVG curve inside Quantitative Dashboard panel
  const mw = 680;
  const mh = 185;
  const mPts = fct.map((d, i) => {
    const x = 18 + (i / (fct.length - 1)) * (mw - 36);
    const y = 20 + (1 - (d.cpm - 9.8) / (11.5 - 9.8)) * (mh - 40);
    return `${i === 0 ? 'M' : 'L'} ${x.toFixed(1)} ${y.toFixed(1)}`;
  }).join(' ');

  const dashSpring = spring({
    frame: frame - 110,
    fps,
    config: { damping: 20, stiffness: 160 },
  });

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
      {/* 2-Viewport Wide Canvas (3840px) */}
      <div
        style={{
          position: 'absolute',
          left: 0,
          top: 0,
          width: 3840,
          height: 1080,
          transform: `translateX(${worldX}px)`,
        }}
      >
        {/* RIGHT HALF (x=1920..3840): Starting Bridge with Arrow Guiding Left Pan */}
        <div
          style={{
            position: 'absolute',
            left: 1920,
            top: 0,
            width: 1920,
            height: 1080,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '0 154px',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: 48 }}>
            <div
              style={{
                width: 132,
                height: 132,
                borderRadius: 999,
                backgroundColor: ADERA.colors.action,
                color: '#FFFFFF',
                display: 'grid',
                placeItems: 'center',
                boxShadow: '0 24px 60px rgba(112, 70, 206, 0.35)',
                transform: `translateX(${arrowPulse}px)`,
                flexShrink: 0,
              }}
            >
              <ArrowLeft size={66} strokeWidth={2.5} />
            </div>
            <div>
              <PillBadge label="SCENA AGGIUNTA · PAN A SINISTRA GUIDATO" tone="light" />
              <div style={{ fontSize: 64, fontWeight: 850, letterSpacing: '-0.035em', lineHeight: 1.06, marginTop: 18 }}>
                Portiamo i due piani nella dashboard ADERA.
              </div>
              <div style={{ fontSize: 24, color: ADERA.colors.inkSoft, marginTop: 14 }}>
                Previsione quantitativa e segnali qualitativi restano separati e verificabili.
              </div>
            </div>
          </div>
        </div>

        {/* LEFT HALF (x=0..1920): ADERA Dashboard (adera-revamp styling) */}
        <div
          style={{
            position: 'absolute',
            left: 0,
            top: 0,
            width: 1920,
            height: 1080,
            padding: '54px 120px',
            transform: `scale(${collapseScale})`,
            opacity: collapseOpacity,
          }}
        >
          {/* Top Bar */}
          <div
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              backgroundColor: '#FFFFFF',
              border: `1px solid ${ADERA.colors.borderLight}`,
              borderRadius: 20,
              padding: '16px 28px',
              boxShadow: '0 12px 34px rgba(41, 35, 57, 0.05)',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: 20 }}>
              <AderaOriginalLogo height={44} />
              <div style={{ width: 1.5, height: 30, backgroundColor: ADERA.colors.borderLight }} />
              <span style={{ fontSize: 18, fontWeight: 750, color: ADERA.colors.plum }}>
                ADERA Decision Workspace · Cutoff {VERIFIED_DATA.source.cutoff}
              </span>
            </div>
            <PillBadge label="PIANI DISTINTI · NESSUNA FUSIONE PREDITTIVA AUTOMATICA" tone="accent" />
          </div>

          {/* Headline */}
          <div style={{ marginTop: 26, display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
            <div>
              <div style={{ fontSize: 42, fontWeight: 850, letterSpacing: '-0.03em' }}>
                Quantitativo e qualitativo restano distinti.
              </div>
              <div style={{ fontSize: 19, color: ADERA.colors.inkSoft, marginTop: 4 }}>
                Nessuna pipeline mescola le probabilità Decision 1 dentro i modelli numerici Timestral / CatBoost.
              </div>
            </div>
            <div style={{ fontSize: 15, fontWeight: 650, color: ADERA.colors.inkMuted }}>
              Fonte: adera-revamp/public/data/overview.json & product-story.json
            </div>
          </div>

          {/* Two Strictly Separate Dashboard Columns */}
          <div
            style={{
              marginTop: 26,
              display: 'grid',
              gridTemplateColumns: '1fr 1fr',
              gap: 28,
              opacity: interpolate(dashSpring, [0, 1], [0.4, 1]),
            }}
          >
            {/* PANEL A: QUANTITATIVE FORECAST & BUDGET */}
            <div
              style={{
                backgroundColor: '#FFFFFF',
                border: `1.5px solid ${ADERA.colors.borderLight}`,
                borderRadius: 24,
                padding: 30,
                boxShadow: '0 22px 60px rgba(41, 35, 57, 0.07)',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
                height: 690,
              }}
            >
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <PillBadge label="PIANO 1 · ANALISI QUANTITATIVA" tone="light" />
                  <span style={{ fontSize: 13, fontWeight: 700, color: ADERA.colors.action }}>
                    {VERIFIED_DATA.source.method}
                  </span>
                </div>

                <div style={{ fontSize: 28, fontWeight: 800, marginTop: 16 }}>
                  Forecast 16–30 Nov & Scenario Budget ±20%
                </div>

                {/* KPI Strip */}
                <div style={{ marginTop: 18, display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 14 }}>
                  <div style={{ backgroundColor: '#F7F5FB', borderRadius: 16, padding: 16 }}>
                    <div style={{ fontSize: 12, fontWeight: 700, color: ADERA.colors.inkMuted }}>Righe forecast</div>
                    <div style={{ fontSize: 28, fontWeight: 900, color: ADERA.colors.plum, marginTop: 4 }}>
                      {VERIFIED_DATA.forecastRowsCount}
                    </div>
                  </div>
                  <div style={{ backgroundColor: '#F7F5FB', borderRadius: 16, padding: 16 }}>
                    <div style={{ fontSize: 12, fontWeight: 700, color: ADERA.colors.inkMuted }}>Budget totale</div>
                    <div style={{ fontSize: 26, fontWeight: 900, color: ADERA.colors.ink, marginTop: 4 }}>
                      {formatEurIT(budget.originalTotal, 0)}
                    </div>
                  </div>
                  <div style={{ backgroundColor: '#EAF7F0', borderRadius: 16, padding: 16, border: '1px solid #BFE5D0' }}>
                    <div style={{ fontSize: 12, fontWeight: 700, color: '#16744C' }}>Click scenario ±20%</div>
                    <div style={{ fontSize: 26, fontWeight: 900, color: '#16744C', marginTop: 4 }}>
                      {formatIntIT(budget.scenarioClicks)}
                    </div>
                    <div style={{ fontSize: 12, color: '#16744C', fontWeight: 650 }}>
                      vs {formatIntIT(budget.baseClicks)} base (+{budget.scenarioClicks - budget.baseClicks})
                    </div>
                  </div>
                </div>

                {/* Mini CPM Forecast Chart */}
                <div style={{ marginTop: 22, backgroundColor: '#FAF8FD', borderRadius: 18, padding: 18, border: '1px solid #ECE7F5' }}>
                  <div style={{ fontSize: 13, fontWeight: 700, color: ADERA.colors.inkSoft, marginBottom: 6 }}>
                    CPM previsto Timestral 28M · Black Week (€10,26) → Black Friday (€10,92) → Cyber Monday (€10,87)
                  </div>
                  <svg width={mw} height={mh} viewBox={`0 0 ${mw} ${mh}`}>
                    <path d={mPts} fill="none" stroke={ADERA.colors.action} strokeWidth={4} strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                </div>
              </div>

              <div style={{ fontSize: 15, color: ADERA.colors.inkSoft, borderTop: `1px solid ${ADERA.colors.borderLight}`, paddingTop: 14 }}>
                Serie storica da kit organizzatori simulato (`9.359.976` impression). Validazione su 2 fold (`759` righe): Timestral CPM WMAE `0.699` vs CatBoost `0.700`.
              </div>
            </div>

            {/* PANEL B: QUALITATIVE DECISION 1 & INTERVIEWS */}
            <div
              style={{
                backgroundColor: ADERA.colors.bgDark,
                border: `1.5px solid ${ADERA.colors.borderDark}`,
                borderRadius: 24,
                padding: 30,
                color: '#FFFFFF',
                boxShadow: '0 22px 60px rgba(25, 18, 36, 0.18)',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
                height: 690,
              }}
            >
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <PillBadge label="PIANO 2 · SEGNALI QUALITATIVI SINTETICI" tone="dark" />
                  <span style={{ fontSize: 13, fontWeight: 700, color: '#C2A5FF' }}>
                    600 profili · 7.200 valutazioni
                  </span>
                </div>

                <div style={{ fontSize: 28, fontWeight: 800, marginTop: 16 }}>
                  Probabilità simulate Decision 1 (non CTR) & Interviste
                </div>

                {/* Asset Comparison Rows */}
                <div style={{ marginTop: 18, display: 'flex', flexDirection: 'column', gap: 12 }}>
                  {[u3, s1, b1].map((asset, idx) => (
                    <div
                      key={asset.asset_id}
                      style={{
                        display: 'grid',
                        gridTemplateColumns: '100px 1fr 110px 110px',
                        alignItems: 'center',
                        gap: 12,
                        padding: '15px 18px',
                        borderRadius: 16,
                        backgroundColor: idx === 0 ? 'rgba(34, 227, 155, 0.10)' : '#231934',
                        border: `1px solid ${idx === 0 ? '#22E39B' : '#3A2C52'}`,
                      }}
                    >
                      <span style={{ fontSize: 18, fontWeight: 850, color: idx === 0 ? '#22E39B' : '#FFFFFF' }}>
                        {asset.asset_id}
                      </span>
                      <span style={{ fontSize: 15, color: '#EAE4F7' }}>{asset.headline}</span>
                      <div style={{ textAlign: 'right' }}>
                        <div style={{ fontSize: 11, color: '#9E93BA' }}>Click sim.</div>
                        <div style={{ fontSize: 18, fontWeight: 800 }}>
                          {formatPctIT(asset.decision.actions.click * 100, 1)}
                        </div>
                      </div>
                      <div style={{ textAlign: 'right' }}>
                        <div style={{ fontSize: 11, color: '#9E93BA' }}>Interviste</div>
                        <div
                          style={{
                            fontSize: 18,
                            fontWeight: 800,
                            color: asset.interviews.net_mentions >= 0 ? '#22E39B' : '#FF7087',
                          }}
                        >
                          {asset.interviews.net_mentions >= 0 ? `+${asset.interviews.net_mentions}` : asset.interviews.net_mentions}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>

                {/* Verbatim Takeaway */}
                <div style={{ marginTop: 18, backgroundColor: '#231934', borderRadius: 18, padding: 20, border: '1px solid #3A2C52' }}>
                  <div style={{ fontSize: 12, fontWeight: 750, color: '#C2A5FF', letterSpacing: '0.07em' }}>
                    VERDETTO ESECUTIVO DA PRODUCT-STORY.JSON
                  </div>
                  <div style={{ fontSize: 15.5, color: '#EAE4F7', marginTop: 8, lineHeight: 1.5 }}>
                    «{VERIFIED_DATA.overallStory.executive_verdict}»
                  </div>
                </div>
              </div>

              <div style={{ fontSize: 15, color: '#B7ACD1', borderTop: '1px solid #3A2C52', paddingTop: 14 }}>
                Le probabilità Decision 1 guidano la revisione creativa e di copy; non sostituiscono né correggono il forecast numerico.
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
