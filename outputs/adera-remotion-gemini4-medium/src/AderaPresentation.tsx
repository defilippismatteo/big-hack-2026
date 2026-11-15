import React from 'react';
import { Sequence } from 'remotion';
import { SCENES } from './styles/theme';
import { loadInterVariableFont } from './styles/fonts';
import { S01_Domanda } from './scenes/S01_Domanda';
import { S02_AderaBrand } from './scenes/S02_AderaBrand';
import { S03_DatiChallenge } from './scenes/S03_DatiChallenge';
import { S04_ForecastGap } from './scenes/S04_ForecastGap';
import { S05_EventiModelli } from './scenes/S05_EventiModelli';
import { S06_Orchestrazione } from './scenes/S06_Orchestrazione';
import { S07_PersonaChiara } from './scenes/S07_PersonaChiara';
import { S08_FeedDecision } from './scenes/S08_FeedDecision';
import { S09_Scala10Avatar } from './scenes/S09_Scala10Avatar';
import { S10_MorphSegnali } from './scenes/S10_MorphSegnali';
import { S11_IntervisteT3 } from './scenes/S11_IntervisteT3';
import { S12_PanDashboard } from './scenes/S12_PanDashboard';
import { S13_Chiusura } from './scenes/S13_Chiusura';

loadInterVariableFont();

const SCENE_COMPONENTS: Record<(typeof SCENES)[number]['id'], React.FC> = {
  S01_Domanda,
  S02_AderaBrand,
  S03_DatiChallenge,
  S04_ForecastGap,
  S05_EventiModelli,
  S06_Orchestrazione,
  S07_PersonaChiara,
  S08_FeedDecision,
  S09_Scala10Avatar,
  S10_MorphSegnali,
  S11_IntervisteT3,
  S12_PanDashboard,
  S13_Chiusura,
};

export const AderaPresentation: React.FC = () => {
  return (
    <div style={{ width: '100%', height: '100%', backgroundColor: '#F6F5F9', position: 'relative' }}>
      {SCENES.map((scene) => {
        const Component = SCENE_COMPONENTS[scene.id];
        return (
          <Sequence key={scene.id} name={scene.label} from={scene.start} durationInFrames={scene.duration}>
            <Component />
          </Sequence>
        );
      })}
    </div>
  );
};
