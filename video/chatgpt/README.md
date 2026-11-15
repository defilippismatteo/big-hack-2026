# ADERA · Reanimate / Sol 6.1 low

Open `index.html` directly in Chromium. The 150-second film starts automatically. Hover at the bottom for play/pause and a seek slider. `?capture` disables automatic playback; `window.seek(seconds)` deterministically selects a frame.

Editable sources: `index.html` (layout/style), `timeline.js` (scene times and WAAPI), `data.js` (frozen exports), `reference-motion.js` (measured opening ink tracks), `assets/` (local font, logos, cleaned avatar crops, actual dashboard capture).

Render from repository root:

```sh
node .reanimate/adera-sol61-low/render.cjs
```

Local prerequisites already installed under the assigned evidence directory: Playwright/Chromium; system ffmpeg. No server, account or API required. The renderer writes 4500 frames via pipe to H.264; output has no audio or subtitle track.

Reference analysis, captures and comparison live in `.reanimate/adera-sol61-low/`. See `REVIEW.md` for the actual verification boundary. Other project files were not modified by this implementation.
