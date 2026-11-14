---
name: wevion-persona-writer
description: Completa gli slot demografici generati in profili sintetici brevi, coerenti e non stereotipati usando Gemini 4 Hydrogen.
---
# Persona writer · Hydrogen
Inputs: one set of preassigned slots plus the sector's *general* description only. Forbidden: creatives, ad IDs, ad-set IDs, performance observations, inferred audience ranking, other personas' reactions, forecasting results. Keep both prompt and returned outputs away from those files.
`gemini-4-hydrogen` with `LOW` reasoning is a good starting setting for JSON output, but subscription availability and API quotas must be tested. The generator fills occupation, home context, interests, motivations, ad skepticism, trust requirements, a real-life contradiction and habits. Never ask whether they would click the specific challenge ad. Use compact profile/card, not 12-question deep interviews in the MVP. Return validated JSON for each persona with stable `persona_id`, `vertical`, `schema_version`, `seed`, `provider` and `model`; retry only missing/invalid records.
