---
name: wevion-decision-simulation
description: Valuta azioni plausibili per coppie persona-creatività con Gemini Decision 1 e/o feed test MarketMirror.
---

# wevion-decision-simulation

## Input consentiti
Una persona per volta (o istruzioni separate per domanda indipendente), creative_packet, contesto Meta/feed, data/evento e seed; nessuna metrica storica.

## Input vietati e confini
No CTR/CPM storici, niente previsioni, nessuna decisione di altre personas, nessuna comparazione con creatività non assegnate.

## Output obbligatori
outputs/persona_reactions.jsonl con persona_id, ad_id, adset_id, scenario, model, action scores, reason, seed, prompt hash.

## Procedura essenziale
Eseguire un primo test 1 creatività x 4 personas; Decision API client.decisions.create con input condiviso della creatività e questions distinte per persona. Choice scroll/glance/stop/click. Non trattare score come CTR. Fare un test paired con stesso pool e seed resettato quando si confrontano creatività.

## Requisiti comuni
Restituire JSON valido, versione schema, cut-off, modello, seed, errori e fonte dei dati. Segnalare i limiti senza riempire a fantasia. Non leggere altri file, anche se accessibili tecnicamente.
