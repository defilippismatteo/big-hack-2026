---
name: wevion-signal-validation
description: Verifica con ablation cronologica se i segnali persona aggiungono valore al forecasting, senza trasformarli direttamente in CTR.
---

Estensione P4 non ancora implementata: non deve bloccare P0–P3. Usa segnali simulated_decision,
predizioni forecast-only e metriche train dello stesso cutoff. Mai usare fixture.
Confronta baseline, forecast-only e forecast+segnali; pesi/calibrazione scelti
prima del holdout, inclusa l'inferenza del pubblico. Tieni 02–15/11 come verifica
finale di sviluppo anziché ottimizzare ripetutamente su quelle etichette.
Il comando `market_mirror join` affianca colonne esplicative e verifica le chiavi:
non allena, non calibra e non dimostra miglioramenti. Il CPM resta quantitativo.
Output futuro: persona_ablation.json con fold, seed, errori CTR in punti
percentuali, errori CPM in euro e provenienza.

Vedi [integrazione Timestral](../../../docs/MARKET_MIRROR_GUIDA.md).
