# Wevion Persona Engine · starter v1

This starter is a **scoped design + runnable, offline, no-key data preparation prototype**. It is *not* a fork or a complete ADERA engine. It implements sector-level safe contexts, balanced deterministic slots, creative-only catalog, and batched request generation for Gemini Decision 1. No live decision inference was executed here; optional runner requires a personal Gemini API key and official Google SDK.

## First dry run

```bash
cd Wevion_Personas_Architettura_v1
export WEVION_DATA_DIR='/path/to/Wevion BigHack - materiale challenger/dati'
DATA="$WEVION_DATA_DIR"
python scripts/prepare_safe_inputs.py --data-dir "$DATA" --out examples/persona_only/public_context.json
python scripts/make_slots.py --context examples/persona_only/public_context.json --n-per-vertical 24 --out examples/persona_only/persona_slots.json
python scripts/build_creative_catalog.py --data-dir "$DATA" --out examples/decision_only/creative_catalog.json
python scripts/decision1_requests.py --creatives examples/decision_only/creative_catalog.json --personas examples/persona_only/persona_slots.json --asset-id NDL-S1 --out examples/decision_only/decision1_NDL-S1.json
python scripts/run_decisions.py --request examples/decision_only/decision1_NDL-S1.json --out examples/decision_only/raw_response.json  # dry run
python scripts/test_contracts.py  # validates deterministic slots, isolation, creative catalog
```

`persona_slots.json` contains only deterministic specifications, not finished natural-language people; `wevion-persona-writer` must expand them before a real study. This simple request generator can accept either slots or finished cards, but the latter is recommended for genuine persona-dependent behavior.

## Live Decisions API probe (optional)

Use a **separate** Google AI Studio API key, verify availability, and test only 4 people and 1 asset first. `google-genai` must expose `client.decisions.create` with `api_version='v1beta'`. The SDK response is saved verbatim; schema parsing must be written after observing an actual response.

```bash
python -m pip install -U google-genai
export GEMINI_API_KEY='YOUR_KEY'
python scripts/run_decisions.py --request examples/decision_only/decision1_NDL-S1.json --out examples/decision_only/raw_response.json --live
```

The subscription used by T3 Code / Antigravity does not automatically provide Gemini API calls. The Gemini Decisions API is separate from a normal chat/completions endpoint.

## Security boundary

For the demo the scripts are safe-by-construction, because they read only allowlisted files. For a strict guarantee, execute the generator and decision worker inside a runtime in which the other files **are not mounted**. `.agents/skills` files only describe desired behavior; they cannot enforce OS-level file restrictions.

## What goes back to the forecasting team

`signal_by_asset_and_persona`: action-choice probabilities, reason-choice probabilities, provider, batch/run ID, seed and input hash. Distinguish per-person simulated choices from observed click/impression data. The analyst may fit ad-set-specific weights using training-period history separately. Personas do not receive these weights or labels.

**Development-only audit:** `dev_audit/data_map.json` records the complete organizer-file linkage, including ad/set IDs and whether an ad has history. It is NOT safe for the blind persona generator. Never mount `dev_audit/` into either runtime.
