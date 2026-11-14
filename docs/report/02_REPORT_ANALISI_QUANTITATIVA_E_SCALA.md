# Report Analisi Quantitativa: Approcci Utilizzati, Dati Usati vs Esclusi e Alternative su Larga Scala

**Ambito:** Forecasting CTR/CPM (`699` righe `2026-11-16` → `2026-11-30`), validazione cronologica (`759` righe su 2 fold), calibrazione/incertezza e scenari Black Friday/Cyber Monday.  
**Fonti verificate nel repository:**
- `main`: [market_mirror/forecast.py](../../market_mirror/forecast.py), [market_mirror/delivery.py](../../market_mirror/delivery.py), [Wevion_Validation_Baseline.py](../../TEST%20INIZIALI%20FATTI%20DA%20CHAT%20GPT%20DA%20VERIFICARE%20/Wevion_Validation_Baseline.py), [TIMESTRAL_REPLICA_E_STATO_V4.md](../TIMESTRAL_REPLICA_E_STATO_V4.md), [method_comparison.csv](../../artifacts/timestral_reproduction/results/method_comparison.csv), [interval_diagnostics.csv](../../artifacts/timestral_reproduction/results/interval_diagnostics.csv).
- `origin/feat/timestral-pilot`: `Test_Timestral/timestral_pilot.py`, `Prima_Analisi/analisi.py`, `Prima_Analisi/valida_modelli.py`, `Prima_Analisi/prevedi_periodo_vuoto.py`, `Prima_Analisi/arricchisci_black_friday.py`, `Prima_Analisi/Validazione_Modelli/metriche.json`, `Prima_Analisi/Analisi_Completa_Black_Friday/riepilogo_analisi.json`.

---

## 1. Tutti gli Approcci Quantitativi Utilizzati nel Repository

Nel corso del progetto sono stati sviluppati, replicati e confrontati **6 approcci quantitativi principali** (più 2 varianti di analisi di sensibilità/scenario):

### Approccio 1 — Baseline Gerarchica Ponderata a 14 Giorni (`weighted_hierarchical_14d_v1`)
- **Dove si trova:** `baseline()` in [market_mirror/forecast.py](../../market_mirror/forecast.py), `heuristic()` in [Wevion_Validation_Baseline.py](../../TEST%20INIZIALI%20FATTI%20DA%20CHAT%20GPT%20DA%20VERIFICARE%20/Wevion_Validation_Baseline.py), `baseline()` in `Test_Timestral/timestral_pilot.py`.
- **Funzionamento:** usa gli ultimi 14 giorni prima del cutoff (`cutoff - 13gg → cutoff`). Calcola tassi aggregati sui conteggi (`CTR = 100 * sum(click) / sum(impression)`, `CPM = 1000 * sum(spesa) / sum(impression)`) lungo una cascata di fallback:
  $$\text{ad\_id} \rightarrow \text{asset\_id} \rightarrow \text{adset\_id} \rightarrow \text{vertical} \rightarrow \text{globale (tutto lo storico)}$$
- **Caratteristiche:** zero parametri da addestrare, deterministica (scarto 0 tra piattaforme), gestisce naturalmente i 12 annunci cold-start risalendo a `asset_id` o `adset_id`. **Limite:** predice un valore costante piatto per i 15 giorni futuri (nessuna dinamica temporale né shock Black Friday).

