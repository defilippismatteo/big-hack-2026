# Ambito 5 — Interfacce, Frontend, Governance, Testing & Stato Git

---

## 1. Mappa delle Interfacce e dei Viewer Esistenti

Nel repository convivono **6 visualizzazioni HTML standalone** più **1 app React/Vite** su branch separato:

| Artefatto / Percorso | Branch | Funzione | Stato & Dati Collegati |
|---|---|---|---|
| [artifacts/wevion_v4/viewer.html](../../artifacts/wevion_v4/viewer.html) | `main` (generato da `market_mirror/viewer.py`) | **Viewer ufficiale consegna v4:** 4 tab (*Decisioni*, *Previsioni*, *Pubblici*, *Validazione e limiti*), grafici CTR/CPM, download CSV | Collegato a tutti i file reali generati da `deliver` (`699` forecast, `12` audience, `180` decisioni). Nessun server richiesto. |
| [dashboard_unificata.html](../../dashboard_unificata.html) | `main` (untracked) | **Dashboard unificata Track A + Track B:** matrice Information Boundary, schede delle 4 personas, confronto Fold 1/2, 12 ad set unificati, ranking `NDL-*` vs forecast, 4 A/B proposti | Dati incorporati da `wevion_v4` + `personas_t3`. Origine non generata automaticamente da `deliver`. |
| [artifacts/personas_t3/viewer.html](../../artifacts/personas_t3/viewer.html) | `main` | Schede persona T3 e feed simulato | Collegato a `persona_cards.json` (4 schede reali Beauty). |
| [artifacts/personas_t3/analyses/results.html](../../artifacts/personas_t3/analyses/results.html) & `diagnostic-patterns.html` & `interviews/preferences.html` | `main` | Analisi Decision 1, pattern motivi e preferenze interviste | Collegati a `analyses/` e `interviews/` (`beauty_skincare`). |
| [artifacts/timestral_reproduction/results/confronto.html](../../artifacts/timestral_reproduction/results/confronto.html) | `main` (locale) | Grafici MAE/WMAE di Baseline, Timestral-5M, Timestral-28M e CatBoost | Collegato a `method_comparison.csv`. |
| [artifacts/wevion_v4/periodo_vuoto_chart.html](../../artifacts/wevion_v4/periodo_vuoto_chart.html) & `periodo_vuoto_plotly.html` | `main` (locale) | Confronto serie 2025 vs 2026 + blocco vuoto 16–30 nov | Grafici esplorativi del periodo vuoto. |
| [artifacts/personas_t3/load-estimate.html](../../artifacts/personas_t3/load-estimate.html) | `main` (locale) | Calcolatore interattivo di carico chiamate/valutazioni per scaling personas | Tool di dimensionamento (es. `5` fasce × `2` sessi × `N` × `3` settori). |
| `frontend/` (`React + Vite + Lucide`) | `origin/feat/adera-dashboard` | Shell UI multi-sezione (*Overview, Audience Lab, Creative Explorer, Forecast Analytics, Budget Planner, Model Validation*) | **Solo struttura UI:** non ancora popolata con i dati reali di `deliver`. |

---

## 2. Skill Canoniche (`.agents/skills/`), Runtime e Test

- **11 skill canoniche** in `.agents/skills/`: `audit-marketmirror`, `wevion-persona-diversity`, `wevion-persona-writer`, `wevion-decision1`, `wevion-persona-signals`, `wevion-evidence`, `wevion-audience-inference`, `wevion-signal-validation`, `wevion-persona-explain`, `wevion-delivery` (più le skill globali di workspace).
- **Dipendenza dinamica da preservare:** `market_mirror/starter.py` e `Dockerfile.market-mirror` importano per percorso 4 script da `Wevion_Personas_Architettura_v1/scripts/` (`prepare_safe_inputs`, `build_creative_catalog`, `make_slots`, `decision1_requests`).
- **Suite di test (`567` righe su 5 file in `tests/`):**
  - [test_market_mirror.py](../../tests/test_market_mirror.py) (190 righe)
  - [test_decision_runs.py](../../tests/test_decision_runs.py) (133 righe)
  - [test_delivery.py](../../tests/test_delivery.py) (107 righe)
  - [test_t3_personas.py](../../tests/test_t3_personas.py) (83 righe)
  - [test_interviews.py](../../tests/test_interviews.py) (54 righe)
  - Documentazione recente attesta **43 test superati** dopo il riordino documentale.

---

## 3. Riordino Documentale (`code-rot-cleaner`) e Stato Git

- **Riordino eseguito (`outputs/code-rot-cleaner/`):** `13` file storici (`Specifica_Operativa_v3.md`, `Wevion_Personas_Architettura_v1.zip`, `Wevion_Personas_Skill_Starter/`) spostati sotto `archive/` senza cancellazioni (`applicazione_riordino.json`). Unico candidato statico `CRT-001` (`Wevion_Validation_Baseline.py`) marcato **KEEP** perché importato dalla replica Timestral.
- **Situazione critica Git & Persistenza:**
  - La cartella `artifacts/` (~`872 MiB`, inclusi `wevion_v4/`, `personas_t3/analyses/ledger.sqlite`, `interviews/`, `timestral_reproduction/`) è **ignorata da `.gitignore`**. Un semplice `git commit && git push` non salva né le prove né i modelli/registri.
  - Sul working tree di `main` sono presenti modifiche non committate (`decision_runs.py`, `__main__.py`, `interviews.py`, `docs/`, `archive/`, `outputs/`, `dashboard_unificata.html`).
  - I due rami remoti `origin/feat/timestral-pilot` (con l'arricchimento Black Friday e la validazione CatBoost+Mix 50/50) e `origin/feat/adera-dashboard` (con il frontend React) non sono ancora stati integrati su `main`.
