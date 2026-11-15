# CatBoost e Timestral sullo storico Wevion

**Sviluppare il CPM con la media 50/50 di CatBoost e Timestral-28M. Tenere la baseline gerarchica a 14 giorni per il CTR.** La media riduce l'errore CPM in entrambe le finestre, anche per gli annunci nuovi. Per il CTR il metodo migliore cambia tra i due periodi. Il vantaggio aggregato della media sul CTR ponderato è circa 0,0004 punti percentuali.

## Risultati

Tutti i metodi sono valutati sulle stesse **759 righe annuncio/giorno** del kit simulato. Valori più bassi indicano errori minori. MAE significa errore assoluto medio. WMAE è lo stesso errore pesato per le impression della riga. Le impression del periodo di test sono usate qui solo per misurare l'errore a posteriori.

| Finestra | Metodo | MAE CTR (pp) | WMAE CTR (pp) | MAE CPM (€) | WMAE CPM (€) |
| --- | --- | ---: | ---: | ---: | ---: |
| 19 ott – 1 nov · 315 righe | Baseline | 0,2451 | **0,1977** | 0,7986 | 0,7143 |
| | CatBoost | 0,3536 | 0,3057 | 0,7122 | 0,6862 |
| | Timestral-28M | **0,2420** | 0,2020 | 0,7649 | 0,6927 |
| | Media 50/50 | 0,2507 | 0,2146 | **0,6975** | **0,6653** |
| 2–15 nov · 444 righe | Baseline | 0,3163 | 0,2576 | 1,0218 | 0,8022 |
| | CatBoost | **0,2743** | **0,2103** | 0,9274 | 0,7161 |
| | Timestral-28M | 0,3446 | 0,2815 | 0,8841 | 0,7067 |
| | Media 50/50 | 0,3023 | 0,2378 | **0,8741** | **0,6841** |
| Insieme · 759 righe | Baseline | 0,2868 | 0,2260 | 0,9292 | 0,7559 |
| | CatBoost | 0,3072 | 0,2606 | 0,8381 | 0,7004 |
| | Timestral-28M | 0,3020 | 0,2396 | 0,8346 | 0,6993 |
| | Media 50/50 | **0,2809** | **0,2256** | **0,8008** | **0,6742** |

Sul CPM, il mix riduce il WMAE del **10,8%** complessivo rispetto alla baseline e del **3,6%** rispetto a Timestral-28M, il migliore dei due modelli singoli sul totale. Sugli annunci nuovi il WMAE del CPM passa da **€0,9011 a €0,7721** nella prima finestra e da **€1,2349 a €1,0303** nella seconda. Sul CTR dei nuovi annunci, la baseline vince nella prima finestra e CatBoost nella seconda. I pesi del mix sono fissati a 50/50 per entrambi i KPI senza ottimizzarli sui risultati. L'aggregato è calcolato direttamente sulle 759 righe, con le rispettive impression.

## Verifica temporale

- Lo script CatBoost originale riproduce i valori pubblicati a quattro decimali in entrambe le finestre. Il training termina il 18 ottobre e il 1° novembre. Il CatBoost del confronto riusa le feature e gli iperparametri originali, senza passare a `fit` le righe o le etichette del test. Il target è il logit del CTR con correzione per i conteggi a zero e il log del CPM del kit, arrotondato a quattro decimali.
- Per il training, i segnali storici per annuncio, asset, ad set e settore escludono il giorno corrente tramite uno shift. Per il test le medie delle ultime sette osservazioni sono congelate al cutoff. L'audit ha azzerato gli outcome dopo ogni cutoff e controllato che matrici CatBoost, contesto e covariate Timestral rimanessero identici. Ha verificato anche l'invarianza delle feature CatBoost del giorno stesso alle estremità del training.
- Le coppie annuncio/giorno coincidono con il calendario di lancio e fine del kit. Il budget per ogni coppia ad set/giorno coincide con la tabella separata dei budget. Il backtest assume che il piano degli annunci e i budget fossero disponibili a ogni cutoff. In un uso reale servono le versioni del piano salvate a quella data.
- CatBoost vede nel training feature aggiornate ogni giorno, mentre in previsione le mantiene congelate per 14 giorni. La prossima prova sul CTR dovrebbe ricreare in training origini di previsione e orizzonti da 1 a 14 giorni, poi confrontare le prestazioni per orizzonte su una finestra cronologica indipendente. Prima di usare il mix CPM per decisioni Black Friday, verificare anche un periodo promozionale con esiti osservati. Le due finestre di questo test precedono il Black Friday.

## Riproduzione

In VS Code, eseguire il task **Wevion: confronta CatBoost e Timestral** dalla palette dei comandi. Dal terminale, con l'ambiente e i pesi locali già scaricati:

```bash
.cache/timestral-env/bin/python -m pip install -r Prima_Analisi/requirements-catboost.txt
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 HF_HUB_OFFLINE=1 PYTHONPATH=Test_Timestral \
  .cache/timestral-env/bin/python Prima_Analisi/valida_modelli.py \
  --kit "Wevion BigHack - materiale challenger/dati" \
  --model-28m .cache/timestral-28m --output .cache/validazione-riproduzione
```

[Metriche del backtest](metriche.json) · [Righe del primo fold](previsioni_2026-10-19.csv) · [Righe del secondo fold](previsioni_2026-11-02.csv) · [Script di validazione](../valida_modelli.py)
