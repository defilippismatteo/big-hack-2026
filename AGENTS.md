# ADERA — Orchestrazione multi-agente con T3 Code

Architettura modulare del progetto ADERA (Big Hack 2026 — Wevion *Clienti che non esistono*):

- **Analisi quantitativa (`quantitative_analysis/`)**: baseline gerarchica 14g, validazione cronologica CatBoost + Mistral Timestral-5M/28M, ensemble Mix 50/50 + arricchimento Black Friday anti-doppio-conteggio, motore di riallocazione budget ±20% e delivery v4 (`python3 -m quantitative_analysis.pipeline.delivery`).
- **Simulazione personas (`personas_simulation/`)**: generazione *outcome-blind* (`simulation_blind`) di 600 personas (50% `unbiased`, 50% `category_conditioned` critiche) via subagenti T3/Antigravity, valutazioni isolate con **Gemini Decision 1** (`v1beta`) e 600 interviste cieche (`python3 -m personas_simulation.runtime`).
- **Dashboard esplicativa (`dashboard/`)**: interfaccia React/Vite + preview offline standalone (`dashboard/preview.html#/overview`). È puramente esplicativa e non esegue inferenza live né azioni autonome: tutta l'orchestrazione attiva è affidata al coding agent.
- **Skill canoniche (`skills/` e `.agents/skills/`)**: workflow modulari usati da T3 Code per generazione, validazione, segnali, delivery e produzione video.
- **Dati acquisiti (`data/`)**: kit della challenge, 699 previsioni, metriche di backtest, 600 schede persona, 7.200 valutazioni Decision 1 e 600 interviste cieche.
- **Video (`video/`)**: montaggio unificato 150s, asset grafici, copione, tracce audio e script di rendering.

## Regole di separazione e integrità
- I segnali sintetici (`attention_signal`, `click_intent_signal`) hanno `calibrated_to_ctr: false` e non vengono mai iniettati come CTR misurato né usati per alterare i forecast quantitativi.
- I dati esterni di mercato sono usati esclusivamente per validazione di plausibilità ex-post e scenari di stress test, mai per l'inferenza/addestramento dei modelli predittivi.
- Le persone sintetiche e le interviste cieche sono generate e condotte senza esposizione a CTR/CPM osservati, forecast o risposte altrui.
