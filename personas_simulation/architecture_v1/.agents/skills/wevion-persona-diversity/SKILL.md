---
name: wevion-persona-diversity
description: Progetta il campionamento eterogeneo e riproducibile delle persone fittizie senza utilizzare risultati pubblicitari o ad set.
---
# Outcome-blind diversity
Inputs ONLY `safe_inputs/public_context.json` and a documented `manual_priors.json`. Do not read the organizer's outcome tables. No ad-set or asset IDs, headlines, historical CTR/CPM or inferred ad-set winners.
Use deterministic age-band and gender-identity quotas, interests (including disengaged people), economic attitudes, tech comfort, ad avoidance, uncertainty in latent weights, different routines and skepticism. Distinguish **manual assumed sampling weights** from observed population shares (none are available). Verify coverage, uniqueness, fixed seed, weight sums and repeatability. Output `persona_slots.json` for Hydrogen and metrics on diversity; reject unjustified demographic facts.
