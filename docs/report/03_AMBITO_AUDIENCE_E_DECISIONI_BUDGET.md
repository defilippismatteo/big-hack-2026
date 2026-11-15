# Ambito 3 — Audience Inference & Motore Decisionale Budget/Creatività

**Moduli di riferimento:** [personas_simulation.runtime/analytics.py](../../personas_simulation.runtime/analytics.py), [personas_simulation.runtime/marketing.py](../../personas_simulation.runtime/marketing.py), [personas_simulation.runtime/delivery.py](../../personas_simulation.runtime/delivery.py), [artifacts/wevion_v4/persona_adset.json](../../artifacts/wevion_v4/persona_adset.json), [decisions.csv](../../artifacts/wevion_v4/decisions.csv), più `Prima_Analisi/arricchisci_black_friday.py` su `origin/feat/timestral-pilot`.

---

## 1. Inferenza dei 12 Pubblici (`audience_evidence` & `persona_adset.json`)

Poiché il kit oscura intenzionalmente i pubblici reali di Meta, il sistema deduce **12 ipotesi comportamentali** (mai demografiche) usando esclusivamente evidenze fino al cutoff (`2026-11-15`, con snapshot dedicati anche al `2026-10-18` e `2026-11-01` per non contaminare i fold):

- **Metodo (`analytics.py`):** calcola metriche pesate complessive e sugli ultimi 14 giorni, frequenza media ponderata per impression, ranking di `by_lever` e `by_format`, e **confronto controllato sullo stesso `(data, asset_id)` tra ad set fratelli della stessa campagna** (`matched_asset_day_comparison`).
- **Struttura ricorrente emersa nei 3 verticali:**
  1. **`AS4` (`CDF-AS4`, `FGR-AS4`, `NDL-AS4`):** CTR storico massimo (`1,89% – 2,39%`), CPM elevato (`€9,95 – €13,42`), forte risposta a `black_friday` e `video` → compatibile con **pubblico caldo / alta intenzione** (es. retargeting o visitatori recenti).
  2. **`AS1` (`CDF-AS1`, `FGR-AS1`, `NDL-AS1`):** CPM più basso (`€5,22 – €7,63`) e CTR più basso (`0,89% – 1,13%`), assorbe il budget più alto → compatibile con **prospecting ampio / traffico freddo**.
  3. **`AS2` e `AS3`:** fascia intermedia con sensibilità mista a `scarcity` e `black_friday`.
- **Cautela dichiarata:** tutte le 12 schede riportano `confidence: "bassa"`, `demografia: "Non identificabile dai dati forniti"` e **2 ipotesi alternative** esplicite (es. confusione da delivery/calendario, oppure click di pura curiosità senza conversione).

---

## 2. Motore di Decisione Budget & Creatività: Due Versioni nel Repository

| Aspetto | Pipeline `main` (`personas_simulation.runtime/marketing.py`) | Pipeline arricchita (`origin/feat/timestral-pilot`: `arricchisci_black_friday.py`) |
|---|---|---|
| **Previsione sottostante** | `ctr_baseline14d__cpm_timestral28m` (senza moltiplicatore BF esplicito sul CTR) | `ctr_baseline14d` + `cpm_mix_50_50` + curva 2025 anti-doppio-conteggio + picchi BF/CM |
| **Budget totale 15 giorni** | **€16.950,00** (`€1.130/giorno`) | **€16.950,00** (`€1.130/giorno`) |
| **Regola di riallocazione** | Ottimizzazione greedy esatta in centesimi (`bounded_allocation`) entro **±20% per ad set**, a **totale giornaliero di campagna invariato** (`180` righe) | Classifica ad set per CPC stimato e valutazione variazione rispetto al pre-evento |
| **Pacing storico** | Mediana ultimi 14g (`spesa / budget`), **escludendo i 2 giorni overspend** (`21/10 FGR-AS1`, `10/11 CDF-AS3`) | Assume spesa = budget allocato per stimare volumi potenziali |
| **Quote di delivery ad-level** | **90%** proporzionale a spesa storica 14g + **10%** uniforme (esplorazione nuovi annunci) | **Identica** regola **90/10** |
| **Output su 15 giorni** | Click attesi da **18.170,1 → 18.717,6** (`+547,5` click, `+3,0%` a budget costante) | Click base **19.439 → 19.296** arricchiti (`-0,7%`, perché l'aumento CPM riduce le impression `-11,6%`, da `1.660.642` a `1.468.220`, quasi compensato dal picco CTR) |
| **Natura dichiarata** | `conditional_what_if_not_causal` (non stima elasticità causale al cambio budget) | Scenario condizionale interno al kit 2025 |

---

## 3. Indicazioni Operative per Settore (Sintesi Unificata)

- **Abbigliamento (`FGR-C1`):** spostare budget verso **`FGR-AS4`** (CPC arricchito `€0,5579`, CTR medio `2,85%`, asset top `FGR-B2`), riducendo `FGR-AS3` (`€1,3417`/click, `-20%` nello scenario `main`) e `FGR-AS2` (`-20%`).
- **Beauty & Skincare (`NDL-C1`):** unico settore dove nello scenario arricchito i click crescono (`+8,3%`). Premiare **`NDL-AS2`** (CPC arr. `€0,9813`, `+20%` in `main`) e `NDL-AS3` (`+20%` in `main`), riducendo **`NDL-AS1`** (assorbe €2.250 ma ha il CPC peggiore a `€1,2608` e CTR `0,85%`). Nota: `NDL-AS4` ha CTR alto (`2,26%`) ma CPM molto caro (`€22,98` arr., `€27,50` in `main`), quindi va monitorato per efficienza marginale.
- **Pet E-commerce (`CDF-C1`):** premiare **`CDF-AS4`** (CPC arr. `€0,6180`, `+20%` in `main`) e **`CDF-AS2`** (`€0,7569`, `+20%` in `main`), tagliando `CDF-AS3` (`€1,0586`, `-20%` in `main`) e parte di `CDF-AS1` (`€2.025` base).
