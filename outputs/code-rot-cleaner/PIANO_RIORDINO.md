> **APPLICATO dopo approvazione dell’utente.** ORG-001, ORG-002 e ORG-003 completati; 13 file spostati con hash invariati. La sezione seguente conserva il piano originale. Ricevuta: `applicazione_riordino.json`.

# Piano di riordino — da approvare

Riordino documentale eseguito aggiungendo indice e dossier; sorgenti e artefatti esistenti preservati. Gli spostamenti qui sotto NON sono stati applicati. La skill code-rot-cleaner richiede approvazione esplicita dei candidati prima di rinominare/spostare il progetto reale.

## Proposed cleanup

| ID | File o cartella → destinazione | Evidenza / prova | Rischio |
|---|---|---|---|
| ORG-001 | `Specifica_Operativa_v3.md` → `archive/specifications/Specifica_Operativa_v3.md` | Storico/pacchetto non usato dal runtime corrente; nessuna prova dinamica, REVIEW | basso-medio |
| ORG-002 | `Wevion_Personas_Architettura_v1.zip` → `archive/source-packages/Wevion_Personas_Architettura_v1.zip` | Storico/pacchetto non usato dal runtime corrente; nessuna prova dinamica, REVIEW | basso-medio |
| ORG-003 | `Wevion_Personas_Skill_Starter/` → `archive/source-packages/Wevion_Personas_Skill_Starter/` | Storico/pacchetto non usato dal runtime corrente; nessuna prova dinamica, REVIEW | basso-medio |

Elenco esatto di ogni file, destinazione, byte e hash: `piano_spostamenti.json`. Spazio liberato previsto: **0 byte**, perché si propone archivio senza cancellazioni. Nessuna voce SAFE TO REMOVE.

## Materiale da conservare

- CRT-001: vecchio script baseline/CatBoost, KEEP per provenienza e replica.
- Architettura_v1/scripts, runtime, test, skill canoniche e kit: KEEP.
- Tutti i raw/registri/ricevute/personas/interviste: KEEP.
- Ambienti e pesi: ingombro principale, ma fuori da questa proposta; la loro rimozione impedirebbe riesecuzioni immediate.
- dashboard_unificata.html: file locale non tracciato di origine non ricostruita; KEEP.
- writer_prompt: REVIEW come possibile residuo; nessuna modifica proposta senza prova mirata.

## Controlli prima/dopo un eventuale spostamento

1. Salvare snapshot del worktree sporco e backup degli artefatti non in Git.
2. Verificare hash e collisioni di destinazione secondo piano; aggiornare i riferimenti documentali ai tre percorsi storici.
3. Test pertinenti: `.venv-market-mirror/bin/python -m unittest discover -s tests -v`; nessuna inferenza necessaria per questi spostamenti. Non eseguiti in questo audit.
4. Verificare link e diff; non toccare Test_Timestral, forecasting o file estranei.

Limiti: analisi statica senza esecuzione del progetto; scanner senza ambienti, artifacts, pesi e output. Lo scanner originale includeva erroneamente `.venv-market-mirror`: il risultato è stato sostituito con lo stesso scanner limitato alle sorgenti (walk con pruning e esclusioni esplicite). Nessun esperimento di rimozione in copia temporanea, nessuna rimozione provata.

Si richiede approvazione soltanto di ORG-001, ORG-002 e ORG-003 per applicare questi spostamenti; nessuna cancellazione.
