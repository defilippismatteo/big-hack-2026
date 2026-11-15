# Analisi Reference Video & Mapping Storyboard ADERA (150s / 4500f @ 30fps)

## 1. Specifiche Reference Video Analizzato
- **File**: `/Users/fede/.t3/userdata/attachments/8fbeb383-0c4d-4a5b-a591-edcfe3dc03f7-fdd6f97e-75af-4d73-b48f-febae4a64c6d-mp4.mp4`
- **Formato**: 1920×1080, H.264 (High, yuv420p), 30.00 fps, 1818 frame video (60.60s video / 60.70s audio).
- **Artefatti estratti in locale**:
  - Contact sheets 1fps: `analysis/contact_sheets/sheet_{1_00_19s,2_20_39s,3_40_60s}.jpg`
  - Strisce dense 6fps intorno ai tagli e ingressi: `analysis/dense/dense_*.jpg`
  - Analisi OCR + bounding box normalizzati 3fps (182 frame, Apple Vision): `analysis/vision_3fps.json`, `analysis/timeline_3fps.txt`
  - Analisi fotogramma-per-fotogramma 30fps (differenza RGB + centroide variazione): `analysis/frames_30fps_tiny/`

## 2. Grammatica Visiva, Tempi, Polarità & Easing Misurati sul Riferimento

| # | Intervallo Ref | Frame Ref | Polarità / Sfondo RGB | Layout & Tipografia (bbox su 1080p) | Movimento & Transizione misurati a 30fps |
|---|---|---|---|---|---|
| R1 | 0.00–6.00s | 0–180 | Chiaro `[243,239,232]` | Headline sinistra (`x=0.08, y=0.25, h=0.11`), 3 domande sequenziali (`y=0.45`), card isolata destra (`x=0.72..0.93`) | Domande a scatto morbido ogni ~1.0s; card destra entra a `f=77..88` (11f / 0.37s, ease-out). Taglio `f=180..190` (10f / 0.33s): **wipe verticale dal basso verso l'alto** (`cy: 0.99 -> 0.02`). |
| R2 | 6.00–10.20s | 180–306 | Scuro `[11,11,9]` | Label piccola (`y=0.44`) + numero gigante `$10,000` (`x=0.07, y=0.49, h=0.26`), testo progressivo sopra (`y=0.17`) | Contatore accelera al ribasso (`$10,000 -> $0` con easing quadratico); parole appaiono progressivamente. Taglio `f=305..311` (6f / 0.20s): **wipe rapido da sinistra a destra** (`cx: 0.19 -> 0.86`). |
| R3 | 10.20–16.33s | 306–490 | Accento `[240,214,74]` | Brand grande in alto-sinistra (`x=0.14, y=0.22`), payoff asimmetrico sotto (`y=0.41..0.49`), 2 chip in basso (`y=0.71`) | Comparsa scaglionata (`10.3s`, `14.0s`, `15.0s`). Taglio `f=491..516` (25f / 0.83s): **dissolvenza cromatica morbida** verso il chiaro. |
| R4 | 16.33–20.20s | 490–606 | Chiaro `[243,239,232]` | Numero enorme (`x=0.08, y=0.14, h=0.21`) + due righe bold (`y=0.33, 0.41`) | Contatore `1,185 -> 3,000` in ~2.0s con **ease-out cubico** (scatto iniziale veloce, rallentamento netto finale). |
| R5 | 20.20–25.50s | 606–765 | Chiaro `[243,239,232]` | Card profilo centrata (`x=0.28..0.72`), righe chiave-valore impilate (`y=0.37, 0.44, 0.56, 0.63`) | Rivelazione per righe ogni ~0.7–1.2s (`20.3s`, `21.0s`, `21.7s`, `22.7s`, `24.0s`). Taglio `f=764..775` (11f / 0.37s): **wipe verticale dal basso verso l'alto** verso scuro. |
| R6 | 25.50–33.30s | 765–999 | Scuro `[11,11,9]` | Split asimmetrico: sinistra (`x=0.08..0.36`) titolo fisso sopra + label fase sotto (`y=0.58`); destra (`x=0.40..0.92`) UI card scorrevole | Card destra scrolla verticalmente (`28.3–29.7s`), poi swap netto ogni ~1.5–2.0s (`f=902..910`, `f=949..954`, `f=973..977`, ~8f ease-out). |
| R7 | 33.30–40.33s | 999–1210 | Scuro `[11,11,9]` | Sinistra titolo (`y=0.11`) + verdetti impilati (`GO / ITERATE / NO-GO`, `y=0.45..0.67`); destra documento (`x=0.52..0.92 -> 0.40..0.92`) | **Pan/zoom e scroll del documento** (`f=1154..1170`, 16f / 0.53s ease-in-out): il documento si allarga e scorre verso l'alto per mostrare le righe dettagliate. |
| R8 | 40.33–46.13s | 1210–1384 | Scuro `[11,11,9]` | Counter `3,000` in alto-sinistra (`h=0.22`) + tabella comparativa multi-modello in basso (`y=0.55..0.75`) | Counter rapido (2.0s), tabella entra dal basso a `44.3s`, poi **pan/zoom** finale `f=1380`. Taglio `f=1381..1393` (12f / 0.40s): **wipe da sinistra a destra** (`cx: 0.00 -> 0.93`). |
| R9 | 46.13–48.87s | 1384–1466 | Accento `[240,214,74]` | Parola gigante (`h=0.25`) + riga evidenza (`y=0.50`) | Slam tipografico immediato (`46.6s`) + sottotitolo a `47.3s`. Taglio `f=1464..1474` (10f / 0.33s): **wipe dall'alto verso il basso** (`cy: 0.00 -> 0.51`). |
| R10 | 48.87–53.13s | 1466–1594 | Chiaro `[243,239,232]` | Card workspace/terminale centrata con riga di comando + log progressivi + strip loghi/agenti (`y=0.80`) | Digitazione/streaming progressivo e apparizione step log (`0.33s` per step). Taglio `f=1591..1598` (7f / 0.23s): **collasso/scale-down** della card su sfondo chiaro. |
| R11 | 53.13–60.60s | 1594–1818 | Chiaro `[243,239,232]` | Logo centrato (`y=0.30`), headline (`y=0.48`), metadata in basso (`y=0.65, 0.80`) | Reveal lineare sinistra->destra della headline (`54.6–55.6s`), fade metadati e hold pulito. |

