import React from 'react';
import { Img, staticFile } from 'remotion';
import { ADERA } from '../styles/theme';

export const AderaOriginalLogo: React.FC<{
  height?: number;
  style?: React.CSSProperties;
}> = ({ height = 90, style }) => {
  return (
    <Img
      src={staticFile('assets/brands/adera-original.png')}
      style={{
        height,
        width: 'auto',
        objectFit: 'contain',
        display: 'block',
        ...style,
      }}
    />
  );
};

// Geometric vector symbol preserving the violet triangle + 3 horizontal white bars identity
// Used strictly when animating symbol opening into workspace frames (Scene 2), while original PNG appears in logo beats.
export const AderaVectorTriangle: React.FC<{
  size?: number;
  barProgress?: number; // 0..1
  fill?: string;
}> = ({ size = 120, barProgress = 1, fill = ADERA.colors.action }) => {
  const barWidths = [0.24, 0.42, 0.6];
  return (
    <svg width={size} height={size} viewBox="0 0 120 120" fill="none">
      <path
        d="M60 10 C63 10 66 12 68 15 L110 96 C113 102 109 109 102 109 H18 C11 109 7 102 10 96 L52 15 C54 12 57 10 60 10 Z"
        fill={fill}
      />
      {barWidths.map((bw, idx) => {
        const y = 48 + idx * 17;
        const fullW = bw * 88;
        const w = fullW * barProgress;
        const x = 60 - w / 2;
        return (
          <rect
            key={idx}
            x={x}
            y={y}
            width={Math.max(0, w)}
            height={7.5}
            rx={3.75}
            fill="#FFFFFF"
          />
        );
      })}
    </svg>
  );
};

export const ProviderLogo: React.FC<{
  name: 't3' | 'claude' | 'gemini' | 'chatgpt' | 'catboost' | 'mistral';
  size?: number;
  style?: React.CSSProperties;
}> = ({ name, size = 44, style }) => {
  const fileMap = {
    t3: 'assets/brands/t3-code.svg',
    claude: 'assets/brands/claude.svg',
    gemini: 'assets/brands/gemini.svg',
    chatgpt: 'assets/brands/chatgpt.svg',
    catboost: 'assets/brands/catboost.svg',
    mistral: 'assets/brands/mistral.svg',
  };
  return (
    <Img
      src={staticFile(fileMap[name])}
      style={{
        width: size,
        height: size,
        objectFit: 'contain',
        display: 'block',
        ...style,
      }}
    />
  );
};
