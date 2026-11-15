---
name: wevion-persona-signals
description: Verifica e aggrega output probabilistici della Decisions API senza confonderli con CTR/CPM pubblicitari.
---
# Signal aggregation · no feedback LLM
Only normalized Decision 1 outputs, input provenance, seeds and persona weights manually defined in the generic pool. Check probability mass, missing responses, confidence, per-person independence, repeated-seed stability and coverage by vertical. Export scores `attention_signal`, `click_intent_signal`, `top_reason_distribution` keyed by **asset_id** with uncertainty and a synthetic/uncalibrated marker. Do not use a generative model to invent individual feedback. No direct calibration on `storico_giornaliero.csv`: pass signals to the analytics/forecast team via a strict interface, where adset-specific reweighting and historical fitting are permitted only on train-period data.
