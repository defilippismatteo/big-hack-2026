# Guida rapida alla struttura del kit Wevion

**Le righe dei CSV non rappresentano persone reali.** I pubblici dei 12 ad set sono completamente ignoti. L'età, sesso/genere e professione che compariranno nelle personas sono campioni costruiti artificialmente, non ricavati dai risultati.

```text
Nuvola Derma Lab (NDL)
  └── NDL-C1 (campagna Meta, obiettivo vendite)
       ├── NDL-AS1 (ad set, budget+pubblico, 6 annunci)
       │     ├── NDL-AD01 -> NDL-S1  (creatività "Siero Vitamina C")
       │     ├── NDL-AD03 -> NDL-S3  (creatività "Kit routine autunno")
       │     └── ...
       ├── NDL-AS2 (5 annunci)
       ├── NDL-AS3 (6 annunci)
       │     ├── NDL-AD12 -> NDL-S1  (stessa creatività di NDL-AD01,
       │     │                        ma in un ad set diverso)
       │     └── ...
       └── NDL-AS4 (6 annunci)
```

La struttura di CDF e FGR è la stessa: 4 ad set con 6/5/6/6 annunci, 23 annunci per campagna. I 12 asset per settore sono 4 `S*` (scarcity), 4 `U*` (urgency) e 4 `B*` (black_friday). Il set degli asset e la matrice completa `campaign → adset → ad_id → asset_id` sono salvati in `data_map.json`.

### Cosa si unisce con cosa

| Dato che vuoi | Tabella iniziale | Join |
|---|---|---|
| Creatività mostrata da un annuncio | `annunci.csv` | `asset_id` ↔ `asset_creativi/asset_*.csv` |
| Tutti gli annunci in un ad set | `adset.csv` | `adset_id` ↔ `annunci.csv` |
| Performance storica per annuncio | `annunci.csv` | `ad_id` ↔ `storico_giornaliero.csv` |
| Budget per ad set/giorno | `adset.csv` | `(adset_id,data)` ↔ `budget_giornaliero.csv` |
| Annunci da prevedere per data | `da_prevedere.csv` | `(ad_id,data)`; NON contiene KPI |

### Segmenti e ad set: distinzione cruciale

Il **settore** (skincare/pet/abbigliamento) è noto. Il **pubblico/target dell'ad set** non lo è. Il ramo personas può creare tre pool realistici per settore con distribuzioni *ipotetiche e documentate*; il ramo forecasting/analytics può ipotizzare quali tipi di persone descrivano meglio i quattro ad set usando esclusivamente dati storici consentiti. Questi pesi vengono calcolati **dopo** la generazione e la simulazione. Non vanno retroiniettati nei profili.

### Ciò che manca materialmente

Nel kit non ci sono: CSV con età/sesso/target di ogni ad set, profili cliente individuali, immagini/video originali (solo descrizioni testuali), risultati reali esterni delle campagne (sono simulate), ground truth futura (CTR/CPM dal 16 al 30 novembre).
