import React from 'react';
import { Easing, interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { ADERA } from '../styles/theme';
import { CurtainWipeOverlay, PillBadge, SlideUpBlock, StaggeredWords } from '../components/MotionPrimitives';
import { AdCreativeIllustrationCard } from '../components/AdCardIllustrations';
import { VERIFIED_DATA } from '../data/verifiedData';

export const S01_Domanda: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Card entrance from right (mapped to Reference R1 f=77..92)
  const cardProgress = spring({
    frame: frame - 72,
    fps,
    config: { damping: 18, stiffness: 150, mass: 0.85 },
  });
  const cardTranslateX = interpolate(cardProgress, [0, 1], [460, 0]);
  const cardOpacity = interpolate(cardProgress, [0, 0.4, 1], [0, 1, 1]);
  const cardFloatY = Math.sin(frame / 22) * 5;

  // Cycle the 4 carousel panels of FGR-U3 slowly as preview
  const carouselIdx = frame < 130 ? 0 : frame < 185 ? 1 : frame < 230 ? 2 : 3;

  const microQuestions = [
    { start: 54, text: 'Quanto costerà davvero il CPM a novembre?' },
    { start: 96, text: 'Quali profili sintetici si fermeranno sul feed?' },
    { start: 138, text: 'Cosa convince o frena prima di spendere?' },
  ];

  const fgrU3 = VERIFIED_DATA.creatives['FGR-U3'];

  return (
    <div
      style={{
        width: ADERA.width,
        height: ADERA.height,
        backgroundColor: ADERA.colors.bgLight,
        position: 'relative',
        overflow: 'hidden',
        fontFamily: ADERA.fontFamily,
      }}
    >
      {/* Subtle geometric violet accent glow top-right */}
      <div
        style={{
          position: 'absolute',
          right: -180,
          top: -180,
          width: 720,
          height: 720,
          borderRadius: '50%',
          background: 'radial-gradient(circle, rgba(136,97,232,0.14) 0%, rgba(246,245,249,0) 70%)',
          pointerEvents: 'none',
        }}
      />

      {/* Left Column: 8% margin (154px), matching reference R1 asymmetric split */}
      <div
        style={{
          position: 'absolute',
          left: ADERA.marginX,
          top: 148,
          width: 820,
        }}
      >
        <SlideUpBlock startFrame={4} distance={18}>
          <PillBadge label="SIMULAZIONE PRE-LANCIO · KIT ORGANIZZATORI SIMULATO" tone="light" />
        </SlideUpBlock>

        <div style={{ marginTop: 28 }}>
          <StaggeredWords
            text="E se potessi testare una campagna prima di investirci?"
            startFrame={10}
            framesPerWord={4}
            fontSize={74}
            fontWeight={800}
            lineHeight={1.06}
            maxWidth={820}
            highlightWords={{ prima: ADERA.colors.action, investirci: ADERA.colors.action }}
          />
        </div>

        {/* 3 sequential micro-questions matching R1 cadence */}
        <div style={{ marginTop: 52, display: 'flex', flexDirection: 'column', gap: 18 }}>
          {microQuestions.map((q, idx) => {
            const p = spring({
              frame: frame - q.start,
              fps,
              config: { damping: 20, stiffness: 170, mass: 0.75 },
            });
            const y = interpolate(p, [0, 1], [24, 0]);
            const op = interpolate(p, [0, 0.5, 1], [0, 1, 1]);
            return (
              <div
                key={idx}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 16,
                  transform: `translateY(${y}px)`,
                  opacity: op,
                }}
              >
                <div
                  style={{
                    width: 10,
                    height: 10,
                    borderRadius: 99,
                    backgroundColor: ADERA.colors.accent,
                    flexShrink: 0,
                  }}
                />
                <span
                  style={{
                    fontSize: 28,
                    fontWeight: 550,
                    color: ADERA.colors.inkSoft,
                    letterSpacing: '-0.015em',
                  }}
                >
                  {q.text}
                </span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Right Column: Isolated ADERA Campaign Card (R1 isolated object entry) */}
      <div
        style={{
          position: 'absolute',
          right: ADERA.marginX,
          top: 210,
          width: 660,
          transform: `translateX(${cardTranslateX}px) translateY(${cardFloatY}px)`,
          opacity: cardOpacity,
        }}
      >
        <div
          style={{
            marginBottom: 12,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            fontSize: 14,
            fontWeight: 650,
            color: ADERA.colors.inkMuted,
            letterSpacing: '0.03em',
          }}
        >
          <span>BOZZA CAMPAGNA PRIMA DEL LANCIO</span>
          <span>FGR-U3 · ILLUSTRAZIONE KIT</span>
        </div>
        <AdCreativeIllustrationCard
          assetId="FGR-U3"
          headline={fgrU3.headline}
          body={fgrU3.body}
          cta={fgrU3.cta}
          carouselIndex={carouselIdx}
          darkTheme={false}
        />
      </div>

      {/* Bottom-to-top Curtain Wipe at f=258..270 (matching R1 -> R2 11f wipe) */}
      <CurtainWipeOverlay startFrame={258} durationFrames={12} color={ADERA.colors.action} direction="bottom-to-top" />
    </div>
  );
};
