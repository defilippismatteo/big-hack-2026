import React from 'react';
import { Composition } from 'remotion';
import { ADERA } from './styles/theme';
import { AderaPresentation } from './AderaPresentation';

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="AderaPresentation"
        component={AderaPresentation}
        durationInFrames={ADERA.durationInFrames}
        fps={ADERA.fps}
        width={ADERA.width}
        height={ADERA.height}
      />
    </>
  );
};
