# Piano Video 180 Secondi: Punti Plausibili, Numeri Verificati e Architettura di Visualizzazione

**Riferimenti nel repository:** [docs/VIDEO_180S.md](../VIDEO_180S.md) e [BigHack2026_Wevion_Specifica_Operativa_v4.md](../../BigHack2026_Wevion_Specifica_Operativa_v4.md) §11.

> **Regola aurea di plausibilità:** mostrare **solo** numeri presenti nei CSV/JSON effettivamente prodotti, distinguere sempre cosa è *simulato dal kit* vs *calcolato localmente* vs *importato*, non mostrare come live componenti non ancora collegati (es. se il video mostra `Mix 50/50 + arricchimento BF`, prima va integrato `Prima_Analisi` o dichiarato chiaramente il ramo `feat/timestral-pilot`; se il video usa l'attuale `viewer.html` su `main`, usare i numeri di `wevion_v4`).

---

## 1. Scelta Strategica Prima di Registrare: Quale Stato Raccontare?

Esistono **due versioni coerenti e 100% veritiere** dei numeri a seconda che si completi o meno il merge dei risultati di `feat/timestral-pilot` dentro `deliver`:

- **Opzione A (Consigliata — Integrazione rapida `Mix 50/50 + BF` prima della registrazione):**
  - Chiude il punto aperto nel manifest di `main` ("Confrontare CatBoost e completare la selezione").
  - Numeri forti e difendibili: **Mix 50/50 CatBoost+Timestral-28M vince su entrambi i fold per il CPM** (`WMAE €0,6742` aggregato, `-10,8%` vs baseline), **Baseline 14g per CTR** (`0,2260 pp`), arricchimento BF interno anti-doppio-conteggio (`27/11`: CPM mediana `€17,04`, CTR `1,55%`), 15 gg con `€16.950` → `19.296` click (`CPC €0,8784`).
- **Opzione B (Stato attuale `main` senza merge):**
  - Numeri di `artifacts/wevion_v4/`: selezione Fold 1 `Baseline 14g CTR + Timestral-28M CPM`, riallocazione ±20% entro campagna (`18.170,1 → 18.717,6` click a `€16.950` fissi, `+547,5` click), e test pilota su 4 personas + 12 asset Beauty mostrato come **estensione qualitativa esplicativa** (mai come sostituto del forecast).

---

## 2. Punti Plausibili per il Video da 180 Secondi (9 Scene)

| Tempo | Titolo Scena | Messaggio Chiave (Voce / Testo) | Numeri Esatti e Verificati da Mostrare |
|---|---|---|---|
| **0–15 s** | **Il Problema** | Chi lancia campagne Meta decide pubblico, creatività e budget *prima* di avere i risultati. Con Wevion portiamo questa decisione prima di spendere. | `3` campagne Meta (`Beauty`, `Pet`, `Abbigliamento`) · `€16.950` budget nei 15 gg futuri (`€1.130/giorno`) |
| **15–29 s** | **Il Kit & La Sfida Tecnica** | Non è un dataset statico: ci sono nuovi annunci senza storico e lo shock del Black Friday che nello storico recente non c'è mai stato. | `91` gg storici (`1.879` righe) · `12` ad set · **`699` righe** target (`16–30 nov`) · **`114` righe cold-start** (`12` nuovi annunci, `6` nuovi asset BF) · `2` anomalie QA flaggate (`FGR-AS1` `€397,55` vs `€100`) |
| **29–45 s** | **Pubblico Nascosto (12 Ipotesi)** | Senza inventare età o genere non osservabili, confrontiamo gli ad set *a parità di asset e giorno* nella stessa campagna per ricostruire profili comportamentali. | `AS4` = alta intenzione (`CTR 1,89%–2,39%`, `CPM €9,95–€13,42`) · `AS1` = prospecting ampio (`CTR 0,89%–1,13%`, `CPM €5,22–€7,63`) · confidenza dichiarata `bassa` + alternative |
| **45–66 s** | **Motore Quantitativo (Ibrido, non Scorciatoia)** | Confronto onesto tra Baseline 14g, CatBoost ad-level (`logit CTR` / `log CPM`) e Mistral Timestral-28M a livello ad set (`12×2×91` + `7` covariate): nessuno vince ovunque da solo. | Fold 1+2 (`759` righe): **CPM** vince **Mix 50/50 CatBoost+Timestral-28M** (`WMAE €0,6742`, `-10,8%` vs baseline `€0,7559`); **CTR** stabile con **Baseline 14g** (`0,2260 pp`) |
| **66–82 s** | **Black Friday senza Doppio Conteggio** | Il picco `27/11` e `30/11` non esiste nello storico aug–nov: usiamo i benchmark Meta IT 2025 del kit (`r = 0,88–0,94` sul CPM storico), rimuovendo la quota già espressa da Timestral. | Benchmark 2025 BW: CPM `156–160`, CTR `116–135` · Picco `27/11`: CPM mediana **`€17,04`**, CTR **`1,55%`** · `30/11` CM: **`€13,82`** / **`1,36%`** |
| **82–107 s** | **Validazione Rigorosa & Incertezza** | Zero data leakage (verificato alterando i target futuri), backtest su 2 finestre cronologiche, analisi onesta degli errori sui nuovi annunci e bande `q10–q90` ancora non calibrate. | Fold 1 (`19/10–01/11`, `315` righe) · Fold 2 (`02/11–15/11`, `444` righe) · Copertura CPM 28M globale `82,5%–83,1%` ma **cold-start `66,7%–69,7%`** (sotto l'80% nominale) |
| **107–137 s** | **Demo Prototipo: 699 Previsioni & Personas Diagnostiche** | Esplorazione interattiva per verticale/giorno/ad set, export CSV esatto e *in parallelo* (senza contaminare il CTR) il layer qualitativo `Personas T3 + Decision 1` per capire *perché* una creatività frena. | `699` righe esportabili · `4` personas Beauty × `12` asset (`48` valutazioni `gemini-decision-1` + `288` risposte intervista): es. `NDL-B2` alto eCTR in `AS4` (`2,28%`) ma 12°/12 in freddo; `NDL-U1` `27,1%` scetticismo |
| **137–165 s** | **Decisioni: Dove Spostare il Budget in 10 Secondi** | Riallocazione vincolata ±20% a totale campagna invariato, quote delivery `90/10` per esplorare i nuovi annunci e ranking per CPC previsto. | `€16.950` invariati · Best CPC per vertical: `FGR-AS4` (`€0,56/click` vs `FGR-AS3 €1,34`), `CDF-AS4` (`€0,62`), `NDL-AS2` (`€0,98` vs `NDL-AS1 €1,26`) · Beauty `+8,3%` click |
| **165–180 s** | **Chiusura: Valore, Limiti & Riproducibilità** | Strumento leggero, riproducibile offline su CPU, onesto su ciò che non è stimabile senza conversioni o test causali, pronto a scalare. | `43` test automatici verdi · SHA-256 pesi tracciati · `manifest.json` + road to production (Conformal CQR, Bayes/GBDT, curve di saturazione) |

---

## 3. Come Strutturare le Visualizzazioni per il Video (Architettura Pratica)

Per ottenere un video da 3 minuti pulito, leggibile in 10 secondi da un giudice e fedele alla direzione grafica della **Specifica v4 §11** (sfondo chiaro/bianco ad alto contrasto, tipografia nera netta, **accento viola `#7C3AED` / `#8062E3`** per previsioni/futuro, verde teal `#0F766E` per baseline/sintetico, blu `#1D4ED8` per quantitativo), conviene **evitare di registrare file diversi saltando tra 6 tab del browser** e strutturare invece un **Video Presentation Mode in 3 livelli**:

### Livello 1 — Unico "Video Deck + Live Viewer" Controllabile da Tastiera (Consigliato)
Costruire una singola pagina HTML dedicata alla presentazione (`video_deck.html`, offline, senza server) con **9 slide-frame 16:9 (`1920×1080`)** navigabili con `← / →` e timer integrato per il relatore (nascosto in fullscreen):
1. **Slide 1–2 (0–29s) — Animated Timeline & Problem Framing:** barra temporale orizzontale SVG (`91 gg` in grigio/nero → taglio netto `15/11` → `15 gg` in **viola** con marker `20/11 BW`, `27/11 BF`, `30/11 CM` e badge `+12 annunci cold-start`).
2. **Slide 3 (29–45s) — Audience Matrix Card:** griglia compatta `3 vertical × 4 ad set` con solo `CTR%`, `CPM €` e tag comportamentale (`Alta intenzione` vs `Prospecting ampio`), con focus zoom su un confronto *stesso asset, stesso giorno*.
3. **Slide 4–6 (45–107s) — Quantitative Proof Charts (Interactive ECharts/SVG):**
   - Grafico a barre raggruppate **WMAE Fold 1 vs Fold 2 vs Aggregato** (mostra visivamente perché nessuno vince ovunque e perché il Mix 50/50 domina sul CPM);
   - Grafico a linee **Curva 2025 vs 2026 + Shock 27/11 e 30/11** (mostrando la linea pre-evento tratteggiata vs linea arricchita in viola);
   - Gauge/barra **Copertura `q10–q90` Globale (`83%`) vs Cold-Start (`67%`)** per evidenziare rigore scientifico invece di nascondere il limite.
4. **Slide 7–8 (107–165s) — Live Embed del Prototipo (`viewer.html` + pannello Track B):** invece di cambiare finestra, incorporare una vista focalizzata dei filtri reali (`Settore → Giorno → Ad Set`), tabella `699` righe con download CSV, **slider/tabella riallocazione ±20%** (mostra in 3 secondi `FGR-AS3 → FGR-AS4` e `NDL-AS1 → NDL-AS2`), più un **callout laterale "Perché?"** con lo split `NDL-B2` vs `NDL-S3` da `Decision 1 / Interviste`.
5. **Slide 9 (165–180s) — Closing Summary Card:** 3 KPI finali, badge modelli/tecnologie usate realmente (`Python`, `CatBoost`, `Mistral Timestral-28M`, `Gemini Decision 1 / T3`, `43/43 test`), link repo.

### Livello 2 — Regole Visive per la Leggibilità in Screen Recording
- **Massimo 3 numeri grandi per schermata**, mai tabelle con 15 colonne durante la narrazione (usare tabelle compatte `4–5` colonne o evidenziazione riga attiva).
- **Badge di stato esplicito** in alto a destra su ogni grafico (`Osservato Kit` · `Backtest Anti-Leakage` · `Forecast 16–30 Nov` · `Simulazione Sintetica Non Calibrata`) così la giuria non confonde mai dati reali/simulati e previsioni.
- **Registrazione consigliata:** registrare in `1920×1080` a `30/60 fps` (QuickTime/OBS) scorrendo le 9 scene in sincrono con una traccia audio pulita (20s di margine per tenere 175–180s netti).
