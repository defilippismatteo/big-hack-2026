import React from 'react';
import { Easing, Img, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from 'remotion';
import { ADERA, formatPctIT } from '../styles/theme';
import { CurtainWipeOverlay, PillBadge } from '../components/MotionPrimitives';
import { AdCreativeIllustrationCard } from '../components/AdCardIllustrations';
import { VERIFIED_DATA } from '../data/verifiedData';

export const S08_FeedDecision: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const assets = [
    VERIFIED_DATA.creatives['FGR-U3'],
    VERIFIED_DATA.creatives['FGR-B1'],
    VERIFIED_DATA.creatives['FGR-S1'],
  ];

  // Segment timetable inside 570 frames:
  // 0..195: FGR-U3 (swipe out left at 172..195)
  // 190..385: FGR-B1 (swipe out left at 362..385)
  // 380..570: FGR-S1 (settles cleanly)
  const activeIdx = frame < 190 ? 0 : frame < 380 ? 1 : 2;
  const activeAsset = assets[activeIdx];
  const actions = activeAsset.decision.actions;

  const actionRows = [
    { key: 'Scroll', val: actions.scroll * 100, color: '#9E93BA' },
    { key: 'Glance', val: actions.glance * 100, color: '#C2A5FF' },
    { key: 'Stop', val: actions.stop * 100, color: '#8861E8' },
    { key: 'Click (simulato)', val: actions.click * 100, color: '#22E39B' },
  ];

  // Carousel preview for FGR-U3
  const u3CarouselIdx = frame < 55 ? 0 : frame < 105 ? 1 : frame < 150 ? 2 : 3;

  // Compute Tinder-style swipe transforms for each card
  const renderDeckCard = (assetIdx: number) => {
    const asset = assets[assetIdx];
    let enterStart = 0;
    let exitStart = 9999;
    let exitEnd = 9999;
    if (assetIdx === 0) {
      enterStart = 6;
      exitStart = 170;
      exitEnd = 192;
    } else if (assetIdx === 1) {
      enterStart = 175;
      exitStart = 360;
      exitEnd = 382;
    } else {
      enterStart = 365;
    }

    if (frame > exitEnd + 4) return null;

    const enterP = spring({
      frame: frame - enterStart,
      fps,
      config: { damping: 19, stiffness: 165, mass: 0.8 },
    });

    const isExiting = frame >= exitStart;
    const exitP = isExiting
      ? interpolate(frame, [exitStart, exitEnd], [0, 1], {
          extrapolateLeft: 'clamp',
          extrapolateRight: 'clamp',
          easing: Easing.in(Easing.cubic),
        })
      : 0;

    // Slight stack preview for next card
    const isQueued = assetIdx === activeIdx + 1;
    const baseScale = isQueued ? 0.94 : interpolate(enterP, [0, 1], [0.94, 1]);
    const baseY = isQueued ? 26 : interpolate(enterP, [0, 1], [36, 0]);
    const tx = exitP * -740;
    const ty = baseY - exitP * 95;
    const rot = exitP * -16;
    const op = isQueued ? 0.45 : interpolate(exitP, [0, 0.8, 1], [1, 0.85, 0]);

    // Tinder decision stamp before swipe
    const stampStart = assetIdx === 0 ? 120 : assetIdx === 1 ? 310 : 480;
    const stampOp = interpolate(frame, [stampStart, stampStart + 12], [0, 1], {
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
    });
    const stampText =
      assetIdx === 0 ? 'STOP + CLICK 41,5%' : assetIdx === 1 ? 'SCROLL 37,3%' : 'SCROLL 36,2%';
    const stampColor = assetIdx === 0 ? '#22E39B' : '#FF7087';

    return (
      <div
        key={asset.asset_id}
        style={{
          position: 'absolute',
          inset: 0,
          zIndex: 30 - assetIdx,
          transform: `translateX(${tx}px) translateY(${ty}px) rotate(${rot}deg) scale(${baseScale})`,
          opacity: op,
          transformOrigin: 'center center',
        }}
      >
        <AdCreativeIllustrationCard
          assetId={asset.asset_id}
          headline={asset.headline}
          body={asset.body}
          cta={asset.cta}
          carouselIndex={assetIdx === 0 ? u3CarouselIdx : 0}
          darkTheme={true}
        />

        {/* Tinder-style verdict stamp */}
        {!isQueued && stampOp > 0.01 && (
          <div
            style={{
              position: 'absolute',
              top: 128,
              right: 42,
              padding: '10px 18px',
              borderRadius: 12,
              border: `3px solid ${stampColor}`,
              backgroundColor: 'rgba(19, 13, 30, 0.92)',
              color: stampColor,
              fontSize: 20,
              fontWeight: 900,
              letterSpacing: '0.06em',
              transform: 'rotate(7deg)',
              opacity: stampOp,
            }}
          >
            {stampText}
          </div>
        )}
      </div>
    );
  };

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
      {/* Left Fixed Column matching R6 */}
      <div
        style={{
          position: 'absolute',
          left: ADERA.marginX,
          top: 96,
          width: 660,
        }}
      >
        <PillBadge label="FEED SIMULATO · DECISION 1 SU 200 PROFILI SINTETICI" tone="dark" />

        <div style={{ fontSize: 54, fontWeight: 800, letterSpacing: '-0.035em', lineHeight: 1.07, marginTop: 20 }}>
          Swipe sui feed simulati.
        </div>
        <div style={{ fontSize: 20, color: '#C9BFE0', marginTop: 14, lineHeight: 1.45 }}>
          Distribuzioni di probabilità simulate da <strong>Gemini Decision 1</strong> (<strong>non CTR misurato</strong>). Le creatività mostrate sono illustrazioni SVG/HTML dai testi del kit.
        </div>

        {/* Active Persona & Run Strip */}
        <div
          style={{
            marginTop: 26,
            display: 'flex',
            alignItems: 'center',
            gap: 14,
            padding: '14px 18px',
            borderRadius: 16,
            backgroundColor: ADERA.colors.bgDarkCard,
            border: `1px solid ${ADERA.colors.borderDark}`,
          }}
        >
          <Img
            src={staticFile('assets/avatars/avatar-01.png')}
            style={{ width: 48, height: 48, borderRadius: 12, objectFit: 'cover' }}
          />
          <div>
            <div style={{ fontSize: 16, fontWeight: 750 }}>
              Chiara Bellini + 199 profili Abbigliamento
            </div>
            <div style={{ fontSize: 13, color: '#A598C4', marginTop: 2 }}>
              Asset: <strong>{activeAsset.asset_id}</strong> · Run ID: <code>{activeAsset.decision.run_id}</code>
            </div>
          </div>
        </div>

        {/* Probability Bars (Scroll / Glance / Stop / Click) */}
        <div
          style={{
            marginTop: 26,
            backgroundColor: ADERA.colors.bgDarkCard,
            border: `1px solid ${ADERA.colors.borderDark}`,
            borderRadius: 20,
            padding: 24,
            display: 'flex',
            flexDirection: 'column',
            gap: 16,
          }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 13, fontWeight: 750, color: ADERA.colors.accentSoft }}>
            <span>PROBABILITÀ SIMULATE DECISION 1 ({activeAsset.asset_id})</span>
            <span>n = {activeAsset.decision.n_personas}</span>
          </div>

          {actionRows.map((row) => (
            <div key={row.key}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 16, fontWeight: 650, marginBottom: 6 }}>
                <span>{row.key}</span>
                <span style={{ color: row.color, fontVariantNumeric: 'tabular-nums' }}>{formatPctIT(row.val, 1)}</span>
              </div>
              <div style={{ height: 10, borderRadius: 99, backgroundColor: '#161021', overflow: 'hidden' }}>
                <div
                  style={{
                    height: '100%',
                    width: `${Math.min(100, row.val * 2.1)}%`,
                    backgroundColor: row.color,
                    borderRadius: 99,
                  }}
                />
              </div>
            </div>
          ))}
        </div>

        {/* Step Indicator */}
        <div style={{ marginTop: 22, display: 'flex', gap: 10 }}>
          {assets.map((a, idx) => (
            <div
              key={a.asset_id}
              style={{
                padding: '8px 16px',
                borderRadius: 999,
                fontSize: 14,
                fontWeight: 700,
                backgroundColor: idx === activeIdx ? ADERA.colors.action : '#241B35',
                color: idx === activeIdx ? '#FFFFFF' : '#9E93BA',
                border: `1px solid ${idx === activeIdx ? ADERA.colors.accent : '#392B52'}`,
              }}
            >
              {a.asset_id} · Click sim. {formatPctIT(a.decision.actions.click * 100, 1)}
            </div>
          ))}
        </div>
      </div>

      {/* Right Stage: Tinder Swipe Deck */}
      <div
        style={{
          position: 'absolute',
          right: ADERA.marginX,
          top: 160,
          width: 780,
          height: 670,
        }}
      >
        {[2, 1, 0].map((idx) => renderDeckCard(idx))}
      </div>

      <CurtainWipeOverlay startFrame={558} durationFrames={12} color={ADERA.colors.bgLight} direction="left-to-right" />
    </div>
  );
};