**Principi chiave rilevati (da preservare su ADERA)**:
1. **Alternanza polare continua**: Chiaro (`#F6F5F9`) ↔ Scuro (`#191224`) ↔ Accento brand (`#7046CE` / `#35214F`) con transizioni direzionali (wipe verticale 10–11f, wipe orizzontale 10–12f, dissolvenza cromatica, collasso card 7f).
2. **Griglia asimmetrica e margini costanti**: margine sinistro costante `8%` (`154px` su 1920), colonna testuale sinistra `30–36%` e oggetti UI/grafici isolati a destra (`44–92%`), mai centrati passivamente tranne profilo, brand e chiusura.
3. **Micro-animazione continua**: nessuna scena statica; i testi scorrono/rivelano, i numeri contano con `easeOutCubic`, gli oggetti UI si muovono (camera follow, zoom-out, swipe, pan guidato da freccia, morph).
4. **Zero sottotitoli in basso** (esplicitamente rimossi come da `SPECIFICHE.md`) e **nessun disclaimer microscopico a piè di pagina** (natura sintetica dichiarata nel titolo/header principale).

---

## 3. Mapping Completo Storyboard ADERA (150s = 4500 frame @ 30fps)

| Scena | Tempo (s) | Frame (0–4500) | Durata | Sfondo ADERA | Mapping al Riferimento & Dichiarazione Scene Aggiunte |
|---|---|---|---:|---|---|
| **S01 · Domanda** | 0–9s | 0–270 | 270f | `#F6F5F9` | **Da R1**: headline cinetica sinistra «E se potessi testare una campagna prima di investirci?», 3 micro-domande sequenziali + card campagna ADERA (`FGR-U3`, dichiarata illustrazione) in ingresso da destra + wipe dal basso a `f=258..270`. |
| **S02 · ADERA** | 9–16s | 270–480 | 210f | `#7046CE` → `#35214F` | **Da R3**: wipe sinistro→destro rivela logo originale ADERA (`adera-original.png`), payoff «Prima di investire, capisci.», apertura del simbolo nel workspace a 3 moduli (cutoff 2026-11-15). |
| **S03 · Dati Challenge** | 16–27s | 480–810 | 330f | `#F6F5F9` | **Scena aggiunta (dichiarata)**: «Partiamo dai dati.» Contatore reale `9.359.976` impression / `1.879` righe storiche (kit organizzatori simulato, 17 ago–15 nov); righe e colonne di `storico_giornaliero.csv` si compattano e trasformano nella serie temporale CPM osservata. |
| **S04 · Forecast & Gap** | 27–44s | 810–1290 | 480f | `#191224` | **Scena aggiunta (dichiarata)** con camera motion dinamica: la camera segue la punta della curva storica fino al cutoff `15 nov`, evidenzia lo stacco tra **serie nota** (17 ago–15 nov) e **orizzonte di previsione** (`16–30 nov`, metodo `ctr_baseline14d__cpm_timestral28m`), poi **zoom-out** sull'intero orizzonte. Nessun picco inventato. |
| **S05 · Eventi e Modelli** | 44–53s | 1290–1590 | 300f | `#191224` → `#35214F` | **Scena aggiunta (dichiarata)**: popup reali **Black Week 20/11**, **Black Friday 27/11/2026** (CPM €10,92) e **Cyber Monday 30/11** (€10,87) ancorati ai dati di `overview.json`; confronto ruoli verificati **Mistral (`mistral.svg`) + «Timestral 28M»** (CPM, WMAE `0.699`) e **CatBoost (`catboost.svg`)** (validazione 2 fold cronologici, senza chiamare `overview` un ensemble CatBoost). |
| **S06 · Orchestrazione T3** | 53–65s | 1590–1950 | 360f | `#F6F5F9` | **Da R10 + R8**: **T3 Code** (`t3-code.svg`) al centro orchestra il flusso multi-agente con loghi ufficiali **Claude**, **Gemini**, **ChatGPT** (ruoli verificati dove documentati — `t3:antigravity` / `gemini-4-hydrogen` per schede/interviste e `Gemini Decision 1` per valutazioni; collaborazione multi-agente confermata senza inventare ruoli non documentati). |
| **S07 · Persona Chiara** | 65–76s | 1950–2280 | 330f | `#F6F5F9` | **Da R5**: «Un pubblico sintetico. Profili diversi.» Card **Chiara Bellini**, 46 anni (`abbigliamento-P001`), avatar `avatar-01.png` (`chiara-hero.png`), tecnica di laboratorio a Padova; righe scaglionate dai profili salvati. |
| **S08 · Feed Decision 1** | 76–95s | 2280–2850 | 570f | `#191224` | **Da R6**: wipe dal basso; feed simulato asimmetrico a destra con **swipe stile Tinder** tra `FGR-U3`, `FGR-B1`, `FGR-S1` (card SVG/HTML dichiarate **illustrazioni** dai testi del kit, non bitmap originali valutati). Affiancate le probabilità reali Decision 1 su 200 profili (run verificati, etichettate come **probabilità simulate, non CTR**). |
| **S09 · Scala 10 → 600** | 95–104s | 2850–3120 | 270f | `#F6F5F9` | **Da R4**: zoom-out dall'avatar di Chiara sui **10 avatar separati e puliti** (`avatar-01..10.png`) + griglia parzialmente fuori campo che suggerisce la scala, mentre il contatore sale `1 → 600` profili sintetici (`200` per settore · `7.200` valutazioni). |
| **S10 · Morph Segnali** | 104–112s | 3120–3360 | 240f | `#7046CE` → `#191224` | **Da R7 + R9**: «Dalle reazioni, segnali.» Card e indicatori convergono radialmente con morph fluido in un documento strutturato dei segnali per asset. |
| **S11 · Interviste T3** | 112–127s | 3360–3810 | 450f | `#191224` | **Da R7**: pan/zoom sul documento intervista **T3 + Gemini (`gemini-4-hydrogen`)** su `FGR-U3` (176 risposte, `+151` più utile / `-1` meno utile): domanda + **due risposte letterali** da `product-story.json` (Chiara Bellini `P001` e Sergio Lombardi `P002`). |
| **S12 · Pan & Dashboard** | 127–144s | 3810–4320 | 510f | `#F6F5F9` | **Scena aggiunta (dichiarata)**: pan a sinistra guidato da freccia animata verso la dashboard ADERA (`adera-revamp`), mostrando **Analisi Quantitativa** (Forecast CPM/CTR + Scenario Budget ±20%) e **Segnali Qualitativi** (Decision 1 + Interviste) in **viste distinte e separate**, senza alcuna fusione predittiva non implementata. |
| **S13 · Chiusura** | 144–150s | 4320–4500 | 180f | `#F6F5F9` | **Da R11**: collasso della vista dashboard sul logo originale ADERA (`adera-original.png`) e chiusura «ADERA. Prima di investire, capisci.» con indicazione sintetica/cutoff chiara. |
