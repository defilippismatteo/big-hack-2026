# Mappa del repository e dei dati

Snapshot del 14 novembre 2026; lettura dei file attuali, senza rieseguire inferenze o chiamate API. Inventario dettagliato: `outputs/code-rot-cleaner/inventario/FILES.md`; hash e stato Git in `files.json`; righe/intestazioni dei 35 CSV in `csv_metadata.json`; duplicati byte-identici in `duplicati_esatti.json`. Sono inventariati 341 file pertinenti allo snapshot, esclusi ambienti, pesi, cache, segreti e output dell'audit.

## Cartelle e responsabilità

| Percorso | Funzione / stato | Azione consigliata |
|---|---|---|
| `market_mirror/` | Runtime Python corrente | KEEP |
| `.agents/skills/` | Skill canoniche del progetto | KEEP |
| `docs/` | Guide, prompt worker, report replica, video e mappe | KEEP; usare questo indice |
| `tests/` | Test del runtime, inclusi cache e visibilità | KEEP |
| `scripts/preview_persona.py` | Preview locale, entry point manuale | KEEP |
| `info fornite dagli organizzatori /` | Kit originale, CSV e PDF; spazio finale nel nome reale | KEEP immutato |
| `Wevion_Personas_Architettura_v1/` | Pacchetto sorgente, ma anche dipendenza dinamica corrente | KEEP; non spostare in blocco |
| `archive/source-packages/Wevion_Personas_Skill_Starter/` | Prima proposta con audience, superata e non canonica | Archiviato; contenuto preservato |
| `TEST INIZIALI FATTI DA CHAT GPT DA VERIFICARE /` | Baseline/CatBoost e fonte storica; spazio finale nel nome | KEEP per provenienza; non confondere con Timestral |
| `artifacts/personas_t3/` | Run corrente di schede, feed, Decision, interviste | KEEP completo |
| `artifacts/market_mirror/` | Input preparati e smoke offline, usati anche dal plan corrente | KEEP; non eliminare per nome generico |
| `artifacts/wevion_v4/` | Consegna candidata e viewer, 699 forecast | KEEP come snapshot distinto |
| `artifacts/timestral_reproduction/` | Replica separata, sorgenti, risultati, ambiente e pesi | KEEP risultati/provenienza; ambiente e pesi sono ingombro operativo |
| `artifacts/persona_preview/` | Preview precedente | REVIEW; verificare eventuali contenuti unici prima di archiviare |
| `artifacts/timestral_audit/` | Audit precedente | KEEP come evidenza finché confrontato con replica |
| `.venv-market-mirror/` | Ambiente operativo principale | KEEP; non materiale di consegna |
| `dashboard_unificata.html` | Dashboard locale non tracciata al momento dell'audit | KEEP; entry point manuale, origine/integrazione da verificare |
| `archive/specifications/Specifica_Operativa_v3.md` | Specifica precedente | Archiviato; contenuto preservato |
| `BigHack2026_Wevion_Specifica_Operativa_v4.md` | Fonte progettuale corrente | KEEP |
| `archive/source-packages/Wevion_Personas_Architettura_v1.zip` | Pacchetto compresso sorgente | Archiviato; non dichiarato identico alla cartella |

`Test_Timestral/` non è presente nella root attuale. Esiste nella copia sorgente della replica e nel ref Git indicato dalla guida. Non modificato.

## Runtime: cosa usa cosa

| Area | Moduli |
|---|---|
| CLI / contratti | `__main__.py`, `contracts.py` |
| Preparazione e schede | `starter.py`, `personas.py`, `t3_personas.py` |
| Feed / API / cache | `feed.py`, `providers.py`, `decision_runs.py`, `signals.py` |
| Colloqui e confronto | `interviews.py` (funzioni Python, nessun sottocomando CLI dedicato) |
| Visualizzazioni | `decision_view.py`, `viewer.py`, `t3_personas.render_cards` |
| Quantitativo e consegna | `analytics.py`, `forecast.py`, `marketing.py`, `delivery.py` |
| Scambio successivo | `handoff.py` |

