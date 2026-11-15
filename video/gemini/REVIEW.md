# ADERA — Review di Verifica Reanimate (`adera-gemini4-medium`)

## 1. Riepilogo consegna
- **Output HTML editabile**: `outputs/adera-reanimate-gemini4-medium/index.html` (`styles.css`, `timeline.js`, `data.js`, `manifest.json`)
- **Output Video**: `outputs/adera-reanimate-gemini4-medium/adera-presentation-150s.mp4` (`1920x1080`, `30 fps`, `150.0s`, `4500` frame, `yuv420p`, muto, senza sottotitoli né note in basso)
- **Specifica di movimento**: `.reanimate/adera-gemini4-medium/spec.md`
- **Riferimento di movimento**: `/Users/fede/.t3/userdata/attachments/8fbeb383-0c4d-4a5b-a591-edcfe3dc03f7-fdd6f97e-75af-4d73-b48f-febae4a64c6d-mp4.mp4` (`1920x1080`, `30 fps`, `60.7s`)
- **Fidelity**: `mixed` — microsequenze clonate dal riferimento (ingresso cinetico, easing, durata locale dei burst, overshoot dello swipe, nodi di orchestrazione, chiusura) verificate con `easing.ts` e `compare.ts`, combinate con palette (`#F6F5F9`, `#35214F`, `#7046CE`, `#8861E8`), font (`Inter Variable`), copy italiano, dati reali e scene aggiuntive ADERA fino a `150.0s`.

---

## 2. Storico dei round e verifica delle microsequenze (`±80ms` & easing)

| Round | Obiettivo e interventi | Esito chiave |
|---|---|---|
| **Round 1** | Prima cattura `clone-round-1` delle 6 microsequenze clonate + audit font/img/DOM | `Inter Variable` caricato, `23/23` immagini OK, `0` errori; scoperto bug critico CSS (`display: grid` centrava `#stage` a `(480,270)` tagliando `.s1-card-*` fuori schermo). |
| **Round 2** | Fix `#stage` (`position: absolute; left: 50%; top: 50%; margin: -540px 0 0 -960px`) + scala Y grafico Scene 4/5 (`0–16,5 €`) | Tutte le 6 sequenze visibili su intero `960x540`; `compare.ts` ha evidenziato: (a) auto-align sfalsato per colori diversi (`-5`/`+15`), (b) frame vuoto a `8.7s` in Scena 1, (c) `seq3`/`seq4`/`seq6` statici nei primi `0–3.7s` prima dell'ingresso principale, (d) pan Scena 12 orientato verso destra nonostante freccia a sinistra. |
| **Round 3** | Allineamento ingressi iniziali (`seq1` parole a `567ms`, `seq3` copy a `33ms`, `seq4` phone/telemetry a `33ms`/`2600ms`, `seq5` hub a `33ms`, `seq6` wipe a `33ms` + reveal `3433ms`), uscita fluida Scena 1 (`inOutCubic`), **vero pan a sinistra** in Scena 12 (`dash` a sinistra `0..1920`, `intro` a destra `1920..3840`, track `-1920 -> 0`) | **0 frame vuoti** su 44 keyframe; `easing.ts` RMSE `0.0007–0.0038`; start delle microsequenze `seq2–seq6` entro `0–33ms` dal riferimento; Scena 12 segue la freccia verso sinistra (`0` OOB su tutte le 13 scene). |

### Verifica `easing.ts` e tempi locali (Round 3 vs Reference)

| Microsequenza | Selettore & proprietà | Reference (start / dur / easing) | Clone Round 3 (`easing.ts`) | Errore timing azione | RMSE curva |
|---|---|---|---|---|---|
| `seq1-opening` (Scena 1) | `.s1-card-1` (`y`) | `2533ms` / `600ms` / `easeOutCirc` (`0.075,0.82,0.165,1`) | `delay 2533ms` / `608ms` / `easeOutCirc` | `0ms` start, `+8ms` dur | `0.0022` |
| `seq2-brand` (Scena 2) | `#s2-pill` (`x`) + `#s2-wipe` | wipe `0ms/267ms`; pill `3433ms/400ms` `easeOutCirc` | `delay 3433ms` / `405ms` / `easeOutCirc` | `0ms` start, `+5ms` dur | `0.0030` |
| `seq3-crowd` (Scena 7) | `#s7-card` (`y`) | copy `33ms`; card `3700ms/600ms` `easeOutExpo` | `delay 3700ms` / `600ms` / `easeOutExpo` | `0ms` start, `0ms` dur | `0.0007` |
| `seq4-feed` (Scena 8) | `#fc-u3` (`x` swipe) | swipe `4367ms/433ms` `easeOutBack` | `delay 4367ms` / `440ms` / `easeOutBack` (`9.9%` overshoot) | `0ms` start, `+7ms` dur | `0.0038` |
| `seq5-orch` (Scena 6) | `#s6-a1` (`y`) | hub `33ms`; agenti `4167ms/500ms` `easeOutExpo` | `delay 4167ms` / `500ms` / `easeOutExpo` | `0ms` start, `0ms` dur | `0.0008` |
| `seq6-closing` (Scena 13) | `#s13-lockup` (`scale`) | wipe `33ms`; lockup `400ms/533ms` `easeOutExpo` | `delay 400ms` / `540ms` / `easeOutExpo` | `0ms` start, `+7ms` dur | `0.0027` |

### Risultati `compare.ts` (`--offset 0`, confronto fotogramma per fotogramma)

