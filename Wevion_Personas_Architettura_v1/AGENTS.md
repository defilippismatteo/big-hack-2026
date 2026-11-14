# Wevion · Persona branch — T3 Code / coding agents

Scope: design and implement only the **outcome-blind persona generation and Gemini Decision 1 evaluation**. Predictive CTR/CPM and audience inference based on historical data are separate modules owned by the forecasting/analytics team.

## Data governance
- The persona generation runtime has access only to `safe_inputs/public_context.json`, `safe_inputs/persona_slots.json`, and eventually vetted `persona_cards.json`. It must not read `dati/storico_giornaliero.csv`, `cpm_storici.csv`, `benchmark_mercato_settimanale_2025.csv`, `budget_giornaliero.csv`, `da_prevedere.csv`, or any calibration/forecaster output.
- The synthetic generator never receives creative descriptions, headlines, ad IDs, ad set IDs, real metrics, or audience hypotheses reverse-engineered from outcomes. It receives only the sector context + deterministic slots.
- Decision 1 receives one sanitized creative, one standalone persona per question, and generic feed exposure context. No history, no model forecast, no other persona answers.
- T3 Code SKILL.md file instructions are *not* a security barrier. Enforce isolation via explicit JSON projections and separate process/container/OS permissions; a coding agent with full repository access cannot be isolated merely by these instructions.
- Provenance: `observed`, `hypothesis`, `synthetic`, `simulated_decision` must be separated. Never call simulated `p_click` a measured CTR.
- Backtests must run all inference and aggregation at the corresponding historical cut-off; no leakage from later data.

## Delivery sequence
1. Validate safe data contracts via `python scripts/test_contracts.py` (requires a copy of the organizer data in the documented location).
2. Build the generic sector-level persona pool (`24` people per vertical suggested, 72 in total); keep the seed fixed.
3. Use Gemini 4 Hydrogen with `LOW` thinking for a short JSON card of each person, not 12-question interviews on all slots. Preserve a provider-neutral structure.
4. Run one single-asset / 4-person Gemini Decision 1 live probe before batching.
5. Preserve raw per-person probabilities and criteria-level reasons; analytics decides if/how they affect forecasting, not this branch.

## MarketMirror upstream
Study `persona_planner.py`, `fast_population.py`, `feed_test.py`, `docs/PROVIDERS_AND_SCALE.md`, `docs/HUMAN_BEHAVIOR_RESEARCH.md`. Do not bring OASIS, graph memory, full interview pipeline, surveys, Jev, website tests, or original CTR extrapolation into the MVP. If code is copied, preserve AGPL-3.0 notices and review distribution obligations.
