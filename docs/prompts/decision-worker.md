# Task del subagente Decision

Esegui solo il worker di analisi Decision del run personas T3. Non generare
o riscrivere persone, non aprire storico, budget, forecast, audience ipotizzate,
risposte precedenti o repository diversi. Non delegare altro lavoro.

Input unico: `artifacts/personas_t3/decision_plan.json`.
Interprete: `.venv-market-mirror/bin/python` nella root del progetto.

1. Esegui `python -m market_mirror decide --preflight` usando quel piano e
   scrivendo `artifacts/personas_t3/decision_preflight.json`. Questo controllo
   deve avvenire prima della chiamata API.
2. Se il task richiesto è PRECHECK, fermati dopo aver letto il report. Non
   eseguire `--live` e non chiamare API. Riporta che i risultati Decision mancano.
3. Se il task richiesto è LIVE e la chiave Decision è disponibile nell'ambiente
   locale, esegui `decide --live` e salva `decision_raw.json`, poi `aggregate`
   in `signals.json`. Leggi la chiave solo tramite il client Python: non
   stamparla, non copiarla in prompt, report o comandi con valore letterale.
4. Se manca la chiave o l'API rifiuta la richiesta, registra il blocco senza
   sostituire le risposte con fixture o un modello diverso.

Ogni domanda della richiesta contiene una persona distinta e il suo feed;
non unire i profili nel contesto condiviso e non usare risposte di altre persone.
Non chiamare endpoint generativi Google: l'unica API è client.decisions.create.
Riporta percorso dei file, API chiamate realmente e stato live/non eseguito.
