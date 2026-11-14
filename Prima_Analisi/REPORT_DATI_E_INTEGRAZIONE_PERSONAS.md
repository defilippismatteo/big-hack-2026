# Report sui Dati e Piano di Integrazione con il Pubblico Sintetico

Questo documento verifica la solidità tecnica delle stime sul periodo **16–30 novembre 2026**, riassume i risultati ottenuti **usando al 100% i dati interni del kit degli organizzatori** e definisce il piano operativo per unire i numeri del modello quantitativo con l'analisi del pubblico sintetico (`market_mirror` / Personas T3).

---

## 1. Verifica di sensatezza dell'analisi (Cosa abbiamo controllato e corretto)

L'audit della prima versione dell'arricchimento (`commit 07f99ad`) ha individuato **tre distorsioni metodologiche** che sono state corrette in [`arricchisci_black_friday.py`](arricchisci_black_friday.py):

1. **Rimozione del doppio conteggio stagionale sul CPM:**
   - La previsione scelta per il CPM (`cpm_scelto_eur`) è la media 50/50 tra **CatBoost** e **Timestral-28M**. Poiché Timestral-28M riceve già `indice_cpm` del 2025 come covariata nota, `cpm_scelto_eur` incorporava già una crescita media tra `+7%` e `+19%` rispetto alla baseline a 14 giorni.
   - Moltiplicando `cpm_scelto_eur` direttamente per `fattore_settimanale_cpm`, l'effetto veniva contato due volte (portando il 16 novembre a €12,87 e il Black Friday a €20,22).
   - **Correzione applicata:** per ogni `(vertical, settimana)`, calcoliamo la crescita già espressa dal modello (`modello_cpm_vs_base = media(cpm_scelto_eur / cpm_baseline)`) e applichiamo soltanto il **fattore residuo** (`fattore_settimanale_cpm / modello_cpm_vs_base`). Così la media settimanale corrisponde esattamente al livello 2025 del kit rispetto al riferimento `2–15 nov`, mantenendo però il ranking relativo tra annunci stimato da CatBoost + Timestral-28M.
2. **Correzione dell'anomalia di calendario sul Cyber Monday (`30/11`):**
   - Il `2026-11-30` cade di lunedì ed era abbinato alla settimana `2025-12-01` (`1–7 dic 2025`), il cui indice medio scende perché dal 2 al 7 dicembre la promozione è finita. Di conseguenza il Cyber Monday risultava meno caro e meno cliccato di sabato 28 e domenica 29 novembre.
   - **Correzione applicata:** mantenendo la conservazione esatta della media sui 7 giorni della settimana Black Friday (`23–29 nov`, con peso `2,2` il `27/11` e `0,8` gli altri 6 giorni, media `(6 × 0,8 + 2,2) / 7 = 1,0`), sul **Cyber Monday (`30/11`)** si applica un peso di picco `1,35` all'incremento della Black Week (`calendario.csv` chiude la Black Week proprio il 30/11).
3. **Quote di spesa realistiche (90/10) e KPI ponderati per ad set:**
   - Al posto della divisione in parti uguali (`1 / n_attivi`), il budget giornaliero di ciascun ad set viene distribuito con la stessa regola di `market_mirror/marketing.py`: **90%** proporzionale alla spesa storica degli ultimi 14 giorni (`2–15 nov`) e **10%** diviso in parti uguali per dare spazio esplorativo ai **12 annunci nuovi** (`nuovo_annuncio = True`).
   - Le medie di CPM, CTR e CPC per ad set in [`decisioni_adset_budget.csv`](Analisi_Completa_Black_Friday/decisioni_adset_budget.csv) sono calcolate come **medie ponderate su budget e impression**.

---

## 2. Report dei dati e delle previsioni (16–30 novembre 2026)

### 2.1 Solidità dei modelli scelti (Validazione su 759 righe storiche)
Nel confronto cronologico anti-leakage su due finestre (`19 ott – 1 nov` e `2–15 nov`, 759 righe totali) in [`Validazione_Modelli`](Validazione_Modelli/README.md):
- **CPM (€/1.000 impression):** vince la **Media 50/50 (CatBoost + Timestral-28M)** con WMAE aggregato **€0,6742** (**-10,8%** rispetto alla baseline €0,7559; **-3,6%** rispetto a Timestral-28M €0,6993; CatBoost €0,7004).
- **CTR (% clic):** si mantiene la **Baseline gerarchica a 14 giorni** (WMAE **0,2260 pp**, sostanzialmente alla pari con la media 50/50 a 0,2256 pp e più stabile tra i due fold rispetto a CatBoost 0,2606 pp e Timestral-28M 0,2396 pp).

