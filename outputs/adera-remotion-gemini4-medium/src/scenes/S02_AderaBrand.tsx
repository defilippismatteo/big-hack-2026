import React from 'react';
import { Easing, interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { ADERA } from '../styles/theme';
import { AderaOriginalLogo, AderaVectorTriangle } from '../components/BrandLogo';
import { CurtainWipeOverlay, SlideUpBlock } from '../components/MotionPrimitives';

export const S02_AderaBrand: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Gradient transition #7046CE -> #35214F
  const bgProgress = interpolate(frame, [20, 120], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.inOut(Easing.cubic),
  });

  // Original Logo entrance
  const logoSpring = spring({
    frame: frame - 8,
    fps,
    config: { damping: 18, stiffness: 150, mass: 0.9 },
  });
  const logoScale = interpolate(logoSpring, [0, 1], [0.84, 1]);
  const logoOpacity = interpolate(logoSpring, [0, 0.4, 1], [0, 1, 1]);

  // Payoff wipe left-to-right (matching R3 staggered reveal)
  const payoffReveal = interpolate(frame, [42, 70], [0, 100], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.out(Easing.cubic),
  });

  // Vector triangle bars extend into 3 workspace frames (frame 85..150)
  const barProgress = interpolate(frame, [25, 65], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.out(Easing.cubic),
  });

  const pillars = [
    {
      num: '01',
      title: 'Forecast & Cutoff',
      desc: 'Serie storica simulata 17 ago – 15 nov e proiezione Timestral 28M',
      start: 78,
    },
    {
      num: '02',
      title: 'Feed & Decision 1',
      desc: '600 profili sintetici T3/Gemini, probabilità simulate (non CTR)',
      start: 96,
    },
    {
      num: '03',
      title: 'Interviste & Scenari',
      desc: 'Motivazioni letterali cieche e riallocazione budget ±20%',
      start: 114,
    },
  ];

  return (
    <div
      style={{
        width: ADERA.width,
        height: ADERA.height,
        background: `linear-gradient(135deg, ${ADERA.colors.action} ${Math.round((1 - bgProgress) * 100)}%, ${ADERA.colors.plum} 100%)`,
        position: 'relative',
        overflow: 'hidden',
        fontFamily: ADERA.fontFamily,
        color: '#FFFFFF',
      }}
    >
      {/* Ambient radial light */}
      <div
        style={{
          position: 'absolute',
          left: 120,
          top: 120,
          width: 900,
          height: 900,
          borderRadius: '50%',
          background: 'radial-gradient(circle, rgba(194,165,255,0.22) 0%, rgba(53,33,79,0) 68%)',
          pointerEvents: 'none',
        }}
      />

      {/* Top-Left Brand Reveal matching R3 */}
      <div
        style={{
          position: 'absolute',
          left: ADERA.marginX,
          top: 150,
          right: ADERA.marginX,
        }}
      >
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 36,
            transform: `scale(${logoScale})`,
            transformOrigin: 'left center',
            opacity: logoOpacity,
          }}
        >
          <div
            style={{
              backgroundColor: '#FFFFFF',
              borderRadius: 24,
              padding: '22px 34px',
              boxShadow: '0 24px 60px rgba(17, 8, 34, 0.34)',
              display: 'inline-flex',
              alignItems: 'center',
              gap: 24,
            }}
          >
            <AderaOriginalLogo height={82} />
            <div style={{ width: 2, height: 54, backgroundColor: '#E5DFEF' }} />
            <AderaVectorTriangle size={74} barProgress={barProgress} fill={ADERA.colors.action} />
          </div>
          <div
            style={{
              padding: '10px 18px',
              borderRadius: 999,
              backgroundColor: 'rgba(255,255,255,0.14)',
              border: '1px solid rgba(255,255,255,0.28)',
              fontSize: 16,
              fontWeight: 650,
              letterSpacing: '0.04em',
            }}
          >
            CUTOFF OPERATIVO · 2026-11-15
          </div>
        </div>

        {/* Payoff */}
        <div
          style={{
            marginTop: 52,
            clipPath: `inset(0 ${100 - payoffReveal}% 0 0)`,
          }}
        >
          <div
            style={{
              fontSize: 92,
              fontWeight: 800,
              letterSpacing: '-0.04em',
              lineHeight: 1.02,
              color: '#FFFFFF',
            }}
          >
            Prima di investire, <span style={{ color: ADERA.colors.accentSoft }}>capisci.</span>
          </div>
          <div
            style={{
              marginTop: 18,
              fontSize: 30,
              fontWeight: 500,
              color: 'rgba(255,255,255,0.88)',
              maxWidth: 1120,
            }}
          >
            Previsione quantitativa su serie storica simulata e reazioni qualitative su 600 profili sintetici, tenute su piani distinti.
          </div>
        </div>

        {/* 3 Workspace Frames opening from the triangle bars */}
        <div
          style={{
            marginTop: 68,
            display: 'grid',
            gridTemplateColumns: 'repeat(3, 1fr)',
            gap: 28,
          }}
        >
          {pillars.map((p) => (
            <SlideUpBlock key={p.num} startFrame={p.start} distance={40}>
              <div
                style={{
                  backgroundColor: 'rgba(25, 18, 36, 0.42)',
                  border: '1px solid rgba(255, 255, 255, 0.22)',
                  borderRadius: 20,
                  padding: '28px 30px',
                  backdropFilter: 'blur(8px)',
                }}
              >
                <div
                  style={{
                    fontSize: 15,
                    fontWeight: 750,
                    letterSpacing: '0.1em',
                    color: ADERA.colors.accentSoft,
                  }}
                >
                  MODULO {p.num}
                </div>
                <div style={{ fontSize: 28, fontWeight: 750, marginTop: 10, color: '#FFFFFF' }}>{p.title}</div>
                <div style={{ fontSize: 18, lineHeight: 1.45, marginTop: 10, color: 'rgba(255,255,255,0.82)' }}>
                  {p.desc}
                </div>
              </div>
            </SlideUpBlock>
          ))}
        </div>
      </div>

      {/* Smooth light wipe toward S03 */}
      <CurtainWipeOverlay startFrame={198} durationFrames={12} color={ADERA.colors.bgLight} direction="left-to-right" />
    </div>
  );
};
