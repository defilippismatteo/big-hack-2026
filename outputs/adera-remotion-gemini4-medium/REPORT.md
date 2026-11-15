# Report Verifica — ADERA Video (Remotion React · Gemini 4 Hydrogen Medium)

## 1. Riepilogo Esecutivo & Deliverable Verificati
- **Modello & Thinking**: `gemini-4-hydrogen` (`thinking_level: medium`), implementazione diretta in Remotion React v4.0.543 dentro `/Users/fede/Documents/Progetti/hackathon/big-hack-2026/outputs/adera-remotion-gemini4-medium/`.
- **Composizione**: `AderaPresentation` (`1920x1080`, `30 fps`, `4500` frame, durata esatta `150.000000s`).
- **Remotion Studio attivo (preview locale autorizzata)**: `http://localhost:3111` (Network: `http://192.168.1.17:3111`) — verificato HTTP `200`, mantenuto aperto durante e al termine del lavoro.
- **Render MP4 finale locale**: `/Users/fede/Documents/Progetti/hackathon/big-hack-2026/outputs/adera-remotion-gemini4-medium/out/adera-presentation.mp4`
  - Verifica `ffprobe`: codec `h264`, `1920x1080`, `yuv420p`, `30/1` fps, `4500` frame, `duration: 150.000000`s, `size: 11,900,305` byte (`~11.9 MB`).
- **Font locale**: `Inter Variable` (`public/assets/fonts/inter-latin-wght-normal.woff2`) caricato deterministicamente con `delayRender` / `continueRender`.

---

## 2. Verifica Fonti Dati, Asset & Onestà dei Claims
Tutti i dati sono stati estratti in sola lettura dalle fonti condivise e congelati in `src/data/aderaVerifiedData.json`:
1. **Brief & Stato Asset**:
   - `outputs/adera-video-v1/SPECIFICHE.md`, `ASSET_E_PROMPT.md`, `ASSET_STATO_2026-11-15.md` (ultimo prevalente).
2. **Dati & Dashboard ADERA (`adera-revamp`)**:
   - `adera-revamp/public/data/overview.json`: metodo attivo `ctr_baseline14d__cpm_timestral28m`, cutoff `2026-11-15`, `699` righe forecast (`2026-11-16..2026-11-30`), budget `€1.695.000` (`baseClicks: 18.170`, `scenarioClicks: 18.718` con `budgetBound: 0.2`), probabilità simulate `Decision 1` su `n_personas = 200` per asset (`FGR-U3` `Click 15,0%`, `FGR-B1` `10,3%`, `FGR-S1` `11,7%`). **Mai presentato come ensemble CatBoost né come CTR misurato**.
   - `info fornite dagli organizzatori /dati/storico_giornaliero.csv` + `calendario.csv`: `1.879` righe storiche su `91` giorni (`2026-08-17..2026-11-15`), `9.359.976` impression, `111.754` click, `€69.525,96`, CTR medio `1,19%`, CPM medio `€7,43` (`€8,97` il `15/11`). Eventi calendario verificati: `Black Week 20/11` (`€10,26`), `Black Friday 27/11` (`€10,92`), `Cyber Monday 30/11` (`€10,87`), senza picchi inventati.
   - `adera-revamp/public/data/model-validation.json`: `2` fold cronologici (`759` righe combinate): CPM WMAE `baseline 0.756`, `CatBoost 0.700`, `Timestral-28M 0.699`, `mix_50_50 0.674`; CTR WMAE `baseline 0.226`, `CatBoost 0.261` (`0.210` su fold 2), `Timestral-28M 0.240`. Mistral AI (`mistral.svg`) affiancato a `Timestral 28M`; CatBoost (`catboost.svg`) mostrato con il proprio ruolo reale di validazione.
   - `adera-revamp/public/data/persona-library.json` & `product-story.json`: profilo `Chiara Bellini` (`abbigliamento-P001`), `600` profili sintetici (`200` per settore) e `7.200` valutazioni `Decision 1`, oltre alle due risposte **letterali** per `FGR-U3` (`Chiara Bellini P001` e `Sergio Lombardi P002`).
3. **Loghi & Avatar separati/puliti**:
   - Loghi copiati localmente in `public/assets/brands/`: `adera-original.png`, `t3-code.svg`, `claude.svg`, `gemini.svg`, `chatgpt.svg`, `catboost.svg`, `mistral.svg`.
   - `10` avatar trasparenti `512x512` RGBA in `public/assets/avatars/avatar-01.png..avatar-10.png` (`avatar-01.png` da `chiara-hero.png`; `avatar-02..10.png` estratti da `sheet-ten-grid.png` con `corner_alpha_max = 0` e scarto di `sheet-five-grid.png`/`sheet-five-row.png` che contenevano sfondi grigi/a scacchiera).