### 2.2 Perché l'arricchimento interno del kit è affidabile (senza trend esterni)
- Confrontando lo storico 2026 (`17/08–15/11`) con `benchmark_mercato_settimanale_2025.csv` (Meta IT), la correlazione settimanale sul **CPM** è altissima in tutti e tre i settori: **`beauty_skincare` = 0,939**, **`pet_ecommerce` = 0,934**, **`abbigliamento` = 0,877**.
- `cpm_storici.csv` (`meta`, `IT`, `vendite`) conferma un salto mensile mediano tra ottobre e novembre 2025 da **€7,01** a **€9,45** (**+34,8%**).
- Nella settimana del Black Friday (`2025-11-24` nel kit, contro riferimento ponderato `2–15 nov` rispettivamente CPM/CTR `113,91`/`108,49` abbigliamento, `117,64`/`101,24` beauty, `114,37`/`101,44` pet):
  - **Abbigliamento:** indice CPM sale a **159,9**, indice CTR a **135,1**.
  - **Beauty & Skincare:** indice CPM sale a **156,6**, indice CTR a **123,7**.
  - **Pet E-commerce:** indice CPM sale a **156,2**, indice CTR a **115,8**.

### 2.3 Andamento giornaliero verificato nei giorni chiave

| Data | Annunci attivi | CTR base | CTR arricchito | CPM base (€) | CPM settimanale (€) | CPM arricchito (€) | CPC arricchito (€) | Click stimati (base → arr.) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **2026-11-16** (Pre-Black Week) | 39 | 1,0082% | 1,0547% | €11,1188 | €11,1425 | €11,1425 | €0,9424 | 1.309 → 1.287 |
| **2026-11-20** (Inizio Black Week) | 45 | 1,0082% | 1,0547% | €10,7801 | €10,8031 | €10,8031 | €0,9159 | 1.324 → 1.301 |
| **2026-11-27** (**Black Friday**) | 51 | 1,0503% | **1,5522%** | €11,6954 | €13,1223 | **€17,0401** | **€1,0638** | 1.285 → 1.172 |
| **2026-11-28** (Sabato post-BF) | 51 | 1,0503% | 1,2253% | €10,8839 | €12,3701 | €11,7185 | €0,9233 | 1.313 → 1.341 |
| **2026-11-29** (Domenica post-BF) | 51 | 1,0503% | 1,2253% | €10,7274 | €12,1751 | €11,5692 | €0,8978 | 1.314 → 1.342 |
| **2026-11-30** (**Cyber Monday**) | 51 | 1,0503% | **1,3635%** | €11,2717 | €11,3696 | **€13,8207** | **€0,9867** | 1.267 → 1.235 |

Su tutti i **15 giorni** con budget totale invariato di **€16.950,00** (€1.130/giorno):
- Le **impression** scendono da **1.660.642** a **1.468.220** (**-11,6%**) a causa del rincaro delle aste.
- I **click** restano quasi invariati (**19.439 → 19.296**, **-0,7%**), perché la crescita del CTR in Black Week compensa gran parte dell'aumento del CPM; il **CPC medio** complessivo passa da **€0,8720** a **€0,8784**.

### 2.4 Classifica dei 12 Ad Set e dove conviene mettere il budget

| Settore | Ad Set | Budget 15gg (€) | CPM medio arr. (€) | CTR medio arr. | **CPC arr. (€/click)** | Var. Impression | Var. Click |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `abbigliamento` | **`FGR-AS4`** | €1.875 | €15,88 | 2,85% | **€0,5579** | -16,9% | -5,0% |
| `abbigliamento` | `FGR-AS1` | €2.400 | €8,80 | 1,08% | €0,8120 | -16,9% | -5,0% |
| `abbigliamento` | `FGR-AS2` | €900 | €10,95 | 1,24% | €0,8861 | -16,9% | -5,0% |
| `abbigliamento` | `FGR-AS3` | €600 | €16,02 | 1,19% | €1,3417 | -16,9% | -5,0% |
| `beauty_skincare` | **`NDL-AS2`** | €1.200 | €12,14 | 1,24% | **€0,9813** | -5,7% | **+8,3%** |
| `beauty_skincare` | **`NDL-AS4`** | €1.650 | €22,98 | 2,26% | **€1,0150** | -5,9% | **+8,3%** |
| `beauty_skincare` | `NDL-AS3` | €1.650 | €13,34 | 1,23% | €1,0867 | -5,9% | **+8,3%** |
| `beauty_skincare` | `NDL-AS1` | €2.250 | €10,74 | 0,85% | €1,2608 | -5,8% | **+8,3%** |
| `pet_ecommerce` | **`CDF-AS4`** | €900 | €14,75 | 2,39% | **€0,6180** | -11,3% | -3,7% |
| `pet_ecommerce` | `CDF-AS2` | €750 | €9,00 | 1,19% | €0,7569 | -11,3% | -3,7% |
| `pet_ecommerce` | `CDF-AS1` | €2.025 | €8,61 | 0,94% | €0,9164 | -11,2% | -3,7% |
| `pet_ecommerce` | `CDF-AS3` | €750 | €10,08 | 0,95% | €1,0586 | -11,2% | -3,7% |

