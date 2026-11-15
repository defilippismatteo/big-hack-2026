import React from 'react';
import { Easing, interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { ADERA } from '../styles/theme';

export type WipeDirection = 'bottom-to-top' | 'top-to-bottom' | 'left-to-right' | 'right-to-left';

export const CurtainWipeOverlay: React.FC<{
  startFrame: number;
  durationFrames?: number;
  color: string;
  direction?: WipeDirection;
}> = ({ startFrame, durationFrames = 12, color, direction = 'bottom-to-top' }) => {
  const frame = useCurrentFrame();
  if (frame < startFrame) return null;

  const progress = interpolate(frame, [startFrame, startFrame + durationFrames], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.inOut(Easing.cubic),
  });

  let transform = '';
  if (direction === 'bottom-to-top') {
    transform = `translateY(${(1 - progress) * 100}%)`;
  } else if (direction === 'top-to-bottom') {
    transform = `translateY(${-(1 - progress) * 100}%)`;
  } else if (direction === 'left-to-right') {
    transform = `translateX(${-(1 - progress) * 100}%)`;
  } else {
    transform = `translateX(${(1 - progress) * 100}%)`;
  }

  return (
    <div
      style={{
        position: 'absolute',
        inset: 0,
        backgroundColor: color,
        transform,
        pointerEvents: 'none',
        zIndex: 50,
      }}
    />
  );
};

export const StaggeredWords: React.FC<{
  text: string;
  startFrame?: number;
  framesPerWord?: number;
  fontSize?: number;
  fontWeight?: number;
  color?: string;
  lineHeight?: number;
  letterSpacing?: string;
  maxWidth?: number;
  highlightWords?: Record<string, string>;
}> = ({
  text,
  startFrame = 0,
  framesPerWord = 4,
  fontSize = 84,
  fontWeight = 800,
  color = ADERA.colors.ink,
  lineHeight = 1.06,
  letterSpacing = '-0.035em',
  maxWidth = 960,
  highlightWords = {},
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const words = text.split(' ');

  return (
    <div
      style={{
        display: 'flex',
        flexWrap: 'wrap',
        gap: `0 ${Math.round(fontSize * 0.24)}px`,
        maxWidth,
        fontFamily: ADERA.fontFamily,
        fontSize,
        fontWeight,
        lineHeight,
        letterSpacing,
        color,
      }}
    >
      {words.map((word, idx) => {
        const wStart = startFrame + idx * framesPerWord;
        const p = spring({
          frame: frame - wStart,
          fps,
          config: { damping: 18, stiffness: 190, mass: 0.7 },
        });
        const y = interpolate(p, [0, 1], [34, 0]);
        const op = interpolate(p, [0, 0.6, 1], [0, 1, 1]);
        const cleanKey = word.replace(/[«».,?!:;]/g, '').toLowerCase();
        const wordColor = highlightWords[cleanKey] ?? color;

        return (
          <span
            key={`${word}-${idx}`}
            style={{
              display: 'inline-block',
              overflow: 'hidden',
              paddingBottom: 6,
            }}
          >
            <span
              style={{
                display: 'inline-block',
                transform: `translateY(${y}px)`,
                opacity: op,
                color: wordColor,
              }}
            >
              {word}
            </span>
          </span>
        );
      })}
    </div>
  );
};

export const SlideUpBlock: React.FC<{
  children: React.ReactNode;
  startFrame?: number;
  distance?: number;
  style?: React.CSSProperties;
}> = ({ children, startFrame = 0, distance = 36, style }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const p = spring({
    frame: frame - startFrame,
    fps,
    config: { damping: 20, stiffness: 165, mass: 0.8 },
  });
  const y = interpolate(p, [0, 1], [distance, 0]);
  const opacity = interpolate(p, [0, 0.5, 1], [0, 1, 1]);

  return (
    <div
      style={{
        transform: `translateY(${y}px)`,
        opacity,
        ...style,
      }}
    >
      {children}
    </div>
  );
};

export const PillBadge: React.FC<{
  label: string;
  tone?: 'light' | 'dark' | 'accent' | 'mint' | 'amber' | 'coral';
  style?: React.CSSProperties;
}> = ({ label, tone = 'light', style }) => {
  const palettes = {
    light: { bg: '#EFEAFA', fg: '#5B39B6', border: '#DDD3F4' },
    dark: { bg: '#2B1F42', fg: '#D4C2FA', border: '#463368' },
    accent: { bg: ADERA.colors.action, fg: '#FFFFFF', border: ADERA.colors.accent },
    mint: { bg: '#E7F6EE', fg: '#16744C', border: '#B9E4CD' },
    amber: { bg: '#FFF4DF', fg: '#9A5B00', border: '#F5D693' },
    coral: { bg: '#FDECEF', fg: '#B4233C', border: '#F6BDC7' },
  }[tone];

  return (
    <span
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: 8,
        padding: '7px 14px',
        borderRadius: 999,
        backgroundColor: palettes.bg,
        color: palettes.fg,
        border: `1px solid ${palettes.border}`,
        fontSize: 15,
        fontWeight: 650,
        letterSpacing: '0.02em',
        fontFamily: ADERA.fontFamily,
        ...style,
      }}
    >
      {label}
    </span>
  );
};
