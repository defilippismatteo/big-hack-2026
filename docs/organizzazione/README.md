# Gestione del repository

Punto di ingresso per orientarsi senza spostare percorsi da cui il codice dipende.

1. [Mappa delle cartelle, codice e dati](MAPPA_REPOSITORY.md).
2. [Decisioni recuperate dalla conversazione](DECISIONI_E_CHAT.md).
3. [Piano di archivio approvato e applicato](../../outputs/code-rot-cleaner/PIANO_RIORDINO.md).
4. [Inventario file e dimensioni](../../outputs/code-rot-cleaner/inventario/FILES.md).
5. [Archivio della conversazione](../../outputs/code-rot-cleaner/chat/CONVERSAZIONE.md).
6. [Audit del codice inutilizzato](../../outputs/code-rot-cleaner/CODE-ROT-REPORT.md).

## Leggere i risultati per area

| Area | Documento principale | Dati / viewer |
|---|---|---|
| Personas | [Guida T3](../PERSONAS_T3.md) | [Schede e feed](../../artifacts/personas_t3/viewer.html) |
| Decision | [Report](../../artifacts/personas_t3/analyses/REPORT.md) | [Risultati](../../artifacts/personas_t3/analyses/results.html) |
| Analisi creativa precedente | [Analisi rivista](../../artifacts/personas_t3/analyses/creative_analysis.reviewed.md) | `analyses/diagnosis_input.json` |
| Interviste cieche | [Report completo](../../artifacts/personas_t3/interviews/REPORT.md) | `interviews/frozen.json`, `comparison.json` |
| Consegna candidata | [README output](../../artifacts/wevion_v4/README.md) | [Viewer](../../artifacts/wevion_v4/viewer.html) |
| Replica Timestral/CatBoost | [Stato e confronto](../TIMESTRAL_REPLICA_E_STATO_V4.md) | [Grafici](../../artifacts/timestral_reproduction/results/confronto.html) |
| Operatività generale | [Guida](../MARKET_MIRROR_GUIDA.md) | [Video da registrare](../VIDEO_180S.md) |

I link sotto artifacts dipendono dai file locali, esclusi da Git. Stato verifiche precedente: 43 test passati nel lavoro sulle interviste; questo audit non ha rieseguito test, deliver, inferenze o API. Nessuna rimozione è stata dimostrata sicura.

Verifica dopo gli spostamenti approvati: 43 test superati, hash dei 13 file preservati, link del nuovo indice verificati. Ricevuta: `outputs/code-rot-cleaner/applicazione_riordino.json`.