### Approccio 2 — CatBoost Regressor ad-level su `logit(CTR)` e `log(CPM)`
- **Dove si trova:** [Wevion_Validation_Baseline.py](../../TEST%20INIZIALI%20FATTI%20DA%20CHAT%20GPT%20DA%20VERIFICARE%20/Wevion_Validation_Baseline.py) (riprodotto in [artifacts/timestral_reproduction/](../../artifacts/timestral_reproduction/) e rieseguito in `origin/feat/timestral-pilot:Prima_Analisi/valida_modelli.py`).
- **Funzionamento:**
  - Due modelli `CatBoostRegressor` separati (`iterations=550`, `depth=5`, `learning_rate=0.045`, `l2_leaf_reg=8`, `loss_function='RMSE'`, `random_seed=17`).
  - **Trasformazione target:**
    - CTR: $\text{logit\_ctr} = \ln\left(\frac{\text{click} + 0.5}{\text{impression} - \text{click} + 0.5}\right)$ (Laplace smoothing per gestire le 9 righe a 0 click), decodificato con sigmoide $\times 100$.
    - CPM: $\ln(\text{cpm})$, decodificato con $\exp(\cdot)$.
  - **Feature (27 totali):**
    - 7 categoriche native (`ad_id`, `adset_id`, `asset_id`, `vertical`, `leva`, `formato`, `campaign_id`);
    - 12 di base calendario/età/mercato (`budget_giornaliero_adset`, `dow`, `days_from_start`, `days_to_bf`, `ad_age`, `asset_age`, `market_index_cpm`, `market_index_ctr`, `is_weekend`, `is_black_week`, `is_black_friday`, `is_cyber_monday`);
    - 8 feature storiche rolling a 7 giorni (`daily_ctr_l7` e `daily_cpm_l7` per `ad_id`, `adset_id`, `asset_id`, `vertical`), con `shift(1)` in training e congelate alle ultime 7 osservazioni prima del cutoff in validazione/test (missing riempiti con `-1.0`).
- **Limite:** su 1.879 righe tende a overfittare sul Fold 1 CTR (WMAE `0,3057 pp` vs `0,1977 pp` baseline) e non avendo osservato `black_friday=1` nello storico non estrapola il salto dell'evento (su `prevedi_periodo_vuoto.py` la mediana CPM CatBoost in Black Week è €10,23 vs €10,49 pre-BW).

### Approccio 3 — Mistral Timestral Zero-Shot (5M e 28M) a livello Ad Set + Adattatore Ad-Level
- **Dove si trova:** `Test_Timestral/timestral_pilot.py`, `Prima_Analisi/analisi.py`, replicato su macOS arm64 in [artifacts/timestral_reproduction/verify.py](../../artifacts/timestral_reproduction/verify.py).
- **Funzionamento:**
  - Invece di modellare 69 serie incomplete di singoli annunci, aggrega lo storico giornaliero nei **12 ad set** (serie continue senza buchi).
  - Passa a `TimestralForecaster` (`mistralai/Timestral-5M` e `mistralai/Timestral-28M`, CPU, zero fine-tuning):
    - `context`: tensore `(12, 2, T)` con `T ∈ {63, 77, 91}` (CTR e CPM giornalieri per ad set);
    - `known_covariates`: tensore `(12, 7, T + H)` con 7 covariate note sul passato e sul futuro (`budget_adset`, `market_ctr_2025 / 100`, `market_cpm_2025 / 100`, `weekend`, `black_week`, `black_friday`, `cyber_monday`);
    - estrae i quantili `p10`, `p50` (mediana), `p90` ad-set level (`(12, 2, H)`).
  - **Adattatore moltiplicativo ad-level:** riporta la curva temporale dell'ad set sui singoli annunci moltiplicando la baseline 14g dell'annuncio per il rapporto relativo previsto da Timestral sull'ad set, con clamp fisso di sicurezza `[0.25, 4.0]`:
    $$\widehat{y}_{\text{ad}, t}^{(q)} = \text{clip}\left(\text{baseline}_{14\text{g}}(\text{ad}) \times \text{clip}\left(\frac{\widehat{y}_{\text{adset}, t}^{(q)}}{\text{ref}_{14\text{g}}(\text{adset})},\; 0.25,\; 4.0\right)\right)$$
