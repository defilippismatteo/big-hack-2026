---
name: wevion-delivery
description: Prepara e verifica la consegna Wevion v4 con 699 forecast, 12 audience motivate, scenari budget e viewer, coordinando gli export del ramo Timestral.
---

Leggi la specifica operativa v4 prima di definire le priorità. P0 forecast e
backtest, P1 Timestral solo se utile, P2 pubblici e decisioni, P3 viewer/README/video.
Il pool generico e Decision 1 sono P4 opzionale e non producono il CTR numerico.

Runtime: `python3 -m quantitative_analysis.pipeline.delivery`. L'opzione
`--timestral-ref origin/feat/timestral-pilot` legge Prima_Analisi da un commit
senza cambiare checkout; conserva il commit e lo snapshot del CSV. La regola
attuale sceglie separatamente CTR/CPM sul primo fold WMAE fra baseline e Timestral.
CatBoost resta da confrontare: non dichiarare la selezione definitiva.

Verifica 699 chiavi esatte e uniche, CTR 0–100, CPM positivo, 114 righe cold-start,
12 audience con prove/alternative, cutoff di ogni fold, budget conservato per
campagna/giorno entro ±20%, pacing e quote delivery che sommano a 1.
Gli scenari 2025 sono prior dal kit, non quantili calibrati. La riallocazione è
un what-if con risposta al budget e costi d'asta assunti invariati.

Output in artifacts/wevion_v4: CSV forecast e decisioni, JSON audience/metriche,
viewer.html, README e manifest di provenienza. Prima del pitch rivedere audience,
calibrazione e selezione, quindi registrare video di 180 secondi.
Test: `python -m unittest discover -s tests -v`. Non avviare servizi per il viewer:
è un HTML standalone che legge risultati precomputati incorporati.
