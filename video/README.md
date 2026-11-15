# ADERA — video unificato

Aprire `index.html` per riproduzione locale; `?capture` ferma il playback. `await ready; seek(secondi)` permette la cattura deterministica. Chromium richiede `--allow-file-access-from-files` per accedere ai due runtime iframe locali.

Il progetto unico compone i DOM editabili di Matteo, ChatGPT e Gemini, senza concatenare filmati. `unified.js` coordina i layer: grafico ChatGPT originale e soli popup/widget Gemini sovrapposti. Le copie sorgenti mantengono asset, CSS e timeline locali. `chatgpt/data.js` conserva i dati originali della serie FGR-AD09. La precedente versione MP4 è conservata come `ADERA-UNIFICATO-v1.mp4`.

Revisione corrente: etichette ancorate ai punti reali del 20/27/30 novembre, guide e indicatori; fondo plum con pannello come riferimento utente. `ADERA-UNIFICATO-v2.mp4` conserva il render prima di questa modifica. Copione approvato in `COPIONE.md`, tempi di lettura pianificati in `SINCRONIZZAZIONE.md`; audio non ancora generato.

Render dalla root repository: `node .reanimate/adera-unified/render.cjs`. Richiede il Playwright già installato in `.reanimate/adera-sol61-low/node_modules` e `/opt/homebrew/bin/ffmpeg`. Nessun server, API o servizio cloud. Il render ricattura la dashboard dalla build copiata in `dashboard/preview.html`.

La directory `dashboard/` contiene la copia delle sorgenti correnti, build e cattura: gli originali non sono modificati. Il symlink node_modules riusa le dipendenze installate; per trasferire il progetto reinstallare le dipendenze dal package.json nella copia. Le scene video e gli asset sono editabili; la vista dashboard è una cattura raster, come previsto dal brief.

Mappa, dati, hash e limiti: `manifest.json`, `REVIEW.md` e `.reanimate/adera-unified/spec.md`. Matteo proviene dal commit 2a9019ecfa6ee2785fe88471a70c4ce34af4ead0. Le copie degli MP4 sorgenti sono riferimenti, non layer del video finale.
