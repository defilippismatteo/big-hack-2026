# Replica locale Timestral · 14 novembre 2026

Report completo: `../../docs/TIMESTRAL_REPLICA_E_STATO_V4.md`.

Sono stati scaricati Timestral-5M e Timestral-28M in `models/` e riprodotti i
risultati del commit `2d8adf033e747e147c401246c07ce656f9f1cfb7`.
Stessi pesi e metriche pubblicate; piccole differenze numeriche nei CSV tra CPU.
Anche il primo esperimento CatBoost coincide con i risultati salvati.

Dalla root del repository:

```bash
bash artifacts/timestral_reproduction/reproduce.sh
```

La procedura richiede `uv` e `hf`, già installati sul PC, usa Python 3.12.13 e
il lock esatto, recupera sorgenti/pesi quando servono e poi esegue offline.
È stata eseguita integralmente con successo. Per la sola verifica senza rete:

```bash
HF_HUB_OFFLINE=1 OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 \
  artifacts/timestral_reproduction/venv/bin/python artifacts/timestral_reproduction/verify.py
```

`results/verification.json` contiene le prove; `results/confronto.html` mostra
il confronto dei quattro metodi. `results/forecast_candidate_2026-11-16_30.csv`
è la replica della candidata baseline CTR + 28M CPM, separata dalla consegna
esistente e con intervalli dichiarati non calibrati. Non è una selezione finale
tra tutti i modelli. `raw/` conserva i backtest completi e `source/` i sorgenti
originali. I dati del kit sono simulati; non esistono esiti futuri con cui validare
le 699 previsioni. Tutta questa cartella è locale e ignorata da Git.
