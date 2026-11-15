import React from 'react';
import { Clock, Package, RotateCcw, Tag, Sparkles } from 'lucide-react';
import { ADERA } from '../styles/theme';

export type AdAssetId = 'FGR-U3' | 'FGR-B1' | 'FGR-S1';

// Illustrative SVG/HTML creative cards built strictly from kit metadata (ASSET_STATO_2026-11-15.md)
// Explicitly labeled as illustrative reconstructions, NOT original input bitmaps evaluated by Decision 1.
export const AdCreativeIllustrationCard: React.FC<{
  assetId: AdAssetId;
  headline: string;
  body: string;
  cta: string;
  carouselIndex?: number; // 0..3 for FGR-U3
  darkTheme?: boolean;
  compact?: boolean;
}> = ({ assetId, headline, body, cta, carouselIndex = 0, darkTheme = true, compact = false }) => {
  const cardBg = darkTheme ? '#FFFFFF' : '#FFFFFF';
  const borderCol = darkTheme ? '#3D2E57' : ADERA.colors.borderLight;

  const renderVisualArea = () => {
    if (assetId === 'FGR-U3') {
      // 4 carousel panels: timer, pacco, capo indossato, reso facile
      const panels = [
        {
          bg: 'linear-gradient(135deg, #35214F 0%, #7046CE 100%)',
          icon: <Clock size={46} color="#FFFFFF" strokeWidth={2.2} />,
          tag: '48 ORE · TIMER',
          title: 'Ordina in 48h',
          sub: 'Spedizione gratuita attiva',
        },
        {
          bg: 'linear-gradient(135deg, #2B1A44 0%, #5835A8 100%)',
          icon: <Package size={46} color="#FFFFFF" strokeWidth={2.2} />,
          tag: 'PACCO INCLUSO',
          title: 'Spedizione €0',
          sub: 'Consegna standard tracciata',
        },
        {
          bg: 'linear-gradient(135deg, #EFEAFA 0%, #DCD1F5 100%)',
          icon: (
            <svg width="78" height="78" viewBox="0 0 80 80" fill="none">
              <path
                d="M25 18 L34 14 Q40 19 46 14 L55 18 L66 32 L57 38 L53 31 V64 H27 V31 L23 38 L14 32 Z"
                fill="#35214F"
                stroke="#7046CE"
                strokeWidth="2.5"
                strokeLinejoin="round"
              />
              <path d="M35 16 Q40 24 45 16" stroke="#C2A5FF" strokeWidth="2.5" fill="none" />
            </svg>
          ),
          tag: 'CAPO INDOSSATO',
          title: 'Collezione Autunno-Inverno',
          sub: 'Illustrazione scheda prodotto',
          light: true,
        },
        {
          bg: 'linear-gradient(135deg, #1E6B4F 0%, #2AA876 100%)',
          icon: <RotateCcw size={46} color="#FFFFFF" strokeWidth={2.2} />,
          tag: 'RESO FACILE',
          title: 'Reso gratuito',
          sub: 'Cambio o rimborso rapido',
        },
      ];
      const active = panels[carouselIndex % panels.length];
      return (
        <div
          style={{
            height: compact ? 220 : 280,
            borderRadius: 14,
            background: active.bg,
            padding: 24,
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'space-between',
            position: 'relative',
            overflow: 'hidden',
          }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span
              style={{
                fontSize: 12,
                fontWeight: 750,
                letterSpacing: '0.08em',
                padding: '5px 10px',
                borderRadius: 999,
                backgroundColor: active.light ? '#35214F' : 'rgba(255,255,255,0.18)',
                color: '#FFFFFF',
              }}
            >
              {active.tag}
            </span>
            <span
              style={{
                fontSize: 12,
                fontWeight: 650,
                color: active.light ? '#35214F' : 'rgba(255,255,255,0.85)',
              }}
            >
              Scheda {(carouselIndex % 4) + 1}/4
            </span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 18 }}>
            <div
              style={{
                width: 86,
                height: 86,
                borderRadius: 18,
                backgroundColor: active.light ? '#FFFFFF' : 'rgba(255,255,255,0.14)',
                display: 'grid',
                placeItems: 'center',
                flexShrink: 0,
              }}
            >
              {active.icon}
            </div>
            <div>
              <div
                style={{
                  fontSize: 28,
                  fontWeight: 800,
                  letterSpacing: '-0.02em',
                  color: active.light ? ADERA.colors.ink : '#FFFFFF',
                }}
              >
                {active.title}
              </div>
              <div
                style={{
                  fontSize: 16,
                  fontWeight: 500,
                  marginTop: 6,
                  color: active.light ? ADERA.colors.inkSoft : 'rgba(255,255,255,0.85)',
                }}
              >
                {active.sub}
              </div>
            </div>
          </div>
          <div style={{ display: 'flex', gap: 6 }}>
            {[0, 1, 2, 3].map((dot) => (
              <div
                key={dot}
                style={{
                  height: 5,
                  flex: dot === carouselIndex % 4 ? 2.2 : 1,
                  borderRadius: 99,
                  backgroundColor:
                    dot === carouselIndex % 4
                      ? active.light
                        ? '#7046CE'
                        : '#FFFFFF'
                      : active.light
                        ? '#C9BCE8'
                        : 'rgba(255,255,255,0.35)',
                }}
              />
            ))}
          </div>
        </div>
      );
    }

    if (assetId === 'FGR-B1') {
      // Grafica nera con '-30%' gigante, capi in basso, molte righe di condizioni
      return (
        <div
          style={{
            height: compact ? 220 : 280,
            borderRadius: 14,
            background: '#110E18',
            padding: 24,
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'space-between',
            color: '#FFFFFF',
            position: 'relative',
            overflow: 'hidden',
          }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span
              style={{
                fontSize: 12,
                fontWeight: 750,
                letterSpacing: '0.08em',
                padding: '4px 10px',
                borderRadius: 6,
                backgroundColor: '#8861E8',
                color: '#FFFFFF',
              }}
            >
              BLACK FRIDAY ANTICIPATO
            </span>
            <Tag size={20} color="#C2A5FF" />
          </div>
          <div style={{ display: 'flex', alignItems: 'baseline', justifyContent: 'space-between' }}>
            <div style={{ fontSize: 96, fontWeight: 900, letterSpacing: '-0.05em', lineHeight: 0.9, color: '#FFFFFF' }}>
              -30%
            </div>
            <svg width="110" height="82" viewBox="0 0 110 82" fill="none">
              <rect x="6" y="20" width="44" height="54" rx="8" fill="#2A203E" stroke="#6E55A3" strokeWidth="2" />
              <rect x="58" y="12" width="46" height="62" rx="8" fill="#35214F" stroke="#8861E8" strokeWidth="2" />
              <path d="M20 20 L28 32 L36 20" stroke="#C2A5FF" strokeWidth="2" />
              <path d="M72 12 L81 26 L90 12" stroke="#C2A5FF" strokeWidth="2" />
            </svg>
          </div>
          <div style={{ borderTop: '1px solid #2D2342', paddingTop: 10, fontSize: 11, color: '#9E94B8', lineHeight: 1.45 }}>
            *Valido su selezione autunno-inverno. Esclusi articoli continuativi e bundle. Condizioni e soglie applicate al checkout.
          </div>
        </div>
      );
    }

    // FGR-S1: ULTIME TAGLIE, percentuali grandi, date e condizioni, molto testo
    return (
      <div
        style={{
          height: compact ? 220 : 280,
          borderRadius: 14,
          background: '#F2EDF9',
          border: '1px solid #D7CCE9',
          padding: 22,
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'space-between',
          color: ADERA.colors.ink,
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span
            style={{
              fontSize: 12,
              fontWeight: 800,
              letterSpacing: '0.07em',
              padding: '4px 10px',
              borderRadius: 6,
              backgroundColor: ADERA.colors.plum,
              color: '#FFFFFF',
            }}
          >
            SALDI FINE ESTATE
          </span>
          <span style={{ fontSize: 13, fontWeight: 700, color: ADERA.colors.action }}>FINO AL -50%</span>
        </div>
        <div>
          <div style={{ fontSize: 44, fontWeight: 900, letterSpacing: '-0.04em', lineHeight: 1, color: ADERA.colors.plum }}>
            ULTIME TAGLIE
          </div>
          <div style={{ fontSize: 13, color: ADERA.colors.inkSoft, marginTop: 8, lineHeight: 1.45 }}>
            Sconti progressivi fino al 50% su fine serie stagionali. Disponibilità limitata per misura; validità 10–15 nov, non cumulabile con altri codici.
          </div>
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          {['XS', 'S', 'XL'].map((sz) => (
            <span
              key={sz}
              style={{
                padding: '4px 10px',
                borderRadius: 6,
                backgroundColor: '#FFFFFF',
                border: '1px solid #D1C5E8',
                fontSize: 12,
                fontWeight: 700,
                color: ADERA.colors.inkSoft,
              }}
            >
              {sz}
            </span>
          ))}
        </div>
      </div>
    );
  };

  return (
    <div
      style={{
        width: '100%',
        backgroundColor: cardBg,
        borderRadius: 20,
        border: `1px solid ${borderCol}`,
        padding: compact ? 18 : 22,
        boxShadow: darkTheme ? '0 22px 60px rgba(8, 4, 16, 0.55)' : '0 18px 46px rgba(41, 35, 57, 0.10)',
        fontFamily: ADERA.fontFamily,
        color: ADERA.colors.ink,
      }}
    >
      {/* Feed Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 14 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <div
            style={{
              width: 34,
              height: 34,
              borderRadius: 10,
              backgroundColor: ADERA.colors.action,
              color: '#FFFFFF',
              display: 'grid',
              placeItems: 'center',
              fontSize: 13,
              fontWeight: 800,
            }}
          >
            FGR
          </div>
          <div>
            <div style={{ fontSize: 14, fontWeight: 700, color: ADERA.colors.ink }}>FGR · Autunno-Inverno</div>
            <div style={{ fontSize: 12, color: ADERA.colors.inkMuted }}>Feed simulato · Sponsorizzato · {assetId}</div>
          </div>
        </div>
        <span
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: 5,
            fontSize: 11,
            fontWeight: 650,
            padding: '4px 9px',
            borderRadius: 999,
            backgroundColor: '#F3EEFA',
            color: '#5D3BB8',
          }}
        >
          <Sparkles size={12} />
          Illustrazione SVG/HTML
        </span>
      </div>

      {/* Primary copy */}
      <div style={{ fontSize: 15, color: ADERA.colors.inkSoft, marginBottom: 12, lineHeight: 1.4 }}>{body}</div>

      {/* Creative Illustration */}
      {renderVisualArea()}

      {/* Footer CTA */}
      <div
        style={{
          marginTop: 14,
          paddingTop: 12,
          borderTop: '1px solid #EBE6F3',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: 12,
        }}
      >
        <div>
          <div style={{ fontSize: 12, color: ADERA.colors.inkMuted, textTransform: 'uppercase', letterSpacing: '0.06em' }}>
            {assetId} · Ricostruzione illustrativa da scheda kit
          </div>
          <div style={{ fontSize: 17, fontWeight: 750, color: ADERA.colors.ink, marginTop: 2 }}>{headline}</div>
        </div>
        <div
          style={{
            padding: '10px 18px',
            borderRadius: 10,
            backgroundColor: ADERA.colors.action,
            color: '#FFFFFF',
            fontSize: 14,
            fontWeight: 700,
            whiteSpace: 'nowrap',
          }}
        >
          {cta}
        </div>
      </div>
    </div>
  );
};
