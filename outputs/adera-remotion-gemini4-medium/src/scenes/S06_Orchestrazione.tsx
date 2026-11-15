import React from 'react';
import { Easing, interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { ADERA } from '../styles/theme';
import { PillBadge, SlideUpBlock } from '../components/MotionPrimitives';
import { ProviderLogo } from '../components/BrandLogo';

export const S06_Orchestrazione: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Animated dash flow on SVG connectors
  const dashOffset = -(frame * 2.5);

  const providers: Array<{
    key: 'claude' | 'gemini' | 'chatgpt';
    name: string;
    role: string;
    start: number;
    y: number;
  }> = [
    {
      key: 'claude',
      name: 'Claude',
      role: 'Agente attivo nell’orchestrazione T3',
      start: 42,
      y: 78,
    },
    {
      key: 'gemini',
      name: 'Gemini',
      role: 'Schede & interviste (gemini-4-hydrogen) + Decision 1',
      start: 62,
      y: 230,
    },
    {
      key: 'chatgpt',
      name: 'ChatGPT',
      role: 'Agente attivo nell’orchestrazione T3',
      start: 82,
      y: 382,
    },
  ];

  const logSteps = [
    { start: 112, tag: 'CUTOFF', text: 'cutoff_2026-11-15.lock · 0 leakage oltre la soglia' },
    { start: 138, tag: 'PERSONAS', text: 'personas_t3_600.json → 600 profili sintetici indipendenti' },
    { start: 164, tag: 'DECISION 1', text: '36 asset × 200 profili → 7.200 probabilità simulate (non CTR)' },
    { start: 190, tag: 'INTERVISTE', text: 'product-story.json → 600 interviste cieche tracciate' },
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
      {/* Left Header */}
      <div
        style={{
          position: 'absolute',
          left: ADERA.marginX,
          top: 96,
          width: 610,
        }}
      >
        <SlideUpBlock startFrame={4} distance={18}>
          <PillBadge label="ORCHESTRAZIONE MULTI-AGENTE · WORKSPACE T3 CODE" tone="light" />
        </SlideUpBlock>

        <SlideUpBlock startFrame={10} distance={24}>
          <div style={{ fontSize: 58, fontWeight: 800, letterSpacing: '-0.035em', lineHeight: 1.07, marginTop: 22 }}>
            T3 coordina gli agenti su piani isolati.
          </div>
          <div style={{ fontSize: 22, color: ADERA.colors.inkSoft, marginTop: 18, lineHeight: 1.48 }}>
            Claude, Gemini e ChatGPT lavorano come agenti nel flusso T3 Code senza contaminare i profili sintetici con i risultati delle campagne.
          </div>
        </SlideUpBlock>

        {/* Workspace Terminal Log Card (matching R10 streaming step rhythm) */}
        <div
          style={{
            marginTop: 38,
            backgroundColor: ADERA.colors.bgDark,
            borderRadius: 22,
            padding: 26,
            color: '#FFFFFF',
            boxShadow: '0 24px 60px rgba(25, 18, 36, 0.22)',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 18 }}>
            <div style={{ width: 10, height: 10, borderRadius: 99, backgroundColor: '#FF5F56' }} />
            <div style={{ width: 10, height: 10, borderRadius: 99, backgroundColor: '#FFBD2E' }} />
            <div style={{ width: 10, height: 10, borderRadius: 99, backgroundColor: '#27C93F' }} />
            <span style={{ fontSize: 13, fontWeight: 650, color: '#A79CC4', marginLeft: 8 }}>
              t3-orchestrator · pipeline verificata
            </span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            {logSteps.map((step) => {
              const sp = spring({
                frame: frame - step.start,
                fps,
                config: { damping: 20, stiffness: 180 },
              });
              return (
                <div
                  key={step.tag}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 12,
                    padding: '10px 14px',
                    borderRadius: 12,
                    backgroundColor: '#241A36',
                    border: '1px solid #3A2C52',
                    transform: `translateY(${interpolate(sp, [0, 1], [16, 0])}px)`,
                    opacity: interpolate(sp, [0, 1], [0, 1]),
                  }}
                >
                  <span
                    style={{
                      fontSize: 11,
                      fontWeight: 800,
                      padding: '4px 8px',
                      borderRadius: 6,
                      backgroundColor: ADERA.colors.action,
                      color: '#FFFFFF',
                      minWidth: 88,
                      textAlign: 'center',
                    }}
                  >
                    {step.tag}
                  </span>
                  <span style={{ fontSize: 15, color: '#EAE4F7', fontWeight: 550 }}>{step.text}</span>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Right Stage: T3 Hub + Official Logos (Claude, Gemini, ChatGPT) */}
      <div
        style={{
          position: 'absolute',
          right: ADERA.marginX,
          top: 96,
          width: 900,
          height: 820,
          backgroundColor: '#FFFFFF',
          border: `1px solid ${ADERA.colors.borderLight}`,
          borderRadius: 28,
          padding: 36,
          boxShadow: '0 26px 70px rgba(41, 35, 57, 0.08)',
        }}
      >
        <div style={{ fontSize: 14, fontWeight: 750, color: ADERA.colors.action, letterSpacing: '0.07em' }}>
          ARCHITETTURA AGENTICA VERIFICATA
        </div>

        {/* SVG Animated Connectors */}
        <svg
          width={828}
          height={560}
          viewBox="0 0 828 560"
          style={{ position: 'absolute', left: 36, top: 82, pointerEvents: 'none' }}
        >
          {providers.map((p, idx) => {
            const targetY = 74 + idx * 164;
            return (
              <g key={p.key}>
                <path
                  d={`M 255 240 C 340 240, 350 ${targetY}, 430 ${targetY}`}
                  fill="none"
                  stroke="#DCD2F2"
                  strokeWidth={3}
                />
                <path
                  d={`M 255 240 C 340 240, 350 ${targetY}, 430 ${targetY}`}
                  fill="none"
                  stroke={ADERA.colors.action}
                  strokeWidth={3}
                  strokeDasharray="10 10"
                  strokeDashoffset={dashOffset}
                />
              </g>
            );
          })}
        </svg>

        {/* Central T3 Code Hub */}
        <SlideUpBlock
          startFrame={18}
          distance={20}
          style={{
            position: 'absolute',
            left: 36,
            top: 214,
            width: 256,
            padding: 24,
            borderRadius: 22,
            backgroundColor: ADERA.colors.plum,
            color: '#FFFFFF',
            boxShadow: '0 20px 44px rgba(53, 33, 79, 0.30)',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            textAlign: 'center',
          }}
        >
          <div
            style={{
              width: 72,
              height: 72,
              borderRadius: 18,
              backgroundColor: '#FFFFFF',
              display: 'grid',
              placeItems: 'center',
            }}
          >
            <ProviderLogo name="t3" size={48} />
          </div>
          <div style={{ fontSize: 24, fontWeight: 850, marginTop: 14 }}>T3 Code</div>
          <div style={{ fontSize: 14, color: '#D4C2FA', marginTop: 6, lineHeight: 1.4 }}>
            Orchestratore workspace & tracciabilità artifact
          </div>
        </SlideUpBlock>

        {/* 3 Agent Cards */}
        {providers.map((p, idx) => {
          const sp = spring({
            frame: frame - p.start,
            fps,
            config: { damping: 18, stiffness: 165 },
          });
          const topY = 98 + idx * 164;
          return (
            <div
              key={p.key}
              style={{
                position: 'absolute',
                left: 462,
                top: topY,
                width: 400,
                height: 112,
                backgroundColor: '#F8F6FC',
                border: `1.5px solid ${p.key === 'gemini' ? ADERA.colors.accent : ADERA.colors.borderLight}`,
                borderRadius: 18,
                padding: '0 22px',
                display: 'flex',
                alignItems: 'center',
                gap: 18,
                transform: `translateX(${interpolate(sp, [0, 1], [44, 0])}px)`,
                opacity: interpolate(sp, [0, 1], [0, 1]),
              }}
            >
              <div
                style={{
                  width: 56,
                  height: 56,
                  borderRadius: 14,
                  backgroundColor: '#FFFFFF',
                  border: `1px solid ${ADERA.colors.borderLight}`,
                  display: 'grid',
                  placeItems: 'center',
                  flexShrink: 0,
                }}
              >
                <ProviderLogo name={p.key} size={36} />
              </div>
              <div>
                <div style={{ fontSize: 22, fontWeight: 800, color: ADERA.colors.ink }}>{p.name}</div>
                <div style={{ fontSize: 14.5, color: ADERA.colors.inkSoft, marginTop: 4, lineHeight: 1.35 }}>{p.role}</div>
              </div>
            </div>
          );
        })}

        {/* Explicit honesty note cleanly below all 3 agent cards */}
        <div
          style={{
            position: 'absolute',
            left: 36,
            right: 36,
            bottom: 32,
            fontSize: 16,
            color: ADERA.colors.inkSoft,
            borderTop: `1px solid ${ADERA.colors.borderLight}`,
            paddingTop: 18,
            lineHeight: 1.5,
          }}
        >
          Ruoli specifici verificati nei run salvati: <strong>t3:antigravity / gemini-4-hydrogen</strong> (600 schede e interviste) e <strong>Gemini Decision 1</strong> (feed); Claude, Gemini e ChatGPT confermati come agenti nel workflow senza ruoli non documentati.
        </div>
      </div>
    </div>
  );
};
