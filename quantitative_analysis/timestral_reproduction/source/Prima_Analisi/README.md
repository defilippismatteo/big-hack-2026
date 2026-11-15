# Prima analisi · Wevion BigHack 2026

Per questo pilota, **baseline a 14 giorni per il CTR e Timestral-28M per il CPM**. Nei due backtest la baseline ha avuto il CTR con l'errore più basso ponderato per impression. Il 28M ha ridotto l'errore CPM sullo stesso criterio e ha completato caricamento, due backtest e previsione in circa 11 secondi sul MacBook Air Intel con 8 GB di RAM. Il 5M ha impiegato circa 4 secondi.

## Verifica del branch

Il pilota proviene da `feat/timestral-pilot` al commit [`c0f0281`](https://github.com/defilippismatteo/big-hack-2026/commit/c0f02811724f8ab61e37d4e7a26035b4096e19f7). Sono stati eseguiti i 4 test del branch, la preparazione e l'inferenza locale. Il kit contiene 1.879 righe storiche, 12 ad set e 699 coppie univoche annuncio/giorno da prevedere dal 16 al 30 novembre, di cui 114 per 12 annunci nuovi. Per ciascun modello, tutte le chiavi coincidono con quelle richieste e le previsioni sono finite, con CTR nel range 0–100, CPM positivo e quantili ordinati.

L'analisi riusa le funzioni di previsione e baseline del branch. Il codice originale calcola anche un punteggio chiamato `timestral_direct_adset` confrontando ogni previsione di ad set con i singoli annunci. Qui il confronto diretto usa una riga per giorno e ad set e ricalcola i target come rapporti fra le somme di click, spesa e impression. Lo script indica anche l'identità dei pesi usati nel JSON. Nel comando originale, `preparation.json` e `run_summary.json` espongono il nome del modello predefinito anche se si passa `--model`. Le metriche per annuncio continuano a misurare il metodo del branch, che applica alla baseline gerarchica il rapporto fra previsione Timestral e storico recente dell'ad set. Il budget resta per ad set.

### Backtest cronologico

Il primo fold usa lo storico fino al 18 ottobre, il secondo fino al 1° novembre. CTR espresso in punti percentuali e CPM in euro. La tabella riporta l'errore assoluto medio ponderato per impression, calcolato sui dati **simulati** del kit.

| Finestra di verifica | Metodo | CTR per annuncio | CPM per annuncio | CTR per ad set | CPM per ad set |
| --- | --- | ---: | ---: | ---: | ---: |
| 19 ott – 1 nov · 315 righe | Baseline | **0,1977** | 0,7143 | **0,1574** | 0,6625 |
| | Timestral-5M | 0,2235 | 0,7013 | 0,1691 | 0,6577 |
| | Timestral-28M | 0,2020 | **0,6927** | 0,1781 | **0,6349** |
| 2–15 nov · 444 righe | Baseline | **0,2576** | 0,8022 | **0,1836** | 0,7479 |
| | Timestral-5M | 0,2859 | 0,7573 | 0,2111 | 0,6891 |
| | Timestral-28M | 0,2815 | **0,7067** | 0,2047 | **0,6045** |

Il CPM del 28M per annuncio migliora del **3,0%** e dell'**11,9%** nei due fold. Per gli annunci nuovi del secondo fold il CPM ponderato passa da **€1,2349** a **€1,0431**. La copertura osservata dei quantili CPM q10–q90 del 28M per annuncio è **82,5%** e **83,1%**. Per gli annunci nuovi scende rispettivamente a **66,7%** e **69,7%**. I quantili restano esplorativi. Il Black Friday è fuori dalle due finestre e una validazione su campagne reali richiede esiti osservati e confrontabili.

## Confronto con campagne pubbliche

| Settore | Settembre 2026, kit simulato | Riferimento pubblicato |
| --- | --- | --- |
| Beauty e skincare | CTR link 1,19%, CPM €8,44 | adtribute beauty, settembre 2026: 1,58% e €20,06 |
| Abbigliamento | CTR link 1,26%, CPM €6,96 | adtribute fashion, settembre 2026: 1,13% e €9,93 |
| Pet e-commerce | CTR link 1,36%, CPM €5,84 | Kanbar Digital, retailer pet USA: CTR link 0,77% dopo il cambio di obiettivo |

Il kit e il panel adtribute mostrano entrambi un CPM beauty più alto del fashion, con una differenza di livello più ampia nel panel. Il confronto serve a valutare la plausibilità e dipende da mercato, obiettivi e placement. Le fonti e i dettagli sono in [Fonti.md](Fonti.md).

### Scenari CPM per il 27 novembre

| Settore | Mediana delle previsioni per annuncio, 28M | Scenario Biddyco ×1,57 | Scenario Olifant ×2,12 |
| --- | ---: | ---: | ---: |
| Beauty e skincare | €13,70 | €14,76 | €19,93 |
| Abbigliamento | €12,60 | €12,14 | €16,39 |
| Pet e-commerce | €10,02 | €10,22 | €13,81 |

Gli scenari applicano i fattori dei due campioni pubblici al CPM del kit a ottobre 2026. Per il Cyber Monday lo stesso calcolo produce **€13,25** beauty, **€10,90** abbigliamento e **€9,18** pet (Biddyco ×1,41). Il confronto suggerisce pressione più alta sul CPM beauty e pet se si ripetono i rialzi dei campioni del 2025. Il CPM per settore del modello è qui la mediana semplice delle stime giornaliere per annuncio. Le impression future servirebbero per calcolare un CPM aggregato ponderato.

## File e riesecuzione in VS Code

- [analisi.py](analisi.py) esegue il confronto offline e genera i risultati.
- [previsioni_28m.csv](previsioni_28m.csv) contiene anche le colonne da usare per il pilota: `ctr_baseline_pct` e `cpm_timestral_p50`. [previsioni_5m.csv](previsioni_5m.csv) contiene il confronto con il modello più leggero. I due file includono q10, q50 e q90 per entrambi i KPI.
- [metriche.json](metriche.json) riporta ambiente, hash dei pesi, errori e copertura per fold, annunci nuovi e ad set.
- [scenari_cpm.csv](scenari_cpm.csv) contiene i moltiplicatori delle fonti. [cpm_scenari_evento.csv](cpm_scenari_evento.csv) contiene i risultati calcolati.

Nel Mac usato per la prova, aprire la cartella `Hackthon` in VS Code. Nel terminale integrato dalla root della cartella, eseguire:

```bash
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 HF_HUB_OFFLINE=1 PYTHONPATH=Test_Timestral \
  .cache/timestral-env/bin/python Prima_Analisi/analisi.py \
  --kit "Wevion BigHack - materiale challenger/dati" \
  --model-5m .cache/timestral-5m --model-28m .cache/timestral-28m \
  --output .cache/risultati-riproduzione
```

L'ambiente locale è Python 3.12 con PyTorch 2.7.1 CPU da conda-forge. In un altro checkout, creare un ambiente Python 3.12, installare le dipendenze da `Test_Timestral/requirements.txt` e usare il suo interprete. Su macOS Intel è disponibile la build CPU di conda-forge. Per il comando usare il percorso del kit originale (ZIP o directory), oppure `info fornite dagli organizzatori /dati` dal repository. Scaricare `config.json` e `model.safetensors` dai repository ufficiali di ciascun modello e passare i due percorsi locali. L'analisi dei pesi pubblicati è riproducibile con gli hash in `metriche.json`. [Timestral-5M](https://huggingface.co/mistralai/Timestral-5M) · [Timestral-28M](https://huggingface.co/mistralai/Timestral-28M)
