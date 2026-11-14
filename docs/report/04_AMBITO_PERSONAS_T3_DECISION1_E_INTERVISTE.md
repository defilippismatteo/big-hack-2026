# Ambito 4 — Simulazione Sintetica: Personas T3, Decision 1 & Interviste Cieche

**Moduli e artefatti:** [Wevion_Personas_Architettura_v1/](../../Wevion_Personas_Architettura_v1/), [market_mirror/t3_personas.py](../../market_mirror/t3_personas.py), [feed.py](../../market_mirror/feed.py), [decision_runs.py](../../market_mirror/decision_runs.py), [signals.py](../../market_mirror/signals.py), [interviews.py](../../market_mirror/interviews.py), [handoff.py](../../market_mirror/handoff.py), [artifacts/personas_t3/](../../artifacts/personas_t3/).

---

## 1. Architettura `simulation_blind` e Confini Informativi (Information Boundary)

La pipeline qualitativa nasce separata dal forecasting numerico (**P4 opzionale** nella Specifica v4):
1. **`prepare_safe_inputs.py`:** legge solo `inserzionisti.csv` e `campagne.csv`. Nessun CTR, CPM, storico o testo creativo.
2. **`make_slots.py`:** genera con `seed=2026` **72 slot deterministici** (`24` per verticale, 6 fasce d'età, quote genere 45% donna / 45% uomo / 10% non binario/non dichiarato, motivazioni, abitudine social, propensione al rischio, interesse categoria).
3. **Writer T3 (`gemini-4-hydrogen` via abbonamento Antigravity, no API generativa):** arricchisce uno slot alla volta con biografia, routine, timori e contraddizioni.
4. **Feed controllato (`feed.py`):** 3 post organici neutri fittizi + 1 annuncio descritto testualmente (nessuna immagine o video reale; non simula l'algoritmo Meta).
5. **Worker Decision (`gemini-decision-1` via `client.decisions.create`, `v1beta`):** unica chiamata API Google consentita; ogni domanda contiene **solo** una persona, il suo feed e la creatività condivisa. Risponde su 12 opzioni chiuse `action__reason` (`scroll`, `glance`, `stop`, `click` × 12 motivi).
6. **Aggregazione (`signals.py`) & Handoff (`handoff.py`):** esporta `attention_signal = 1 - P(scroll)` e `click_intent_signal = P(click)` con `calibrated_to_ctr: False`. I segnali **non modificano mai i forecast numerici**.

---

## 2. Cosa è Stato Eseguito vs Cosa È Solo Pianificato

| Componente | Pianificato / Predisposto | Eseguito Effettivamente | Note operative |
|---|---|---|---|
| **Slot persona** | 72 slot (`18` job da 4 schede) | `1` job importato (`beauty_skincare-01`) = **4 schede reali** (`Chiara Bellini`, `Patrizia Ferri`, `Lorenzo Cattaneo`, `Davide Marchetti`) | I restanti 17 job in `artifacts/personas_t3/jobs/` sono piani non eseguiti |
| **Valutazioni Decision 1** | 36 asset × 24 persone = 864 | **12 asset Beauty × 4 persone = 48 valutazioni** | 12 richieste API riuscite + 1 tentativo iniziale `HTTP 429` recuperato; `53.056` token input totali; cache in `ledger.sqlite` (replay a 0 API) |
| **Interviste cieche** | Round qualitativo post-Decision | **4 colloqui completi** (`12` asset × `6` domande = **288 risposte aperte**) | Congelati in `interviews/frozen.json` prima del confronto; `executedModel` restituito `null` nelle ricevute T3 |
| **Domande diagnostiche extra** | `diagnostic_questions.proposal.json` (3 domande) | **Non eseguite** | Specifica pronta da implementare |
| **Settori `pet` e `abbigliamento`** | 24 asset (`CDF-*`, `FGR-*`) | **Non ancora valutati** in Decision 1 | Prossimo passo dopo espansione batch |

---

## 3. Risultati Chiave del Pilota `beauty_skincare` (4 Personas × 12 Asset)

### Ranking Decision 1 (`artifacts/personas_t3/analyses/REPORT.md`)
- **Top 3 per `click_intent_signal`:**
  1. `NDL-S3` (*Edizione limitata: kit routine autunno*, `scarcity`): `click_intent = 0,1392`, `attention = 0,6974`
  2. `NDL-S4` (*Rimasti in pochi: SPF 50 invisibile*, `scarcity`): `click_intent = 0,1363`, `attention = 0,6618`
  3. `NDL-S2` (*Torna disponibile, ma per poco*, `scarcity`): `click_intent = 0,1277`, `attention = 0,5775`
- **Cold-start `black_friday`:** `NDL-B3` (carosello, `0,1244`) quasi raddoppia `NDL-B1` (`0,0842`) e `NDL-B2` (`0,0625`).
- **Fondo classifica:** `NDL-B2` (`0,0625`) e `NDL-U1` (`0,0794`, picco di `scroll__skeptical = 27,1%`).
- **Divergenza chiave Track A vs Track B:** `NDL-B2` ha il CTR previsto più alto nel forecast quantitativo (`2,28%` perché gira su ad set caldi come `NDL-AS4`), ma arriva **12° su 12** nel test creativo isolato su pubblico misto.

### Interviste Cieche (`artifacts/personas_t3/interviews/REPORT.md`) e Divergenze Conservate
- **Cosa funziona qualitativamente:** chiarezza e utilità concreta (`NDL-U3` dermatologa calma, `NDL-S4` SPF50 pratico, citati ciascuno da 2/4 persone).
- **Cosa crea attrito:** urgenza, countdown e saldi generici (`NDL-B4` tra i meno utili per 4/4 persone; `NDL-B3` per 3/4).
- **Divergenze preservate (non appiattite):**
  - *Patrizia / `NDL-S2`:* score Decision più alto per lei (`0,3093`), ma critica lo scaffale vuoto nell'intervista.
  - *Lorenzo / `NDL-B3`:* 2° miglior score Decision (`0,1520`), ma inserito tra i meno utili nell'intervista.
- **4 Test A/B controllati proposti (`creative_analysis.reviewed.md`, una variabile alla volta, non ancora eseguiti):**
  1. `NDL-U1 / Patrizia`: spostare il countdown in chiusura mantenendo prodotto/sconto.
  2. `NDL-S4 / Lorenzo`: ridurre la densità dell'infografica a parità di copy e scarsità.
  3. `NDL-S3 / Lorenzo`: testare CTA informativa al posto di "Acquista ora".
  4. `NDL-U2 / Davide`: mettere spedizione gratuita in primo piano rispetto alla scadenza.
