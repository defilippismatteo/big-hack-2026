---
name: audit-marketmirror
description: Ispeziona MarketMirror e prepara una lista minima di moduli da riusare, senza eseguire una simulazione completa.
---

# audit-marketmirror

## Input consentiti
Sorgenti upstream MarketMirror, README e licenza; contratti Wevion.

## Input vietati e confini
Non modificare src/forecast; non introdurre OASIS, social feed, survey o web scraping senza giustificazione.

## Output obbligatori
docs/marketmirror_adaptation.md con funzioni, dipendenze, licenza, punti di adapter e piano di test.

## Procedura essenziale
Esaminare persona_planner.generate_personas, fast_population, feed_test.normalize_creatives/assign/scroll_prompt/run_feed_test/summarize, predict/calibration. Documentare cosa dipende da OpenAI-compatible chat e cosa richiede un adapter; proporre chiamate testabili, non fare riscritture massive.

## Requisiti comuni
Restituire JSON valido, versione schema, cut-off, modello, seed, errori e fonte dei dati. Segnalare i limiti senza riempire a fantasia. Non leggere altri file, anche se accessibili tecnicamente.
