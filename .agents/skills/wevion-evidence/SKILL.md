---
name: wevion-evidence
description: Costruisce evidenze quantitative per i 12 ad set usando soltanto lo storico disponibile al cutoff.
---

Questa fase P2 è Analytics, separata dall'estensione feed P4. È implementata in
`market_mirror/analytics.py` e invocata da `python -m market_mirror deliver`.
Leggi storico, mapping annuncio/asset/adset e creative soltanto
per date <= cutoff. CTR=100*sum(click)/sum(impression),
CPM=1000*sum(spesa)/sum(impression). Confronta stessi asset negli stessi periodi
tra ad set, frequenza, trend e incertezza. Non dedurre demografia certa.
Output: `artifacts/wevion_v4/audience_evidence_<cutoff>.json`, 12 record,
con cutoff e fonti. Non passare questi record al writer di personas.
Validazione 02–15/11: cutoff 01/11; forecast 16–30/11: cutoff 15/11.

Vedi [guida](../../../docs/MARKET_MIRROR_GUIDA.md).
