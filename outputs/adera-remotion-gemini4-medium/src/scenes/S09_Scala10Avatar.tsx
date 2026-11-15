import React from 'react';
import { Easing, Img, interpolate, staticFile, useCurrentFrame } from 'remotion';
import { ADERA, formatIntIT } from '../styles/theme';
import { CurtainWipeOverlay, PillBadge, SlideUpBlock } from '../components/MotionPrimitives';
import { VERIFIED_DATA } from '../data/verifiedData';

export const S09_Scala10Avatar: React.FC = () => {
  const frame = useCurrentFrame();

  // easeOutCubic counter 1 -> 600 (matching R4)
  const countP = interpolate(frame, [16, 130], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.out(Easing.cubic),
  });
  const currentProfiles = Math.max(1, Math.round(1 + (VERIFIED_DATA.syntheticCount - 1) * countP));
  const currentEvals = Math.round(7200 * countP);

  // Camera zoom-out from Chiara's avatar (slot 1) to full 10-avatar grid + out-of-frame extension
  const zoomScale = interpolate(frame, [0, 28, 138], [2.45, 2.35, 1.0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.inOut(Easing.cubic),
  });
  const panX = interpolate(frame, [0, 28, 138], [320, 300, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.inOut(Easing.cubic),
  });
  const panY = interpolate(frame, [0, 28, 138], [210, 195, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.inOut(Easing.cubic),
  });

  const personas = VERIFIED_DATA.personas10;

  // Partial edge tiles reusing clean slots to suggest scale beyond the 10 portraits without inventing fake faces
  const extraEdgeSlots = [
    { label: 'P042 · Abbigliamento', bg: '#EAE2FA', avatar: 'assets/avatars/avatar-02.png', opacity: 0.48 },
    { label: 'P108 · Beauty', bg: '#E6F4EE', avatar: 'assets/avatars/avatar-06.png', opacity: 0.45 },
    { label: 'P164 · Pet E-comm', bg: '#F2ECF9', avatar: 'assets/avatars/avatar-09.png', opacity: 0.42 },
    { label: 'P199 · Abbigliamento', bg: '#EDE6FA', avatar: 'assets/avatars/avatar-04.png', opacity: 0.4 },
  ];

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
      {/* Left Column: Big R4 Counter */}
      <div
        style={{
          position: 'absolute',
          left: ADERA.marginX,
          top: 132,
          width: 580,
          zIndex: 20,
        }}
      >
        <SlideUpBlock startFrame={4} distance={18}>
          <PillBadge label="SCALA SINTETICA · 3 SETTORI INDIPENDENTI" tone="light" />
        </SlideUpBlock>

        <div
          style={{
            fontSize: 164,
            fontWeight: 900,
            letterSpacing: '-0.055em',
            lineHeight: 0.92,
            color: ADERA.colors.action,
            marginTop: 26,
            fontVariantNumeric: 'tabular-nums',
          }}
        >
          {formatIntIT(currentProfiles)}
        </div>

        <SlideUpBlock startFrame={16} distance={22}>
          <div style={{ fontSize: 48, fontWeight: 800, letterSpacing: '-0.03em', lineHeight: 1.08, marginTop: 18 }}>
            profili sintetici.
            <br />
            <span style={{ color: ADERA.colors.plum }}>200 per settore.</span>
          </div>
        </SlideUpBlock>

        <SlideUpBlock startFrame={32} distance={20}>
          <div style={{ fontSize: 21, color: ADERA.colors.inkSoft, marginTop: 22, lineHeight: 1.5 }}>
            Ogni avatar rappresenta uno slot distinto su Abbigliamento, Beauty & Skincare e Pet E-commerce: in totale <strong>{formatIntIT(currentEvals)}</strong> valutazioni Decision 1 su 36 creatività.
          </div>
        </SlideUpBlock>

        <div style={{ marginTop: 32, display: 'flex', gap: 12, flexWrap: 'wrap' }}>
          <PillBadge label="200 Abbigliamento" tone="accent" />
          <PillBadge label="200 Beauty Skincare" tone="light" />
          <PillBadge label="200 Pet E-commerce" tone="light" />
        </div>
      </div>

      {/* Right Stage: Zoom-out across 10 clean separated avatars + partial edge overflow suggesting larger scale */}
      <div
        style={{
          position: 'absolute',
          left: 790,
          top: 96,
          right: -120,
          bottom: -110,
          overflow: 'visible',
        }}
      >
        <div
          style={{
            transform: `translate(${panX}px, ${panY}px) scale(${zoomScale})`,
            transformOrigin: 'top left',
            display: 'grid',
            gridTemplateColumns: 'repeat(4, 246px)',
            gap: 20,
          }}
        >
          {personas.map((p, idx) => (
            <div
              key={p.persona_id}
              style={{
                backgroundColor: '#FFFFFF',
                border: idx === 0 ? `2.5px solid ${ADERA.colors.action}` : `1px solid ${ADERA.colors.borderLight}`,
                borderRadius: 22,
                padding: 16,
                boxShadow: idx === 0 ? '0 20px 50px rgba(112, 70, 206, 0.22)' : '0 14px 36px rgba(41, 35, 57, 0.07)',
              }}
            >
              <div
                style={{
                  width: '100%',
                  height: 176,
                  borderRadius: 16,
                  background: idx === 0 ? 'linear-gradient(135deg, #EFEAFA 0%, #DFD2F8 100%)' : '#F5F2FB',
                  display: 'grid',
                  placeItems: 'center',
                  overflow: 'hidden',
                }}
              >
                <Img
                  src={staticFile(p.avatar)}
                  style={{ width: 172, height: 172, objectFit: 'contain' }}
                />
              </div>
              <div style={{ marginTop: 12, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: 15, fontWeight: 800, color: ADERA.colors.ink }}>
                  {idx === 0 ? 'Chiara · P001' : p.persona_id.split('-')[1]}
                </span>
                <span style={{ fontSize: 12, fontWeight: 700, color: ADERA.colors.action }}>{p.age_band}</span>
              </div>
              <div style={{ fontSize: 12, color: ADERA.colors.inkMuted, marginTop: 4 }}>
                {p.vertical.replace('_', ' ')} · {p.motivation}
              </div>
            </div>
          ))}

          {/* Partial out-of-frame hint cards */}
          {extraEdgeSlots.map((ex, i) => (
            <div
              key={i}
              style={{
                backgroundColor: '#FFFFFF',
                border: `1px dashed ${ADERA.colors.borderLight}`,
                borderRadius: 22,
                padding: 16,
                opacity: ex.opacity,
              }}
            >
              <div
                style={{
                  width: '100%',
                  height: 176,
                  borderRadius: 16,
                  backgroundColor: ex.bg,
                  display: 'grid',
                  placeItems: 'center',
                  filter: 'blur(2px)',
                }}
              >
                <Img src={staticFile(ex.avatar)} style={{ width: 160, height: 160, objectFit: 'contain' }} />
              </div>
              <div style={{ marginTop: 12, fontSize: 13, fontWeight: 700, color: ADERA.colors.inkMuted }}>
                {ex.label}
              </div>
            </div>
          ))}
        </div>
      </div>

      <CurtainWipeOverlay startFrame={258} durationFrames={12} color={ADERA.colors.action} direction="bottom-to-top" />
    </div>
  );
};
