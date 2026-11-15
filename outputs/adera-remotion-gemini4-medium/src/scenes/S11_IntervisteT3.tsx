import React from 'react';
import { Easing, Img, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from 'remotion';
import { ADERA } from '../styles/theme';
import { CurtainWipeOverlay, PillBadge, SlideUpBlock } from '../components/MotionPrimitives';
import { ProviderLogo } from '../components/BrandLogo';
import { VERIFIED_DATA } from '../data/verifiedData';

export const S11_IntervisteT3: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const u3 = VERIFIED_DATA.creatives['FGR-U3'];
  const chiaraQuote = u3.interviews.sample_opinions[0];
  const sergioQuote = u3.interviews.sample_opinions[1];

  // Document pan/zoom matching Reference R7 (16f smooth easeInOut expansion & upward scroll)
  const docExpand = interpolate(frame, [215, 236], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.inOut(Easing.cubic),
  });
  const docWidth = interpolate(docExpand, [0, 1], [860, 980]);
  const docScrollY = interpolate(docExpand, [0, 1], [0, -78]);

  const qSpring = spring({
    frame: frame - 34,
    fps,
    config: { damping: 20, stiffness: 170 },
  });
  const a1Spring = spring({
    frame: frame - 82,
    fps,
    config: { damping: 20, stiffness: 165 },
  });
  const a2Spring = spring({
    frame: frame - 155,
    fps,
    config: { damping: 20, stiffness: 165 },
  });

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
      {/* Left Column: T3 + Gemini Interview Context */}
      <div
        style={{
          position: 'absolute',
          left: ADERA.marginX,
          top: 104,
          width: interpolate(docExpand, [0, 1], [620, 520]),
        }}
      >
        <SlideUpBlock startFrame={4} distance={18}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <div style={{ width: 40, height: 40, borderRadius: 10, backgroundColor: '#FFFFFF', display: 'grid', placeItems: 'center' }}>
              <ProviderLogo name="t3" size={26} />
            </div>
            <div style={{ width: 40, height: 40, borderRadius: 10, backgroundColor: '#FFFFFF', display: 'grid', placeItems: 'center' }}>
              <ProviderLogo name="gemini" size={26} />
            </div>
            <PillBadge label="INTERVISTE CIECHE T3 · GEMINI-4-HYDROGEN" tone="dark" />
          </div>
        </SlideUpBlock>

        <SlideUpBlock startFrame={12} distance={24}>
          <div style={{ fontSize: 54, fontWeight: 850, letterSpacing: '-0.035em', lineHeight: 1.07, marginTop: 22 }}>
            Chiediamo il perché alle personas.
          </div>
          <div style={{ fontSize: 21, color: '#C9BFE0', marginTop: 16, lineHeight: 1.5 }}>
            Ogni risposta è generata in modalità cieca sul testo e sulla descrizione dell’annuncio, senza vedere altri KPI o campagne.
          </div>
        </SlideUpBlock>

        {/* Verdicts stacked matching R7 left side */}
        <div style={{ marginTop: 42, display: 'flex', flexDirection: 'column', gap: 16 }}>
          <SlideUpBlock startFrame={46} distance={20}>
            <div
              style={{
                padding: '18px 22px',
                borderRadius: 18,
                backgroundColor: 'rgba(34, 227, 155, 0.10)',
                border: '1px solid #22E39B',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
              }}
            >
              <div>
                <div style={{ fontSize: 13, fontWeight: 750, color: '#22E39B', letterSpacing: '0.06em' }}>FGR-U3 · PIÙ UTILE</div>
                <div style={{ fontSize: 20, fontWeight: 700, marginTop: 4 }}>Spedizione e reso gratuiti</div>
              </div>
              <div style={{ fontSize: 34, fontWeight: 900, color: '#22E39B' }}>+{u3.interviews.most_useful_count}</div>
            </div>
          </SlideUpBlock>

          <SlideUpBlock startFrame={64} distance={20}>
            <div
              style={{
                padding: '18px 22px',
                borderRadius: 18,
                backgroundColor: 'rgba(255, 112, 135, 0.08)',
                border: '1px solid #FF7087',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
              }}
            >
              <div>
                <div style={{ fontSize: 13, fontWeight: 750, color: '#FF7087', letterSpacing: '0.06em' }}>ATTRITO SEGNALATO</div>
                <div style={{ fontSize: 20, fontWeight: 700, marginTop: 4 }}>Timer 48h & pochi dettagli prodotto</div>
              </div>
              <div style={{ fontSize: 34, fontWeight: 900, color: '#FF7087' }}>-{u3.interviews.least_useful_count}</div>
            </div>
          </SlideUpBlock>
        </div>
      </div>

      {/* Right Stage: Interview Document with R7 Pan/Zoom */}
      <div
        style={{
          position: 'absolute',
          right: ADERA.marginX,
          top: 96,
          width: docWidth,
          height: 888,
          backgroundColor: '#FFFFFF',
          borderRadius: 28,
          color: ADERA.colors.ink,
          padding: 36,
          boxShadow: '0 30px 90px rgba(0,0,0,0.48)',
          overflow: 'hidden',
        }}
      >
        <div style={{ transform: `translateY(${docScrollY}px)` }}>
          {/* Document Header */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingBottom: 18, borderBottom: `1px solid ${ADERA.colors.borderLight}` }}>
            <div>
              <div style={{ fontSize: 13, fontWeight: 800, color: ADERA.colors.action, letterSpacing: '0.07em' }}>
                PRODUCT-STORY.JSON · TRASCRIZIONE LETTERALE ({u3.interviews.n_responses} RISPOSTE)
              </div>
              <div style={{ fontSize: 24, fontWeight: 800, marginTop: 4 }}>Asset {u3.asset_id} — «{u3.headline}»</div>
            </div>
            <PillBadge label="Testo verbatim" tone="light" />
          </div>

          {/* Question */}
          <div
            style={{
              marginTop: 20,
              padding: '18px 22px',
              borderRadius: 16,
              backgroundColor: '#EFEAFA',
              border: '1px solid #D6C7F5',
              transform: `translateY(${interpolate(qSpring, [0, 1], [16, 0])}px)`,
              opacity: interpolate(qSpring, [0, 1], [0, 1]),
            }}
          >
            <div style={{ fontSize: 12, fontWeight: 800, color: ADERA.colors.action, letterSpacing: '0.08em' }}>
              DOMANDA DELL’INTERVISTATORE T3
            </div>
            <div style={{ fontSize: 19, fontWeight: 700, color: ADERA.colors.plum, marginTop: 6 }}>
              «Quali elementi dell’annuncio FGR-U3 ti danno fiducia e cosa invece ti frena prima di cliccare?»
            </div>
          </div>

          {/* Verbatim Answer 1: Chiara Bellini */}
          <div
            style={{
              marginTop: 22,
              padding: 24,
              borderRadius: 20,
              backgroundColor: '#FAF8FD',
              border: `1.5px solid ${ADERA.colors.borderLight}`,
              transform: `translateY(${interpolate(a1Spring, [0, 1], [22, 0])}px)`,
              opacity: interpolate(a1Spring, [0, 1], [0, 1]),
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: 14, marginBottom: 12 }}>
              <Img
                src={staticFile('assets/avatars/avatar-01.png')}
                style={{ width: 46, height: 46, borderRadius: 12, objectFit: 'cover', backgroundColor: '#EFEAFA' }}
              />
              <div>
                <div style={{ fontSize: 18, fontWeight: 800 }}>{chiaraQuote.name}</div>
                <div style={{ fontSize: 13, color: ADERA.colors.inkMuted }}>{chiaraQuote.persona_id} · coorte {chiaraQuote.cohort}</div>
              </div>
            </div>
            <div style={{ fontSize: 16, lineHeight: 1.5, color: '#155B3D', backgroundColor: '#EAF7F0', padding: '12px 16px', borderRadius: 12 }}>
              <strong>Positivo:</strong> «{chiaraQuote.positive}»
            </div>
            <div style={{ fontSize: 16, lineHeight: 1.5, color: '#8E1D31', backgroundColor: '#FDECEF', padding: '12px 16px', borderRadius: 12, marginTop: 10 }}>
              <strong>Freno:</strong> «{chiaraQuote.negative}»
            </div>
          </div>

          {/* Verbatim Answer 2: Sergio Lombardi */}
          <div
            style={{
              marginTop: 18,
              padding: 24,
              borderRadius: 20,
              backgroundColor: '#FAF8FD',
              border: `1.5px solid ${ADERA.colors.borderLight}`,
              transform: `translateY(${interpolate(a2Spring, [0, 1], [22, 0])}px)`,
              opacity: interpolate(a2Spring, [0, 1], [0, 1]),
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: 14, marginBottom: 12 }}>
              <Img
                src={staticFile('assets/avatars/avatar-02.png')}
                style={{ width: 46, height: 46, borderRadius: 12, objectFit: 'cover', backgroundColor: '#EFEAFA' }}
              />
              <div>
                <div style={{ fontSize: 18, fontWeight: 800 }}>{sergioQuote.name}</div>
                <div style={{ fontSize: 13, color: ADERA.colors.inkMuted }}>{sergioQuote.persona_id} · coorte {sergioQuote.cohort}</div>
              </div>
            </div>
            <div style={{ fontSize: 16, lineHeight: 1.5, color: '#155B3D', backgroundColor: '#EAF7F0', padding: '12px 16px', borderRadius: 12 }}>
              <strong>Positivo:</strong> «{sergioQuote.positive}»
            </div>
            <div style={{ fontSize: 16, lineHeight: 1.5, color: '#8E1D31', backgroundColor: '#FDECEF', padding: '12px 16px', borderRadius: 12, marginTop: 10 }}>
              <strong>Freno:</strong> «{sergioQuote.negative}»
            </div>
          </div>
        </div>
      </div>

      {/* Wipe left-to-right to S12 light */}
      <CurtainWipeOverlay startFrame={438} durationFrames={12} color={ADERA.colors.bgLight} direction="left-to-right" />
    </div>
  );
};
