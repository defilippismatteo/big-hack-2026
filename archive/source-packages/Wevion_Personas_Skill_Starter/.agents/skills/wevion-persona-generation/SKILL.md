---
name: wevion-persona-generation
description: Crea personas sintetiche diverse e coerenti con le ipotesi, usando Gemini Hydrogen a basso thinking e test multi-provider.
---

# wevion-persona-generation

## Input consentiti
Solo audience_hypotheses sanitizzato: comportamenti, bisogni, mercato italiano, pesi ipotizzati e slot diversità deterministici.

## Input vietati e confini
Non vedere headline/copy di annunci specifici, CTR/CPM, ranking, creatività vincente, forecasting, altre risposte di personas.

## Output obbligatori
outputs/persona_cards_<cutoff>.json: persona_id, adset_id, hypothesis_id, seed, provider/model, età come ipotesi, budget_sensitivity, trust, ad_avoidance, topic_interest, decision_routine, contradiction, weight.

## Procedura essenziale
Generare prima gli slot deterministicamente; far completare i dettagli a Hydrogen. Iniziare con 8 persone/ad set; seed fisso; validare duplicati, stereotipi, copertura e pesi. Usare un secondo modello su un campione stratificato. Non inventare un CTR per persona.

## Requisiti comuni
Restituire JSON valido, versione schema, cut-off, modello, seed, errori e fonte dei dati. Segnalare i limiti senza riempire a fantasia. Non leggere altri file, anche se accessibili tecnicamente.
