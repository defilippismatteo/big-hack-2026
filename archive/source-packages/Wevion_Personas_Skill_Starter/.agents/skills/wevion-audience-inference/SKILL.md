---
name: wevion-audience-inference
description: Formula 12 ipotesi di pubblico motivate dai dati per la challenge Wevion.
---

# wevion-audience-inference

## Input consentiti
Solo audience_evidence_<cutoff>.json, descrizione generale del prodotto e creatività pertinenti; nessuna metrica del periodo successivo.

## Input vietati e confini
Non leggere da_prevedere per estrarre risultati, niente forecasts/holdout, no demografia certa o pubblico "vero".

## Output obbligatori
outputs/audience_hypotheses_<cutoff>.json con adset_id, 2-3 ipotesi comportamentali, prove, alternative, confidenza qualitativa, pesi dichiarati euristici.

## Procedura essenziale
Per ciascun ad set spiegare chi potrebbe reagire così e perché, includendo almeno una spiegazione alternativa. Usare creatività comuni tra ad set per una comparazione più solida.

## Requisiti comuni
Restituire JSON valido, versione schema, cut-off, modello, seed, errori e fonte dei dati. Segnalare i limiti senza riempire a fantasia. Non leggere altri file, anche se accessibili tecnicamente.
