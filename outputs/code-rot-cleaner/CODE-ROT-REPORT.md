> Riordino approvato applicato: ORG-001, ORG-002 e ORG-003, 13 file archiviati con contenuto invariato; 43 test superati. Zero cancellazioni. Ricevuta: `applicazione_riordino.json`. Lo screening statico sottostante resta lo snapshot precedente.

# Code Rot Report

> **REPORT READY** — The real project was not changed.

Project: `/Users/fede/Documents/Progetti/hackathon/big-hack-2026`  
Generated: `2026-11-14T15:03:30Z`

## Executive summary

| Result | Candidates | LOC | Size |
|---|---:|---:|---:|
| SAFE TO REMOVE | 0 | 0 | 0 B |
| REVIEW | 0 | 0 | 0 B |
| KEEP | 1 | 129 | 7.5 KB |

## Ranked candidates

| ID | Status | Category | Subject | Confidence | Risk | LOC | Proof |
|---|---|---|---|---|---|---:|---|
| CRT-001 | **KEEP** | orphan-file | `TEST INIZIALI FATTI DA CHAT GPT DA VERIFICARE /Wevion_Validation_Baseline.py` | medium | medium | 129 | Sorgente del confronto CatBoost: citato in docs/TIMESTRAL_REPLICA_E_STATO_V4.md e nel riproduttore; assenza di import statico non prova inutilizzo. |

## Evidence by candidate

### CRT-001 — KEEP

- Location: `TEST INIZIALI FATTI DA CHAT GPT DA VERIFICARE /Wevion_Validation_Baseline.py`
- Category: `orphan-file`
- Potential size: 129 LOC / 7.5 KB
- Status reason: Sorgente del confronto CatBoost: citato in docs/TIMESTRAL_REPLICA_E_STATO_V4.md e nel riproduttore; assenza di import statico non prova inutilizzo.
- Evidence: No resolved static inbound import was found. The file is not a detected package or conventional entry point. Repository text contains possible string/name references: Wevion_Validation_Baseline, Wevion_Validation_Baseline.py.
- Caveats: Dynamic loading, reflection, external consumers, or incomplete framework detection can hide reachability. Possible string reachability prevents high-confidence deletion.

## Cleanup approval checklist

No cleanup has been applied. To continue, select exact candidate IDs and review their paths, evidence, proof, and residual risk. Manifest or lockfile changes require separate explicit approval.

```text
Approved candidate IDs: ____________________
Approved files / manifest entries: __________
Approved verification commands: _____________
```

## Scope and limitations

- Scanned 32 source files, 2,662 LOC, 171.8 KB.
- Static analysis cannot prove absence of dynamic, reflective, operational, platform-specific, or external use.
- JavaScript/TypeScript and Python import resolution is intentionally conservative and does not implement every alias or framework convention.
- Unused dependencies and exports are leads only until project-native tooling and focused proof support removal.
- No project code, package command, or dependency was executed by this scanner.
