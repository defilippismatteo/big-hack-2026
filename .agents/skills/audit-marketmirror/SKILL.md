---
name: audit-marketmirror
description: Confronta il ramo personas e feed di MarketMirror con lo scheletro Wevion e propone riuso limitato e verificabile.
---

Upstream: https://github.com/DarkWorldCoder/market-mirror.
Leggi persona_planner.py, fast_population.py, feed_test.py, PROVIDERS_AND_SCALE.md
e HUMAN_BEHAVIOR_RESEARCH.md. Parti dall'audit in docs/MARKET_MIRROR_GUIDA.md.
Traccia slot, schede, assegnazione creatività, visibilità, social proof, provider,
attenzione imposta dal codice e aggregazione expected_ctr. Non assumere che
quest'ultimo sia un CTR calibrato su dati umani.
Proponi KEEP/ADAPT/EXCLUDE con file e funzione. Non importare OASIS, scraping,
survey o grafo di memoria nel prototipo senza un requisito concreto.
Non modificare upstream o forecasting. Codice copiato da MarketMirror è AGPL-3.0:
preserva notice e gestisci gli obblighi; il runtime corrente riusa solo lo starter
locale, senza incorporare codice upstream.
