---
name: wevion-evidence
description: Prepara evidenze quantitative ammesse e confronti a creatività costante per ogni ad set.
---

# wevion-evidence

## Input consentiti
storico_giornaliero.csv, annunci.csv, asset_creativi/*.csv, adset.csv, campagne.csv, solo fino al cut-off ricevuto.

## Input vietati e confini
Nessuna etichetta del fold di test, nessuna metrica futura; nessuna interpretazione demografica presentata come fatto.

## Output obbligatori
data/views/audience_evidence_<cutoff>.json (12 record): impression/click/spesa aggregati, CTR/CPM pesati, frequenza, trend, confronti stesso asset fra ad set, incertezze.

## Procedura essenziale
Calcolare CTR=100*sum(click)/sum(impression), CPM=1000*sum(spesa)/sum(impression). Normalizzare per periodo e creatività; distinguere correlazione da causalità. Test: cutoff ed esattamente 12 ad set.

## Requisiti comuni
Restituire JSON valido, versione schema, cut-off, modello, seed, errori e fonte dei dati. Segnalare i limiti senza riempire a fantasia. Non leggere altri file, anche se accessibili tecnicamente.
