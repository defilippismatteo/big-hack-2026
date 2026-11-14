# Ambito 1 — Dati Sorgente, Schema del Kit & Data Quality

**Fonte primaria:** [Wevion-BigHack-sfida.pdf](../../info%20fornite%20dagli%20organizzatori%20/Wevion-BigHack-sfida.pdf), [LEGGIMI.md](../../info%20fornite%20dagli%20organizzatori%20/LEGGIMI.md), [data_quality.json](../../artifacts/wevion_v4/data_quality.json).

> **Natura del dataset:** tutti i numeri, inserzionisti, creatività e serie storiche sono **simulati dagli organizzatori** per l'hackathon. L'etichetta *osservato* nel repository indica valori forniti nello storico simulato del kit, non misure raccolte da campagne reali.

---

## 1. Inventario Completo dei 13 File CSV del Kit

| File | Righe | Granularità / Chiave | Periodo | Ruolo nel progetto |
|---|---:|---|---|---|
| `inserzionisti.csv` | 3 | `inserzionista_id` (`NDL`, `CDF`, `FGR`) | Statico | Descrizione business per 3 vertical (`beauty_skincare`, `pet_ecommerce`, `abbigliamento`) |
| `campagne.csv` | 3 | `campaign_id` (`NDL-C1`, `CDF-C1`, `FGR-C1`) | Da `2026-08-01` | Meta, obiettivo `vendite` |
| `adset.csv` | 12 | `adset_id` (4 per campagna) | Statico | `ottimizzazione=acquisti`, `strategia_offerta=costo più basso (senza limite)`, `pubblico=da definire` |
| `annunci.csv` | 69 | `ad_id` → `adset_id`, `asset_id` | Lancio/fine | Mapping tra 69 annunci e 36 asset; stesso asset riusabile in più ad set |
| `asset_creativi/asset_*.csv` | 36 (12×3) | `asset_id` | Lancio/fine | `leva` (`scarcity`, `urgency`, `black_friday`), `formato` (`immagine`, `video`, `carosello`), `durata_video_s`, testi, CTA, `descrizione_visual` (nessun file immagine/video) |
| `storico_giornaliero.csv` | 1.879 | `(data, ad_id)` | `2026-08-17` → `2026-11-15` (91 gg) | 57 annunci attivi nello storico; `spesa`, `impression`, `copertura`, `frequenza`, `click`, `ctr`, `cpc`, `cpm`, `budget_giornaliero_adset` |
| `budget_giornaliero.csv` | 1.272 | `(data, adset_id)` | 106 giorni (12 × 106) | Budget pianificati storici e futuri (€1.130/giorno = €16.950 nei 15 gg futuri) |
| `da_prevedere.csv` | 699 | `(data, ad_id)` | `2026-11-16` → `2026-11-30` (15 gg) | 51 annunci distinti, nessun outcome presente |
| `calendario.csv` | 106 | `data` | 106 giorni | `weekend`, `evento` (`Rientro dalle ferie`, `Halloween`, `Ognissanti`, `Singles Day`, `Inizio Black Week 20/11`, `Black Friday 27/11`, `Cyber Monday 30/11`), `periodo` |
| `benchmark_mercato_settimanale_2025.csv` | 66 | `(settimana_dal, vertical)` | Autunno 2025 (22 sett. × 3) | Indici settimanali `indice_cpm`, `indice_ctr` (`meta`, `IT`, base `100` = media set–ott 2025) |
| `cpm_storici.csv` | 704 | `(piattaforma, paese, mese, obiettivo)` | `2025-01` → `2026-10` | `meta`/`tiktok`, `IT`/`DE`/`FR`/`ES`, 4 obiettivi; `cpm_mediano`, `cpm_q1`, `cpm_q3`, `n_campagne` |

---

## 2. Complessità Strutturale del Periodo Target (`da_prevedere.csv`)

1. **Cold-start di annunci e asset:**
   - Su `69` annunci complessivi, `57` compaiono nello storico e `51` nel futuro.
   - **`12` annunci sono completamente nuovi** nel periodo futuro (`4` per settore: `CDF-AD06/11/17/23`, `FGR-AD06/11/17/23`, `NDL-AD06/11/17/23`) e generano **`114` delle `699` righe target (16,3%)**.
   - **`6` asset sono completamente inediti** nel futuro (`CDF-B3`, `CDF-B4`, `FGR-B3`, `FGR-B4`, `NDL-B3`, `NDL-B4`), tutti con leva `black_friday`. Gli annunci storici con leva `black_friday` (`*-B1`, `*-B2`) hanno solo `22` righe per verticale (attivi soltanto a ridosso del cutoff `2026-11-15`).
2. **Espansione progressiva della griglia:**
   - `16–19 novembre`: **39** annunci attivi/giorno;
   - `20–22 novembre` (avvio Black Week): **45** annunci attivi/giorno;
   - `23–30 novembre` (settimana Black Friday + Cyber Monday): **51** annunci attivi/giorno.
3. **Shock stagionale assente dallo storico recente:**
   - I flag di calendario `black_week`, `black_friday`, `cyber_monday` valgono **sempre `0` nello storico fino al 15 novembre** e diventano `1` solo nel periodo da prevedere.

---

## 3. Anomalie di Qualità Dati Rilevate (`quality_audit`)

Verificate in [market_mirror/analytics.py](../../market_mirror/analytics.py) e [data_quality.json](../../artifacts/wevion_v4/data_quality.json):

1. **Giornate di overspend rispetto al budget ad set (preservate nei CSV sorgente, escluse dal calcolo pacing):**
   - `2026-10-21` · `FGR-AS1`: spesa aggregata di **`€397,55`** contro un budget pianificato di **`€100,00`** (quasi `4×`).
   - `2026-11-10` · `CDF-AS3`: spesa aggregata di **`€50,01`** contro **`€50,00`** (`+€0,01`).
2. **Righe con zero click:** `9` righe nello storico hanno `click = 0` e `cpc` vuoto (richiedono ricalcolo sicuro senza divisioni per zero e smoothing per il `logit(CTR)`).
3. **Budget condiviso ad set:** `budget_giornaliero_adset` è ripetuto identico su tutte le righe degli annunci attivi nello stesso ad set/giorno; sommarlo per annuncio moltiplicherebbe erroneamente il budget.
4. **Target ricalcolati dai conteggi:** tutti i moduli (`analytics.py`, `valida_modelli.py`, `timestral_pilot.py`) ricalcolano `CTR = 100 * click / impression` e `CPM = 1000 * spesa / impression` invece di fare medie semplici dei rapporti già presenti nel CSV.

---

## 4. Controlli Anti-Leakage Implementati

Sia `market_mirror/forecast.py` sia `Prima_Analisi/valida_modelli.py` (su `origin/feat/timestral-pilot`) e `artifacts/timestral_reproduction/verify.py` verificano:
- **Cutoff rigido (`<= cutoff`):** le feature rolling a 7 giorni in CatBoost usano `shift(1).rolling(7)`; nei test `verify_no_leakage`, alterare a `0` tutti gli outcome dopo il cutoff o nello stesso giorno agli estremi del training produce matrici `X_train`, `X_holdout` e tensori Timestral **bit-identici**.
- **Assenza di colonne target future:** `future_outcomes_present = []` verificato programmaticamente su `da_prevedere.csv`.
- **Evidenze audience separate per fold:** `market_mirror/delivery.py` genera `audience_evidence_2026-10-18.json` e `audience_evidence_2026-11-01.json` oltre a `2026-11-15` per evitare retrospettive con dati futuri.
