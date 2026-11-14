---
name: wevion-persona-explain
description: Prepara narrazione verificabile delle 12 audience e motivi delle reazioni per README/dashboard.
---

# wevion-persona-explain

## Input consentiti
audience_hypotheses, persona_signals aggregati, metriche di validazione già calcolate e forecast finale pubblicabile.

## Input vietati e confini
Non modificare risultati predittivi, non chiamare numeri simulati "CTR reali", non inventare demografia verificata.

## Output obbligatori
outputs/audience_report.md e outputs/audience_report.json, 12 schede con prove, alternative, cautela e impatto decisionale.

## Procedura essenziale
Mostrare con chiarezza fatti osservati, ipotesi, segnali simulati e risultati di backtest come classi separate.

## Requisiti comuni
Restituire JSON valido, versione schema, cut-off, modello, seed, errori e fonte dei dati. Segnalare i limiti senza riempire a fantasia. Non leggere altri file, anche se accessibili tecnicamente.
