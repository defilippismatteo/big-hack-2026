# Task del subagente Decision

Esegui solo il worker di analisi Decision del run personas T3. Non generare
o riscrivere persone, non aprire storico, budget, forecast, audience ipotizzate,
risposte precedenti o repository diversi. Non delegare altro lavoro.

Input unico: `data/personas_600/decision_plan.json`.
Interprete: `python3` nella root del progetto.

1. Esegui `python3 -m personas_simulation.runtime decide --preflight` usando quel piano e
   scrivendo `data/personas_600/decision_preflight.json`. Questo controllo
   deve avvenire prima della chiamata API.
2. Se il task richiesto è PRECHECK, fermati dopo aver letto il report. Non
   eseguire `--live` e non chiamare API. Riporta che i risultati Decision mancano.
3. Se il task richiesto è LIVE e la chiave Decision è disponibile nell'ambiente
   locale, usa `analyze --live --asset-id ASSET_ID` per il primo asset, poi
   `analyze --live` sugli asset autorizzati. Il registro in analyses/ledger.sqlite
   evita invii duplicati; non cambiare cartella del registro per aggirarlo.
   Anche `decide --live` usa lo stesso registro. Leggi la chiave solo tramite il client Python: non
   stamparla, non copiarla in prompt, report o comandi con valore letterale.
4. Se manca la chiave o l'API rifiuta la richiesta, registra il blocco senza
   sostituire le risposte con fixture o un modello diverso.
   Un retry di stato rejected richiede una ripresa esplicita; pending/ambiguous
   e invalid_response non vengono mai reinviati automaticamente.

Ogni domanda della richiesta contiene una persona distinta e il suo feed;
non unire i profili nel contesto condiviso e non usare risposte di altre persone.
Non chiamare endpoint generativi Google: l'unica API è client.decisions.create.
Riporta percorso dei file, API chiamate realmente e stato live/non eseguito.
