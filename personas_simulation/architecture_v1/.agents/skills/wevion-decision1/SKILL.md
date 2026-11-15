---
name: wevion-decision1
description: Implementa l'adapter che invia una creatività per richiesta e più domande indipendenti alla Gemini Decisions API.
---
# Simulated decisions only · Gemini Decision 1
Inputs: `creative_catalog` from organizer's **textual** creative descriptions, `persona_cards`, normal Meta-feed exposure instruction. Never expose performance history, ad-set KPI, budget forecast, other personas' responses. API access through `client.decisions.create(model='gemini-decision-1', input=[...], questions={...})` using `google-genai` `v1beta`; model is *not* a text-generator or a ADERA chat provider.
Each persona generates ONE `choice` question with mutually exclusive `action__reason` options. Marginalize outcome probabilities to obtain action probabilities and reason distribution; this prevents a click outcome from having a separately classified 'scroll-because-busy' reason. Group many independent persona questions under one creative's shared input. Save raw probabilities, decisions and confidence; do not produce verbal 'interviews' from Decision 1. Start with 4 personas and one creative, inspect actual SDK response fields before making a parser; API usage requires separate credentials. On uncertainty choose 'unknown/insufficient evidence' and record rather than manufacture results. Never present predicted human CTR as calibrated.
