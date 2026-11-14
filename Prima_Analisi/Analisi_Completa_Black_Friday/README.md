# Analisi completa Black Friday (100% dati interni al kit)

Arricchimento delle 699 previsioni base ([Previsioni_Periodo_Vuoto](../Previsioni_Periodo_Vuoto/README.md)) per colmare i gap sul periodo 16–30 novembre **senza utilizzare trend esterni**, sfruttando esclusivamente i segnali interni del kit (`benchmark_mercato_settimanale_2025.csv`, `storico_giornaliero.csv`, `budget_giornaliero.csv`).

## Metodo

1. **Curva settimanale 2025 per settore (`benchmark_mercato_settimanale_2025.csv`, Meta IT):**
   rapporto tra l'indice della settimana target e l'indice medio ponderato delle ultime due settimane note (`2–15 nov`).
2. **Picco Black Friday a media settimanale invariata:**
   nella settimana `23–29 nov`, l'incremento settimanale viene concentrato sul venerdì **27/11** (peso `2,2`) rispetto agli altri 6 giorni (peso `0,8`), mantenendo la media dei 7 giorni esattamente uguale all'indice 2025 del kit (`(6 × 0,8 + 2,2) / 7 = 1,0`).
3. **KPI decisionali dal budget (`budget_giornaliero.csv`):**
   ripartendo il budget giornaliero dell'ad set sugli annunci attivi, vengono stimati **Impression**, **Click** e **CPC (€/click)** nello scenario base e in quello arricchito.

## Impatto sui 15 giorni (16–30 novembre)

| Metrica | Scenario base (pre-evento) | Scenario arricchito (kit 2025 + picco BF) |
| --- | ---: | ---: |
| Budget totale 15 giorni | €16.950,00 | €16.950,00 |
| Impression stimate totali | 1.654.042 | 1.318.690 |
| Click stimati totali | 19.633 | 17.375 |
| **CPC medio stimato** | **€0,8633** | **€0,9756** |
| **CPM mediana Black Friday (27/11)** | **€11,6954** | **€20,2172** |
| **CTR mediana Black Friday (27/11)** | **1,0503%** | **1,5522%** |

## Dove conviene allocare il budget (`decisioni_adset_budget.csv`)

A budget invariato, l'aumento dei costi d'asta riduce le impression (~-18%/-22%), ma l'aumento del CTR contiene il calo dei click. Gli ad set con il miglior **CPC arricchito** per settore sono:

- **Abbigliamento:** `FGR-AS4` (**€0,5847**/click, CTR medio 2,92%) è il più efficiente; `FGR-AS3` è il più caro (**€1,5511**/click).
- **Beauty & Skincare:** `NDL-AS4` (**€1,1102**/click, CTR medio 2,37%) e `NDL-AS2` (**€1,1154**/click) sono più efficienti di `NDL-AS1` (**€1,5079**/click, che oggi riceve €2.250).
- **Pet E-commerce:** `CDF-AS4` (**€0,6381**/click, CTR medio 2,54%) e `CDF-AS2` (**€0,7818**/click) battono `CDF-AS1` (**€1,0311**/click, che oggi riceve €2.025) e `CDF-AS3` (**€1,1778**/click).

## Riproduzione

```bash
python Prima_Analisi/arricchisci_black_friday.py \
  --kit "info fornite dagli organizzatori /dati" \
  --base-forecast Prima_Analisi/Previsioni_Periodo_Vuoto/previsioni_2026-11-16_30.csv \
  --output Prima_Analisi/Analisi_Completa_Black_Friday
```

[Previsioni arricchite CSV](previsioni_arricchite_2026-11-16_30.csv) · [Decisioni ad set/budget CSV](decisioni_adset_budget.csv) · [Riepilogo giornaliero CSV](riepilogo_giornaliero.csv) · [Riepilogo JSON](riepilogo_analisi.json) · [Script](../arricchisci_black_friday.py)
