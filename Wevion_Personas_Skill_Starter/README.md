# Starter architetturale T3 Code / MarketMirror per Wevion

Questi file sono **skill di delegazione e contratti**, non moduli runtime già funzionanti. Copiare `.agents/skills` e `AGENTS.md` nella cartella principale del progetto, leggere le skill con `$`, riavviare la sessione e generare implementazioni una skill alla volta.

## Perché questo ordine
1. Audit MarketMirror senza portare dentro tutto OASIS. 2. Evidenze storiche con cut-off. 3. Audience hypotheses (obbligo della challenge). 4. Creatività + personas in parallelo. 5. Adapter Gemini Decision 1 / feed. 6. Validazione per ablation. 7. README e demo.

## Contratto di privacy e leakage
I divieti nei prompt non bastano a isolare le informazioni. Un processo coordinatore deve creare JSON ridotti per ciascuna skill e il codice runtime deve consegnare al modello **solo questi payload**, senza accesso libero al repository. Nei backtest, applicare il cutoff a OGNI passaggio, compresa la ricostruzione delle audience.

## Riutilizzo MarketMirror
- Riusa selettivamente `backend/app/services/persona_planner.py` (slot demografici, generazione fast, controlli diversità e cache), `feed_test.py` (normalizzazione creatività, assegnazione, abitudini stabili, feed/policy), parti di `predict.py` (guardrail senza real pairs); leggi `docs/HUMAN_BEHAVIOR_RESEARCH.md`.
- Adatta le chiamate chat del feed a un adapter `gemini-decision-1` che riceve shared input + domande per persona. Non inserire Decision 1 in un pool di chat LLM.
- Non includere nel MVP OASIS round/social simulation, knowledge graph da internet, HN/Reddit/App Store scraping, survey SSR, Jev, landing page browser, pitch pricing, benchmark ROI senza dati.
- MarketMirror licenza AGPL-3.0: verificare obblighi di distribuzione se incorpori codice, e documentare l'attribuzione.

## Risultato e test
Per ogni adset consegnare ipotesi motivata e spiegazione alternativa. Per la simulation produrre segnali separati dai CTR reali. Validare in test cronologico ad es. usando 01/11 come cutoff e 02–15/11 come holdout; dopo, rifare sui dati fino al 15/11. Non introdurre le personas nel modello forecast se non migliorano il confronto con baseline.