**Indicazioni operative sul budget:**
- **Abbigliamento:** spostare quota di budget da `FGR-AS3` (€1,34/click) verso **`FGR-AS4`** (€0,56/click, quasi 2,4× più conveniente).
- **Beauty & Skincare:** è l'unico settore in cui la crescita CTR supera il rincaro residuo del CPM (**+8,3% click stimati** nella finestra). Ridurre la quota su `NDL-AS1` (€2.250 a €1,26/click) a favore di **`NDL-AS2`** (€0,98/click) e **`NDL-AS4`** (€1,02/click).
- **Pet E-commerce:** premiare **`CDF-AS4`** (€0,62/click) e **`CDF-AS2`** (€0,76/click) rispetto a `CDF-AS1` (€2.025 a €0,92/click) e `CDF-AS3` (€1,06/click).

---

## 3. Analisi dei segnali già ottenuti sul Pubblico Sintetico

### 3.1 I 12 profili comportamentali di Ad Set (`persona_adset.json`)
Dall'evidenza storica in `market_mirror/analytics.py`, in tutti e tre i settori emerge una struttura coerente:
- **`AS4` (`CDF-AS4`, `FGR-AS4`, `NDL-AS4`):** CTR storico più alto (**1,89%–2,39%**), CPM più alto (**€9,95–€13,42**), leva dominante **`black_friday`** e formato **`video`** — compatibile con pubblico caldo ad alta intenzione (retargeting / acquirenti recenti).
- **`AS1` (`CDF-AS1`, `FGR-AS1`, `NDL-AS1`):** CPM più basso (**€5,22–€7,63**) e CTR più basso (**0,89%–1,13%**) — compatibile con traffico freddo / prospecting ampio che assorbe oggi la quota maggiore di budget.
- **`AS2` e `AS3`:** fascia intermedia con sensibilità mista a **`scarcity`** e **`black_friday`**.

### 3.2 Valutazione delle prime 11 creatività Beauty con Personas T3 (`gemini-decision-1`)
Nel workspace `main` (`artifacts/personas_t3/analyses/assets/*/signals.json`), 4 personas sintetiche (`beauty_skincare-P001..P004`) hanno già valutato in feed simulato tutti gli **11 asset Beauty**:

| Asset | Leva | Attenzione (`attention_signal`) | Intenzione clic (`click_intent_signal`) | Prime 2 motivazioni (`reason_distribution`) |
| --- | --- | ---: | ---: | --- |
| **`NDL-S3`** | `scarcity` | **0,6974** | **0,1392** | `irrelevant` (15,0%), `interested` (12,4%) |
| `NDL-S4` | `scarcity` | 0,6618 | 0,1363 | `skeptical` (15,0%), `weak_offer` (12,7%) |
| `NDL-S2` | `scarcity` | 0,5775 | 0,1277 | `irrelevant` (20,9%), `skeptical` (14,5%) |
| **`NDL-B3`** *(cold-start)* | `black_friday` | 0,6423 | **0,1244** | `irrelevant` (17,0%), `skeptical` (12,5%) |
| `NDL-S1` | `scarcity` | 0,6236 | 0,1232 | `irrelevant` (18,1%), `skeptical` (12,5%) |
| `NDL-U2` | `urgency` | 0,6335 | 0,1200 | `irrelevant` (17,4%), `skeptical` (12,5%) |
| `NDL-U4` | `urgency` | 0,6194 | 0,1188 | `skeptical` (16,7%), `irrelevant` (13,8%) |
| `NDL-U3` | `urgency` | 0,6224 | 0,1160 | `irrelevant` (18,6%), `skeptical` (12,6%) |
| `NDL-B1` | `black_friday` | 0,5468 | 0,0842 | `irrelevant` (18,8%), `skeptical` (18,8%) |
| `NDL-U1` | `urgency` | 0,4775 | 0,0794 | `skeptical` (27,1%), `irrelevant` (19,4%) |
| `NDL-B2` | `black_friday` | 0,5276 | 0,0625 | `irrelevant` (22,5%), `skeptical` (16,6%) |

