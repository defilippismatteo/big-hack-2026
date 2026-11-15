import React from 'react';
import { Easing, interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { ADERA } from '../styles/theme';
import { AderaOriginalLogo } from '../components/BrandLogo';
import { PillBadge, SlideUpBlock } from '../components/MotionPrimitives';
import { VERIFIED_DATA } from '../data/verifiedData';

export const S13_Chiusura: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Logo entrance after 7f card collapse (matching Reference R11)
  const logoSpring = spring({
    frame: frame - 6,
    fps,
    config: { damping: 20, stiffness: 150, mass: 0.9 },
  });

  // Left-to-right linear headline wipe matching R11 (54.6..55.6s = ~30f)
  const textWipe = interpolate(frame, [26, 62], [0, 100], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.out(Easing.cubic),
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
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
      }}
    >
      {/* Subtle radial glow */}
      <div
        style={{
          position: 'absolute',
          width: 920,
          height: 920,
          borderRadius: '50%',
          background: 'radial-gradient(circle, rgba(136,97,232,0.14) 0%, rgba(246,245,249,0) 68%)',
          pointerEvents: 'none',
        }}
      />

      {/* Centered Original ADERA PNG Logo */}
      <div
        style={{
          transform: `scale(${interpolate(logoSpring, [0, 1], [0.85, 1])})`,
          opacity: interpolate(logoSpring, [0, 0.4, 1], [0, 1, 1]),
          marginBottom: 40,
        }}
      >
        <AderaOriginalLogo height={126} />
      </div>

      {/* Main Closing Headline with left-to-right wipe */}
      <div
        style={{
          clipPath: `inset(0 ${100 - textWipe}% 0 0)`,
          textAlign: 'center',
        }}
      >
        <div
          style={{
            fontSize: 82,
            fontWeight: 850,
            letterSpacing: '-0.04em',
            lineHeight: 1.06,
            color: ADERA.colors.ink,
          }}
        >
          ADERA. <span style={{ color: ADERA.colors.action }}>Prima di investire, capisci.</span>
        </div>
      </div>

      {/* Main-level transparent provenance strip (NO tiny footer notes) */}
      <SlideUpBlock startFrame={74} distance={20}>
        <div
          style={{
            marginTop: 46,
            display: 'flex',
            gap: 14,
            flexWrap: 'wrap',
            justifyContent: 'center',
          }}
        >
          <PillBadge label={`Cutoff ${VERIFIED_DATA.source.cutoff}`} tone="light" />
          <PillBadge label="Forecast: Timestral 28M + Baseline CTR" tone="light" />
          <PillBadge label="600 profili sintetici T3 / Gemini · 7.200 Decision 1 (non CTR)" tone="accent" />
          <PillBadge label="Kit organizzatori simulato" tone="light" />
        </div>
      </SlideUpBlock>
    </div>
  );
};
