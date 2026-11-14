---
name: wevion-creative-packets
description: Normalizza le creatività fornite a un formato uniforme per la simulazione.
---

# wevion-creative-packets

## Input consentiti
asset_creativi/*.csv, annunci.csv, campagne.csv, calendario.csv; soltanto chiavi e date pertinenti.

## Input vietati e confini
Non vedere CTR, CPM, spesa, ranking storici o output previsionali.

## Output obbligatori
outputs/creative_packets.json con ad_id, asset_id, adset_id, vertical, leva, formato, headline, testo, CTA, descrizione_visual, date/evento (senza risultati).

## Procedura essenziale
Preservare la natura testuale delle descrizioni visual. Non generare immagini spacciandole per creatività ufficiali; usare la piattaforma Meta.

## Requisiti comuni
Restituire JSON valido, versione schema, cut-off, modello, seed, errori e fonte dei dati. Segnalare i limiti senza riempire a fantasia. Non leggere altri file, anche se accessibili tecnicamente.