- **Limiti:** i flag `black_week`, `black_friday`, `cyber_monday` sono tutti `0` nel contesto storico (il modello non ha mai visto l'impulso nello storico); inoltre `market_cpm_2025 / 100` raggiunge `1,599` nel futuro oltre il massimo storico visto (`1,218`), richiedendo estrapolazione fuori range; i quantili trasformati non sono calibrati a livello annuncio.

### Approccio 4 — Selezione Separata su Fold 1 in `main` (`ctr_baseline14d__cpm_timestral28m`)
- **Dove si trova:** `from_timestral_ref()` in [market_mirror/forecast.py](../../market_mirror/forecast.py) e deliverable in [artifacts/wevion_v4/forecasts_2026-11-16_30.csv](../../artifacts/wevion_v4/forecasts_2026-11-16_30.csv).
- **Funzionamento:** legge l'export `previsioni_28m.csv` dal commit `2d8adf0`, applica una regola fissa di selezione per singolo target sulla WMAE del **primo fold (`2026-10-19 → 2026-11-01`)** tra `baseline` e `Timestral-28M` (escludendo CatBoost dal confronto). Risultato: **Baseline 14g per CTR** + **Timestral-28M per CPM**.

### Approccio 5 — Ensemble Mix 50/50 CatBoost + Timestral-28M (`origin/feat/timestral-pilot`)
- **Dove si trova:** `Prima_Analisi/valida_modelli.py` e `Prima_Analisi/prevedi_periodo_vuoto.py` su `origin/feat/timestral-pilot`.
- **Funzionamento:** combina in modo semplice (`0.5 * CatBoost + 0.5 * Timestral-28M`) le previsioni ad-level. In `prevedi_periodo_vuoto.py`, in base al confronto su 759 righe storiche, seleziona:
  - **`CTR`: `baseline_14g`** (scelto per maggiore stabilità tra Fold 1 e Fold 2 rispetto a CatBoost/Timestral, pur essendo a 0,0004 pp dal Mix 50/50 aggregato);
  - **`CPM`: `mix_50_50_catboost_timestral28m`** (miglior WMAE CPM in assoluto su Fold 1, Fold 2, aggregato e annunci nuovi).

### Approccio 6 — Arricchimento Stagionale Black Friday / Cyber Monday vs Scenari di Sensibilità
Nel repository coesistono **tre modalità distinte** di modellazione dello shock Black Friday:
1. **Arricchimento interno anti-doppio-conteggio (`Prima_Analisi/arricchisci_black_friday.py` su `origin/feat/timestral-pilot`):**
   - Usa esclusivamente `benchmark_mercato_settimanale_2025.csv` (`meta/IT`, allineato `-364` giorni) rispetto al riferimento ponderato `2–15 nov`.
   - **Rimozione doppio conteggio CPM:** poiché `cpm_scelto_eur` (Mix 50/50) include già una parte di stagionalità dalla covariata di Timestral, divide il fattore settimanale atteso per la variazione media già espressa dal modello (`cpm_scelto / cpm_baseline`), portando il livello settimanale esattamente a quello del benchmark 2025.
   - **Concentrazione intra-settimanale:** nella settimana `23–29 nov` assegna peso `2,2` al Black Friday (`27/11`) e `0,8` agli altri 6 giorni (media esatta `(6×0,8 + 2,2)/7 = 1,0`); sul Cyber Monday (`30/11`) applica peso `1,35` sull'incremento della Black Week per evitare il calo artificiale di dicembre.
   - **Effetto sui 15 giorni:** mediana CPM BF (`27/11`) passa da `€11,70` → **`€17,04`**; mediana CTR BF da `1,05%` → **`1,55%`**; mediana CPM CM (`30/11`) `€11,27` → **`€13,82`**; mediana CTR CM `1,05%` → **`1,36%`**.
2. **Scenari stagionali ex-ante (`seasonal_scenarios()` in `market_mirror/forecast.py`):**
   - Applicati sopra la `baseline_14d` con esponenti assunti ex-ante `strength ∈ {0.5 (conservative), 1.0 (central), 1.5 (high_pressure)}` sul rapporto tra indice 2025 futuro e indice 2025 degli ultimi 14 giorni. Mantenuti in file separato (`seasonal_scenarios.csv`) come analisi di sensibilità.
3. **Scenari esterni da letteratura (`Prima_Analisi/analisi.py` + `scenari_cpm.csv` / `Fonti.md`):**
   - Moltiplicatori Biddyco (`1,35×` BW, `1,57×` BF, `1,41×` CM) e Olifant (`2,12×` BF) applicati al CPM di ottobre per vertical. **Correttamente esclusi da `predict()`** perché provengono da account reali USA/EU non comparabili direttamente al dataset simulato.

---

## 2. Confronto Quantitativo Completo dei Modelli

### 2.1 Accuratezza su Fold 1, Fold 2 e Aggregato (759 righe, target ricalcolati dai conteggi)

| Finestra | Modello | MAE CTR (pp) | WMAE CTR (pp) | MAE CPM (€) | WMAE CPM (€) | Fonte |
|---|---|---:|---:|---:|---:|---|
| **Fold 1** (`19/10–01/11`, 315 righe, 63 cold-start) | Baseline 14g | 0,2451 | **0,1977** | 0,7986 | 0,7143 | `method_comparison.csv` / `metriche.json` |
| | Timestral-5M (adj) | 0,2727 | 0,2235 | 0,7705 | 0,7013 | `method_comparison.csv` |
| | Timestral-28M (adj) | **0,2420** | 0,2020 | 0,7649 | 0,6927 | `method_comparison.csv` |
| | CatBoost | 0,3536 | 0,3057 | 0,7122 | 0,6862 | `method_comparison.csv` |
| | **Mix 50/50 (CB + T28M)** | 0,2507 | 0,2146 | **0,6975** | **0,6653** | `Validazione_Modelli/metriche.json` |
| **Fold 2** (`02/11–15/11`, 444 righe, 66 cold-start) | Baseline 14g | 0,3163 | 0,2576 | 1,0218 | 0,8022 | `method_comparison.csv` |
| | Timestral-5M (adj) | 0,3585 | 0,2859 | 0,9673 | 0,7573 | `method_comparison.csv` |
| | Timestral-28M (adj) | 0,3446 | 0,2815 | 0,8841 | 0,7067 | `method_comparison.csv` |
| | CatBoost | **0,2743** | **0,2103** | 0,9274 | 0,7161 | `method_comparison.csv` |
| | **Mix 50/50 (CB + T28M)** | 0,3023 | 0,2378 | **0,8741** | **0,6841** | `Validazione_Modelli/metriche.json` |
| **Aggregato (Fold 1 + 2, 759 righe)** | Baseline 14g | 0,2868 | 0,2260 | 0,9292 | 0,7559 | `Validazione_Modelli/metriche.json` |
| | CatBoost | 0,3072 | 0,2606 | 0,8381 | 0,7004 | `Validazione_Modelli/metriche.json` |
| | Timestral-28M (adj) | 0,3020 | 0,2396 | 0,8346 | 0,6993 | `Validazione_Modelli/metriche.json` |
| | **Mix 50/50 (CB + T28M)** | **0,2809** | **0,2256** | **0,8008** | **0,6742** | `Validazione_Modelli/metriche.json` |

### 2.2 Cold-Start (`annunci_nuovi`) e Livello Ad Set

- **Cold-start Fold 1 (63 righe, 9 nuovi annunci):**
  - CTR WMAE: Baseline `0,2969 pp` (migliore) vs Timestral-28M `0,3352 pp` vs Mix 50/50 `0,3792 pp` vs CatBoost `0,4653 pp`.
  - CPM WMAE: **Mix 50/50 `€0,7721`** (migliore) vs CatBoost `€0,7778` vs Timestral-28M `€0,8827` vs Baseline `€0,9011`.
- **Cold-start Fold 2 (66 righe):**
  - CTR WMAE: **CatBoost `0,3743 pp`** (migliore) vs Mix 50/50 `0,3992 pp` vs Baseline `0,4073 pp` vs Timestral-28M `0,4280 pp`.
  - CPM WMAE: **Mix 50/50 `€1,0303`** (migliore) vs Timestral-28M `€1,0431` vs CatBoost `€1,0746` vs Baseline `€1,2349`.
- **Livello Ad Set aggregato (168 righe per fold, `Prima_Analisi/analisi.py`):**
  - Fold 1 WMAE: CTR `0,1574` (Base) → `0,1781 pp` (28M); CPM `0,6625` (Base) → **`0,6349 €`** (28M).
  - Fold 2 WMAE: CTR `0,1836` (Base) → `0,2047 pp` (28M); CPM `0,7479` (Base) → **`0,6045 €`** (28M, `-19,2%`).

### 2.3 Diagnostica Intervalli `q10–q90` (Copertura nominale attesa: 80%)

Da [interval_diagnostics.csv](../../artifacts/timestral_reproduction/results/interval_diagnostics.csv) (quantili esplorativi **non calibrati**):
- **Timestral-28M globale:** copertura CPM `82,54%` (Fold 1, ampiezza media `€3,01`) e `83,11%` (Fold 2, ampiezza `€3,12`); copertura CTR `86,98%` (Fold 1) e `69,59%` (Fold 2).
- **Timestral-28M cold-start (annunci nuovi):** copertura scende nettamente sotto l'80%: **`66,67%`** (Fold 1 CPM) e **`69,70%`** (Fold 2 CPM); sul CTR scende al **`56,06%`** nel Fold 2. Timestral-5M degrada ancora di più (`40,91%` CPM e `45,45%` CTR cold-start nel Fold 2).
- **Conclusione:** gli intervalli attuali sono esplorativi e **non vanno spacciati per intervalli calibrati** (specialmente sugli annunci nuovi o sul Black Friday).

---

## 3. Dati Usati per la Predizione vs Dati Esclusi (Analisi Colonna per Colonna)

| File del Kit | Campi **USATI** nella predizione | Come sono usati | Campi **ESCLUSI** dalla predizione | Perché sono esclusi / dove vanno invece |
|---|---|---|---|---|
| `storico_giornaliero.csv` | `data`, `ad_id`, `adset_id`, `asset_id`, `vertical`, `campaign_id`, `leva`, `formato`, `budget_giornaliero_adset`, `click`, `impression`, `spesa` | Target ricalcolati (`CTR`, `CPM`), lag rolling `l7` strict-past in CatBoost, aggregati ad-set per Timestral, baseline 14g, pesi `WMAE` e quote 90/10 | **`copertura`**, **`frequenza`**, **`cpc`**, **`ctr`**, **`cpm`**, **`inserzionista_id`**, **`campaign_name`**, **`piattaforma`**, **`giorno_settimana`** | `ctr`/`cpm` precalcolati sostituiti dal calcolo esatto sui conteggi; `cpc` derivabile a valle; `copertura` e `frequenza` **non usate come feature** in nessuno dei modelli (usate solo in `analytics.evidence` per descrivere il pubblico); `piattaforma` costante (`meta`) |
| `da_prevedere.csv` | Tutte le chiavi (`data`, `ad_id`, `adset_id`, `asset_id`, `vertical`, `campaign_id`, `leva`, `formato`, `budget_giornaliero_adset`) | Griglia esatta delle 699 previsioni e covariate note | `giorno_settimana` (ricalcolato da `data`), `piattaforma` (costante) | Nessun outcome presente (verificato: `future_outcomes_present=[]`) |
| `budget_giornaliero.csv` | `data`, `adset_id`, `budget_giornaliero_eur` | Covariata continua `(12, 1, 106)` in Timestral, feature CatBoost e vincoli del motore budget | `periodo` (`storico` / `da_prevedere`) | Escluso esplicitamente per evitare leakage tra train/validazione/test |
| `benchmark_mercato_settimanale_2025.csv` | `settimana_dal`, `vertical`, `indice_cpm`, `indice_ctr` (filtrato `piattaforma=meta`, `paese=IT`) | Allineati `-364` giorni: 2 covariate in Timestral/CatBoost, `seasonal_scenarios` e curva 2025 in `arricchisci_black_friday.py` | Altre righe se presenti (nessuna extra oltre `meta/IT` in questo file) | Solo serie italiana Meta rilevante |
| `calendario.csv` | Date chiave: weekend, `20–30/11` Black Week, `27/11` Black Friday, `30/11` Cyber Monday | 4 flag binari + `dow`, `days_from_start`, `days_to_bf` | Eventi pre-cutoff (`Rientro dalle ferie` 01/09, `Halloween` 31/10, `Ognissanti` 01/11, `Singles Day` 11/11), `periodo` | Ignorati dai modelli quantitativi attuali; `Singles Day` e `Halloween` potrebbero essere testati come segnali di promo minori |
| `asset_creativi/asset_*.csv` | Solo **`data_lancio`** (per `asset_age` in CatBoost) | Età dell'asset al giorno `t` | **`headline`**, **`testo_principale`**, **`call_to_action`**, **`descrizione_visual`**, **`durata_video_s`**, **`data_fine`** | Esclusi dalle feature di tutti i modelli quantitativi per evitare overfitting su soli 36 asset; usati invece nel catalogo testuale di `Personas T3 / Decision 1` |
| `annunci.csv` | Solo **`data_lancio`** (per `ad_age` in CatBoost) | Età dell'annuncio al giorno `t` | `ad_name`, `data_fine` | Ridondanti o assenti nel calcolo rolling |
| `adset.csv` | Solo `adset_id`, `campaign_id` (via mapping) | Gerarchia 12 ad set | **`ottimizzazione`**, **`strategia_offerta`**, **`budget_giornaliero_iniziale`**, **`adset_name`**, **`pubblico`** | `ottimizzazione` (`acquisti`) e `strategia_offerta` (`costo più basso`) sono **identiche su tutti i 12 ad set** (varianza zero); `pubblico` è da definire |
| `cpm_storici.csv` (704 righe) | **NESSUNA colonna usata nei modelli predittivi** | — | Tutto il file (`meta`/`tiktok`, `IT/DE/FR/ES`, 4 obiettivi, `2025-01 → 2026-10`, quartili) | Usato **solo come sanity check macro** (`+34,8%` ott→nov 2025 per `meta/IT/vendite`) nella documentazione, non in `fit()`/`predict()` |
| `inserzionisti.csv` & `campagne.csv` | Solo mapping `campaign_id → vertical` | Raggruppamento gerarchico | `nome`, `descrizione`, `obiettivo`, `data_inizio` | Usati solo in `prepare_safe_inputs.py` per dare contesto cieco alle Personas |
| Segnali `gemini-decision-1` | **NESSUNA colonna usata nei modelli predittivi** | — | `attention_signal`, `click_intent_signal`, `reason_distribution` | `calibrated_to_ctr: False`; solo affiancati post-predizione in `handoff.py` |

> **Nota critica sui dati esclusi ma potenzialmente utili:** `frequenza` (e saturazione della frequenza cumulativa su finestra mobile 7/14 giorni) e `durata_video_s` / feature testuali controllate (es. presenza di sconto `%` numerico nell'headline, numero parole) sono le principali informazioni presenti nel kit ma non ancora sfruttate da CatBoost. Inoltre `copertura` / `frequenza` consentirebbero di scomporre il decadimento dell'attenzione per saturazione del pubblico (ad fatigue).

---

## 4. Alternative per una Distribuzione su Larga Scala

Portare questa pipeline da un kit hackathon (3 clienti, 12 ad set, 69 annunci, 91 giorni) a una piattaforma **Wevion multi-tenant in produzione** (centinaia di inserzionisti, migliaia di ad set, decine di migliaia di creatività attive e storico eterogeneo con serie brevi/sparse) mette in luce precisi colli di bottiglia negli approcci attuali e richiede alternative ingegneristiche e modellistiche dedicate.

### 4.1 Limiti degli approcci attuali su larga scala
1. **Baseline 14g:** non cattura interazioni (es. *video + scarcity nel weekend*), non trasferisce conoscenza cross-inserzionista e non modella stagionalità o saturazione di budget.
2. **CatBoost attuale (`Wevion_Validation_Baseline.py`):** addestramento monolitico in memoria (`pandas`), target encoding non out-of-fold, loss `RMSE` su logit non pesata per varianza binomiale (un annuncio con 50 impression pesa quanto uno con 50.000), nessuna feature testuale/visiva per nuovi asset.
3. **Timestral zero-shot (`(B, 2, T)`):** richiede serie temporali dense a livello ad set; con migliaia di ad set spesso intermittenti o appena lanciati (poche osservazioni `<14gg`), il tensore diventa sparso; inoltre il fattore moltiplicativo ad-level è lineare e non cattura effetti incrociati tra creatività e picco d'asta.
4. **Incertezza (`q10–q90`):** non calibrata, fallisce sul cold-start (`41%–70%` di copertura invece dell'80%).
5. **Personas / Decision 1:** costo e latenza $O(N_{\text{persone}} \times N_{\text{asset}})$; impossibile rieseguire LLM su decine di migliaia di annunci ogni giorno.

### 4.2 Architettura & Modelli Alternativi Raccomandati per la Larga Scala

| Dimensione | Approccio Hackathon Attuale | Alternativa Scalabile in Produzione | Perché scala meglio |
|---|---|---|---|
| **Data & Feature Store** | CSV letti in `pandas` / Python puro (`analytics.py`) | **DuckDB / Polars / BigQuery + dbt** con materializzazione di rolling lag incremental-only e controlli automatici di schema/leakage | Elabora milioni di righe `(data, ad_id)` in secondi con memory-footprint costante |
| **Modello Tabulare Principale (Ad-level + Cold Start)** | CatBoost `RMSE` su `logit(CTR)` non pesato | **LightGBM / CatBoost con `sample_weight = impression` + obiettivo Binomiale/Poisson (o GLM-GBDT ibrido) + Empirical Bayes Shrinkage** | Modella correttamente l'eteroschedasticità del CTR (pochi click vs grandi volumi) ed evita overfitting su micro-annunci |
| **Cold Start Gerarchico & Incertezza Nativa** | Fallback deterministico `ad→asset→adset→vertical` | **Modelli Gerarchici Bayesiani (PyMC / NumPyro / INLA) o GLMM** su `(paese × piattaforma × obiettivo × vertical × adset × asset)` | Sfrutta davvero `cpm_storici.csv` su 4 paesi e 2 piattaforme come prior informativi; produce **intervalli di credibilità nativamente più ampi** sul cold-start |
| **Serie Temporali & TSFM** | Timestral-28M zero-shot ad set + media 50/50 fissa | **Residual Forecasting / Stacking Dinamico:** TSFM (**Timestral-28M/123M fine-tuned**, **Chronos-2** o **TimesFM**) a livello `cluster/vertical/paese` per il macro-regime + **GBDT sui residui ad-level** con meta-learner per i pesi | Supera il limite delle serie corte dei nuovi ad set; evita lo shock "mai visto nel contesto" tramite pre-training/fine-tuning su storici pluriennali multi-cliente |
| **Feature Creative su Migliaia di Asset** | Solo `leva`, `formato`, `asset_age` | **Multimodalità compressa:** estrazione offline una-tantum di embedding testuali + visivi (**SigLIP / CLIP + text embedding**) ridotti con **PCA/SVD a 8–16 componenti** + feature strutturate (presenza `%` sconto, durata, hook nei primi 3s) | Generalizza su creatività inedite quando `leva` e `formato` non bastano più a distinguere la qualità esecutiva |
| **Calibrazione Incertezza (`q10–q90`)** | Quantili grezzi Timestral non calibrati | **Conformalized Quantile Regression (CQR)** o **Adaptive Conformal Inference (ACI / EnbPI)** stratificata per `seen` vs `cold_start` | Garanzia matematica di copertura finita (es. `≥80%`) separatamente per annunci noti e nuovi |
| **Motore Budget su Larga Scala** | Riallocazione lineare greedy ±20% (assume rendimento costante al variare del budget) | **Curve di saturazione (Hill / Log-response) stimate via MMM o esperimenti incrementali + Ottimizzazione Convessa (`cvxpy` / `scipy.optimize`)** o **Contextual Bandits / Thompson Sampling** | Risolve il limite fondamentale dell'approccio attuale: raddoppiare il budget su un ad set piccolo fa salire frequenza e CPM (diminishing returns) |
| **Simulazione Sintetica (Personas / Decision 1)** | 4–72 personas fisse interpellabili via API | **Archetipi ponderati + Distillation Surrogate Model:** eseguire Decision 1 solo su $K$ archetipi rappresentativi e nuovi asset candidati (pre-lancio), distillando un classificatore leggero (es. DeBERTa/embedding head) per lo scoring massivo | Riduce di 100× le chiamate API mantenendo il layer diagnostico *"perché non cliccano"* sui vincitori/perdenti |

### 4.3 Piano Pratico di Evoluzione in 3 Fasi
1. **Immediato (Chiusura Hackathon / V4.1):** unire su `main` la pipeline di `origin/feat/timestral-pilot` (`Mix 50/50 CatBoost+Timestral-28M` per CPM, `Baseline 14g` per CTR, arricchimento BF/CM anti-doppio-conteggio), aggiungere `frequenza` rolling 7g e feature testuali minime in CatBoost, e calibrare i quantili sui residui di Fold 1 (`Split Conformal`).
2. **Breve Termine (Pilota Multi-Cliente, 10–50 inserzionisti):** sostituire i CSV con DuckDB, introdurre **prior bayesiani da `cpm_storici.csv`** (paese/piattaforma/obiettivo), `sample_weight=impression`, stacking out-of-fold al posto della media fissa 50/50 e Conformal Prediction stratificata cold-start.
3. **Larga Scala (Piattaforma SaaS Wevion):** architettura **TSFM macro-regime + GBDT residuo con embedding creativi PCA + CQR**, ottimizzatore di budget non-lineare con curve di saturazione/frequenza e Decision 1 usato esclusivamente in **pre-flight creativo** (A/B test sintetico pre-spesa) con caching per hash e distillazione.
