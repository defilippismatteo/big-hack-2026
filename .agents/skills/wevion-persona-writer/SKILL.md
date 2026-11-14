---
name: wevion-persona-writer
description: Genera schede persona con un subagente Gemini in T3/Antigravity usando l'abbonamento, senza API generativa e senza dati pubblicitari.
---

L'architettura corrente è descritta in [PERSONAS_T3.md](../../../docs/PERSONAS_T3.md).
Usa t3-prepare per slot e job. Delega il contenuto di un .prompt.txt come task
nuovo a Gemini Hydrogen tramite Antigravity, thinking low: nessuna storia del
padre, nessun annuncio/KPI/forecast. Il figlio usa solo input inline, non legge
file e restituisce JSON. Non usare models.generate_content o una chiave Google.

Python fissa quote, età esatta, genere, routine social, rischio e interesse.
Gemini aggiunge nome, interessi e i nove dettagli del contratto, senza stereotipi
né una popolazione di soli clienti ideali. Primo probe: quattro persone.
Il coordinatore salva risposta e ricevuta T3 effettiva, quindi t3-import valida,
congela e fonde le schede. personas-view mostra solo risultati salvati.
Nessun provider alternativo su errore senza istruzione dell'utente.

La generazione in batch può vedere gli slot del batch, non risposte precedenti.
L'indipendenza di reazione si applica alla fase successiva per singola persona.
Le istruzioni di non lettura non sono una sandbox OS: non dichiararle tali.
