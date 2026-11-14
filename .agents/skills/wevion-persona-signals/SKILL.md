---
name: wevion-persona-signals
description: Valida e aggrega risposte Decisions in segnali per asset, mantenendole distinte dai CTR e dalle fixture offline.
---

Percorso corrente: Python → subagente Gemini T3 → schede congelate → worker
Decision. Vedi [PERSONAS_T3.md](../../../docs/PERSONAS_T3.md).


Esegui `python -m market_mirror aggregate`; codice in `market_mirror/signals.py`.
Controlla corrispondenza hash richiesta, copertura esatta delle domande,
probabilità finite, opzioni complete, massa 1, choice e confidence coerenti.
Non imputare risposte mancanti; conserva raw per ispezione.
Esporta probabilità individuali, marginali per azione e reason_distribution.
attention_signal = 1 - P(scroll); click_intent_signal = P(click).
Normalizza i pesi manuali sul campione effettivamente esposto; quattro persone
sono un probe tecnico, non una stima rappresentativa.
Le azioni campionate per demo usano seed locale e non sono clic osservati.
Non chiamare un LLM per inventare feedback o calibrare gli score sullo storico.
Il file segnali deve conservare data_kind e calibrated_to_ctr=false.

Vedi [handoff Analytics](../../../docs/MARKET_MIRROR_GUIDA.md).