4. **Creatività mancanti (`FGR-U3`, `FGR-B1`, `FGR-S1`)**:
   - Nessuna bitmap originale disponibile nel repo (`ASSET_STATO_2026-11-15.md`); rese con componenti SVG/HTML in `src/components/AdCardIllustrations.tsx`, dichiarate apertamente come *«Illustrazione SVG/HTML»* e *«Ricostruzione illustrativa da scheda kit»*.
5. **Natura sintetica & assenza sottotitoli/TTS**:
   - Natura sintetica/simulata integrata nei titoli principali e nei badge di intestazione (nessuna nota microscopica a piè di pagina). Zero sottotitoli in basso e zero tracce audio/TTS.

---

## 3. Analisi Riferimento, Scene Mappate vs Scene Aggiunte Dichiarate
Documentazione frame-by-frame completa in `analysis/REFERENCE_ANALYSIS.md` (`1fps`, `6fps` denso intorno ai tagli, OCR Apple Vision `3fps`, diff `30fps`):
- **Scene adattate dal riferimento (`R1..R11`)**:
  - `S01_Domanda` (`0–270f`) ← `R1` (domanda cinetica sinistra, micro-domande, ingresso card da destra, wipe bottom-to-top 12f).
  - `S02_AderaBrand` (`270–480f`) ← `R3` (logo originale + payoff + apertura 3 moduli).
  - `S06_Orchestrazione` (`1590–1950f`) ← `R10 + R8` (hub T3 Code + Claude/Gemini/ChatGPT + log streaming).
  - `S07_PersonaChiara` (`1950–2280f`) ← `R5` (scheda profilo centrata a righe scaglionate + wipe bottom-to-top).
  - `S08_FeedDecision` (`2280–2850f`) ← `R6` (split asimmetrico con card swipe stile Tinder `FGR-U3` → `FGR-B1` → `FGR-S1`).
  - `S09_Scala10Avatar` (`2850–3120f`) ← `R4` (zoom-out sui 10 avatar + estensione fuori campo e contatore `1 → 600` `easeOutCubic`).
  - `S10_MorphSegnali` (`3120–3360f`) ← `R7 + R9` (convergenza radiale e morph nel documento segnali).
  - `S11_IntervisteT3` (`3360–3810f`) ← `R7` (documento intervista T3/Gemini con pan/zoom 21f e due citazioni letterali).
  - `S13_Chiusura` (`4320–4500f`) ← `R11` (logo originale + wipe lineare chiusura `«ADERA. Prima di investire, capisci.»`).
- **Scene aggiunte dichiarate (specifiche ADERA)**:
  - `S03_DatiChallenge` (`480–810f`): contatore `9.359.976` impression e trasformazione delle righe CSV nella curva osservata.
  - `S04_ForecastGap` (`810–1290f`): camera che segue la punta storica fino al cutoff `15 nov`, mostra stacco/orizzonte previsto e fa zoom-out.
  - `S05_EventiModelli` (`1290–1590f`): popup Black Week/Black Friday/Cyber Monday e benchmark verificato Mistral Timestral 28M vs CatBoost.
  - `S12_PanDashboard` (`3810–4320f`): pan a sinistra guidato da freccia animata verso dashboard ADERA con piano Quantitativo e piano Qualitativo separati (nessuna fusione predittiva) + collasso finale in `S13`.

---

## 4. Verifica Rendering & Limiti Noti
- **Verifica visiva/OCR**: eseguita con Apple Vision (`./analysis/vision_analyze`) sui `16` still di controllo (`snapshots/frame_*.png`) e su `6` frame PNG estratti direttamente dall'MP4 decodificato (`snapshots/mp4_samples/mp4_sec_*.png`), oltre al contact sheet (`snapshots/mp4_contact_sheet.jpg`). Individuati e risolti prima del render finale: collisione X-axis `15 Nov / 30 Nov` in `S04`, vicinanza popup `Black Friday / Cyber Monday` in `S05`, sovrapposizione card `ChatGPT` / nota in `S06` e posizione stamp in `S08`.
- **Limiti noti**:
  1. Le creatività `FGR-U3`, `FGR-B1`, `FGR-S1` sono illustrazioni SVG/HTML fedeli ai metadati testuali del kit perché le bitmap originali non erano presenti nel repository condiviso.
  2. In questo subagente il tool `preview_*` del browser condiviso non è attivo (`available: false`); Studio è stato avviato senza `--no-open` su `http://localhost:3111` (verificato HTTP `200`).
  3. Nessuna modifica a `adera-revamp`, `adera-reanimate-*`, `Test_Timestral` o runtime; nessun `git commit`.
