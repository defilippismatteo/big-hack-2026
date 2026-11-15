import React from 'react';
import { Easing, interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { ADERA, formatPctIT } from '../styles/theme';
import { PillBadge, SlideUpBlock } from '../components/MotionPrimitives';
import { VERIFIED_DATA } from '../data/verifiedData';

export const S10_MorphSegnali: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Accent #7046CE -> Dark #191224 background shift
  const darkMix = interpolate(frame, [20, 120], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.inOut(Easing.cubic),
  });

  // Radial convergence progress: floating chips converge toward center-right document (f=28..120)
  const morphP = interpolate(frame, [28, 128], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.inOut(Easing.cubic),
  });

  const docSpring = spring({
    frame: frame - 102,
    fps,
    config: { damping: 19, stiffness: 160, mass: 0.85 },
  });

  const chips = [
    { label: 'FGR-U3 · Click sim. 15,0%', x0: 840, y0: 140, color: '#22E39B' },
    { label: 'FGR-U3 · +150 menzioni nette', x0: 1320, y0: 210, color: '#C2A5FF' },
    { label: 'FGR-B1 · Scroll 37,3%', x0: 760, y0: 480, color: '#FF7087' },
    { label: 'FGR-B1 · -113 menzioni nette', x0: 1360, y0: 560, color: '#FF7087' },
    { label: 'FGR-S1 · -83 menzioni nette', x0: 880, y0: 760, color: '#FFB84D' },
    { label: 'Reso gratuito vs Countdown 48h', x0: 1290, y0: 790, color: '#C2A5FF' },
  ];

  const targetX = 1140;
  const targetY = 470;

  const u3 = VERIFIED_DATA.creatives['FGR-U3'];
  const b1 = VERIFIED_DATA.creatives['FGR-B1'];
  const s1 = VERIFIED_DATA.creatives['FGR-S1'];

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
      {/* Animated Accent Overlay fading to Dark */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          background: 'linear-gradient(135deg, #7046CE 0%, #35214F 100%)',
          opacity: 1 - darkMix,
          pointerEvents: 'none',
        }}
      />

      {/* Left Slam Typography matching R9 + R7 */}
      <div
        style={{
          position: 'absolute',
          left: ADERA.marginX,
          top: 170,
          width: 620,
          zIndex: 10,
        }}
      >
        <SlideUpBlock startFrame={4} distance={18}>
          <PillBadge label="AGGREGAZIONE SEGNALI · 36 ASSET VALUTATI" tone="dark" />
        </SlideUpBlock>

        <SlideUpBlock startFrame={12} distance={28}>
          <div style={{ fontSize: 78, fontWeight: 900, letterSpacing: '-0.04em', lineHeight: 1.0, marginTop: 24 }}>
            Dalle reazioni,
            <br />
            <span style={{ color: '#C2A5FF' }}>segnali.</span>
          </div>
        </SlideUpBlock>

        <SlideUpBlock startFrame={28} distance={22}>
          <div style={{ fontSize: 23, color: '#D6CCE8', marginTop: 26, lineHeight: 1.5 }}>
            Ogni azione del feed e ogni nota di intervista convergono in un documento strutturato per creatività, mantenendo separati segnali qualitativi e stime quantitative.
          </div>
        </SlideUpBlock>
      </div>

      {/* Floating Reaction Pills converging radially */}
      {chips.map((c, idx) => {
        const cx = interpolate(morphP, [0, 1], [c.x0, targetX]);
        const cy = interpolate(morphP, [0, 1], [c.y0, targetY]);
        const sc = interpolate(morphP, [0, 0.75, 1], [1, 0.85, 0.3]);
        const op = interpolate(morphP, [0, 0.7, 1], [1, 0.9, 0]);
        return (
          <div
            key={idx}
            style={{
              position: 'absolute',
              left: cx,
              top: cy,
              transform: `translate(-50%, -50%) scale(${sc})`,
              opacity: op,
              padding: '14px 22px',
              borderRadius: 999,
              backgroundColor: 'rgba(25, 18, 36, 0.86)',
              border: `2px solid ${c.color}`,
              color: '#FFFFFF',
              fontSize: 18,
              fontWeight: 750,
              whiteSpace: 'nowrap',
              boxShadow: '0 16px 40px rgba(0,0,0,0.35)',
              zIndex: 15,
            }}
          >
            {c.label}
          </div>
        );
      })}

      {/* Morphed Structured Signals Document */}
      <div
        style={{
          position: 'absolute',
          right: ADERA.marginX,
          top: 154,
          width: 840,
          backgroundColor: '#211732',
          border: '1.5px solid #594185',
          borderRadius: 26,
          padding: 36,
          boxShadow: '0 30px 90px rgba(0,0,0,0.48)',
          transform: `scale(${interpolate(docSpring, [0, 1], [0.76, 1])})`,
          opacity: interpolate(docSpring, [0, 0.4, 1], [0, 1, 1]),
          zIndex: 20,
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingBottom: 20, borderBottom: '1px solid #3A2C52' }}>
          <div>
            <div style={{ fontSize: 13, fontWeight: 750, color: '#C2A5FF', letterSpacing: '0.08em' }}>
              ASSET_SIGNALS_DOCUMENT · CAMPAGNA FGR
            </div>
            <div style={{ fontSize: 28, fontWeight: 800, marginTop: 6 }}>
              Confronto sintetico su 200 profili Abbigliamento
            </div>
          </div>
          <PillBadge label="Signals != CTR" tone="accent" />
        </div>

        <div style={{ marginTop: 24, display: 'flex', flexDirection: 'column', gap: 16 }}>
          {[u3, s1, b1].map((item, idx) => (
            <div
              key={item.asset_id}
              style={{
                display: 'grid',
                gridTemplateColumns: '130px 1fr 160px 160px',
                alignItems: 'center',
                gap: 16,
                padding: '20px 22px',
                borderRadius: 18,
                backgroundColor: idx === 0 ? 'rgba(34, 227, 155, 0.10)' : '#181124',
                border: `1px solid ${idx === 0 ? '#22E39B' : '#35274D'}`,
              }}
            >
              <div>
                <div style={{ fontSize: 22, fontWeight: 850, color: idx === 0 ? '#22E39B' : '#FFFFFF' }}>{item.asset_id}</div>
                <div style={{ fontSize: 12, color: '#A598C4', textTransform: 'uppercase' }}>{item.leva}</div>
              </div>
              <div>
                <div style={{ fontSize: 18, fontWeight: 700 }}>{item.headline}</div>
                <div style={{ fontSize: 13, color: '#B7ACD1', marginTop: 3 }}>{item.formato} · {item.interviews.n_responses} menzioni intervista</div>
              </div>
              <div style={{ textAlign: 'right' }}>
                <div style={{ fontSize: 12, color: '#A598C4' }}>Click simulato</div>
                <div style={{ fontSize: 24, fontWeight: 850, color: idx === 0 ? '#22E39B' : '#EAE4F7' }}>
                  {formatPctIT(item.decision.actions.click * 100, 1)}
                </div>
              </div>
              <div style={{ textAlign: 'right' }}>
                <div style={{ fontSize: 12, color: '#A598C4' }}>Saldo interviste</div>
                <div
                  style={{
                    fontSize: 24,
                    fontWeight: 850,
                    color: item.interviews.net_mentions >= 0 ? '#22E39B' : '#FF7087',
                  }}
                >
                  {item.interviews.net_mentions >= 0 ? `+${item.interviews.net_mentions}` : item.interviews.net_mentions}
                </div>
              </div>
            </div>
          ))}
        </div>

        <div style={{ marginTop: 22, fontSize: 15, color: '#CFC6E4', lineHeight: 1.5 }}>
          Sintesi: il reso gratuito alza l’interesse su <strong>FGR-U3 (+150)</strong>, mentre sconti aggressivi senza dettagli tecnici penalizzano <strong>FGR-B1 (-113)</strong> e <strong>FGR-S1 (-83)</strong>.
        </div>
      </div>
    </div>
  );
};
