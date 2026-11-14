---
name: audit-marketmirror
description: Audita MarketMirror solo nel ramo di costruzione delle personas, feed test e orchestrazione provider; produce un piano di refactoring minimale.
---
# MarketMirror scoped audit
Read upstream `docs/TECHNICAL_GUIDE.md`, `docs/PROVIDERS_AND_SCALE.md`, `backend/app/services/persona_planner.py`, `fast_population.py`, `feed_test.py`, `predict.py` and their tests. Trace how slots, persona cards, interviews, identity seeds, provider lanes, prompt caching and feed choices are wired. Return a KEEP / ADAPT / EXCLUDE file+function-level map, with exact paths.
Never copy in OASIS, the graph/research pipeline, SSR surveys, Jev, marketing dashboard, landing browser. Explain provider model conventions and limits, licensing AGPL-3.0, and why `gemini-decision-1` needs its own adapter instead of an OpenAI-compatible chat backend.
Output: concise technical report + change set limited to persona modules; do not modify original upstream repository.