| Sequenza | Frame confrontati | Start error (`compare.ts`) | End / Duration error | Mean pixel mismatch | Nota tecnica (`Fidelity: mixed`) |
|---|---|---|---|---|---|
| `seq1-opening` | `189 / 189` | `+0.200s` (prime lettere) | `-1.433s` / `-1.633s` | `13.35%` | Scena 1 estesa a `9.0s` (uscita a `8.53s` anziché `5.80s` per leggibilità copy); card `1/2/3` a `0ms` dal ref. |
| `seq2-brand` | `186 / 186` | `0.000s` | `-2.467s` / `-2.467s` | `98.19%` | Sfondo plum `#35214F` vs giallo `#E6FF00` del ref spiega il mismatch cromatico del 98%. |
| `seq3-crowd` | `180 / 282` | `+0.033s` | `-4.867s` / `-4.900s` | `25.78%` | Nel video ADERA la persona (`Scena 7`, `11s`) e il zoom-out a 10 avatar (`Scena 9`, `9s`) sono due scene distinte. |
| `seq4-feed` | `190 / 228` | `+0.033s` | `-2.067s` / `-2.100s` | `29.25%` | Scena 8 dura `19s` (3 swipe completi `FGR-U3`, `FGR-B1`, `FGR-S1`) vs finestra `6.3s` catturata. |
| `seq5-orch` | `174 / 174` | `0.000s` | `-0.933s` / `-0.933s` | `17.68%` | Stacco ingresso hub (`33ms`) e nodi agenti (`4167ms`) allineati; sfondi e testi diversi. |
| `seq6-closing` | `180 / 228` | `0.000s` (`peak -0.067s`) | `-3.000s` / `-3.000s` | `9.89%` | Wipe iniziale, lockup (`400ms`), payoff e reveal secondario (`3433ms`) corrispondenti; durata totale `6.0s`. |

---

## 3. Audit scene aggiuntive (0–150s) e integrità dati

- **44 keyframe di audit** (`.reanimate/adera-gemini4-medium/keyframes-audit/sheets/sheet-01.png`, `sheet-02.png`): `0` frame vuoti, `0` errori console/pagina, `0` elementi fuori dallo stage `1920x1080` (`OOB: 0` su tutte le 13 scene).
- **Scena 3–5 (Dati & Forecast)**:
  - Usa esclusivamente serie e metriche salvate in `adera-revamp/public/data/{overview,model-validation}.json`: `9.359.976` impr., `111.754` clic, `69.525,96 €`, CTR `1,19%`, CPM `7,43 €`; `699` righe forecast `16–30 nov` con metodo `ctr_baseline14d__cpm_timestral28m`.
  - Popup `Black Week (20/11/2026)`, `Black Friday (27/11/2026)` e `Cyber Monday (30/11/2026)` posizionati a `y=343..444px` sopra la curva (`y=488..509px`), **zero sovrapposizioni**, senza picchi inventati.
  - Logo **Mistral** affiancato all'etichetta `Timestral 28M` (CPM MAE `0,8841 €`, WMAE `0,7067 €`); **CatBoost** CTR MAE `0,2743 pp` vs Baseline 14gg `0,3163 pp` (Fold 2).
- **Scena 6 & 11 (Orchestrazione & Interviste)**:
  - **T3 Code** al centro con ruoli distinti per **Gemini** (`Decision 1` + `600` interviste cieche), **Claude** e **ChatGPT**.
  - Citazioni **letterali** da `product-story.json` su `FGR-U3` (`+151 / -1`, saldo `+150`) da **Chiara Bellini** (`abbigliamento-P001`) ed **Ettore Marchetti** (`abbigliamento-P003`).
- **Scena 7–9 (Persona, Feed Decision 1, Scala)**:
  - Avatar `chiara-hero.png` e 10 avatar estratti da `sheet-ten-grid.png` con alfa pulita (`sheet-five-grid.png` e `sheet-five-row.png` scartate per scacchiera incorporata non alpha).
  - Probabilità `Decision 1` (`FGR-U3` `14,96%` click intent, `FGR-B1` `37,35%` scroll, `FGR-S1` `36,24%` scroll) distinte dai CTR.
- **Scena 12 (Pan a sinistra -> Dashboard)**:
  - Camera effettua pan orizzontale verso **sinistra** (`dash-pane x: -1920 -> 0`, `intro-pane x: 0 -> +1920`) seguendo la freccia verso sinistra e mostrando viste quantitative (`16.950 €`, `+3,01%`) e qualitative (`600` profili, `7.200` valutazioni) separate.

---

## 4. Limiti documentati (senza simulazioni)
1. **Asset creativi mancanti (`FGR-U3`, `FGR-B1`, `FGR-S1`)**: nessuna API generativa chiamata; rappresentati con card HTML/CSS tipografiche tratte dalle descrizioni del kit e segnalate esplicitamente come card illustrative.
2. **Serie storica pre-cutoff in `overview.json`**: il file contiene i totali storici aggregati per ad set fino al `15/11/2026` (non serie giornaliere pre-cutoff); la Scena 4 rappresenta quindi la fascia storica aggregata (`CPM 7,43 €`, `CTR 1,19%`), il gap di cutoff al `15/11` e la curva giornaliera prevista `16–30/11`.
3. **Pixel mismatch elevato nelle sequenze clonate**: atteso con `Fidelity: mixed` per cambio completo di palette (plum/lilla vs giallo/nero), font (`Inter Variable`) e testo italiano; l'aderenza al riferimento è verificata sui timestamp di attivazione e sulle curve di easing (`RMSE ≤ 0.0038`).
