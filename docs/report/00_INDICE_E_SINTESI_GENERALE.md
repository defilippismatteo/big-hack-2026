# Indice Generale e Mappa per Ambiti — Repository `big-hack-2026` (Wevion)

**Data analisi:** 14 novembre 2026 · **Cutoff dati:** `2026-11-15` · **Orizzonte forecast:** `2026-11-16` → `2026-11-30` (15 giorni, `699` righe).

Questo dossier scompone l'intero repository (inclusi il branch `main`, i branch remoti `origin/feat/timestral-pilot`, `origin/feat/adera-dashboard`, `origin/feat/wevion-mvp-foundation` e le directory locali `artifacts/` e `outputs/`) in **6 ambiti operativi**, più un **piano strutturato per il video da 180 secondi e la sua visualizzazione**.

---

## Mappa dei Report per Ambito

| # | Ambito | Report dedicato | Componenti principali coperti |
|---|---|---|---|
| 1 | **Dati Sorgente & Data Quality** | [01_AMBITO_DATI_E_QUALITA.md](01_AMBITO_DATI_E_QUALITA.md) | 13 CSV in `info fornite dagli organizzatori /dati/`, brief PDF, relazioni gerarchiche, cold-start, anomalie e test anti-leakage |
| 2 | **Analisi Quantitativa, Forecasting & Larga Scala** | [02_REPORT_ANALISI_QUANTITATIVA_E_SCALA.md](02_REPORT_ANALISI_QUANTITATIVA_E_SCALA.md) | Tutti i 6 approcci modellistici, metriche Fold 1/2 e cold-start, matrice completa **dati usati vs esclusi**, alternative architetturali su larga scala |
| 3 | **Audience Inference & Motore Decisionale** | [03_AMBITO_AUDIENCE_E_DECISIONI_BUDGET.md](03_AMBITO_AUDIENCE_E_DECISIONI_BUDGET.md) | 12 ipotesi comportamentali di ad set, riallocazione budget ±20%, pacing, quote 90/10, confronto pre-evento vs arricchimento BF/CM |
| 4 | **Simulazione Sintetica (Personas T3, Decision 1 & Interviste)** | [04_AMBITO_PERSONAS_T3_DECISION1_E_INTERVISTE.md](04_AMBITO_PERSONAS_T3_DECISION1_E_INTERVISTE.md) | Architettura `simulation_blind`, 72 slot vs 4 schede effettive, 48 valutazioni `gemini-decision-1`, 4 interviste cieche (288 risposte), 4 test A/B |
| 5 | **Interfacce, Frontend, Governance & Stato Git** | [05_AMBITO_INTERFACCE_GOVERNANCE_E_REPO.md](05_AMBITO_INTERFACCE_GOVERNANCE_E_REPO.md) | Tutti i viewer HTML e il frontend React (`feat/adera-dashboard`), skill `.agents/skills/`, 5 file di test, `code-rot-cleaner`, stato Git |
| 6 | **Punti Plausibili per il Video 180s & Visualizzazione** | [06_PIANO_VIDEO_180S_E_VISUALIZZAZIONI.md](06_PIANO_VIDEO_180S_E_VISUALIZZAZIONI.md) | Storyboard scena per scena (0–180s) con soli numeri verificati e struttura tecnica per renderizzare/registrare i visual |

---

## Quadro Sintetico dello Stato Attuale del Progetto

1. **Esistono due rami principali di lavoro quantitativo non ancora fusi in un unico runtime su `main`:**
   - Su `main`, `python -m personas_simulation.runtime deliver --timestral-ref origin/feat/timestral-pilot` legge `Prima_Analisi/previsioni_28m.csv` (commit `2d8adf0`) e seleziona sul solo Fold 1 **`baseline_14d` per il CTR** e **`Timestral-28M` per il CPM** (`artifacts/wevion_v4/`).
   - Sul branch remoto `origin/feat/timestral-pilot`, esistono script successivi più completi (`Prima_Analisi/valida_modelli.py`, `prevedi_periodo_vuoto.py`, `arricchisci_black_friday.py`) che confrontano **Baseline + CatBoost + Timestral-28M + Mix 50/50**, identificano nel **Mix 50/50 CatBoost+Timestral-28M** il miglior modello CPM su entrambi i fold (`WMAE €0,6742` aggregato) e applicano un arricchimento Black Friday/Cyber Monday senza doppio conteggio stagionale (`CPM` mediana BF `€17,04`, `CTR` mediana BF `1,55%`).
   - Sul macOS locale esiste inoltre la replica verificata in `artifacts/timestral_reproduction/` (stessi SHA-256 dei pesi 5M/28M, conferma di tutte le metriche dei singoli modelli e diagnosi di copertura `q10–q90` per cold-start).
2. **Il binario qualitativo/sintetico (`Track B` — Personas T3 + Decision 1 + Interviste) è isolato e operativo in modalità pilota su `beauty_skincare`:**
   - `4` schede persona generate via T3/Antigravity (su `72` slot predisposti), `12` asset skincare valutati via `gemini-decision-1` (`48` valutazioni registrate in `ledger.sqlite`), `4` interviste cieche (`288` risposte aperte), `4` esperimenti A/B controllati proposti. `pet_ecommerce` e `abbigliamento` non sono ancora stati valutati da Decision 1.
3. **Le interfacce esistono ma sono frammentate su più entry point:**
   - `artifacts/wevion_v4/viewer.html` (consegna v4 standalone su `main`), `dashboard_unificata.html` (prototipo unificato Track A + Track B su `main`), `artifacts/personas_t3/` viewer vari, `artifacts/timestral_reproduction/results/confronto.html`, più l'app React/Vite su `origin/feat/adera-dashboard:frontend/` (non ancora collegata ai dati).
4. **Il video da 180 secondi non è ancora stato registrato**, ma la traccia (`docs/VIDEO_180S.md` e `BigHack2026_Wevion_Specifica_Operativa_v4.md` §11) e i dati esportati consentono di costruirlo in modo rigoroso.
