---
name: wevion-persona-diversity
description: Prepara slot sintetici eterogenei e riproducibili per settore Wevion, senza usare pubblici inferiti o risultati di campagne.
---

Percorso corrente: Python → subagente Gemini T3 → schede congelate → worker
Decision. Vedi [PERSONAS_T3.md](../../../docs/PERSONAS_T3.md).


Usa `python -m personas_simulation.runtime t3-prepare`: `safe_inputs/public_context.json` e
`safe_inputs/persona_slots.json` sono gli unici input del writer.
La preparazione riusa `Wevion_Personas_Architettura_v1/scripts/make_slots.py`.
Default 24 persone/settore, seed 2026: età, identità di genere, motivazioni,
interesse anche basso, routine social e attitudine al rischio.
Quote e sampling_weight sono un disegno manuale, non stime della popolazione.
Verifica copertura, unicità, somma pesi per settore e ripetibilità.
Non leggere creatività, storico, audience Analytics o forecast per scegliere gli slot.
Per cambiare i prior documenta l'ipotesi e rigenera il pool prima delle decisioni.

Vedi [guida e confini](../../../docs/PERSONAS_T3.md).
