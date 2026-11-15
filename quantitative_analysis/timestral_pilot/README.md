# Test_Timestral: primo pilot Wevion (Challenge 01)

**Obiettivo:** verificare empiricamente Timestral-28M zero-shot sui numeri del kit, senza usare outcome futuri. Questo è un esperimento P1: per la consegna i risultati vanno confrontati con baseline e CatBoost P0, non scelti per il nome del modello.

## Input e ipotesi

- 1.879 righe storiche giornaliere fino al 15/11/2026.
- 12 ad set con 91 giorni storici; le serie sono aggregate ogni giorno per ad set.
- CTR aggregato = 100 × somma(click) / somma(impression), CPM = 1000 × somma(spesa) / somma(impression).
- Timestral: contesto (12, 2, T), con T = 63 / 77 / 91 nei due fold e nel forecast finale.
- Covariate note sia nel passato sia nel futuro: budget giornaliero **per ad set** (non per annuncio), indici mercato 2025 relativi a CTR/CPM riallineati di 364 giorni, weekend, Black Week, Black Friday, Cyber Monday. Sono solo dati disponibili al cutoff. Gli indici 2025 non sono esiti della campagna 2026.
- Periodo da prevedere: 699 righe annuncio/giorno dal 16 al 30 novembre (inclusi nuovi annunci e nuove creatività).

Il pilot produce anche un forecast ad-level tramite adattatore: la baseline gerarchica a 14 giorni per annuncio/asset/ad set/verticale viene moltiplicata per il rapporto Timestral (CTR o CPM atteso dell'ad set / CTR o CPM storico dell'ad set). Fattori limitati ex ante a 0,25–4 per sicurezza. Questa è **un'euristica**: è il backtest, non un'ipotesi, a stabilire se funziona. Il forecast direttamente a livello ad set è valutato separatamente.

## Esecuzione dalla root della repository

Il kit è disponibile in main sotto la cartella «info fornite dagli organizzatori /dati»; lo script accetta anche l'archivio ZIP originale senza estrarlo. Non è necessario duplicare i CSV.

~~~bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r Test_Timestral/requirements.txt
python -m unittest discover -s Test_Timestral -p 'test_*.py' -v

# Analisi input senza modello o download
python Test_Timestral/timestral_pilot.py --kit "info fornite dagli organizzatori /dati" --mode prepare

# Due backtest e previsione delle 699 righe (prima esecuzione scarica Timestral-28M)
python Test_Timestral/timestral_pilot.py --kit "info fornite dagli organizzatori /dati" --mode all --device cpu
~~~

Alternative: --kit "/percorso/Wevion BigHack - materiale challenger-20261114T110351Z-1-001.zip", --mode backtest, --mode forecast, --output /altro/percorso, --offline (solo da cache locale), --model mistralai/Timestral-5M per uno smoke test con meno risorse.

File generati localmente in Test_Timestral/outputs/ (ignorati da git):
- preparation.json: verifica forme e orizzonti, senza inferenza;
- backtest_2026-10-19_2026-11-01.csv e backtest_2026-11-02_2026-11-15.csv;
- backtest_metrics.json: MAE CTR (punti percentuali), MAE CPM (euro), WMAE pesati per impression, metriche cold start e copertura q10–q90;
- forecast_2026-11-16_30.csv: 699 righe con chiavi originali, baseline, Timestral diretto, valori ad-level adattati e quantili;
- run_summary.json.

Due finestre cronologiche: (1) allenamento/contesto fino al 18 ottobre → validazione 19 ottobre–1 novembre, (2) fino al 1 novembre → validazione 2–15 novembre. I test devono impedire il leakage: per tutti i metodi le label durante la validazione non entrano nel contesto. Il periodo Black Friday 27/11 non è osservato nello storico: i quantili adattati non sono intervalli calibrati e vanno dichiarati esplorativi.

## Criteri di validazione

I 699 output devono avere esattamente le coppie (data, ad_id) dell'input, senza duplicati o null, CTR nel range [0, 100], CPM > 0. Il budget è a livello ad set, mai duplicato come spesa per ogni annuncio. Le previsioni per annunci nuovi usano fallback di asset/ad set/verticale.

Non considerare Timestral adottato per l'MVP se il suo MAE non migliora i benchmark. L'attuale baseline/CatBoost sperimentale è nella directory «TEST INIZIALI FATTI DA CHAT GPT DA VERIFICARE » e va verificato indipendentemente. Non utilizzare agenti sintetici per produrre automaticamente valori percentuali di CTR/CPM.

Versioni: codice Timestral installato da commit GitHub a534bdbd244d64f3d9d743f46c7bf6fc330ed4ff, pesi su Hugging Face mistralai/Timestral-28M. Codice Apache 2.0 e pesi con Modified MIT separata; vedi https://github.com/mistralai/timestral. Ambiente: Python >=3.10, PyTorch >=2.4 via dipendenze Timestral.
