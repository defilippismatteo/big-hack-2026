# Analisi completa Black Friday (100% dati interni al kit)

Arricchimento delle 699 previsioni base ([Previsioni_Periodo_Vuoto](../Previsioni_Periodo_Vuoto/README.md)) per colmare i gap sul periodo 16–30 novembre **senza utilizzare trend esterni**, sfruttando esclusivamente i segnali interni del kit (`benchmark_mercato_settimanale_2025.csv`, `storico_giornaliero.csv`, `budget_giornaliero.csv`).

## Metodo verificato e correzioni applicate

1. **Rimozione del doppio conteggio stagionale sul CPM:**
   `cpm_scelto_eur` (media 50/50 CatBoost + Timestral-28M) incorpora già una parte della stagionalità settimanale tramite la covariata `indice_cpm` di Timestral-28M. Per ogni `(vertical, settimana)`, si applica soltanto il **fattore residuo** (`fattore_settimanale_cpm / media(cpm_scelto_eur / cpm_baseline)`), portando il livello settimanale esatto a quello del benchmark 2025 rispetto al riferimento `2–15 nov` e preservando le differenze relative tra annunci.
2. **Picco Black Friday (27/11) e Cyber Monday (30/11):**
   Nella settimana `23–29 nov`, l'incremento settimanale è concentrato sul venerdì **27/11** (peso `2,2`) rispetto agli altri 6 giorni (peso `0,8`), mantenendo la media dei 7 giorni esattamente uguale all'indice 2025 del kit (`(6 × 0,8 + 2,2) / 7 = 1,0`). Per il lunedì **30/11** (Cyber Monday, ultimo giorno della Black Week in `calendario.csv`), si applica un peso di picco `1,35` sull'incremento della Black Week, evitando il calo artificiale dovuto alla settimana `2025-12-01` (1–7 dic).
3. **Quote di spesa realistiche (90/10) e KPI ponderati:**
   Il budget giornaliero di ciascun ad set è ripartito al **90%** in base alla spesa storica degli ultimi 14 giorni (`2–15 nov`) e al **10%** in modo uniforme per l'esplorazione dei nuovi annunci (`nuovo_annuncio`), calcolando **Impression**, **Click** e **CPC (€/click)** ponderati.

## Impatto sui 15 giorni (16–30 novembre)

| Metrica | Scenario base (pre-evento) | Scenario arricchito (kit 2025 + picchi BF/CM) |
| --- | ---: | ---: |
| Budget totale 15 giorni | €16.950,00 | €16.950,00 |
| Impression stimate totali | 1.660.642 | 1.468.220 |
| Click stimati totali | 19.439 | 19.296 |
| **CPC medio stimato** | **€0,8720** | **€0,8784** |
| **CPM mediana Black Friday (27/11)** | **€11,6954** | **€17,0401** |
| **CTR mediana Black Friday (27/11)** | **1,0503%** | **1,5522%** |
| **CPM mediana Cyber Monday (30/11)** | **€11,2717** | **€13,8207** |
| **CTR mediana Cyber Monday (30/11)** | **1,0503%** | **1,3635%** |

## Dove conviene allocare il budget (`decisioni_adset_budget.csv`)

Con la ripartizione 90/10, il maggior costo d'asta riduce le impression (-5,7% Beauty, -11,2% Pet, -16,9% Abbigliamento), mentre la crescita del CTR quasi compensa i click (e in Beauty li fa crescere di **+8,3%**). Gli ad set con il miglior **CPC arricchito** per settore sono:

- **Abbigliamento:** `FGR-AS4` (**€0,5579**/click, CTR medio 2,85%) è il più efficiente; `FGR-AS3` è il più caro (**€1,3417**/click).
- **Beauty & Skincare:** `NDL-AS2` (**€0,9813**/click, CTR medio 1,24%) e `NDL-AS4` (**€1,0150**/click, CTR medio 2,26%) convengono più di `NDL-AS1` (**€1,2608**/click, che oggi assorbe €2.250).
- **Pet E-commerce:** `CDF-AS4` (**€0,6180**/click, CTR medio 2,39%) e `CDF-AS2` (**€0,7569**/click) battono `CDF-AS1` (**€0,9164**/click, oggi a €2.025) e `CDF-AS3` (**€1,0586**/click).

## Riproduzione

```bash
python Prima_Analisi/arricchisci_black_friday.py \
  --kit "info fornite dagli organizzatori /dati" \
  --base-forecast Prima_Analisi/Previsioni_Periodo_Vuoto/previsioni_2026-11-16_30.csv \
  --output Prima_Analisi/Analisi_Completa_Black_Friday
```

[Previsioni arricchite CSV](previsioni_arricchite_2026-11-16_30.csv) · [Decisioni ad set/budget CSV](decisioni_adset_budget.csv) · [Riepilogo giornaliero CSV](riepilogo_giornaliero.csv) · [Riepilogo JSON](riepilogo_analisi.json) · [Script](../arricchisci_black_friday.py)
