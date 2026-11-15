import React from 'react';
import { Img, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from 'remotion';
import { ADERA } from '../styles/theme';
import { CurtainWipeOverlay, PillBadge, SlideUpBlock } from '../components/MotionPrimitives';
import { VERIFIED_DATA } from '../data/verifiedData';

export const S07_PersonaChiara: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const chiara = VERIFIED_DATA.chiara;

  // Profile card scale entrance (mapped to Reference R5)
  const cardSpring = spring({
    frame: frame - 12,
    fps,
    config: { damping: 20, stiffness: 155, mass: 0.9 },
  });

  const rows = [
    { label: 'PROFILO', value: chiara.persona_summary, start: 46 },
    { label: 'COSA RICHIEDE PER FIDARSI', value: chiara.trust_requirements, start: 86 },
    { label: 'COSA EVITA NEL FEED', value: chiara.ad_avoidance, start: 126 },
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
      {/* Header matching R5 */}
      <div
        style={{
          position: 'absolute',
          left: ADERA.marginX,
          right: ADERA.marginX,
          top: 78,
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'flex-end',
        }}
      >
        <div>
          <SlideUpBlock startFrame={4} distance={18}>
            <PillBadge label="PROFILO SINTETICO INDIPENDENTE · NESSUN DATO DI CAMPAGNA" tone="light" />
          </SlideUpBlock>
          <SlideUpBlock startFrame={10} distance={22}>
            <div style={{ fontSize: 54, fontWeight: 800, letterSpacing: '-0.035em', marginTop: 16 }}>
              Un pubblico sintetico. <span style={{ color: ADERA.colors.action }}>Profili diversi.</span>
            </div>
          </SlideUpBlock>
        </div>
        <SlideUpBlock startFrame={18} distance={16}>
          <div style={{ fontSize: 16, fontWeight: 650, color: ADERA.colors.inkMuted }}>
            {chiara.provider} · {chiara.model}
          </div>
        </SlideUpBlock>
      </div>

      {/* Centered Structured Profile Card matching R5 */}
      <div
        style={{
          position: 'absolute',
          left: 240,
          right: 240,
          top: 256,
          backgroundColor: '#FFFFFF',
          border: `1px solid ${ADERA.colors.borderLight}`,
          borderRadius: 28,
          padding: '42px 48px',
          boxShadow: '0 28px 80px rgba(41, 35, 57, 0.10)',
          transform: `scale(${interpolate(cardSpring, [0, 1], [0.94, 1])}) translateY(${interpolate(cardSpring, [0, 1], [28, 0])}px)`,
          opacity: interpolate(cardSpring, [0, 0.4, 1], [0, 1, 1]),
        }}
      >
        {/* Identity Header */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 32,
            paddingBottom: 28,
            borderBottom: `1px solid ${ADERA.colors.borderLight}`,
          }}
        >
          <div
            style={{
              width: 148,
              height: 148,
              borderRadius: 28,
              background: 'linear-gradient(135deg, #EFEAFA 0%, #DED2F7 100%)',
              border: '2px solid #C9B6F2',
              overflow: 'hidden',
              flexShrink: 0,
              display: 'grid',
              placeItems: 'center',
            }}
          >
            <Img
              src={staticFile('assets/avatars/avatar-01.png')}
              style={{ width: '100%', height: '100%', objectFit: 'cover' }}
            />
          </div>

          <div style={{ flex: 1 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
              <span style={{ fontSize: 44, fontWeight: 850, letterSpacing: '-0.03em' }}>{chiara.name}</span>
              <PillBadge label={`${chiara.age_years} anni`} tone="accent" />
              <PillBadge label={chiara.persona_id} tone="light" />
            </div>
            <div style={{ fontSize: 23, fontWeight: 600, color: ADERA.colors.inkSoft, marginTop: 10 }}>
              {chiara.occupation}
            </div>
          </div>
        </div>

        {/* Staggered Key-Value Rows matching R5 0.7-1.2s cadence */}
        <div style={{ marginTop: 28, display: 'flex', flexDirection: 'column', gap: 22 }}>
          {rows.map((r) => {
            const rp = spring({
              frame: frame - r.start,
              fps,
              config: { damping: 20, stiffness: 165 },
            });
            return (
              <div
                key={r.label}
                style={{
                  display: 'grid',
                  gridTemplateColumns: '280px 1fr',
                  gap: 24,
                  alignItems: 'start',
                  padding: '18px 22px',
                  borderRadius: 16,
                  backgroundColor: '#FAF8FD',
                  border: '1px solid #ECE7F5',
                  transform: `translateY(${interpolate(rp, [0, 1], [22, 0])}px)`,
                  opacity: interpolate(rp, [0, 0.5, 1], [0, 1, 1]),
                }}
              >
                <div style={{ fontSize: 13, fontWeight: 800, color: ADERA.colors.action, letterSpacing: '0.08em', paddingTop: 4 }}>
                  {r.label}
                </div>
                <div style={{ fontSize: 20, fontWeight: 500, color: ADERA.colors.ink, lineHeight: 1.45 }}>
                  {r.value}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Bottom-to-top Curtain Wipe to dark S08 (matching R5 -> R6) */}
      <CurtainWipeOverlay startFrame={318} durationFrames={12} color={ADERA.colors.bgDark} direction="bottom-to-top" />
    </div>
  );
};
