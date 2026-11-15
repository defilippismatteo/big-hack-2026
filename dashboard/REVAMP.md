# ADERA revamp

Copia del frontend di `feat/adera-dashboard`, commit `a2e17ce`. La provenienza completa e gli hash dei tre snapshot sono in `REVAMP_SOURCE.json`. I JSON di dati sono identici agli originali del branch; calcoli e filtri restano quelli di ADERA.

Le modifiche riguardano il layout, il tema, il titolo della panoramica e il nome leggibile del modello quantitativo. `src/revamp.css` raccoglie il tema; `src/overview/Overview.jsx` mantiene le componenti originali.

Verifica: `npm test` e `npm run build`.

Per rigenerare la versione offline interattiva: `npm run build` e `python3 scripts/export_preview.py`. Apri `preview.html`. Lo script incorpora build, font, logo e i tre snapshot e non avvia un server. La variante offline sostituisce le unità vh con altezze fisse per il rendering nella conversazione; il frontend conserva il comportamento originale.

Motion film: `python3 scripts/build_motion.py` builds six compositions across three 8-second scenes. `node scripts/export_motion.mjs` renders 720 frames at 30 FPS in Full HD and exports the complete silent MP4 to `public/motion/adera-personas.mp4`. Runtime dependency: `playwright-core` in `/tmp/adera-motion-runtime`, Chrome and FFmpeg. `public/motion/pacing.json` contains timings and proposed narration cues, not a synchronized voice track. `node scripts/check_motion_studio.mjs` checks transport and sequential playback; `node scripts/check_fast_motion.mjs` inspects intermediate frames and samples real-time playback, writing evidence to `review/fast-motion/`.