`starter.py` carica per percorso quattro moduli da `Wevion_Personas_Architettura_v1/scripts/`: `prepare_safe_inputs`, `build_creative_catalog`, `make_slots`, `decision1_requests`. Anche il Dockerfile copia quella cartella. `writer_payload` è usato da `t3_personas`; `make_cards` serve alle fixture/smoke. `writer_prompt` non ha chiamanti individuati nel runtime/test: REVIEW per eventuale residuo storico, non rimozione provata. Lo scanner Python statico non dimostra l'assenza di utilizzatori esterni.

## Dati: originali, derivati e simulati

- Kit: `inserzionisti`, `campagne`, `adset`, `annunci`, `asset_creativi`, `storico_giornaliero`, `budget_giornaliero`, `calendario`, `cpm_storici`, benchmark settimanale e `da_prevedere`. Il kit è simulato dagli organizzatori; observed indica le etichette fornite, non dati reali raccolti da noi.
- Previsione/consegna: `forecasts_2026-11-16_30.csv`, metriche, evidenze audience, scenari e decisioni in `wevion_v4`. Le audience sono hypothesis, non identità delle personas.
- Pool: safe_inputs e jobs sono piani; responses e persona_cards sono schede effettivamente importate. Job presente non equivale a persona generata.
- Decision: `analyses/ledger.sqlite` è il registro operativo; `ledger.json` l'export; `requests/` e `raw/` sono prove da conservare; `assets/` e `summary.json` sono elaborazioni. Non cancellare il registro per liberare spazio: si rischia di pagare analisi ripetute.
- Interviste: jobs = input, responses = output/ricevute, frozen = congelamento, comparison = confronto successivo, analyst_notes/REPORT = interpretazione e verbatim. Non fornire comparison o analyst_notes all'intervistato.
- Smoke: file mock_not_model in `artifacts/market_mirror/` sono prove del plumbing, mai risultati Gemini.
- Replica: source/raw/models/results/catboost separano sorgenti, output, pesi e metriche. Il riproduttore importa anche il vecchio script CatBoost da uno snapshot Git: il candidato scanner CRT-001 è KEEP per questa provenienza.

## Ingombro e persistenza

Misure `du` arrotondate: artifacts 872 MiB, replica Timestral 867 MiB (venv 738 MiB, models 126 MiB), ambiente principale 189 MiB. Nessun file voluminoso è stato cancellato. Dimensioni allocate e byte logici differiscono.

`artifacts/` è interamente ignorata da Git: un commit del codice non salva risultati, ricevute, registri, modelli o interviste. Eseguire un backup esterno prima di qualunque pulizia; non aggiungere ambiente, modelli o `.env` indiscriminatamente al versionamento. `outputs/code-rot-cleaner/` e questa documentazione sono invece nuovi file non ancora committati.

## Contraddizioni da risolvere senza alterare le prove

1. README/manifest consegna: CatBoost pending; report replica successivo: confronto disponibile. Non riscrivere il vecchio manifest, che documenta la selezione effettivamente usata.
2. Default 72 slot contro 4 schede effettive: i job non eseguiti non sono risultati.
3. Dashboard unificata non prova che personas e forecast siano stati uniti nel backend.
4. Le domande diagnostiche sono proposte non eseguite; le interviste invece sono state completate.
5. La specifica v4 in root e due copie negli snapshot sono byte-identiche; le copie restano documenti di provenienza fino alla decisione di archivio.

## Riordino applicato

Approvati e applicati ORG-001, ORG-002 e ORG-003: 13 file spostati sotto archive, 137328 byte preservati, nessuna cancellazione. Inventario originale e conversazione restano snapshot anteriori; la corrispondenza fra percorsi vecchi e nuovi è in `outputs/code-rot-cleaner/applicazione_riordino.json`. Gli ambienti e i pesi non sono stati spostati.