**Cosa emerge subito:**
- Tra le creatività **`black_friday`**, il nuovo asset **`NDL-B3`** (`carosello`, usato nei cold-start `NDL-AD06` e `NDL-AD23` dal 20/11) ottiene un'intenzione di clic quasi **doppia** (`0,1244`) rispetto a `NDL-B1` (`0,0842`) e `NDL-B2` (`0,0625`).
- In **`NDL-U1`**, il freno principale è lo scetticismo (`skeptical` **27,1%**), spiegando in modo qualitativo perché le persone non cliccano anche quando l'offerta promette urgenza.

---

## 4. Piano di integrazione tra Dati Quantitativi e Pubblico Sintetico

### Principio guida: separazione dei ruoli (`calibrated_to_ctr: false`)
I valori numerici di `CTR`, `CPM` e `CPC` restano governati **esclusivamente** dalla pipeline validata (Media 50/50 CatBoost + Timestral-28M per CPM, Baseline 14g per CTR, arricchimento interno 2025 + picchi BF/CM). I segnali del pubblico sintetico **non** sostituiscono le previsioni numeriche né applicano moltiplicatori arbitrari al CTR, ma arricchiscono il sistema decisionale in **4 punti precisi**:

1. **Priorità e tie-breaker sui 12 annunci nuovi (cold-start):**
   - Tutti e 12 gli annunci nuovi nel periodo vuoto (`FGR-B3`, `FGR-B4`, `NDL-B3`, `NDL-B4`, `CDF-B3`, `CDF-B4`, attivi dal 20 o 23 novembre) usano la leva `black_friday` e hanno storico assente o limitato.
   - Nella quota esplorativa del **10%** (o quando si propone una riallocazione entro ±20% tra annunci dello stesso ad set), usare `click_intent_signal` e `attention_signal` delle personas come criterio di priorità (es. spingere `NDL-B3` rispetto a `NDL-B1`/`NDL-B2`).
2. **Spiegazione qualitativa delle decisioni ("perché sì / perché no"):**
   - Affiancare ad ogni riga di decisione su ad set/annuncio le prime due motivazioni da `reason_distribution` (es. *alto `skeptical`*, *`weak_offer`*, *`interested`*), così l'utente non vede solo "sposta €X su Y", ma capisce che tipo di obiezione frena l'annuncio.
3. **Completamento della copertura Personas su tutti i settori e su tutto il campione:**
   - **Stato attuale su `main`:** sono state generate 4 schede su 24 (`beauty_skincare-P001..P004`) e valutati 11 asset Beauty (manca ancora **`NDL-B4`** tra gli asset Beauty, più tutto **`pet_ecommerce`** `CDF-*` e **`abbigliamento`** `FGR-*`).
   - **Azioni successive:**
     1. Completare i batch T3 per ottenere **24 persone per settore** (72 totali) su `beauty_skincare`, `pet_ecommerce` e `abbigliamento`.
     2. Eseguire `market_mirror analyze --live` sui restanti asset cold-start prioritari (`NDL-B4`, `CDF-B3`, `CDF-B4`, `FGR-B3`, `FGR-B4`) e poi sugli altri asset attivi nel `16–30 nov`.
4. **Integrazione tecnica nella pipeline `market_mirror`:**
   - **Aggiornare `market_mirror/forecast.py`** (`from_timestral_ref` o nuovo loader) per leggere `Prima_Analisi/Analisi_Completa_Black_Friday/previsioni_arricchite_2026-11-16_30.csv` (colonne `ctr_arricchito_pct` / `cpm_arricchito_eur` affiancate a `ctr_scelto_pct` / `cpm_scelto_eur`) al posto del vecchio `previsioni_28m.csv` del solo pilota Timestral.
   - **Usare `market_mirror/handoff.py` (`join_forecast`):** fare il join tramite `asset_id` tra il CSV arricchito a 699 righe e i `signals.json` delle personas (`simulation_attention_signal`, `simulation_click_intent_signal`, `simulation_run_id`), mantenendo `Forecast values are unchanged`.
   - **Esporre in `viewer.html` (`market_mirror/viewer.py`):** mostrare per ogni ad set e annuncio i **due scenari** (base pre-evento vs arricchito Black Friday/Cyber Monday), il **CPC stimato**, le **azioni di budget suggerite** e le **motivazioni del pubblico sintetico** in un'unica vista leggibile per la demo finale.
