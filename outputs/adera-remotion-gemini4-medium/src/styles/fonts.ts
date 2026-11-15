import { continueRender, delayRender, staticFile } from 'remotion';

let fontLoaded = false;

export const loadInterVariableFont = (): void => {
  if (fontLoaded || typeof document === 'undefined') {
    return;
  }
  const handle = delayRender('Loading Inter Variable font');
  const font = new FontFace(
    'Inter Variable',
    `url(${staticFile('assets/fonts/inter-latin-wght-normal.woff2')}) format('woff2')`,
    {
      weight: '100 900',
      style: 'normal',
      display: 'swap',
    }
  );
  font
    .load()
    .then((loaded) => {
      document.fonts.add(loaded);
      fontLoaded = true;
      continueRender(handle);
    })
    .catch((err) => {
      console.error('Failed to load Inter Variable font:', err);
      continueRender(handle);
    });
};
