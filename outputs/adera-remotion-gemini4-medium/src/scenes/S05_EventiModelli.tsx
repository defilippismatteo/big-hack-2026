import React from 'react';
import { Easing, interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { ADERA, formatEurIT } from '../styles/theme';
import { CurtainWipeOverlay, PillBadge, SlideUpBlock } from '../components/MotionPrimitives';
import { ProviderLogo } from '../components/BrandLogo';
import { VERIFIED_DATA } from '../data/verifiedData';

export const S05_EventiModelli: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const fct = VERIFIED_DATA.forecastDaily;
  const comb = VERIFIED_DATA.validation.combined;

  // Map forecast points onto SVG
  const w = 960;
  const h = 320;
  const padL = 56;
  const padR = 36;
  const padT = 36;
  const padB = 46;
  const plotW = w - padL - padR;
  const plotH = h - padT - padB;
  const minCpm = 9.6;
  const maxCpm = 11.6;

  const pts = fct.map((d, i) => ({
    x: padL + (i / (fct.length - 1)) * plotW,
    y: padT + (1 - (d.cpm - minCpm) / (maxCpm - minCpm)) * plotH,
    d,
  }));

  const pathD = pts.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x.toFixed(1)} ${p.y.toFixed(1)}`).join(' ');

  // Popup events verified in forecastDaily + calendario.csv
  const eventPopups = [
    { idx: 4, label: 'Black Week', date: '20/11/2026', cpm: fct[4].cpm, start: 34, color: '#C2A5FF' },
    { idx: 11, label: 'Black Friday', date: '27/11/2026', cpm: fct[11].cpm, start: 68, color: '#22E39B' },
    { idx: 14, label: 'Cyber Monday', date: '30/11/2026', cpm: fct[14].cpm, start: 102, color: '#FFB84D' },
  ];

  return (
    <div
      style={{
        width: ADERA.width,
        height: ADERA.height,
        background: `linear-gradient(155deg, ${ADERA.colors.bgDark} 0%, #26183D 65%, ${ADERA.colors.plum} 100%)`,
        position: 'relative',
        overflow: 'hidden',
        fontFamily: ADERA.fontFamily,
        color: '#FFFFFF',
      }}
    >
      {/* Left Header + Method Clarification */}
      <div
        style={{
          position: 'absolute',
          left: ADERA.marginX,
          top: 84,
          width: 560,
        }}
      >
        <SlideUpBlock startFrame={4} distance={18}>
          <PillBadge label="SCENA AGGIUNTA · EVENTI & BENCHMARK CRONOLOGICO" tone="dark" />
        </SlideUpBlock>

        <SlideUpBlock startFrame={10} distance={24}>
          <div style={{ fontSize: 54, fontWeight: 800, letterSpacing: '-0.035em', lineHeight: 1.08, marginTop: 22 }}>
            Eventi di novembre e ruoli verificati dei modelli.
          </div>
        </SlideUpBlock>

        <SlideUpBlock startFrame={22} distance={20}>
          <div
            style={{
              marginTop: 28,
              backgroundColor: 'rgba(19, 13, 30, 0.72)',
              border: '1px solid #483569',
              borderRadius: 18,
              padding: 24,
            }}
          >
            <div style={{ fontSize: 13, fontWeight: 750, color: ADERA.colors.accentSoft, letterSpacing: '0.07em' }}>
              METODO ATTIVO IN OVERVIEW
            </div>
            <div style={{ fontSize: 20, fontWeight: 750, color: '#FFFFFF', marginTop: 8, wordBreak: 'break-word' }}>
              ctr_baseline14d__cpm_timestral28m
            </div>
            <div style={{ fontSize: 16, color: '#CFC6E4', marginTop: 10, lineHeight: 1.45 }}>
              In overview il forecast CPM è affidato a <strong>Timestral 28M</strong> e il CTR alla baseline 14 giorni: <strong>non è un ensemble CatBoost</strong>.
            </div>
          </div>
        </SlideUpBlock>

        <SlideUpBlock startFrame={45} distance={18}>
          <div style={{ marginTop: 22, fontSize: 16, color: '#B7ACD1', lineHeight: 1.5 }}>
            I tre marker sul grafico mostrano i valori reali salvati in <code>overview.json</code> per le date di calendario (nessun picco artificiale aggiunto).
          </div>
        </SlideUpBlock>
      </div>

      {/* Right Top: Forecast Curve with Black Week / Black Friday / Cyber Monday Popups */}
      <div
        style={{
          position: 'absolute',
          right: ADERA.marginX,
          top: 84,
          width: 980,
          backgroundColor: 'rgba(20, 14, 31, 0.85)',
          border: '1px solid #453365',
          borderRadius: 24,
          padding: '24px 28px',
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
          <div style={{ fontSize: 15, fontWeight: 700, color: '#D4C2FA', letterSpacing: '0.05em' }}>
            FORECAST CPM TIMESTRAL 28M · 16–30 NOVEMBRE 2026
          </div>
          <span style={{ fontSize: 14, color: '#A598C4' }}>Spesa forecast costante €1.098,22/giorno</span>
        </div>

        <svg width={w} height={h} viewBox={`0 0 ${w} ${h}`} style={{ overflow: 'visible' }}>
          {[10.0, 10.5, 11.0, 11.5].map((v) => {
            const y = padT + (1 - (v - minCpm) / (maxCpm - minCpm)) * plotH;
            return (
              <g key={v}>
                <line x1={padL} y1={y} x2={w - padR} y2={y} stroke="#2E2244" strokeWidth={1.3} />
                <text x={padL - 10} y={y + 4} textAnchor="end" fontSize={13} fill="#8D80AC">
                  €{v.toFixed(1).replace('.', ',')}
                </text>
              </g>
            );
          })}

          <path d={pathD} fill="none" stroke="#22E39B" strokeWidth={4} strokeLinecap="round" strokeLinejoin="round" />

          {pts.map((p, i) => (
            <circle key={i} cx={p.x} cy={p.y} r={3.5} fill="#22E39B" />
          ))}

          {/* X Labels */}
          {[0, 4, 8, 11, 14].map((idx) => (
            <text key={idx} x={pts[idx].x} y={h - 10} textAnchor="middle" fontSize={13} fill="#A79CC4" fontWeight={650}>
              {pts[idx].d.day.slice(5).replace('-', '/')}
            </text>
          ))}

          {/* Animated Event Popups */}
          {eventPopups.map((ev, idx) => {
            const p = spring({
              frame: frame - ev.start,
              fps,
              config: { damping: 16, stiffness: 180, mass: 0.75 },
            });
            const anchor = pts[ev.idx];
            const isBelow = idx === 2;
            const boxY = isBelow ? anchor.y + 30 : idx === 1 ? anchor.y - 108 : anchor.y - 96;
            const boxX =
              idx === 0
                ? Math.max(padL, anchor.x - 100)
                : idx === 1
                ? anchor.x - 190
                : Math.min(w - 220, anchor.x - 180);
            const lineY2 = isBelow ? boxY : boxY + 66;
            return (
              <g key={ev.label} opacity={interpolate(p, [0, 0.4, 1], [0, 1, 1])}>
                <line
                  x1={anchor.x}
                  y1={anchor.y}
                  x2={anchor.x}
                  y2={lineY2}
                  stroke={ev.color}
                  strokeWidth={2}
                  strokeDasharray="4 4"
                />
                <circle cx={anchor.x} cy={anchor.y} r={8} fill={ev.color} stroke="#140E1F" strokeWidth={3} />
                <g transform={`translate(${boxX}, ${boxY + interpolate(p, [0, 1], [14, 0])})`}>
                  <rect width={212} height={66} rx={12} fill="#291D3F" stroke={ev.color} strokeWidth={1.8} />
                  <text x={14} y={24} fontSize={14} fontWeight={800} fill={ev.color}>
                    {ev.label} · {ev.date.slice(0, 5)}
                  </text>
                  <text x={14} y={48} fontSize={17} fontWeight={750} fill="#FFFFFF">
                    CPM {formatEurIT(ev.cpm)}
                  </text>
                </g>
              </g>
            );
          })}
        </svg>
      </div>

      {/* Right Bottom: Mistral + Timestral 28M vs CatBoost (verified model-validation.json) */}
      <div
        style={{
          position: 'absolute',
          right: ADERA.marginX,
          top: 526,
          width: 980,
          display: 'grid',
          gridTemplateColumns: '1fr 1fr',
          gap: 24,
        }}
      >
        {/* Mistral / Timestral 28M */}
        <SlideUpBlock startFrame={130} distance={26}>
          <div
            style={{
              backgroundColor: 'rgba(20, 14, 31, 0.88)',
              border: '1px solid #594185',
              borderRadius: 22,
              padding: 26,
              height: 410,
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
                <div
                  style={{
                    width: 58,
                    height: 58,
                    borderRadius: 14,
                    backgroundColor: '#FFFFFF',
                    display: 'grid',
                    placeItems: 'center',
                  }}
                >
                  <ProviderLogo name="mistral" size={40} />
                </div>
                <div>
                  <div style={{ fontSize: 13, fontWeight: 700, color: ADERA.colors.accentSoft }}>MISTRAL AI · SERIE TEMPORALI</div>
                  <div style={{ fontSize: 28, fontWeight: 850 }}>Timestral 28M</div>
                </div>
              </div>
              <PillBadge label="Usato in Overview (CPM)" tone="accent" />
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14 }}>
              <div style={{ backgroundColor: '#271B3D', borderRadius: 14, padding: 16 }}>
                <div style={{ fontSize: 13, color: '#B5A8D1' }}>CPM WMAE (2 fold)</div>
                <div style={{ fontSize: 34, fontWeight: 900, color: '#22E39B', marginTop: 4 }}>
                  {comb.cpm_timestral_28m.wmae.toFixed(3)}
                </div>
                <div style={{ fontSize: 13, color: '#9D90BC', marginTop: 4 }}>vs baseline {comb.cpm_baseline.wmae.toFixed(3)}</div>
              </div>
              <div style={{ backgroundColor: '#271B3D', borderRadius: 14, padding: 16 }}>
                <div style={{ fontSize: 13, color: '#B5A8D1' }}>CTR WMAE (2 fold)</div>
                <div style={{ fontSize: 34, fontWeight: 900, color: '#EAE4F7', marginTop: 4 }}>
                  {comb.ctr_timestral_28m.wmae.toFixed(3)}
                </div>
                <div style={{ fontSize: 13, color: '#9D90BC', marginTop: 4 }}>vs baseline {comb.ctr_baseline.wmae.toFixed(3)}</div>
              </div>
            </div>

            <div style={{ fontSize: 15, color: '#CFC6E4', lineHeight: 1.45 }}>
              Ruolo verificato: modello zero-shot per il forecast CPM su 699 righe future (`16–30 nov`).
            </div>
          </div>
        </SlideUpBlock>

        {/* CatBoost */}
        <SlideUpBlock startFrame={150} distance={26}>
          <div
            style={{
              backgroundColor: 'rgba(20, 14, 31, 0.88)',
              border: '1px solid #453365',
              borderRadius: 22,
              padding: 26,
              height: 410,
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
                <div
                  style={{
                    width: 58,
                    height: 58,
                    borderRadius: 14,
                    backgroundColor: '#FFFFFF',
                    display: 'grid',
                    placeItems: 'center',
                  }}
                >
                  <ProviderLogo name="catboost" size={40} />
                </div>
                <div>
                  <div style={{ fontSize: 13, fontWeight: 700, color: '#CFC6E4' }}>BENCHMARK TABELLARE</div>
                  <div style={{ fontSize: 28, fontWeight: 850 }}>CatBoost</div>
                </div>
              </div>
              <PillBadge label="Validazione 759 righe" tone="dark" />
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14 }}>
              <div style={{ backgroundColor: '#271B3D', borderRadius: 14, padding: 16 }}>
                <div style={{ fontSize: 13, color: '#B5A8D1' }}>CPM WMAE (2 fold)</div>
                <div style={{ fontSize: 34, fontWeight: 900, color: '#EAE4F7', marginTop: 4 }}>
                  {comb.cpm_catboost.wmae.toFixed(3)}
                </div>
                <div style={{ fontSize: 13, color: '#9D90BC', marginTop: 4 }}>Mix 50/50: {comb.cpm_mix_50_50.wmae.toFixed(3)}</div>
              </div>
              <div style={{ backgroundColor: '#271B3D', borderRadius: 14, padding: 16 }}>
                <div style={{ fontSize: 13, color: '#B5A8D1' }}>CTR Fold 2 WMAE</div>
                <div style={{ fontSize: 34, fontWeight: 900, color: '#C2A5FF', marginTop: 4 }}>
                  {VERIFIED_DATA.validation.folds[1].tutti.ctr_catboost.wmae.toFixed(3)}
                </div>
                <div style={{ fontSize: 13, color: '#9D90BC', marginTop: 4 }}>Combinato: {comb.ctr_catboost.wmae.toFixed(3)}</div>
              </div>
            </div>

            <div style={{ fontSize: 15, color: '#CFC6E4', lineHeight: 1.45 }}>
              Ruolo verificato: confrontato su 2 fold cronologici; sul combinato CTR resta dietro alla baseline ({comb.ctr_baseline.wmae.toFixed(3)}).
            </div>
          </div>
        </SlideUpBlock>
      </div>

      <CurtainWipeOverlay startFrame={288} durationFrames={12} color={ADERA.colors.bgLight} direction="left-to-right" />
    </div>
  );
};
