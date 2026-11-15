# Previsioni sul periodo vuoto (16–30 novembre 2026)

Previsioni sulle **699 righe annuncio/giorno** di `da_prevedere.csv` (cutoff `2026-11-15`, 51 annunci distinti di cui 12 nuovi per 114 righe cold-start), usando **esclusivamente i dati forniti dagli organizzatori** e senza moltiplicatori esterni Black Friday.

## Scelta dei modelli (da [Validazione_Modelli](../Validazione_Modelli/README.md))

- **CTR (`ctr_scelto_pct`):** Baseline gerarchica a 14 giorni (`baseline_14g`).
- **CPM (`cpm_scelto_eur`):** Media 50/50 tra **CatBoost** e **Timestral-28M** (`mix_50_50_catboost_timestral28m`).
- Nel CSV sono comunque salvate tutte le stime dei singoli modelli (`ctr_baseline`, `ctr_catboost`, `ctr_timestral_28m`, `ctr_mix_50_50`, `cpm_baseline`, `cpm_catboost`, `cpm_timestral_28m`, `cpm_mix_50_50`) per facilitare i confronti e il successivo arricchimento Black Friday.

## Riepilogo delle previsioni

| Segmento | Righe | Annunci | CTR scelto mediana (pp) | CTR scelto media (pp) | CPM scelto mediana (€) | CPM scelto media (€) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| **Totale (16–30 nov)** | **699** | **51** | **1,0243** | **1,2973** | **10,8511** | **11,4515** |
| Pre-Black Week (16–19 nov) | 156 | 39 | 1,0082 | 1,2928 | 11,0321 | 11,3830 |
| Black Week ed eventi (20–30 nov) | 543 | 51 | 1,0243 | 1,2986 | 10,8125 | 11,4712 |
| Annunci già visti | 585 | 39 | 1,0082 | 1,2928 | 10,8607 | 11,4865 |
| Annunci nuovi (cold-start) | 114 | 12 | 1,0719 | 1,3207 | 10,4604 | 11,2722 |

### Dettaglio per settore (`vertical`)

| Settore | Righe | Annunci | CTR scelto mediana (pp) | CPM scelto mediana (€) | CPM CatBoost mediana (€) | CPM Timestral-28M mediana (€) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `abbigliamento` | 233 | 17 | 1,0503 | 12,4125 | 11,9443 | 12,3774 |
| `beauty_skincare` | 233 | 17 | 1,0764 | 12,2896 | 11,5932 | 12,7744 |
| `pet_ecommerce` | 233 | 17 | 0,9316 | 8,5019 | 8,0246 | 9,0404 |

## Nota per il passo successivo (Black Friday)

Senza fattori esterni sullo storico (che termina il 15 novembre prima del Black Friday), CatBoost non estrapola un salto promozionale nella settimana `20–30 nov` (mediana CPM €10,23 vs €10,49 nel `16–19 nov`), mentre Timestral-28M registra un lieve incremento (€11,56 vs €11,37). Questa base pulita serve come riferimento pre-evento su cui applicare l'arricchimento per il picco del Black Friday (27/11) e Cyber Monday (30/11).

## Riproduzione

```bash
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 HF_HUB_OFFLINE=1 PYTHONPATH=Test_Timestral:Prima_Analisi \
  python Prima_Analisi/prevedi_periodo_vuoto.py \
  --kit "info fornite dagli organizzatori /dati" \
  --model-28m <path-timestral-28m> \
  --output Prima_Analisi/Previsioni_Periodo_Vuoto
```

[Previsioni 16–30 nov CSV](previsioni_2026-11-16_30.csv) · [Riepilogo JSON](riepilogo.json) · [Script](../prevedi_periodo_vuoto.py)
