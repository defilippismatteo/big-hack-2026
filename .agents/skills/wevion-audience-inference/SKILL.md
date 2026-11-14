---
name: wevion-audience-inference
description: Formula 12 ipotesi motivate sui pubblici Wevion da evidenze limitate al cutoff, senza condizionare le personas indipendenti.
---

Deliverable P2 obbligatorio: 12 schede adset, non un pool massivo di persone.
Prima implementazione deterministica in `analytics.audiences`, invocata da deliver.
Input: audience_evidence_<cutoff>.json e
creatività pertinenti; non leggere etichette future. Per ogni adset_id produrre
2–3 ipotesi comportamentali, prove, almeno un'alternativa e confidenza qualitativa.
Età, genere e pesi restano ipotesi; non esistono etichette di pubblico vero nel kit.
Output principale: `artifacts/wevion_v4/persona_adset.json`; versioni di fold in
`audience_hypotheses_<cutoff>.json`. La regola iniziale usa ranking di leve e
formati su CTR pesato; è un'associazione da rivedere, non un effetto causale.
Se un LLM migliora la spiegazione, passagli solo evidenze del cutoff e un
campione delle creatività; registra provider e modello senza alterare i numeri.
Non reintrodurre queste ipotesi nel writer del pool simulation_blind: Analytics
può associare e ripesare i segnali dopo la simulazione, allenandosi solo sul train.

Vedi [differenza rispetto allo starter](../../../docs/MARKET_MIRROR_GUIDA.md).
